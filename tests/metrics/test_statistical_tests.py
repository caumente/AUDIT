import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import numpy as np
import pytest

from src.audit.metrics.statistical_tests import lilliefors_test
from src.audit.metrics.statistical_tests import mann_whitney_test
from src.audit.metrics.statistical_tests import paired_ttest
from src.audit.metrics.statistical_tests import shapiro_wilk_test
from src.audit.metrics.statistical_tests import wilcoxon_test


# Test case for valid samples with more than 5 elements
def test_mann_whitney_valid_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

    p_value, result = mann_whitney_test([sample_a, sample_b])

    # Since the distributions are identical (just reversed), the Mann-Whitney U test should accept the null hypothesis
    assert isinstance(p_value, float)
    assert result == "accepted"  # Null hypothesis should be accepted, not rejected
    assert p_value > 0.05  # The p-value should be greater than 0.05 (indicating no significant difference)


def test_mann_whitney_invalid_sample_sizes():
    sample_a = [1, 2, 3]
    sample_b = [10, 9, 8]

    try:
        mann_whitney_test([sample_a, sample_b])
        assert False, "Expected AssertionError due to sample size less than 5"
    except ValueError:
        pass  # Test passes if AssertionError is raised


def test_mann_whitney_significantly_different_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

    p_value, result = mann_whitney_test([sample_a, sample_b])

    # Since the distributions are significantly different, the Mann-Whitney U test should reject the null hypothesis
    assert isinstance(p_value, float)
    assert result == "rejected"  # Null hypothesis should be rejected
    assert p_value <= 0.05  # The p-value should be less than 0.05 (indicating significant difference)


def test_mann_whitney_identical_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    p_value, result = mann_whitney_test([sample_a, sample_b])

    # Since the samples are identical, the Mann-Whitney U test should accept the null hypothesis
    assert isinstance(p_value, float)
    assert result == "accepted"  # Null hypothesis should be accepted
    assert p_value > 0.05  # The p-value should be greater than 0.05 (indicating no significant difference)


def test_mann_whitney_one_empty_sample():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = []

    try:
        mann_whitney_test([sample_a, sample_b])
        assert False, "Expected AssertionError due to empty sample"
    except ValueError:
        pass  # Test passes if AssertionError is raised


# Test case for valid samples with more than 5 elements
def test_paired_ttest_valid_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]

    result = paired_ttest(sample_a, sample_b)

    # The paired t-test should return a p-value and interpretation of the results
    assert isinstance(result["p-value"], float)
    assert "fail to reject" in result["interpretation"]  # Null hypothesis should not be rejected
    assert result["p-value"] > 0.05  # p-value should be greater than 0.05 (indicating no significant difference)


# Test case for invalid sample sizes (less than 5 elements)
def test_paired_ttest_invalid_sample_sizes():
    sample_a = [1, 2, 3]
    sample_b = [10, 9, 8]

    try:
        paired_ttest(sample_a, sample_b)
        assert False, "Expected ValueError due to sample size less than 5"
    except ValueError:
        pass  # Test passes if ValueError is raised


# Test case for significantly different samples
def test_paired_ttest_significantly_different_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

    result = paired_ttest(sample_a, sample_b)

    # Since the distributions are significantly different, the paired t-test should reject the null hypothesis
    assert isinstance(result["p-value"], float)
    assert "reject" in result["interpretation"]  # Null hypothesis should be rejected
    assert result["p-value"] <= 0.05  # p-value should be less than 0.05 (indicating significant difference)


# Test case for identical samples (should fail to reject the null hypothesis)
def test_paired_ttest_identical_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    result = paired_ttest(sample_a, sample_b)

    # Since the samples are identical, the paired t-test should fail to reject the null hypothesis
    assert isinstance(result["p-value"], float)
    assert "fail to reject" in result["interpretation"]  # Null hypothesis should not be rejected
    assert result["p-value"] > 0.05  # p-value should be greater than 0.05 (indicating no significant difference)


# Test case for empty sample (should raise ValueError)
def test_paired_ttest_one_empty_sample():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = []

    try:
        paired_ttest(sample_a, sample_b)
        assert False, "Expected ValueError due to empty sample"
    except ValueError:
        pass  # Test passes if ValueError is raised


