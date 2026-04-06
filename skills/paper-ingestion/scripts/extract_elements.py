#!/usr/bin/env python3
"""Extract and classify elements from MinerU's content_list.json.

Transforms raw MinerU output into StatsClaw's paper-elements.json format
with typed elements: equations, tables, text blocks, figures, and algorithms.

Usage:
    python extract_elements.py --input content_list.json --output paper-elements.json
    python extract_elements.py --input content_list.json --output paper-elements.json --markdown paper.md
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Algorithm detection heuristics
# ---------------------------------------------------------------------------

ALGORITHM_HEADER_RE = re.compile(
    r"^\s*algorithm\s+\d+", re.IGNORECASE
)

IO_KEYWORDS = {"input:", "output:", "return:", "require:", "ensure:"}

PSEUDOCODE_KEYWORDS = {
    "for", "while", "if", "then", "else", "repeat", "until",
    "do", "end", "return", "foreach", "loop", "break", "continue",
}

EQUATION_REF_RE = re.compile(
    r"(?:Eq\.?\s*\(?(\d+)\)?|equation\s*\(?(\d+)\)?|\((\d+)\))",
    re.IGNORECASE,
)

NUMBERED_STEP_RE = re.compile(r"^\s*(\d+)[.)]\s+\S")


def _has_algorithm_header(text: str) -> bool:
    """Check if text starts with 'Algorithm N'."""
    first_line = text.strip().split("\n")[0] if text.strip() else ""
    return bool(ALGORITHM_HEADER_RE.match(first_line))


def _has_io_declarations(text: str) -> bool:
    """Check if text contains I/O declarations in the first 3 lines."""
    lines = text.strip().split("\n")[:3]
    combined = " ".join(lines).lower()
    return any(kw in combined for kw in IO_KEYWORDS)


def _pseudocode_density(text: str) -> int:
    """Count how many pseudocode keywords appear in the text."""
    words = set(re.findall(r"\b\w+\b", text.lower()))
    return len(words & PSEUDOCODE_KEYWORDS)


def _has_numbered_steps_with_control(text: str) -> bool:
    """Check for numbered steps + at least one control flow keyword."""
    lines = text.strip().split("\n")
    numbered = sum(1 for line in lines if NUMBERED_STEP_RE.match(line))
    has_control = _pseudocode_density(text) >= 1
    return numbered >= 3 and has_control


def is_algorithm_block(text: str) -> bool:
    """Determine if a text block is likely an algorithm/pseudocode block."""
    if _has_algorithm_header(text):
        return True
    if _has_io_declarations(text):
        return True
    if _pseudocode_density(text) >= 3:
        return True
    if _has_numbered_steps_with_control(text):
        return True
    return False


def extract_equation_refs(text: str) -> list[str]:
    """Extract equation reference numbers from text."""
    refs = []
    for match in EQUATION_REF_RE.finditer(text):
        num = match.group(1) or match.group(2) or match.group(3)
        if num:
            refs.append(num)
    return refs


# ---------------------------------------------------------------------------
# Element extraction
# ---------------------------------------------------------------------------


def extract_elements(
    content_list: list[dict],
    source_file: str = "",
    markdown_text: str = "",
    images_dir: str = "images/",
) -> dict:
    """Transform MinerU content_list into paper-elements.json format."""
    equations = []
    tables = []
    text_blocks = []
    figures = []
    algorithms = []

    eq_counter = 0
    tbl_counter = 0
    txt_counter = 0
    fig_counter = 0
    alg_counter = 0

    # Build context: for each element, capture the surrounding text
    def _get_context(idx: int, items: list, direction: str) -> str:
        """Get text context before or after an element."""
        step = -1 if direction == "before" else 1
        i = idx + step
        while 0 <= i < len(items):
            item = items[i]
            item_type = item.get("type", "")
            if item_type == "text":
                content = item.get("text", item.get("content", ""))
                if content and len(content.strip()) > 20:
                    return content.strip()[:300]
            i += step
        return ""

    for idx, item in enumerate(content_list):
        item_type = item.get("type", "")
        page = item.get("page", item.get("page_idx", 0))

        # --- Equations ---
        if item_type in ("interline_equation", "equation"):
            eq_counter += 1
            equations.append({
                "id": f"eq_{eq_counter:03d}",
                "type": "interline_equation",
                "latex": item.get("text", item.get("latex", "")),
                "page": page,
                "context_before": _get_context(idx, content_list, "before"),
                "context_after": _get_context(idx, content_list, "after"),
            })

        elif item_type == "inline_equation":
            eq_counter += 1
            equations.append({
                "id": f"eq_{eq_counter:03d}",
                "type": "inline_equation",
                "latex": item.get("text", item.get("latex", "")),
                "page": page,
                "context_before": _get_context(idx, content_list, "before"),
                "context_after": _get_context(idx, content_list, "after"),
            })

        # --- Tables ---
        elif item_type == "table":
            tbl_counter += 1
            caption_list = item.get("table_caption", [])
            caption = caption_list[0] if caption_list else ""
            html = item.get("table_body", item.get("html", ""))
            has_formulas = bool(
                re.search(r"\$.*?\$|\\[a-zA-Z]+", html) if html else False
            )
            tables.append({
                "id": f"tbl_{tbl_counter:03d}",
                "caption": caption,
                "html": html,
                "page": page,
                "has_formulas": has_formulas,
                "context_before": _get_context(idx, content_list, "before"),
            })

        # --- Figures / Images ---
        elif item_type in ("image", "figure"):
            fig_counter += 1
            img_path = item.get("img_path", "")
            caption = item.get("caption", item.get("text", ""))
            figures.append({
                "id": f"fig_{fig_counter:03d}",
                "caption": caption,
                "image_path": img_path,
                "page": page,
            })

        # --- Text blocks ---
        elif item_type == "text":
            content = item.get("text", item.get("content", ""))
            if not content or not content.strip():
                continue

            # Check if this text block is actually an algorithm
            if is_algorithm_block(content):
                alg_counter += 1
                eq_refs = extract_equation_refs(content)
                # Try to link equation refs to actual equation IDs by number
                linked_eqs = []
                for ref_num in eq_refs:
                    # Simple heuristic: match by position in equations list
                    ref_int = int(ref_num)
                    if 1 <= ref_int <= len(equations):
                        linked_eqs.append(equations[ref_int - 1]["id"])

                algorithms.append({
                    "id": f"alg_{alg_counter:03d}",
                    "title": content.strip().split("\n")[0][:100],
                    "raw_text": content.strip(),
                    "page": page,
                    "has_inputs_outputs": _has_io_declarations(content),
                    "referenced_equations": linked_eqs,
                })
            else:
                txt_counter += 1
                # Try to infer section hint from heading-like patterns
                section_hint = ""
                if content.strip() and len(content.strip()) < 100:
                    first_line = content.strip().split("\n")[0]
                    if re.match(r"^(\d+\.?\s+)?[A-Z]", first_line):
                        section_hint = first_line.strip()

                text_blocks.append({
                    "id": f"txt_{txt_counter:03d}",
                    "content": content.strip(),
                    "page": page,
                    "section_hint": section_hint,
                })

    # Count inline equations from text (some versions embed them)
    inline_count = sum(1 for eq in equations if eq["type"] == "inline_equation")
    interline_count = sum(1 for eq in equations if eq["type"] == "interline_equation")

    # Compute total pages
    all_pages = set()
    for item in content_list:
        p = item.get("page", item.get("page_idx"))
        if p is not None:
            all_pages.add(p)
    total_pages = max(all_pages) + 1 if all_pages else 0

    result = {
        "metadata": {
            "title": _infer_title(text_blocks),
            "source_file": source_file,
            "total_pages": total_pages,
            "parse_model": "vlm",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
            "mineru_version": "3.0",
        },
        "equations": equations,
        "tables": tables,
        "algorithms": algorithms,
        "text_blocks": text_blocks,
        "figures": figures,
        "summary": {
            "total_equations": interline_count,
            "total_inline_equations": inline_count,
            "total_tables": len(tables),
            "total_algorithms": len(algorithms),
            "total_figures": len(figures),
            "total_text_blocks": len(text_blocks),
        },
    }

    return result


def _infer_title(text_blocks: list[dict]) -> str:
    """Try to infer paper title from the first text block on page 0 or 1."""
    for block in text_blocks[:5]:
        if block.get("page", 99) <= 1:
            content = block.get("content", "")
            first_line = content.strip().split("\n")[0]
            # Title heuristic: not too short, not too long, on first page
            if 10 < len(first_line) < 200:
                return first_line
    return ""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_output(data: dict) -> list[str]:
    """Validate paper-elements.json structure. Returns list of issues."""
    issues = []
    required_keys = {"metadata", "equations", "tables", "text_blocks", "figures", "summary"}
    missing = required_keys - set(data.keys())
    if missing:
        issues.append(f"Missing top-level keys: {missing}")

    meta = data.get("metadata", {})
    for key in ("title", "source_file", "total_pages", "parse_model"):
        if key not in meta:
            issues.append(f"Missing metadata.{key}")

    # Check that at least some content was extracted
    summary = data.get("summary", {})
    total = (
        summary.get("total_equations", 0)
        + summary.get("total_tables", 0)
        + summary.get("total_text_blocks", 0)
    )
    if total == 0:
        issues.append("Empty extraction: no equations, tables, or text blocks found")

    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Extract elements from MinerU content_list.json."
    )
    parser.add_argument(
        "--input", required=True, help="MinerU content_list.json path"
    )
    parser.add_argument(
        "--output", required=True, help="Output paper-elements.json path"
    )
    parser.add_argument(
        "--markdown", default="", help="MinerU markdown file for context"
    )
    parser.add_argument(
        "--images-dir", default="images/", help="Directory with extracted images"
    )
    parser.add_argument(
        "--source-file", default="", help="Original PDF filename for metadata"
    )
    args = parser.parse_args()

    # Read input
    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(input_path) as f:
        content_list = json.load(f)

    if not isinstance(content_list, list):
        # Some MinerU versions wrap in a dict
        if isinstance(content_list, dict):
            content_list = content_list.get("data", content_list.get("content_list", []))
        if not isinstance(content_list, list):
            print("Error: Unexpected content_list.json format.", file=sys.stderr)
            sys.exit(1)

    # Read markdown for additional context (optional)
    markdown_text = ""
    if args.markdown and Path(args.markdown).is_file():
        markdown_text = Path(args.markdown).read_text(errors="replace")

    # Extract elements
    result = extract_elements(
        content_list,
        source_file=args.source_file or input_path.stem,
        markdown_text=markdown_text,
        images_dir=args.images_dir,
    )

    # Validate
    issues = validate_output(result)
    if issues:
        for issue in issues:
            print(f"Warning: {issue}", file=sys.stderr)

    # Check for empty extraction (exit code 7 per SKILL.md)
    summary = result.get("summary", {})
    if summary.get("total_equations", 0) == 0 and summary.get("total_tables", 0) == 0:
        print(
            "Warning: No equations or tables extracted. "
            "Is this the right paper?",
            file=sys.stderr,
        )
        # Still write output — let the caller decide if this is an error

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Wrote {args.output}", file=sys.stderr)
    print(
        f"  Equations: {summary.get('total_equations', 0)} display + "
        f"{summary.get('total_inline_equations', 0)} inline",
        file=sys.stderr,
    )
    print(f"  Tables: {summary.get('total_tables', 0)}", file=sys.stderr)
    print(f"  Algorithms: {summary.get('total_algorithms', 0)}", file=sys.stderr)
    print(f"  Text blocks: {summary.get('total_text_blocks', 0)}", file=sys.stderr)
    print(f"  Figures: {summary.get('total_figures', 0)}", file=sys.stderr)

    # Output JSON summary to stdout
    print(json.dumps({"output": str(output_path), "summary": summary}))


if __name__ == "__main__":
    main()
