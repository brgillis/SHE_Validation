---
numbersections: true geometry: margin=2cm fontsize: 12pt documentclass: article
---

# SHE_Validation_DataQuality

This module contains executable code to run the following validation tests, dealing with basic data quality checks:

* T-SHE-000008-gal-info
* T-SHE-000011-star-SED-exist
* T-SHE-000013-data-proc

## T-SHE-000008-gal-info

The data products of the weak lensing pipeline must include essential information on any weak lensing object or indicate
why information is missing (flags). All essential data fields require a confidence level and a quality flag.
Furthermore, all objects identified as weak lensing objects prior to OU-SHE have to be included. As additional goal, the
catalogue should also contain quantifiers of the galaxy morphology and type.

### Requirement: R-SHE-PRD-F-180

Parent: R-GDP-DL3-060

R-SHE-PRD-F-180: For each galaxy used in the weak lensing analysis up to the limiting magnitude the following
information should be available:

- at east 1 ellipticity measurement such that a shear estimate can be inferred.
- the posterior probability distribution of the true ellipticity given the data
- the posterior probability distribution of the photometric redshift given the data
- estimate of the covariance between photometric redshift and ellipticity (TBD)
- the classification star / galaxy
- confidence level and quality assessment
- at least one size measurement

### Requirement Comment from GDPRD

Validated by SHE and SGS

### Rationale:

Ensure that every weak lensing object provides the following:

- at least one ellipticity measurement such that a shear estimate can be inferred;
- the posterior distribution of the ellipticity;
- the posterior distribution of the photometric redshift;
- an estimate of the covariance between photometric redshift and ellipticity, from joint inference of redshift and
  ellipticity [TBD];
- the star-galaxy classification;
- at least one measurement of galaxy size;
- quality flags [TBD];
- a morphology/type quantifier is optional but should be clearly flagged if present or not present.

### Input Data

The OU-SHE catalogue of weak lensing objects and a list of all objects identified as weak lensing object (the input
catalogue to OU-SHE).

### Analysis Tools

Completeness, existence of measurement or appropriate flags.

### Test Cases:

#### TC-SHE-100022-gal-N-out

Compare the number of objects in the input and output catalogues for SHE.

**Purpose:** Check that no objects are lost in analysis.

**Output:** Fraction of number output to input objects, Nout/Nin.

**Pass/Fail criteria:** Both conditions in the test description must be fulfilled: All objects on input are present in
the output catalogue (Nout/Nin =1), and all output catalogue entries have valid values or else are flagged.

##### Test Procedure:

1. Evaluate number of objects in SHE input catalogue, N\_in.
2. Evaluate number of objects in SHE output catalogue, N\_out.
3. Take ratio of N\_out to N\_in (Nout/N\_in).
4. Check Nout/N\_in =1

ANT Note: Should we make a pairwise comparison per object?

#### TC-SHE-100023-gal-info-out

Test that all SHE measurements in shear catalogue have a measurement or are flagged appropriately.

**Purpose:** Test that all SHE measurements in shear catalogue have a measurement or are flagged appropriately.

**Output:** Number of objects N\_inv with invalid measurement that are not flagged appropriately.

**Pass/Fail criteria:** Both conditions in the test description must be fulfilled: All objects on input are present in
the output catalogue (Nout/Nin =1), and all output catalogue entries have valid values or else are flagged (N\_inv=0).

##### Test Procedure:

Test all entries in Shear Catalogue have valid measurements or else have appropriate quality flags set (in the case of
NaNs or out-of-range values).

## T-SHE-000011-star-SED-exist

Verify that an estimate of the SED of the stars used in the PSF modelling has been provided, using available data. This
is provided by OU-PHZ.

### Requirement: R-SHE-CAL- F-060

Parent: None

R-SHE-CAL-F-060: An estimate of the SED of the stars used in the PSF modelling shall be provided, using available data.

### Requirement Comment from GDPRD

This shall be provided from PHZ.
[ANT: Note this is updated from SHE RSD which incorrectly named SPE. ]

### Rationale:

Need to ensure adequate SED information is available from PHZ for PSF.

### Input Data

Catalogue of SEDs (from SPE) for stars. This has to include all stars used for the PSF.

### Analysis Tools

TBD

### Test Cases:

#### TC-SHE-100033-star-SED-exist

Tests whether the SED exists of all stars used to determine the PSF model. The SED is provided from PHZ data products.

**Purpose:** Tests whether the SED exists of all stars used to determine the PSF model. The SED is provided from PHZ
data products.

**Output:** Number and identify of stars used in PSF fitting with no SED from PHZ.

**Pass/Fail criteria:** An SED estimate exists for all stars that are used in the PSF model.

##### Test Procedure:

1. Identify stars used for PSF fitting toolkit.
2. Search for corresponding SED input data from PHZ.
3. If no SED from PHZ corresponds to stellar image in PSF fit, flag.
4. Collate number of flags and stellar IDs and output results.

## T-SHE-000013-data-proc

TBD