# Test case for valid samples with more than 5 elements and no significant difference
def test_wilcoxon_identical_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    result = wilcoxon_test(sample_a, sample_b)

    # Since the samples are identical, the Wilcoxon test should fail to reject the null hypothesis
    assert isinstance(result["p-value"], float)
    assert (
        result["interpretation"]
        == "Given the significance level 0.05, it fails to reject the null hypothesis. The differences between both samples are not statistically significant."
    )
    assert result["p-value"] == 1.0  # p-value should be 1 for identical samples


# Test case for valid samples with more than 5 elements and significant difference
def test_wilcoxon_significantly_different_samples():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140]

    result = wilcoxon_test(sample_a, sample_b)

    # The samples are significantly different, so the Wilcoxon test should reject the null hypothesis
    assert isinstance(result["p-value"], float)
    assert "rejects the null hypothesis" in result["interpretation"]  # Null hypothesis should be rejected
    assert result["p-value"] < 0.05  # p-value should be less than 0.05 (indicating significant difference)


# Test case for invalid sample size (less than 5 elements in one sample)
def test_wilcoxon_invalid_sample_sizes():
    sample_a = [1, 2, 3]
    sample_b = [10, 9, 8]

    try:
        wilcoxon_test(sample_a, sample_b)
        assert False, "Expected ValueError due to sample size less than 5"
    except ValueError:
        pass  # Test passes if ValueError is raised


# Test case for valid samples with more than 5 elements but no significant difference
def test_wilcoxon_no_significant_difference():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    sample_b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]

    result = wilcoxon_test(sample_a, sample_b)

    # The samples are not identical, but there is no significant difference between them
    assert isinstance(result["p-value"], float)
    assert "fails to reject the null hypothesis" in result["interpretation"]
    assert result["p-value"] > 0.05  # p-value should be greater than 0.05


def test_wilcoxon_with_invalid_values():
    sample_a = [1, 2, 3, 4, 5, 6, 7, 8, 10]
    sample_b = [1, 2, 3, 4, 5, 6, 7, np.nan, 9]

    result = wilcoxon_test(sample_a, sample_b)

    # The samples are not identical, but there is no significant difference between them
    assert isinstance(result["p-value"], float)
    assert "fails to reject the null hypothesis" in result["interpretation"]
    assert result["p-value"] > 0.05  # p-value should be greater than 0.05


# Test case for empty samples (which should raise an error)
def test_wilcoxon_empty_sample():
    sample_a = []
    sample_b = []

    try:
        wilcoxon_test(sample_a, sample_b)
        assert False, "Expected ValueError due to empty samples"
    except ValueError:
        pass  # Test passes if ValueError is raised


# Test for valid samples (normal distribution)
def test_shapiro_valid_sample():
    sample = np.random.normal(loc=0, scale=1, size=30)  # Generate a normal sample
    result = shapiro_wilk_test(sample)

    assert result["Normally distributed"] is True
    assert float(result["P-value"]) > 0.05  # P-value should indicate normality for a normal distribution


# Test for valid samples (non-normal distribution)
def test_shapiro_non_normal_sample():
    sample = np.random.lognormal(mean=0, sigma=45, size=30)  # Generate a non-normal sample
    result = shapiro_wilk_test(sample)

    assert result["Normally distributed"] is False
    assert float(result["P-value"]) <= 0.05  # P-value should indicate non-normality for a uniform distribution


# Test for sample size too small
def test_shapiro_small_sample():
    sample = [1, 2]
    with pytest.raises(ValueError):
        shapiro_wilk_test(sample)


# Test for valid samples (normal distribution) for Lilliefors test
def test_lilliefors_valid_sample():
    sample = np.random.normal(loc=0, scale=1, size=1000)  # Generate a normal sample
    result = lilliefors_test(sample)

    assert result["Normally distributed"] is True
    assert float(result["P-value"]) > 0.01  # P-value should indicate normality for a normal distribution


# Test for valid samples (non-normal distribution) for Lilliefors test
def test_lilliefors_non_normal_sample():
    sample = np.random.lognormal(mean=0, sigma=45, size=1000)  # Generate a non-normal sample
    result = lilliefors_test(sample)

    assert result["Normally distributed"] is False
    assert float(result["P-value"]) <= 0.01  # P-value should indicate non-normality for a uniform distribution


# Test for sample size too small for Lilliefors test
def test_lilliefors_small_sample():
    sample = [1, 2]
    with pytest.raises(ValueError):
        lilliefors_test(sample)
