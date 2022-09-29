---
numbersections: true geometry: margin=2cm fontsize: 12pt documentclass: article
---

# PSF Validation Test Descriptions

## PSF Model Validation

### Requirement: R-SHE-PRD-F-100:

Parent: R-GDP-DL3-014

The distribution of χ2 (chi-squared) values for each star with respect to the model, over the population of stars,
shall be consistent with the χ2-distribution.

#### Requirement Comment from GDPRD

This shall be demonstrated by estimating the chi-squared distribution of stellar residuals with respect to the PSF
model. Consistency is determined by passing a chi-squared test. 

### Validation Test: T-SHE-000001-PSF-res-star-pos

Comparison of the residual distribution of the measurement with the distribution of the PSF recovery simulation. This
comparison will be carried out with a KS test.

### Rationale:

To verify that the object PSF model residuals are consistent with noise, i.e., that there are no remaining systematics
in the PSF model.

### Test Case: TC-SHE-100001-PSF-res-star-pos-tot

Distribution of PSF residuals at star positions of total population.

#### Test Procedure:

1. Choose population of stars that is:
   - unbinned (using the entire set of stars)
2. From the residuals between the PSF image to the PSF model, calculate the distribution.
3. Estimate the distribution of residual from the PSF recovery simulations.
4. Compute difference between measured and simulated distributions, using a KS test.

### Test Case: TC-SHE-100002-PSF-res-star-pos-SNR

Distribution of PSF residuals at star positions as function of SNR.

#### Test Procedure:

1. Choose population of stars that is:
   - binned as function of S/N. The bin limits should be chosen to provide significant subsamples (e.g. quartiles) of
     the dataset.
2. From the residuals between the PSF image to the PSF model, calculate the distribution.
3. Estimate the distribution of residuals from the PSF recovery simulations.
4. Compute difference between measured and simulated distributions, using a KS test.


## PSF SED Validation

### Requirement: R-SHE-CAL-F-040
 
Parent: R-GDP-CAL-025

The uncertainty on the bias in the ellipticity of an object arising from the transfer of the VIS PSF
ellipticity model to the weak-lensing objects shall be smaller than 3.5x10^-5 (1-sigma)

#### Requirement Comment from GDPRD

This shall be demonstrated on emulated Euclid images with realistic SEDs for stars and galaxies. This Requirement has
been revised by OU-SHE to specify error and 1-sigma measure. This should propagate to GDPRD.

### Requirement: R-SHE-CAL-F-050:

Parent: R-GDP-CAL-035

The bias caused in the inferred R^2 of an object arising from the transfer of the wavelength dependence of the VIS PSF 
shall be < 3.5x10^-4.

#### Requirement Comment from GDPRD

This shall be demonstrated on emulated Euclid images with realistic SEDs for stars and galaxies. [Note a proposed
revision of this Requirement to an error has been proposed by SHE.]

### Validation Test: T-SHE-000002-PSF-lambda

Estimate PSF model residuals at star positions and compare with suitable expected distribution (e.g. chi^2) with e.g.
KS test.

### Rationale:

Ensures that the object PSF model captures the correct wavelength dependence for stars.

### Test Case: TC-SHE-100003-PSF-lambda-ell

Approximate PSF from broad-band magnitudes compared to precise PSF from spectroscopic data, effect on ellipticity.

#### Test Procedure:

1. For every star i, use the spectral information to create the precise reference PSF I_psf,i(g) as function of position
   g for the star SED and the star position.
2. Emulate broad-band magnitudes of the star by using the star SED, broad-band filter curves, and templates provided by
   PHZ.
3. Construct an approximate, interpolated PSF model Ihat_psf,i(g) of the star by making use of the emulated broad-band
   magnitudes only.
4. Compute the unweighted quadrupole moments Q_kl,i and Qhat_kl,i from I_psf,i(g) and Ihat_psf,i(g), respectively;
   k, l = 1, 2 are the components of the 2D tensor Q_kl,i.
5. Compute from Q_kl,i, Qhat_kl,i, respectively:
   - The ellipticity components e_ij, ehat_ij, where j = 1, 2 are the ellipticity components.
6. Obtain difference between reference and estimated, approximate quantities, and their scatter (around zero by
   construction).

### Test Case: TC-SHE-100004-PSF-lambda-R2

Approximate PSF from broad-band magnitudes compared to precise PSF from spectroscopic data, effect on size.

#### Test Procedure:

1. For every star i, use the spectral information to create the precise reference PSF I_psf,i(g) as function of position
   g for the star SED and the star position.
2. Emulate broad-band magnitudes of the star by using the star SED, broad-band filter curves, and templates provided by
   PHZ.
3. Construct an approximate, interpolated PSF model Ihat_psf,i(g) of the star by making use of the emulated broad-band
   magnitudes only.
