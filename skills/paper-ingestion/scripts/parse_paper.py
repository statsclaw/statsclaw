#!/usr/bin/env python3
"""Parse a PDF academic paper using the MinerU API.

This script uploads a PDF to the MinerU API, polls for completion,
downloads the structured output (Markdown + JSON), and extracts it
to the specified output directory.

MinerU API flow (v4):
  1. POST /api/v4/file-urls/batch  → get presigned upload URL + batch_id
  2. PUT  <presigned_url>          → upload raw file bytes
  3. GET  /api/v4/extract-results/batch/<batch_id>  → poll until done
  4. GET  <full_zip_url>           → download result ZIP

Usage:
    python parse_paper.py --input paper.pdf --output ./output/
    python parse_paper.py --check-token
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

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
    """Verify the token by attempting a lightweight batch request.

    MinerU has no dedicated /user/info endpoint. We verify by requesting
    a file-urls batch with a dummy file — a valid token returns code 0,
    an invalid one returns A0202/A0211 error codes.
    """
    body = json.dumps({
        "files": [{"name": "token_check.pdf", "is_ocr": False}],
        "model_version": "vlm",
    }).encode()

    req = Request(
        f"{API_BASE}/file-urls/batch",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("code") == 0
    except HTTPError as e:
        err_body = e.read().decode(errors="replace")
        if "A0202" in err_body or "A0211" in err_body:
            return False
        # Other HTTP errors — could be rate limit etc, treat as indeterminate
        return False
    except (URLError, json.JSONDecodeError):
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
    if cached.is_dir() and (
        (cached / "content_list_v2.json").is_file()
        or (cached / "content_list.json").is_file()
    ):
        return cached
    return None


# ---------------------------------------------------------------------------
# MinerU API interaction (v4 — presigned URL flow)
# ---------------------------------------------------------------------------


def _api_error(e: HTTPError) -> None:
    """Handle common MinerU API error codes."""
    body = e.read().decode(errors="replace")
    if "A0202" in body:
        print("Error: Invalid token.", file=sys.stderr)
        sys.exit(EXIT_TOKEN_INVALID)
    if "A0211" in body:
        print(
            "Error: Token expired. Please regenerate at https://mineru.net",
            file=sys.stderr,
        )
        sys.exit(EXIT_TOKEN_INVALID)
    if "quota" in body.lower() or "limit" in body.lower():
        print(
            "Error: Daily quota exceeded. Wait until tomorrow or use local MinerU.",
            file=sys.stderr,
        )
        sys.exit(EXIT_QUOTA_EXCEEDED)
    print(f"Error: API error {e.code}: {body}", file=sys.stderr)
    sys.exit(EXIT_PARSE_FAILURE)


def request_upload_url(token: str, filename: str, model: str) -> tuple[str, str]:
    """Request a presigned upload URL from MinerU.

    Returns (batch_id, presigned_url).
    """
    body = json.dumps({
        "files": [{"name": filename, "is_ocr": False}],
        "model_version": model,
        "enable_formula": True,
        "enable_table": True,
        "language": "en",
    }).encode()

    req = Request(
        f"{API_BASE}/file-urls/batch",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except HTTPError as e:
        _api_error(e)
    except URLError as e:
        print(f"Error: Network error: {e.reason}", file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)

    if data.get("code") != 0:
        print(
            f"Error: API error: {data.get('msg', 'unknown')}",
            file=sys.stderr,
        )
        sys.exit(EXIT_PARSE_FAILURE)

    batch_id = data.get("data", {}).get("batch_id", "")
    file_urls = data.get("data", {}).get("file_urls", [])

    if not batch_id or not file_urls:
        print("Error: No batch_id or upload URL in response.", file=sys.stderr)
        sys.exit(EXIT_PARSE_FAILURE)

    return batch_id, file_urls[0]


def upload_file_to_presigned_url(presigned_url: str, file_path: str) -> None:
    """Upload raw file bytes to the presigned URL via PUT.

    Uses http.client directly instead of urllib to avoid auto-added
    Content-Type headers. Alibaba Cloud OSS presigned URLs include the
    Content-Type in the signature — any extra or mismatched header
    causes SignatureDoesNotMatch errors.
    """
    import http.client
    import ssl
    from urllib.parse import urlparse

    with open(file_path, "rb") as f:
        file_data = f.read()

    parsed = urlparse(presigned_url)
    path_and_query = parsed.path
    if parsed.query:
        path_and_query += "?" + parsed.query

    try:
        if parsed.scheme == "https":
            ctx = ssl.create_default_context()
            conn = http.client.HTTPSConnection(
                parsed.hostname, parsed.port or 443,
                context=ctx, timeout=120,
            )
        else:
            conn = http.client.HTTPConnection(
                parsed.hostname, parsed.port or 80, timeout=120,
            )

        # Send PUT with NO extra headers — let the presigned URL handle auth
        conn.request("PUT", path_and_query, body=file_data)
        resp = conn.getresponse()
        body = resp.read()

        if resp.status not in (200, 201):
            print(
                f"Error: Upload failed: {resp.status} "
                f"{body.decode(errors='replace')[:500]}",
                file=sys.stderr,
            )
            sys.exit(EXIT_PARSE_FAILURE)
    except (OSError, http.client.HTTPException) as e:
        print(f"Error: Network error during upload: {e}", file=sys.stderr)
        sys.exit(EXIT_NETWORK_ERROR)
    finally:
        conn.close()


def poll_batch(token: str, batch_id: str, timeout: int) -> str:
    """Poll for batch completion. Returns the full_zip_url when done."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = Request(
                f"{API_BASE}/extract-results/batch/{batch_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except HTTPError as e:
            _api_error(e)
        except (URLError, json.JSONDecodeError) as e:
            print(f"Warning: Poll error: {e} — retrying...", file=sys.stderr)
            time.sleep(POLL_INTERVAL)
            continue

        extract_result = data.get("data", {}).get("extract_result", [])
        if extract_result:
            item = extract_result[0]
            state = item.get("state", "unknown")
        else:
            state = data.get("data", {}).get("state", "unknown")

        if state == "done":
            zip_url = ""
            if extract_result:
                zip_url = extract_result[0].get("full_zip_url", "")
            if not zip_url:
                zip_url = data.get("data", {}).get("full_zip_url", "")
            if not zip_url:
                print("Error: No full_zip_url in completed response.", file=sys.stderr)
                print(f"Response: {json.dumps(data, indent=2)}", file=sys.stderr)
                sys.exit(EXIT_PARSE_FAILURE)
            return zip_url

        if state == "failed":
            msg = "unknown error"
            if extract_result:
                msg = extract_result[0].get("err_msg", msg)
            print(f"Error: Parse failed: {msg}", file=sys.stderr)
            sys.exit(EXIT_PARSE_FAILURE)

        elapsed = int(time.time() - start)
        print(f"  Parsing... ({state}, {elapsed}s elapsed)", file=sys.stderr)
        time.sleep(POLL_INTERVAL)

    print(
        f"Error: API timeout after {timeout}s. Batch {batch_id} still not complete.",
        file=sys.stderr,
    )
    sys.exit(EXIT_API_TIMEOUT)


