## Requirement: R-SHE-CAL- F-060
Parent: None

R-SHE-CAL-F-060: An estimate of the SED of the stars used in the PSF modelling shall be provided, using available data.

## Requirement Comment from GDPRD
This shall be provided from PHZ.
[ANT: Note this is updated from SHE RSD which incorrectly named SPE. ]

## Validation Test: T-SHE-000011-star-SED-exist
Verify that an estimate of the SED of the stars used in the PSF modelling has been provided, using available data. This is provided by OU-PHZ.

## Rational:
Need to ensure adequate SED information is available from PHZ for PSF.

## Input Data
Catalogue of SEDs (from SPE) for stars. This has to include all stars used for the PSF.

## Analysis Tools
TBD

## Test Cases:
### TC-SHE-100033-star-SED-exist
Tests whether the SED exists of all stars used to determine the PSF model. The SED is provided from PHZ data products.

**Purpose:** Tests whether the SED exists of all stars used to determine the PSF model. The SED is provided from PHZ data products.

**Output:** Number and identify of stars used in PSF fitting with no SED from PHZ.

**Pass/Fail criteria:** An SED estimate exists for all stars that are used in the PSF model.

#### Test Procedure:
1. Identify stars used for PSF fitting toolkit.
1. Search for corresponding SED input data from PHZ.
1. If no SED from PHZ corresponds to stellar image in PSF fit, flag.
1. Collate number of flags and stellar IDs and output results.

