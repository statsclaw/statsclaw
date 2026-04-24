"""Tests for _parse_algorithm_structure in extract_elements.py."""

from extract_elements import _parse_algorithm_structure


class TestParseAlgorithmStructure:
    def test_full_algorithm(self):
        text = (
            "Algorithm 1: Bootstrap DID\n"
            "Input: Panel data Y, treatment vector D\n"
            "Output: ATT estimate with CI\n"
            "1. Compute point estimate\n"
            "2. For b = 1 to B, draw bootstrap sample\n"
            "3. If convergence, return estimate\n"
        )
        result = _parse_algorithm_structure(text)
        assert result["title"] == "Algorithm 1: Bootstrap DID"
        assert len(result["input_declarations"]) == 1
        assert len(result["output_declarations"]) == 1
        assert len(result["steps"]) == 3
        assert "for" in result["control_flow"]
        assert "return" in result["control_flow"]

    def test_algorithm_without_title(self):
        text = (
            "Input: data X\n"
            "1. Compute mean\n"
            "2. Return result\n"
        )
        result = _parse_algorithm_structure(text)
        assert result["title"] == ""

    def test_require_ensure_declarations(self):
        text = (
            "Require: X is n x p matrix\n"
            "Ensure: theta_hat is consistent\n"
            "1. Initialize theta\n"
            "2. Iterate\n"
            "3. Return theta\n"
        )
        result = _parse_algorithm_structure(text)
        assert len(result["input_declarations"]) == 1
        assert "Require" in result["input_declarations"][0]
        assert len(result["output_declarations"]) == 1
        assert "Ensure" in result["output_declarations"][0]

    def test_inline_numbering(self):
        # Inline numbering fallback only triggers when line-per-step finds nothing.
        # Use text where steps are separated by spaces, not newlines,
        # and the first step doesn't start at column 0 with "N) ".
        text = "Initialize theta, then: 1) Draw sample 2) Compute statistic 3) Repeat B times"
        result = _parse_algorithm_structure(text)
        assert len(result["steps"]) >= 2

    def test_control_flow_keywords_sorted(self):
        text = (
            "1. for each unit\n"
            "2. if treated then compute\n"
            "3. while not converged, repeat\n"
            "4. return estimate\n"
        )
        result = _parse_algorithm_structure(text)
        assert result["control_flow"] == sorted(result["control_flow"])

    def test_step_numbers_extracted(self):
        text = (
            "1. Initialize\n"
            "2. Update\n"
            "3. Check convergence\n"
        )
        result = _parse_algorithm_structure(text)
        nums = [s["num"] for s in result["steps"]]
        assert nums == [1, 2, 3]
