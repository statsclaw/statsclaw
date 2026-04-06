#!/usr/bin/env python3
"""Parse a PDF academic paper using the MinerU API.

This script uploads a PDF to the MinerU API, polls for completion,
downloads the structured output (Markdown + JSON), and extracts it
to the specified output directory.

Usage:
    python parse_paper.py --input paper.pdf --output ./output/
    python parse_paper.py --check-token
"""

import argparse
import hashlib
import json
import os
import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = "https://mineru.net/api/v4"
DEFAULT_MODEL = "vlm"
DEFAULT_TIMEOUT = 600  # 10 minutes
POLL_INTERVAL = 5  # seconds
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB
MAX_PAGES = 600

# Exit codes (documented in SKILL.md)
EXIT_TOKEN_MISSING = 1
EXIT_TOKEN_INVALID = 2
EXIT_FILE_TOO_LARGE = 3
EXIT_FILE_TOO_MANY_PAGES = 4
EXIT_API_TIMEOUT = 5
EXIT_PARSE_FAILURE = 6
EXIT_EMPTY_EXTRACTION = 7
EXIT_QUOTA_EXCEEDED = 8
EXIT_NETWORK_ERROR = 9

# ---------------------------------------------------------------------------
# Token management
# ---------------------------------------------------------------------------


def _find_env_file() -> str | None:
    """Search for .env file in current directory and up to 5 parents."""
    path = Path.cwd()
    for _ in range(6):
        env_path = path / ".env"
        if env_path.is_file():
            return str(env_path)
        parent = path.parent
        if parent == path:
            break
        path = parent
    return None


def _read_token_from_env_file(env_path: str) -> str | None:
    """Read MINERU_API_TOKEN from a .env file."""
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip("'\"")
                if key in ("MINERU_API_TOKEN", "mineru_api"):
                    return value
    return None


def get_token() -> str | None:
    """Retrieve MinerU API token using priority: env var → .env file."""
    # Priority 1: environment variable
    token = os.environ.get("MINERU_API_TOKEN")
    if token:
        return token

    # Priority 2: .env file
    env_path = _find_env_file()
    if env_path:
        token = _read_token_from_env_file(env_path)
        if token:
            return token

    return None


