"""Tests for algorithm detection heuristics in extract_elements.py."""

from extract_elements import (
    _has_algorithm_header,
    _has_assignment_operators,
    _has_io_declarations,
    _has_line_per_statement,
    _has_numbered_steps_with_control,
    _keyword_line_start_ratio,
    _pseudocode_density,
    is_algorithm_block,
)


# ---------------------------------------------------------------------------
# _has_algorithm_header
# ---------------------------------------------------------------------------


class TestHasAlgorithmHeader:
    def test_standard_header(self):
        assert _has_algorithm_header("Algorithm 1: K-Means Clustering")

    def test_case_insensitive(self):
        assert _has_algorithm_header("algorithm 2")

    def test_with_leading_whitespace(self):
        assert _has_algorithm_header("  Algorithm 3: Bootstrap")

    def test_no_header(self):
        assert not _has_algorithm_header("This is a regular paragraph.")

    def test_algorithm_not_first_line(self):
        assert not _has_algorithm_header("Some intro text\nAlgorithm 1: Foo")

    def test_algorithm_without_number(self):
        assert not _has_algorithm_header("Algorithm: no number here")


# ---------------------------------------------------------------------------
# _has_io_declarations
# ---------------------------------------------------------------------------


class TestHasIODeclarations:
    def test_input_output(self):
        assert _has_io_declarations("Input: data matrix X\nOutput: estimates")

    def test_require_ensure(self):
        assert _has_io_declarations("Require: X is positive definite\nEnsure: convergence")

    def test_return_keyword(self):
        assert _has_io_declarations("Return: estimated coefficients")

    def test_io_beyond_first_3_lines(self):
        text = "Line 1\nLine 2\nLine 3\nInput: too late"
        assert not _has_io_declarations(text)

    def test_no_io(self):
        assert not _has_io_declarations("This paragraph has no declarations.")

    def test_io_case_insensitive(self):
        assert _has_io_declarations("INPUT: data\nOUTPUT: result")


# ---------------------------------------------------------------------------
# _pseudocode_density
# ---------------------------------------------------------------------------


class TestPseudocodeDensity:
    def test_pure_pseudocode(self):
        text = "for i in range\n  if x then\n    return y\n  else\n    continue\n  end\nend"
        assert _pseudocode_density(text) >= 6

    def test_tianzhu_example(self):
        text = (
            "For each unit, if the treatment indicator equals one, then compute "
            "the weighted average. While this estimator is consistent, it does not "
            "achieve efficiency. We repeat this procedure for all bootstrap "
            "iterations and return the confidence interval."
        )
        # Should find: for, if, then, while, repeat, return = 6
        assert _pseudocode_density(text) == 6

    def test_no_keywords(self):
        assert _pseudocode_density("The estimator is consistent and unbiased.") == 0

    def test_case_insensitive(self):
        assert _pseudocode_density("FOR WHILE IF") == 3

    def test_partial_word_not_counted(self):
        # "reform" contains "for" but as a word boundary check it should not match
        # _pseudocode_density uses \b\w+\b so "reform" becomes its own word
        density = _pseudocode_density("reform information")
        assert density == 0


# ---------------------------------------------------------------------------
# _has_numbered_steps_with_control
# ---------------------------------------------------------------------------


class TestHasNumberedStepsWithControl:
    def test_three_steps_with_control(self):
        text = "1. Initialize theta\n2. For each observation, update\n3. If converged, return theta"
        assert _has_numbered_steps_with_control(text)

    def test_two_steps_insufficient(self):
        text = "1. Initialize\n2. For each item, compute"
        assert not _has_numbered_steps_with_control(text)

    def test_steps_without_control(self):
        text = "1. Read data\n2. Clean data\n3. Save data"
        assert not _has_numbered_steps_with_control(text)

    def test_parenthesis_numbering(self):
        text = "1) Initialize\n2) For each unit compute\n3) Return estimate"
        assert _has_numbered_steps_with_control(text)


# ---------------------------------------------------------------------------
# is_algorithm_block — true positives
# ---------------------------------------------------------------------------


class TestIsAlgorithmBlockTruePositives:
    def test_explicit_algorithm_header(self):
        text = (
            "Algorithm 1: Generalized Synthetic Control\n"
            "Input: Panel data Y, treatment indicator D\n"
            "1. Estimate factor model on control units\n"
            "2. Obtain factor loadings for treated units\n"
            "3. Compute counterfactual predictions\n"
            "4. Calculate ATT as difference\n"
            "Output: Estimated ATT and standard errors"
        )
        assert is_algorithm_block(text)

    def test_io_declarations(self):
        text = (
            "Input: dataset D with N observations\n"
            "Output: estimate theta_hat\n"
            "1. Compute sample mean\n"
            "2. Iterate until convergence"
        )
        assert is_algorithm_block(text)

    def test_numbered_steps_with_control_flow(self):
        text = (
            "1. Draw bootstrap sample\n"
            "2. For each group g, compute ATT(g,t)\n"
            "3. If convergence criterion met, stop\n"
            "4. Return aggregated estimates"
        )
        assert is_algorithm_block(text)

    def test_structured_pseudocode(self):
        """Multi-line pseudocode with keywords at line starts and assignment."""
        text = (
            "for i = 1 to N do\n"
            "  if T_i == 1 then\n"
            "    delta_i <- Y_i - X_i'beta\n"
            "  else\n"
            "    continue\n"
            "  end\n"
            "end\n"
            "return mean(delta)"
        )
        assert is_algorithm_block(text)