def download_and_extract(zip_url: str, output_dir: str) -> Path:
    """Download the result ZIP from CDN and extract it."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    # CDN URL — no auth header needed
    req = Request(zip_url)

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
        # Might be raw JSON
        result_path = output / "content_list.json"
        result_path.write_bytes(content)

    # MinerU sometimes nests output in a subdirectory — flatten if needed
    subdirs = [d for d in output.iterdir() if d.is_dir() and d.name != "images"]
    if len(subdirs) == 1 and (subdirs[0] / "content_list.json").is_file():
        nested = subdirs[0]
        for item in nested.iterdir():
            dest = output / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            item.rename(dest)
        nested.rmdir()

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

    # Step 1: Request presigned upload URL
    filename = Path(args.input).name
    print(f"Requesting upload URL for {filename} (model={args.model})...", file=sys.stderr)
    batch_id, presigned_url = request_upload_url(token, filename, args.model)
    print(f"Batch ID: {batch_id}", file=sys.stderr)

    # Step 2: Upload file to presigned URL
    print(f"Uploading {filename}...", file=sys.stderr)
    upload_file_to_presigned_url(presigned_url, args.input)
    print("Upload complete.", file=sys.stderr)

    # Step 3: Poll for completion
    print("Waiting for parse to complete...", file=sys.stderr)
    zip_url = poll_batch(token, batch_id, args.timeout)
    print("Parse complete. Downloading results...", file=sys.stderr)

    # Step 4: Download and extract results
    output_path = download_and_extract(zip_url, args.output)

    # Cache the result
    cache_entry = cache_dir / sha
    if cache_entry != output_path:
        cache_entry.mkdir(parents=True, exist_ok=True)
        for item in output_path.iterdir():
            dest = cache_entry / item.name
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    # Output summary — MinerU v3 uses content_list_v2.json (page-grouped)
    content_list = output_path / "content_list_v2.json"
    if not content_list.is_file():
        content_list = output_path / "content_list.json"
    if content_list.is_file():
        with open(content_list) as f:
            data = json.load(f)
        if isinstance(data, list) and data and isinstance(data[0], list):
            # v2 format: list of pages, each page is a list of elements
            count = sum(len(page) for page in data)
            print(f"Extracted {count} elements across {len(data)} pages.", file=sys.stderr)
        else:
            count = len(data) if isinstance(data, list) else 0
            print(f"Extracted {count} content elements.", file=sys.stderr)
    else:
        print("Warning: No content_list JSON found in output.", file=sys.stderr)

    print(
        json.dumps(
            {
                "cached": False,
                "sha256": sha,
                "batch_id": batch_id,
                "output": str(output_path),
            }
        )
    )


if __name__ == "__main__":
    main()
