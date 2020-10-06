## Requirement: R-SHE-CAL-F-020:
Residual of CTI to PSF ellipticity <1.1x10-4 (1-sigma) per VIS exposure per component.

## Requirement Comment from GDPRD
CTI is initially Validated at the pixel level in VIS (R-VIS-PRD-F-196).
In SHE tested on emulated VIS images.
On Euclid data by cross-correlating corrected galaxy ellipticity in image coordinates with e.g. image position, time, object S/N and size, and sky background. The same cross-correlations shall be performed on residuals of stars after subtraction of the PSF model.

Requirements Chain:
R-VIS-PRD-F-196 (R-SHE-VIS-007, R-SHE-VIS-015) "CTI correction and calibration": Pre and post-CTI correction images shall be provided for each exposure.
Note this was a new Requirement for VIS from SHE, with no parent GDPRD Requirement.

Related VIS Validation:
VAL-WL-VIS-0030
Parent: R-VIS-CAL-F-040, R-VIS-CAL-F-020

##Validation Test: T-SHE-000009-CTI-PSF
Linear dependence of PSF ellipticity with read-out register distance (slope).

## Rational:
Residual CTI is expected to leave a trail along the Readout direction of the CCD, which will induce an ellipticity signal as a function of distance from the Readout Register. The absolute value of this is degenerate with other effects, so the test is to measure the gradient of the ellipticity as a function of distance from the Readout Register, which would indicate a residual CTI. Note this is not a strong test (compared to eg a chi^2 fit of the PSF), but is a sanity test of the PSF at the Catalogue Level.

## Test Cases:
TC-SHE-100024-CTI-PSF-SNR
Linear dependence of residual PSF ellipticity with read-out register distance (slope) in bins of SNR of stars.

### Test Procedure:
1. This process is carried out on simulated Euclid Observations.
1. This test is carried out per Observation.
1. Stars are binned by SNR over the range [TBD] with bin intervals of [TBD]. [Note: what sample of stars?]
1. Each SNR sample is binned in distance from the Readout Register on each CCD. [Note: per pixel? Dont need to bin, but would to plot results? ]
1. The average difference between the Model PSF ellipticity and simulated Stellar image ellipticity calculated, with error. Need the SIM PSF used to generate the stellar image and fitted model PSF for star.
1. The linear regression of the slope of the differential ellipticity as a function of readout distance is estimated, with error.
1. The sloped and its error are compare to a threshold [TBD].
1. If slope or error is larger than threshold, flag Observation.
1. Results are stored.
1. Results are collated Globally and compared to Simulated distributions. [TBC]
1. Need to be able to plot results and fit Locally and Globally.
1. Summary Statistics and Figures are produced.

## Test Cases:
TC-SHE-100025-CTI-PSF-bg
As for TC-SHE-100024-CTI-PSF-SNR with SNR replaced by Sky Background Level.

## Test Cases:
TC-SHE-100025-CTI-PSF-col
As for TC-SHE-100024-CTI-PSF-SNR with SNR replaced by Colour.

## Test Cases:
TC-SHE-100025-CTI-PSF-epoch
As for TC-SHE-100024-CTI-PSF-SNR with SNR replaced by Observation Epoch.

## Issues:

SIM is not currently providing images of the PSF models they use. We will need to request that they provide such a data product.