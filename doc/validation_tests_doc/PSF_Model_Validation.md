## Requirement: R-SHE-PRD-F-100:

Parent: R-GDP-DL3-014 The distribution of χ2 (chi-squared) values for each star with respect to the model, over the
population of stars, shall be consistent (TBD) with the χ2-distribution.

[ANT: TBD to be removed in SHE RSD]

## Requirement Comment from GDPRD

This shall be demonstrated by estimating the chi-squared distribution of stellar residuals with respect to the PSF
model.

Requirements Chain:

## Validation Test: T-SHE-000001-PSF-res-star-pos

Estimate PSF model residuals at star positions and compare with suitable expected distribution (e.g. chi^2) with e.g. KL
test (ANT: should this be KS-test?)

This test is defined in the WL Validation doc in VAL-WL-SHE-0010.

## Rational:

To verify that the object PSF model residuals are consistent with noise, i.e., that there are no remaining systematics
in the PSF model.

## Test Cases:

### TC-SHE-100001-PSF-res-star-pos-tot

χ2 distribution of χ2 values of PSF residuals at star positions of total population

#### Test Procedure:

1. This process is carried out on real and simulated Euclid Observations.
1. This test is carried out per Observation.
1. Use each star (how selected? PHZ or SHE flag?) used in the PSF Fitting.
1. From the residuals between the PSF image to the PSF model, calculate the χ2 for each star.
1. Estimate the distribution of the χ2-values on a per-exposure basis.
1. Compute difference between distribution and theoretical χ2 distribution.

### TC-SHE-100002-PSF-res-star-pos-SNR

χ2 distribution of χ2 values of PSF residuals at star positions as function of SNR.

#### Test Procedure:

1. This process is carried out on real and simulated Euclid Observations.
1. This test is carried out per Observation.
1. Stars are binned by SNR (bin size, range?).
1. Use each star (how selected? PHZ or SHE flag?) in each SNR bin used in the PSF Fitting.
1. From the residuals between the PSF image to the PSF model, calculate the χ2 for each star.
1. Estimate the distribution of the χ2-values on a per-exposure basis.
1. Compute difference between distribution and theoretical χ2 distribution.

### TC-SHE-100002-PSF-res-star-pos-SED

As for the TC-SHE-100002-PSF-res-star-pos-SNR test with SNR replaced by SED.

### TC-SHE-100002-PSF-res-star-pos-pix

As for the TC-SHE-100002-PSF-res-star-pos-SNR test with SNR replaced by pixel coordinates.

### TC-SHE-100002-PSF-res-star-pos-epoch

As for the TC-SHE-100002-PSF-res-star-pos-SNR test with SNR replaced by epoch.

### TC-SHE-100002-PSF-res-star-pos-solaspang

As for the TC-SHE-100002-PSF-res-star-pos-SNR test with SNR replaced by solar aspect angle.
