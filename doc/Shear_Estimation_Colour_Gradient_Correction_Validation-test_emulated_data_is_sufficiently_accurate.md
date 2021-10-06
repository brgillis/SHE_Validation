## Requirement: R-SHE-PRD-F-130 / R-SHE-PRD-F-150:
Parent: R-GDP-DL3-045

R-SHE-PRD-F-130: The error on the multiplicative bias (μ) on galaxy ellipticity for those used for weak lensing, determined using mock Euclid data created from HST imaging (an emulation of Euclid corrected for CTI) shall be known to better than 5x10-4.

R-SHE-PRD-F-150: The error on the additive bias (c) on galaxy ellipticity determined using mock Euclid data, created from HST imaging (an emulation of Euclid corrected for CTI) shall be known to better than 5 x10-5 (1 sigma).

[ANT Note: The accuracy was a TBD, will be updated in latest SHE RSD. ]

## Requirement Comment from GDPRD
This shall be demonstrated by an end-to-end analysis on validated HST and emulated Euclid data. This requires sub-Requirements internal to SHE to validate HST data on fields on which there is overlap with Euclid data when available and to validate emulated Euclid

Requirements Chain:

## Validation Test: T-SHE-000005-colgrad-emul

## Rational:
To validate that the emulated Euclid images are sufficiently realistic to be used for an accurate calibration of shear estimation biases, such as colour gradient bias.

## Input Data:
- Images created from multi-colour HST data processed with the same algorithm as was used for the colour gradient estimate.
- Deep Euclid observations of the above fields corrected for instrumental effects (e.g., CTI)
- The Euclid PSF model of those fields

## Analysis Tools:
- KS test
- Relative error
- Completeness

## Test Cases:
### TC-SHE-100013-colgrad-emul-A
Pixel histogram-level comparison of HST emulations of Euclid Deep Field Data and observed Euclid Deep Field Data. HST data is the same Deep Field data.

**Purpose:** Accuracy of emulated Euclid Deep Survey data obtained from multi-colour HST data: pixel histogram.

**Output:** Pixel value histograms of observed and emulated images.

**Pass/Fail criteria:** Test A: The average [TBD] of the differences of the histograms shall be consistent with zero at the TBD level.

#### Test Procedure:
1. Create emulation of Euclid observations of multi-colour HST fields using the PSF model inferred from the actual deep Euclid observations of those fields.
1. Create histograms of the pixel values of the observed and emulated images.
1. Compute the difference of the histograms.
1. Average to estimate μ\_1 = mean difference of the histograms (over some pixel range TBD).  
(This will show if one of the images has higher pixel values at the central regions of objects.)
1. Check that the quantities μ\_1 are within the requirements.

### TC-SHE-100014-colgrad-emul-B
Pixel-level comparison of HST emulations of Euclid Deep Field Data and observed Euclid Deep Field Data. HST data is the same Deep Field data.

**Purpose:** Accuracy of emulated Euclid Deep Survey data obtained from multi-colour HST data: difference images.

**Output:** Mean and skewness of the pixel values obtained by taking the difference image between observation and emulation.

**Pass/Fail criteria:** Test B: The mean as well as the skewness of the distribution of pixel values in the difference images shall be consistent with zero at the TBD level.

#### Test Procedure:
1. Create emulation of Euclid observations of multi-colour HST fields using the PSF model inferred from the actual deep Euclid observations of those fields.
1. Create images of the difference of the emulated and observed images.
1. Mask the locations of transients. [ANT: should this also be in the histogram test?]
1. Define μ1 = mean of the pixel values in the unmasked regions of the difference images.
1. Define μ2 = skewness of the distribution of pixel values.
1. Check that the quantities μ\_1 are within the requirements [TBD].

### TC-SHE-100015-colgrad-emul-C
Test object detection in HST and Deep Fields.

**Purpose:** Accuracy of emulated Euclid Deep Survey data obtained from multi-colour HST data: object detection.

**Output:** Fraction of matched objects between observed and emulated images.

**Pass/Fail criteria:** TBD% of the objects with magnitudes of range TBD shall be in common between the two catalogues.

#### Test Procedure:
1. Create emulation of Euclid observations of multi-colour HST fields using the PSF model inferred from the actual deep Euclid observations of those fields.
1. Carry out object detection on the emulated and observed images.
1. Estimated μ1 = fraction of matched objects within the magnitude range TBD.
1. Check that the quantities μ\_1 are within the requirements (TBD).

### TC-SHE-100016-colgrad-emul-D
Test differences between moments of Emulated HST and Deep Field Data.

**Purpose:** Accuracy of emulated Euclid Deep Survey data obtained from multi-colour HST data: brightness moments.

**Output:** Distribution of the ith moments of the surface brightness of objects, for observed and emulated images, with i = 0, 1, 2.

**Pass/Fail criteria:** The distributions of the differences of the zeroth, first, and second moments of the surface brightness shall be consistent with a median [TBD] of zero at the TBD level.

#### Test Procedure:
1. Create an emulation of the Euclid observations of the multi-colour HST fields using the PSF model inferred from the actual deep Euclid observations of those fields.
1. Compute zeroth, first and second moments [TBD] of the surface brightness for objects with magnitudes TBD.
1. Estimate the distribution of the differences of the moments. Estimate μ\_1, μ\_2, μ\_3 = quantifiers of those distributions, TBD.
1. Check that the quantities μ\_i are within the requirements (TBD).

## Issues:

Need functions to determine if a position lies within Euclid survey, and which observation it lies in.