4. Compute the unweighted quadrupole moments Q_kl,i and Qhat_kl,i from I_psf,i(g) and Ihat_psf,i(g), respectively;
   k, l = 1, 2 are the components of the 2D tensor Q_kl,i.
5. Compute from Q_kl,i, Qhat_kl,i, respectively:
   - The sizes R^2, Rhat^2.
6. Obtain difference between reference and estimated, approximate quantities, and their scatter (around zero by
   construction).


## PSF Spatial Validation

### Requirement: R-SHE-CAL-F-030

Parent: R-GDP-CAL-020

The r.m.s. of the ensemble averaged ΔQij/R^2 (where ΔQij is the quadrupole moment of the residual after the linearity 
correction) for a subset of observed and emulated stars in the range 18 < VIS < 24.5 as a function of magnitude in bins
of width one magnitude shall be: <3.0x10^-5 (1-sigma) per moment if i=j and <1.75x10^-5 (1-sigma) if i≠j, averaging over
magnitude bins and 100 fields.

#### Requirement Comment from GDPRD

This part of the allocation is for the contribution linked to the model selected to represent the PSF that differs from
the true PSF. 

The requirement ensures that the mean PSF model does not lead to biased shapes or sizes. If the PSF model is within
requirements then the residuals at star positions should be consistent with noise (within requirements). This can be
checked with a validation test where subsets of stars not used to derive the PSF model are predicted.

This shall be demonstrated on observed and emulated Euclid stellar images.

### Requirement: R-SHE-PRD-F-090

Parent: R-GDP-DL3-012

The SGS shall create a model of the PSF such that the normalized moments Qii/R^2 of the ensemble averaged residual image 
(observed – PSF model) for a subset of observed stars in the range 18 < VIS < 23 as a function of magnitude in bins of 
width one magnitude shall be: < 8.6x10^-5 (1-sigma) per moment if i=j, and < 5x10^-5 if i≠j, averaging over magnitude
bins and 100 fields.

#### Requirement Comment from GDPRD

This part of the allocation is for the contribution linked to the model selected to represent the PSF that differs from
the true PSF. 

The requirement ensures that the mean PSF model does not lead to biased shapes or sizes. If the PSF model is within
requirements then the residuals at star positions should consistent with noise (within requirements). This can be
checked with a validation test where subsets of stars not used to derive the PSF model are predicted.

This shall be demonstrated on observed Euclid stellar images.

### Validation Test: T-SHE-000003-PSF-res-interp-star-pos

Compare the PSF at a stellar position for a star **not** used in the PSF Fitting.

### Rationale:

To test accuracy of the effective PSF model (i.e., the spatial interpolation of the object PSF model).

### Test Case: TC-SHE-100005-PSF-res-interp-star-pos-tot

Residuals of the interpolated PSF at a subset of star positions not used to derive the model for total population.

#### Test Procedure:

1. Divide the stars in the exposure into a subset used for modeling, and another subset used for testing. The modelling
   subset should contain a number of stars representative for typical galaxy fields. This needs to be accounted for in
   high-density stellar calibration fields.
2. Fit the PSF in the model subset to obtain the object PSF model.
3. Interpolate object PSF model over distance and multi-band photometry (which represents the SED) to the test subset to
   obtain the effective PSF model.
4. Measure PSF residuals on remaining stars, for set of stars that corresponds to:
   - The entire set of stars
5. Obtain the residual of the quadrupole moments as defined in the requirements.
6. Obtain the quadrupole moments of the residuals as defined in the requirements.
7. Check the residual against the requirements.

### Test Case: TC-SHE-100006-PSF-res-interp-star-pos-SNR

Residuals of the interpolated PSF at a subset of star positions not used to derive the model for total population.

#### Test Procedure:

1. Divide the stars in the exposure into a subset used for modeling, and another subset used for testing. The modelling
   subset should contain a number of stars representative for typical galaxy fields. This needs to be accounted for in
   high-density stellar calibration fields.
2. Fit the PSF in the model subset to obtain the object PSF model.
3. Interpolate object PSF model over distance and multi-band photometry (which represents the SED) to the test subset to
   obtain the effective PSF model.
4. Measure PSF residuals on remaining stars, for set of stars that corresponds to:
   - Subsets split according to S/N
5. Obtain the residual of the quadrupole moments as defined in the requirements.
6. Obtain the quadrupole moments of the residuals as defined in the requirements.
7. Check the residual against the requirements.

### Test Case: TC-SHE-100007-PSF-res-interp-star-pos-SED

Residuals of the interpolated PSF at a subset of star positions not used to derive the model for total population.

#### Test Procedure:

1. Divide the stars in the exposure into a subset used for modeling, and another subset used for testing. The modelling
   subset should contain a number of stars representative for typical galaxy fields. This needs to be accounted for in
   high-density stellar calibration fields.
2. Fit the PSF in the model subset to obtain the object PSF model.
3. Interpolate object PSF model over distance and multi-band photometry (which represents the SED) to the test subset to
   obtain the effective PSF model.
