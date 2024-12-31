from itertools import combinations

import numpy as np
from scipy.stats import kruskal
from scipy.stats import mannwhitneyu
from scipy.stats import shapiro
from scipy.stats import ttest_rel
from scipy.stats import wilcoxon
from statsmodels.stats.diagnostic import lilliefors


def mann_whitney_test(samples, alpha=0.05):
    """
    Perform the Mann-Whitney U rank test on two independent samples.

    The Mann-Whitney U test is a nonparametric test of the null hypothesis that the distribution underlying sample x is
    the same as the distribution underlying sample y. It is often used as a test of difference in location between
    distributions.
    """

    sample_a, sample_b = samples
    if len(sample_a) < 5 or len(sample_b) < 5:
        raise ValueError("Each sample must contain at least 5 elements to perform the Mann-Whitney test.")

    # all samples must have more than 5 elements
    statistic, p_value = mannwhitneyu(sample_a, sample_b, nan_policy="omit")
    if p_value <= alpha:
        return round(p_value, 3), "rejected"
    else:
        return round(p_value, 3), "accepted"


def paired_ttest(sample1, sample2, alpha=0.05):
    """
    Perform paired t-test between two samples and interpret the result.

    Parameters:
    - sample1: The first sample.
    - sample2: The second sample.
    - alpha: The significance level for the test (default is 0.05).

    Returns:
    - dict: A dictionary containing the test statistic, p-value, and interpretation.
    """

    if len(sample1) < 5 or len(sample2) < 5:
        raise ValueError("Each sample must contain at least 5 elements to perform the Paired T-test.")

    # Check if the samples are identical
    if sample1 == sample2:
        return {"p-value": 1.0, "interpretation": f"Given the alpha {alpha}, fail to reject the null hypothesis. There "
                                                  f"is no significant difference between the samples."}

    # Perform paired t-test if both samples are normal
    t_stat, p_value = ttest_rel(sample1, sample2, nan_policy="omit")

    # Interpret the result
    if p_value <= alpha:
        interpretation = (
            f"Given the alpha {alpha}, reject the null hypothesis. There is a significant difference "
            f"between the samples."
        )
    else:
        interpretation = (
            f"Given the alpha {alpha}, fail to reject the null hypothesis. There is no significant "
            f"difference between the samples."
        )

    return {"p-value": p_value, "interpretation": interpretation}


def wilcoxon_test(sample1, sample2, alpha=0.05):
    """
    Perform the Wilcoxon signed-rank test between two samples and interpret the result.

    Parameters:
    sample1 (array-like): The first sample.
    sample2 (array-like): The second sample.
    alpha (float): The significance level for the test (default is 0.05).

    Returns:
    dict: A dictionary containing the test statistic, p-value, and interpretation.
    """

    # Check that both samples have at least 5 elements
    if len(sample1) < 5 or len(sample2) < 5:
        raise ValueError("Each sample must contain at least 5 elements to perform the Wilcoxon test.")

    # Check if samples are identical (early exit with p-value = 1)
    if sample1 == sample2:
        return {"p-value": 1.0,
                "interpretation": f"Given the significance level {alpha}, it fails to reject the null hypothesis. The differences between both samples are not statistically significant."}

    # Perform Wilcoxon signed-rank test
    w_stat, p_value = wilcoxon(sample1, sample2, nan_policy="omit")

    # Handle cases with NaN p-values (invalid results)
    if p_value != p_value:  # NaN check
        raise ValueError(
            "The Wilcoxon test returned an invalid p-value. This may be due to identical values or other issues with the input data.")

    # Interpret the result
    if p_value <= alpha:
        interpretation = (
            f"Given the significance level {alpha}, it rejects the null hypothesis. The differences between both samples "
            f"are statistically significant."
        )
    else:
        interpretation = (
            f"Given the significance level {alpha}, it fails to reject the null hypothesis. The differences between "
            f"both samples are not statistically significant."
        )

    # Return the test statistic, p-value, and interpretation
    return {"p-value": p_value, "interpretation": interpretation}


def shapiro_wilk_test(sample, alpha=0.05):
    """
    Perform the Shapiro-Wilk test for normality on a sample and interpret the result.

    Parameters:
    sample: The sample to test for normality.
    alpha: The significance level for the test (default is 0.05).

    Returns:
    dict: A dictionary containing the test statistic, p-value, and interpretation.
    """
    # Ensure the sample has enough elements
    if len(sample) < 3:
        raise ValueError("Sample must have at least 3 elements to perform the Shapiro-Wilk test.")

    # Perform Shapiro-Wilk test
    test_statistic, p_value = shapiro(x=sample, nan_policy="omit")

    # Convert to scientific notation
    stat_sci = f"{test_statistic:.3e}"
    p_value_sci = f"{p_value:.3e}"

    # Interpret the result
    if p_value <= alpha:
        interpretation = "Null hypothesis rejected, the sample does not follow a normal distribution."
        normality = False
    else:
        interpretation = "Fail to reject the null hypothesis, the sample follows a normal distribution."
        normality = True

    # Return the test statistic, p-value, and interpretation
    return {
        "Statistic": stat_sci,
        "P-value": p_value_sci,
        "Normally distributed": normality,
        "Null hypothesis interpretation": interpretation,
    }


def lilliefors_test(sample, alpha=0.05):
    """
    Perform the Lilliefors test for normality on a sample and interpret the result.

    Parameters:
    sample (array-like): The sample to test for normality.
    alpha (float): The significance level for the test (default is 0.05).

    Returns:
    dict: A dictionary containing the test statistic, p-value, and interpretation.
    """
    # Ensure the sample has enough elements
    if len(sample) < 3:
        raise ValueError("Sample must have at least 3 elements to perform the Lilliefors test.")

    # Perform Lilliefors test
    test_statistic, p_value = lilliefors(sample, dist="norm", pvalmethod="approx")

    # Convert to scientific notation
    stat_sci = f"{test_statistic:.3e}"
    p_value_sci = f"{p_value:.3e}"

    # Interpret the result
    if p_value <= alpha:
        interpretation = "Null hypothesis rejected, the sample does not follow a normal distribution."
        normality = False
    else:
        interpretation = "Fail to reject the null hypothesis, the sample follows a normal distribution."
        normality = True

    # Return the test statistic, p-value, and interpretation
    return {
        "Statistic": stat_sci,
        "P-value": p_value_sci,
        "Normally distributed": normality,
        "Null hypothesis interpretation": interpretation,
    }


def normality_test(data, alpha=0.05, threshold_observations=50):
    """
    Check the normality of data using Shapiro-Wilk or Lilliefors test based on the sample size.

    Parameters:
    - data (array-like): The data to be tested for normality.
    - alpha (float): The significance level for the tests (default is 0.05).
    - threshold_observations (int): The sample size threshold for choosing between Shapiro-Wilk and Lilliefors test.

    Returns:
    - dict: A dictionary containing the test name, test statistic, p-value, and normality assessment.
    """
    # Number of observations in the data
    n = len(data)

    if n <= threshold_observations:
        # Use Shapiro-Wilk test for smaller sample sizes
        result = shapiro_wilk_test(data, alpha)
        test_name = "Shapiro-Wilk"
    else:
        # Use Lilliefors test for larger sample sizes
        result = lilliefors_test(data, alpha)
        test_name = "Lilliefors"

    # Building output
    output = {"Test performed": test_name, "Sample length": n, "Alpha": alpha}
    output.update(result)

    return output
