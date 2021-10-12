## Requirement: R-SHE-PRD-F-180

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

## Requirement Comment from GDPRD

Validated by SHE and SGS

## Validation Test: T-SHE-000008-gal-info

The data products of the weak lensing pipeline must include essential information on any weak lensing object or indicate
why information is missing (flags). All essential data fields require a confidence level and a quality flag.
Furthermore, all objects identified as weak lensing objects prior to OU-SHE have to be included. As additional goal, the
catalogue should also contain quantifiers of the galaxy morphology and type.

## Rational:

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

## Input Data

The OU-SHE catalogue of weak lensing objects and a list of all objects identified as weak lensing object (the input
catalogue to OU-SHE).

## Analysis Tools

Completeness, existence of measurement or appropriate flags.

## Test Cases:

### TC-SHE-100022-gal-N-out

Compare the number of objects in the input and output catalogues for SHE.

**Purpose:** Check that no objects are lost in analysis.

**Output:** Fraction of number output to input objects, Nout/Nin.

**Pass/Fail criteria:** Both conditions in the test description must be fulfilled: All objects on input are present in
the output catalogue (Nout/Nin =1), and all output catalogue entries have valid values or else are flagged.

#### Test Procedure:

Evaluate number of objects in SHE input catalogue, N\_in.  
Evaluate number of objects in SHE output catalogue, N\_out.  
Take ratio of N\_out to N\_in (Nout/N\_in).  
Check Nout/N\_in =1

ANT Note: Should we make a pairwise comparison per object?

### TC-SHE-100023-gal-info-out

Test that all SHE measurements in shear catalogue have a measurement or are flagged appropriately.

**Purpose:** Test that all SHE measurements in shear catalogue have a measurement or are flagged appropriately.

**Output:** Number of objects N\_inv with invalid measurement that are not flagged appropriately.

**Pass/Fail criteria:** Both conditions in the test description must be fulfilled: All objects on input are present in
the output catalogue (Nout/Nin =1), and all output catalogue entries have valid values or else are flagged (N\_inv=0).

#### Test Procedure:

Test all entries in Shear Catalogue have valid measurements or else have appropriate quality flags set (in the case of
NaNs or out-of-range values).
