## Requirement: R-SHE-PRD-F-160 / R-SHE-PRD-F-160
Parent: R-GDP- DL3-048 / 049

R-SHE-PRD-F-160: The error on the variance of the probability distribution function (pdf) of the ellipticity distribution for representative sub-samples (TBD) of the galaxies used in the weak lensing analysis shall be less than 5x10-4.

R-SHE-PRD-F-160: The kurtosis and the skewness of the probability distribution function (pdf) of the ellipticity distribution for representative sub- samples (TBD) of the galaxies used in the weak lensing analysis shall be known better than TBD

## Requirement Comment from GDPRD
This will be measured from the Euclid Deep Field data, and the PDF accuracy validated by Euclid emulations.

## Validation Test: T-SHE-000007-pdf-eps-s

## Rational:
All shear estimation algorithms require knowledge of the distribution of the absolute value of the intrinsic galaxy ellipticity (exact definition TBD; see comments), without contributions by measurement noise. This knowledge is specified in terms of the 2nd, 3rd, and 4th central moments of this distribution. By requiring that the rms on the variance, skewness, and kurtosis is below certain thresholds, it is ensured that the statistical uncertainty (governed by the number of galaxies used to measure the distribution) and any systematic uncertainties do not degrade the shear estimation process in a significant manner. The intrinsic galaxy ellipticity distribu- tion is measured from the Euclid Deep survey, in which galaxy shear estimates have negligible measurement noise.

## Input Data
- Set of Euclid Deep Survey degraded realisations emulated to same depth as Wide.
- Set of Euclid Wide Survey fields selected to have same size as Euclid Deep Survey.

## Analysis Tools
Relative error analysis of moments of measured distribution.

## Test Cases:
### TC-SHE-100019-pdf-eps-s-m2
Test that the r.m.s. error on the 2nd moment (variance) of the intrinsic ellipticity distribution per shear measurement method is within specification.

ANT: is this the 2nd moment or the 2nd reduced moment?

**Purpose:** Test the accuracy of the second moment of p(e) is within specification.

**Output:** Field-to-field variance of the ellipticity distribution from (a) patches of the Euclid Wide survey, and (b) degraded realisations of the Deep survey (emulations).

**Pass/Fail criteria:** TBD.

#### Test Procedure:
1. Divide the Wide Survey into patches of the same size as the Deep Survey.
1. Measure the intrinsic galaxy ellipticity distribution (now with measurement noise included) on every patch for every shear measurement method.
1. Obtain the mean distribution.
1. Quantify the statistical uncertainty in the mean of the distributions via field-to-field variance.
1. Divide the exposures of the Deep Survey into subsets that have the same depth as the Wide Survey.
1. Measure the intrinsic galaxy ellipticity distribution (now with measurement noise included) in every subset.
1. Obtain the mean distribution.
1. Quantify the statistical uncertainty in the mean of the distributions via field-to-field vari- ance.
1. Compare the two distributions by estimating the difference of the second moment.
1. Check the difference against the requirement.

Note: A more general test could be performed as follows. The two mean distributions should be consistent with each other with the respective noise limits. This comparison can be performed via Kullback-Leibler divergence. A mapping between the KL divergence and moments of the distributions would have to be established to compare to the requirements.

### TC-SHE-100020-pdf-eps-s-m3
Test that the r.m.s. error on the 3rd moment (skewness) of the intrinsic ellipticity distribution per shear measurement method is within specification.

As for TC-SHE-100019-pdf-eps-s-m2 with variance replaced by skewness.

### TC-SHE-100021-pdf-eps-s-m4
Test that the r.m.s. error on the 4rd moment (kurtosis) of the intrinsic ellipticity distribution per shear measurement method is within specification.

As for TC-SHE-100019-pdf-eps-s-m2 with variance replaced by kurtosis.

