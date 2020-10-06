## Requirement: R-SHE-CAL-F-140:
Residual of CTI to galaxy multiplicative bias mu <5x10-4 (1-sigma).

Note: There is no equivalent CTI Requirement for Additive Bias. Should there be?

## Requirement Comment from GDPRD
None

## Validation Test: T-SHE-000010-CTI-gal
Linear dependence of galaxy ellipticity with read-out register distance (slope).

## Rational:
Residual CTI is expected to leave a trail along the Readout direction of the CCD, which will induce a galaxy ellipticity signal as a function of distance from the Readout Register. The absolute value of this is degenerate with other effects, so the test is to measure the gradient of the ellipticity as a function of distance from the Readout Register, which would indicate a residual CTI.

## Test Cases:
### TC-SHE-100028-CTI-gal-SNR
Linear dependence of residual galaxy ellipticity with read-out register distance (slope) in bins of SNR of galaxies.

#### Test Procedure:
1. This process is carried out on real and simulated Euclid Observations.
1. This test is carried out per Observation.
1. Galaxies are binned by SNR over the range [TBD] with bin intervals of [TBD]. [Note: what sample of galaxies?]
1. Each SNR sample is binned in distance from the Readout Register on each CCD. [Note: per pixel? Dont need to bin, but would to plot results? ]
1. The average galaxy ellipticity per bin in estimated with error.
1. The linear regression of the slope of the ellipticity as a function of readout distance is estimated, with error.
1. The sloped and its error are compare to a threshold [TBD].
1. If slope or error is larger than threshold, flag Observation.
1. Results are stored.
1. Results are collated Globally and compared to Simulated distributions. [TBC]
1. Need to be able to plot results and fit Locally and Globally.
1. Summary Statistics and Figures are produced.

### TC-SHE-100029-CTI-gal-bg
As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by Sky Background Level.

### TC-SHE-100030-CTI-gal-col
As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by galaxy Colour.

### TC-SHE-100031-CTI-gal-size
As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by galaxy size.

### TC-SHE-100031-CTI-gal-epoch
As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by Observation Epoch.

