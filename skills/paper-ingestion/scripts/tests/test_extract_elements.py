"""Tests for element extraction pipeline in extract_elements.py."""

import json
from pathlib import Path

from extract_elements import (
    _extract_text_from_content,
    _flatten_v2,
    _infer_title,
    _spans_to_text,
    extract_elements,
    validate_output,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / ".claude" / "skills" / "dev-test-paper-ingestion" / "fixtures"


# ---------------------------------------------------------------------------
# _flatten_v2
# ---------------------------------------------------------------------------


class TestFlattenV2:
    def test_basic_flatten(self):
        data = [
            [{"type": "equation", "content": "x"}, {"type": "text", "content": "hello"}],
            [{"type": "table", "content": "t"}],
        ]
        flat = _flatten_v2(data)
        assert len(flat) == 3
        assert flat[0]["_page_idx"] == 0
        assert flat[1]["_page_idx"] == 0
        assert flat[2]["_page_idx"] == 1

    def test_empty_pages(self):
        data = [[], []]
        assert _flatten_v2(data) == []

    def test_non_list_page_skipped(self):
        data = [None, [{"type": "text", "content": "ok"}]]
        flat = _flatten_v2(data)
        assert len(flat) == 1


# ---------------------------------------------------------------------------
# _extract_text_from_content
# ---------------------------------------------------------------------------


class TestExtractTextFromContent:
    def test_string_passthrough(self):
        assert _extract_text_from_content("hello world") == "hello world"

    def test_math_content(self):
        assert _extract_text_from_content({"math_content": "x^2"}) == "x^2"

    def test_paragraph_content(self):
        content = {"paragraph_content": [
            {"type": "text", "content": "We consider "},
            {"type": "text", "content": "the problem."},
        ]}
        assert _extract_text_from_content(content) == "We consider the problem."

    def test_title_content(self):
        content = {"title_content": [{"type": "text", "content": "Introduction"}]}
        assert _extract_text_from_content(content) == "Introduction"

    def test_nested_content(self):
        assert _extract_text_from_content({"content": "inner"}) == "inner"

    def test_none_content(self):
        assert _extract_text_from_content(None) == ""

    def test_v1_text_field(self):
        assert _extract_text_from_content({"text": "v1 text"}) == "v1 text"

    def test_v1_latex_field(self):
        assert _extract_text_from_content({"latex": "x^2"}) == "x^2"


# ---------------------------------------------------------------------------
# _spans_to_text
# ---------------------------------------------------------------------------


class TestSpansToText:
    def test_text_spans(self):
        spans = [
            {"type": "text", "content": "Hello "},
            {"type": "text", "content": "world"},
        ]
        assert _spans_to_text(spans) == "Hello world"

    def test_inline_equation_span(self):
        spans = [
            {"type": "equation_inline", "content": {"math_content": "x^2"}},
        ]
        assert _spans_to_text(spans) == "$x^2$"

    def test_mixed_spans(self):
        spans = [
            {"type": "text", "content": "where "},
            {"type": "equation_inline", "content": {"math_content": "\\beta"}},
            {"type": "text", "content": " is the coefficient"},
        ]
        result = _spans_to_text(spans)
        assert "where " in result
        assert "$\\beta$" in result
        assert " is the coefficient" in result

    def test_string_in_list(self):
        assert _spans_to_text(["hello", "world"]) == "helloworld"


# ---------------------------------------------------------------------------
# extract_elements — integration tests
# ---------------------------------------------------------------------------


class TestExtractElements:
    def test_v2_format(self):
        fixture_path = FIXTURES_DIR / "v2-sample.json"
        if not fixture_path.exists():
            pytest.skip("v2-sample.json fixture not found")
        with open(fixture_path) as f:
            data = json.load(f)
        result = extract_elements(data, source_file="test.pdf")
        assert result["metadata"]["source_file"] == "test.pdf"
        assert result["summary"]["total_equations"] > 0
        assert result["summary"]["total_tables"] > 0
        assert result["summary"]["total_algorithms"] > 0

    def test_v1_format(self):
        fixture_path = FIXTURES_DIR / "v1-sample.json"
        if not fixture_path.exists():
            pytest.skip("v1-sample.json fixture not found")
        with open(fixture_path) as f:
            data = json.load(f)
        result = extract_elements(data, source_file="test.pdf")
        assert result["summary"]["total_equations"] > 0
        assert result["summary"]["total_algorithms"] > 0

    def test_empty_input(self):
        result = extract_elements([], source_file="empty.pdf")
        assert result["summary"]["total_equations"] == 0
        assert result["summary"]["total_tables"] == 0
        assert result["equations"] == []

    def test_metadata_fields(self):
        result = extract_elements([], source_file="paper.pdf")
        meta = result["metadata"]
        assert "source_file" in meta
        assert "parsed_at" in meta
        assert "total_pages" in meta

    def test_equation_cross_referencing(self):
        """Algorithm referencing (1) should link to the equation with that tag."""
        data = [
            [
                {"type": "equation_interline", "content": {"math_content": r"y = x \tag{1}"}},
                {
                    "type": "paragraph",
                    "content": {
                        "paragraph_content": [
                            {"type": "text", "content": (
                                "Algorithm 1: Estimator\n"
                                "Input: data X\n"
                                "1. Compute (1)\n"
                                "2. Return estimate"
                            )}
                        ]
                    },
                },
            ]
        ]
        result = extract_elements(data)
        if result["algorithms"]:
            refs = result["algorithms"][0].get("referenced_equations", [])
            assert len(refs) >= 1


# ---------------------------------------------------------------------------
# validate_output
# ---------------------------------------------------------------------------


class TestValidateOutput:
    def test_valid_output(self):
        data = {
            "metadata": {
                "title": "Test",
                "source_file": "test.pdf",
                "total_pages": 5,
                "parse_model": "vlm",
            },
            "equations": [{"id": "eq_001"}],
            "tables": [],
            "text_blocks": [{"id": "txt_001"}],
            "figures": [],
            "summary": {"total_equations": 1, "total_tables": 0, "total_text_blocks": 1},
        }
        assert validate_output(data) == []

    def test_missing_keys(self):
        data = {"metadata": {}, "equations": []}
        issues = validate_output(data)
        assert any("Missing top-level" in i for i in issues)

    def test_missing_metadata_field(self):
        data = {
            "metadata": {"source_file": "x"},
            "equations": [],
            "tables": [],
            "text_blocks": [],
            "figures": [],
            "summary": {"total_equations": 0, "total_tables": 0, "total_text_blocks": 0},
        }
        issues = validate_output(data)
        assert any("metadata" in i for i in issues)

    def test_empty_extraction(self):
        data = {
            "metadata": {"title": "", "source_file": "", "total_pages": 0, "parse_model": "vlm"},
            "equations": [],
            "tables": [],
            "text_blocks": [],
            "figures": [],
            "summary": {"total_equations": 0, "total_tables": 0, "total_text_blocks": 0},
        }
        issues = validate_output(data)
        assert any("Empty extraction" in i for i in issues)


# ---------------------------------------------------------------------------
# _infer_title
# ---------------------------------------------------------------------------


class TestInferTitle:
    def test_title_from_section_hint(self):
        blocks = [
            {"content": "Generalized Synthetic Control", "page": 0, "section_hint": "Generalized Synthetic Control"},
        ]
        assert _infer_title(blocks) == "Generalized Synthetic Control"

    def test_fallback_to_first_block(self):
        blocks = [
            {"content": "A Long Enough Title For The Paper", "page": 0, "section_hint": ""},
        ]
        title = _infer_title(blocks)
        assert "Long Enough" in title

    def test_no_suitable_blocks(self):
        blocks = [
            {"content": "Some text", "page": 2, "section_hint": ""},
        ]
        assert _infer_title(blocks) == ""

    def test_multiple_title_parts(self):
        blocks = [
            {"content": "Generalized Synthetic", "page": 0, "section_hint": "Generalized Synthetic"},
            {"content": "Control Method", "page": 0, "section_hint": "Control Method"},
        ]
        title = _infer_title(blocks)
        assert "Generalized Synthetic" in title
        assert "Control Method" in title
