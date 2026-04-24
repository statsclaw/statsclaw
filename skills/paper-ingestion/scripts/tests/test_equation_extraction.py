"""Tests for equation reference extraction in extract_elements.py."""

from extract_elements import _extract_paper_number, extract_equation_refs


class TestExtractEquationRefs:
    def test_simple_integer_ref(self):
        assert "3" in extract_equation_refs("see equation (3) for details")

    def test_section_numbered_ref(self):
        refs = extract_equation_refs("Using (4.6) and (4.7)")
        assert "4.6" in refs
        assert "4.7" in refs

    def test_appendix_ref(self):
        assert "A.3" in extract_equation_refs("From (A.3) in the appendix")

    def test_eq_prefix(self):
        assert "4.6" in extract_equation_refs("Eq. (4.6)")

    def test_equation_prefix(self):
        assert "7" in extract_equation_refs("equation 7 shows")

    def test_multiple_refs(self):
        text = "Combining (1), Eq. (2.3), and (A.1) yields the result."
        refs = extract_equation_refs(text)
        assert len(refs) >= 3

    def test_no_refs(self):
        assert extract_equation_refs("No equations here.") == []


class TestExtractPaperNumber:
    def test_tag_present(self):
        assert _extract_paper_number(r"x^2 + y^2 \tag{4.6}") == "4.6"

    def test_tag_with_spaces(self):
        assert _extract_paper_number(r"\tag{ 3 }") == "3"

    def test_no_tag(self):
        assert _extract_paper_number(r"x^2 + y^2") == ""

    def test_tag_with_appendix_number(self):
        assert _extract_paper_number(r"\hat\beta \tag{A.2}") == "A.2"