def verify_token(token: str) -> bool:
    """Verify the token is valid with a lightweight API call."""
    try:
        req = Request(
            f"{API_BASE}/user/info",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data.get("code") == 0
    except (HTTPError, URLError, json.JSONDecodeError):
        return False


# ---------------------------------------------------------------------------
# File validation
# ---------------------------------------------------------------------------


def validate_file(path: str) -> None:
    """Check file size and basic accessibility."""
    p = Path(path)
    if not p.is_file():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(EXIT_PARSE_FAILURE)

    size = p.stat().st_size
    if size > MAX_FILE_SIZE:
        mb = size / (1024 * 1024)
        print(
            f"Error: File too large ({mb:.1f} MB). Maximum is 200 MB.",
            file=sys.stderr,
        )
        sys.exit(EXIT_FILE_TOO_LARGE)


def file_sha256(path: str) -> str:
    """Compute SHA-256 hash of a file for caching."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


def get_cache_dir(output_dir: str) -> Path:
    """Return the cache directory, creating it if needed."""
    cache = Path(output_dir).parent / "paper-cache"
    cache.mkdir(parents=True, exist_ok=True)
    return cache


def check_cache(cache_dir: Path, sha: str) -> Path | None:
    """Check if a cached result exists for the given file hash."""
    cached = cache_dir / sha
    if cached.is_dir() and (cached / "content_list.json").is_file():
        return cached
    return None


# ---------------------------------------------------------------------------
# MinerU API interaction
# ---------------------------------------------------------------------------


def upload_file(token: str, file_path: str, model: str) -> str:
    """Upload a PDF to MinerU and return the task ID."""
    import mimetypes
    boundary = f"----PythonBoundary{int(time.time())}"
    filename = Path(file_path).name
    content_type = mimetypes.guess_type(file_path)[0] or "application/pdf"

    with open(file_path, "rb") as f:
        file_data = f.read()

    # Build multipart body
    parts = []

    # File part
    parts.append(f"--{boundary}".encode())
    parts.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode()
    )
    parts.append(f"Content-Type: {content_type}".encode())
    parts.append(b"")
    parts.append(file_data)

    # Model part
    parts.append(f"--{boundary}".encode())
    parts.append(b'Content-Disposition: form-data; name="model"')
    parts.append(b"")
    parts.append(model.encode())

    # Enable formula
    parts.append(f"--{boundary}".encode())
    parts.append(b'Content-Disposition: form-data; name="enable_formula"')
    parts.append(b"")
    parts.append(b"true")

    # Enable table
    parts.append(f"--{boundary}".encode())
    parts.append(b'Content-Disposition: form-data; name="enable_table"')
    parts.append(b"")
    parts.append(b"true")

    parts.append(f"--{boundary}--".encode())
    body = b"\r\n".join(parts)

    req = Request(
        f"{API_BASE}/file_parse",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode(errors="replace")
        if "quota" in body.lower() or "limit" in body.lower():
            print(
                "Error: Daily quota exceeded. Wait until tomorrow or use local MinerU.",
                file=sys.stderr,
            )
            sys.exit(EXIT_QUOTA_EXCEEDED)
        if "A0211" in body:
            print(
                "Error: Token expired. Please regenerate at https://mineru.net",
                file=sys.stderr,
            )
            sys.exit(EXIT_TOKEN_INVALID)
        print(f"Error: Upload failed: {e.code} {body}", file=sys.stderr)
        sys.exit(EXIT_PARSE_FAILURE)
    except URLError as e:
        print(f"Error: Network error during upload: {e.reason}", file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)

    if data.get("code") != 0:
        print(f"Error: API error: {data.get('msg', 'unknown')}", file=sys.stderr)
        sys.exit(EXIT_PARSE_FAILURE)

    task_id = data.get("data", {}).get("task_id")
    if not task_id:
        print("Error: No task_id in API response.", file=sys.stderr)
        sys.exit(EXIT_PARSE_FAILURE)

    return task_id


def poll_task(token: str, task_id: str, timeout: int) -> dict:
    """Poll for task completion. Returns the task result."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = Request(
                f"{API_BASE}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except (HTTPError, URLError) as e:
            print(f"Warning: Poll error: {e} — retrying...", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        status = data.get("data", {}).get("status", "unknown")
        if status == "completed":
            return data.get("data", {})
        if status == "failed":
            msg = data.get("data", {}).get("error", "unknown error")
            print(f"Error: Parse failed: {msg}", file=sys.stderr)
            sys.exit(EXIT_PARSE_FAILURE)

        elapsed = int(time.time() - start)
        print(f"  Parsing... ({status}, {elapsed}s elapsed)", file=sys.stderr)
        time.sleep(POLL_INTERVAL)

    print(
        f"Error: API timeout after {timeout}s. Task {task_id} still not complete.",
        file=sys.stderr,
    )
    sys.exit(EXIT_API_TIMEOUT)


def download_result(token: str, task_id: str, output_dir: str) -> Path:
    """Download and extract the task result ZIP."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    req = Request(
        f"{API_BASE}/tasks/{task_id}/result",
        headers={"Authorization": f"Bearer {token}"},
    )

    try:
        with urlopen(req, timeout=120) as resp:
            content = resp.read()
    except (HTTPError, URLError) as e:
        print(f"Error: Download failed: {e}", file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)

    # Extract ZIP
    try:
        with zipfile.ZipFile(BytesIO(content)) as zf:
            zf.extractall(output)
    except zipfile.BadZipFile:
        # Might be JSON directly (some API versions)
        result_path = output / "content_list.json"
        result_path.write_bytes(content)

    print(f"Results extracted to {output}", file=sys.stderr)
    return output


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Parse a PDF academic paper using the MinerU API."
    )
    parser.add_argument("--input", help="PDF file path")
    parser.add_argument("--output", help="Output directory for results")
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        choices=["vlm", "pipeline"],
        help="Parse model (default: vlm)",
    )
    parser.add_argument(
        "--check-token",
        action="store_true",
        help="Validate token and exit",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"API timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    args = parser.parse_args()

    # Get token
    token = get_token()
    if not token:
        print(
            "Error: MinerU API token not found.\n"
            "Set MINERU_API_TOKEN environment variable or add it to a .env file.\n"
            "Get your token at https://mineru.net",
            file=sys.stderr,
        )
        sys.exit(EXIT_TOKEN_MISSING)

    # Token check mode
    if args.check_token:
        if verify_token(token):
            print("Token is valid.", file=sys.stderr)
            # Output token source for credential verification
            source = "env" if os.environ.get("MINERU_API_TOKEN") else ".env"
            print(json.dumps({"valid": True, "source": source}))
            sys.exit(0)
        else:
            print("Error: Token is invalid or expired.", file=sys.stderr)
            sys.exit(EXIT_TOKEN_INVALID)

    # Validate arguments
    if not args.input or not args.output:
        parser.error("--input and --output are required for parsing")

    # Validate file
    validate_file(args.input)

    # Check cache
    sha = file_sha256(args.input)
    cache_dir = get_cache_dir(args.output)
    cached = check_cache(cache_dir, sha)
    if cached:
        print(f"Using cached result from {cached}", file=sys.stderr)
        # Copy cached result to output
        import shutil
        output = Path(args.output)
        if output != cached:
            output.mkdir(parents=True, exist_ok=True)
            for item in cached.iterdir():
                dest = output / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
        print(json.dumps({"cached": True, "sha256": sha, "output": str(output)}))
        sys.exit(0)

    # Upload and parse
    print(f"Uploading {args.input} (model={args.model})...", file=sys.stderr)
    task_id = upload_file(token, args.input, args.model)
    print(f"Task ID: {task_id}", file=sys.stderr)

    # Poll for completion
    result = poll_task(token, task_id, args.timeout)
    print("Parse complete. Downloading results...", file=sys.stderr)

    # Download results
    output_path = download_result(token, task_id, args.output)

    # Cache the result
    import shutil
    cache_entry = cache_dir / sha
    if cache_entry != output_path:
        cache_entry.mkdir(parents=True, exist_ok=True)
        for item in output_path.iterdir():
            dest = cache_entry / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    # Output summary
    content_list = output_path / "content_list.json"
    if content_list.is_file():
        with open(content_list) as f:
            data = json.load(f)
        count = len(data) if isinstance(data, list) else 0
        print(f"Extracted {count} content elements.", file=sys.stderr)
    else:
        print("Warning: content_list.json not found in output.", file=sys.stderr)

    print(
        json.dumps(
            {
                "cached": False,
                "sha256": sha,
                "task_id": task_id,
                "output": str(output_path),
            }
        )
    )


if __name__ == "__main__":
    main()