# ---------------------------------------------------------------------------
# is_algorithm_block — false positives (must reject)
# ---------------------------------------------------------------------------


class TestIsAlgorithmBlockFalsePositives:
    def test_tianzhu_econometrics_prose(self):
        """Tianzhu's exact example from PR #39 review."""
        text = (
            "For each unit, if the treatment indicator equals one, then compute "
            "the weighted average. While this estimator is consistent, it does not "
            "achieve efficiency. We repeat this procedure for all bootstrap "
            "iterations and return the confidence interval."
        )
        assert not is_algorithm_block(text)

    def test_methodology_prose(self):
        text = (
            "We then estimate the model for each subgroup. If the propensity "
            "score is below the threshold, we return to the matching step. While "
            "doing so, we repeat the bootstrap procedure to end with valid "
            "confidence intervals."
        )
        assert not is_algorithm_block(text)

    def test_theorem_statement(self):
        text = (
            "Theorem 1. If the parallel trends assumption holds, then for all "
            "groups g and time periods t, the estimator is consistent. While the "
            "rate of convergence depends on N and T, we do obtain valid inference "
            "if both dimensions grow."
        )
        assert not is_algorithm_block(text)

    def test_proof_with_keywords(self):
        text = (
            "Proof. For each n, if the condition holds, then by the dominated "
            "convergence theorem, we do obtain the limit. While the argument is "
            "standard, we repeat it here for completeness and return to the main "
            "result."
        )
        assert not is_algorithm_block(text)

    def test_long_methodology_paragraph(self):
        """Long paragraph with several keywords but clearly prose."""
        text = (
            "In this section, we describe the estimation procedure. For each "
            "time period, if the unit is treated, then we compute the outcome "
            "difference. While other approaches exist, we focus on the doubly "
            "robust estimator. We repeat this for all cohorts and return the "
            "aggregated effect. The procedure is robust to model misspecification "
            "under standard regularity conditions. We do not require parametric "
            "assumptions on the outcome model. The bootstrap is used for inference "
            "and we loop over 1000 replications to end with valid standard errors."
        )
        assert not is_algorithm_block(text)


# ---------------------------------------------------------------------------
# is_algorithm_block — edge cases
# ---------------------------------------------------------------------------


class TestIsAlgorithmBlockEdgeCases:
    def test_empty_string(self):
        assert not is_algorithm_block("")

    def test_whitespace_only(self):
        assert not is_algorithm_block("   \n\n  ")

    def test_single_word(self):
        assert not is_algorithm_block("return")

    def test_short_text_few_keywords(self):
        assert not is_algorithm_block("if x then y")


# ---------------------------------------------------------------------------
# _has_line_per_statement
# ---------------------------------------------------------------------------


class TestHasLinePerStatement:
    def test_pseudocode_format(self):
        text = (
            "for i = 1 to N do\n"
            "  if T_i == 1 then\n"
            "    delta_i <- Y_i - X_i'beta\n"
            "  else\n"
            "    continue\n"
            "  end\n"
            "end\n"
            "return mean(delta)"
        )
        assert _has_line_per_statement(text)

    def test_prose_paragraph(self):
        text = (
            "For each unit, if the treatment indicator equals one, then compute "
            "the weighted average. While this estimator is consistent, it does not "
            "achieve efficiency. We repeat this procedure for all bootstrap "
            "iterations and return the confidence interval."
        )
        assert not _has_line_per_statement(text)

    def test_too_few_lines(self):
        assert not _has_line_per_statement("line 1\nline 2\nline 3")

    def test_long_lines(self):
        text = "\n".join(["x" * 100 for _ in range(5)])
        assert not _has_line_per_statement(text)


# ---------------------------------------------------------------------------
# _has_assignment_operators
# ---------------------------------------------------------------------------


class TestHasAssignmentOperators:
    def test_unicode_arrow(self):
        assert _has_assignment_operators("theta \u2190 0")

    def test_walrus_assign(self):
        assert _has_assignment_operators("theta := 0")

    def test_latex_leftarrow(self):
        assert _has_assignment_operators("theta \\leftarrow 0")

    def test_r_style_arrow(self):
        assert _has_assignment_operators("theta <- mean(x)")

    def test_no_assignment(self):
        assert not _has_assignment_operators("We compute the mean and return the result.")

    def test_equality_not_matched(self):
        # "==" is comparison, not assignment
        assert not _has_assignment_operators("if x == 0 then stop")


# ---------------------------------------------------------------------------
# _keyword_line_start_ratio
# ---------------------------------------------------------------------------


class TestKeywordLineStartRatio:
    def test_pseudocode_high_ratio(self):
        text = (
            "for i = 1 to N\n"
            "  if condition\n"
            "  then compute\n"
            "  else skip\n"
            "end\n"
            "return result"
        )
        assert _keyword_line_start_ratio(text) >= 0.5

    def test_prose_low_ratio(self):
        text = (
            "We estimate the model for each subgroup.\n"
            "The propensity score is computed.\n"
            "Standard errors are bootstrapped.\n"
            "Results are reported in Table 1."
        )
        assert _keyword_line_start_ratio(text) < 0.1

    def test_empty_text(self):
        assert _keyword_line_start_ratio("") == 0.0

    def test_numbered_steps_with_keywords(self):
        text = (
            "1. for each unit\n"
            "2. if treated then\n"
            "3. return estimate"
        )
        assert _keyword_line_start_ratio(text) >= 0.5