4. Measure PSF residuals on remaining stars, for set of stars that corresponds to:
   - Subsets split according to SED properties
5. Obtain the residual of the quadrupole moments as defined in the requirements.
6. Obtain the quadrupole moments of the residuals as defined in the requirements.
7. Check the residual against the requirements.

### Test Case: TC-SHE-100008-PSF-res-interp-star-pos-coord

Residuals of the interpolated PSF at a subset of star positions not used to derive the model for total population.

#### Test Procedure:

1. Divide the stars in the exposure into a subset used for modeling, and another subset used for testing. The modelling
   subset should contain a number of stars representative for typical galaxy fields. This needs to be accounted for in
   high-density stellar calibration fields.
2. Fit the PSF in the model subset to obtain the object PSF model.
3. Interpolate object PSF model over distance and multi-band photometry (which represents the SED) to the test subset to
   obtain the effective PSF model.
4. Measure PSF residuals on remaining stars, for set of stars that corresponds to:
   - Subsets split according to pixel coordinates
5. Obtain the residual of the quadrupole moments as defined in the requirements.
6. Obtain the quadrupole moments of the residuals as defined in the requirements.
7. Check the residual against the requirements.

### Test Case: TC-SHE-100009-PSF-res-interp-star-pos-epoch

Residuals of the interpolated PSF at a subset of star positions not used to derive the model for total population.

#### Test Procedure:

1. Divide the stars in the exposure into a subset used for modeling, and another subset used for testing. The modelling
   subset should contain a number of stars representative for typical galaxy fields. This needs to be accounted for in
   high-density stellar calibration fields.
2. Fit the PSF in the model subset to obtain the object PSF model.
3. Interpolate object PSF model over distance and multi-band photometry (which represents the SED) to the test subset to
   obtain the effective PSF model.
4. Measure PSF residuals on remaining stars, for set of stars that corresponds to:
   - Subsets split according to mission epoch
5. Obtain the residual of the quadrupole moments as defined in the requirements.
6. Obtain the quadrupole moments of the residuals as defined in the requirements.
7. Check the residual against the requirements.

### Test Case: TC-SHE-100010-PSF-res-interp-star-pos-aspect

Residuals of the interpolated PSF at a subset of star positions not used to derive the model for total population.

#### Test Procedure:

1. Divide the stars in the exposure into a subset used for modeling, and another subset used for testing. The modelling
   subset should contain a number of stars representative for typical galaxy fields. This needs to be accounted for in
   high-density stellar calibration fields.
2. Fit the PSF in the model subset to obtain the object PSF model.
3. Interpolate object PSF model over distance and multi-band photometry (which represents the SED) to the test subset to
   obtain the effective PSF model.
4. Measure PSF residuals on remaining stars, for set of stars that corresponds to:
   - Subsets split according to solar aspect angle
5. Obtain the residual of the quadrupole moments as defined in the requirements.
6. Obtain the quadrupole moments of the residuals as defined in the requirements.
7. Check the residual against the requirements.

## PSF Ellipticity and Size Validation

### Requirement: R-SHE-PRD-F-110

Parent: R-GDP-DL3-030

For each ellipticity component, the transfer of the VIS PSF model to the weak-lensing objects shall not introduce
errors larger than 5×10^-5 (1-sigma).

#### Requirement Comment from GDPRD

This shall be demonstrated on emulated Euclid images based in processed HST images for galaxies.

### Requirement: R-SHE-PRD-F-120

Parent: R-GDP-DL3-040

For the PSF R^2 component, the transfer of the VIS PSF model to the weak-lensing objects shall not introduce errors
larger than sigma(R)/R< 5×10^-4.

#### Requirement Comment from GDPRD

This shall be demonstrated on emulated Euclid images based in processed HST images for galaxies.

### Validation Test: T-SHE-000004-PSF-model-err-propa

Propagate the uncertainty in the PSF to the galaxy ellipticity and size, and ensure below Requirement.

### Rationale:

This test validates if the propagated errors from the object PSF model to the WL objects remain below the required
thresholds.

### Test Cases:

#### TC-SHE-100011-PSF-model-err-propa-ell

Propagation of PSF model parameter errors from the posterior of the PSF model parameters to galaxy shape and size PDF,
effect on ellipticity.

##### Test Procedure:

1. Applied to emulated (HST) Euclid galaxies.
1. Apply shear estimation to galaxies with fiducial PSF parameters.
1. Repeat shear estimation with a range of PSF parameters based in parameter uncertainties.
1. Measure the variance of galaxy ellipticities.
1. Test is variance is with Requirements.

#### TC-SHE-100011-PSF-model-err-propa-R2

Propagation of PSF model parameter errors from the posterior of the PSF model parameters to galaxy shape and size PDF,
effect on size.

##### Test Procedure:

As for TC-SHE-100011-PSF-model-err-propa-ell with ellipticity reply red by size.
