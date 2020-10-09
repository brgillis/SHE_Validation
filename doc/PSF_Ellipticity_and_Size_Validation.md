## Requirement: R-SHE-PRD-F-110 / R-SHE-PRD-F-120
Parent: R-GDP-DL3-030 / R-GDP-DL3-040

R-SHE-PRD-F-110: For each ellipticity component, the transfer of the VIS PSF model to the weak-lensing objects shall not introduce errors larger than 5×10-5 (one sigma TBC).

R-SHE-PRD-F-120: For the PSF R2 component, the transfer of the VIS PSF model to the weak-lensing objects shall not introduce errors larger than sigma(R)/R< 5×10-4.

## Requirement Comment from GDPRD
This shall be demonstrated on emulated Euclid images based in processed HST images for galaxies.

Requirements Chain:

## Validation Test: T-SHE-000004-PSF-model-err-propa
Propagate the uncertainty in the PSF to the galaxy ellipticity and size, and ensure below Requirement.

## Rational:
This test validates if the propagated errors from the object PSF model to the WL objects remain below the required thresholds.

## Test Cases:
### TC-SHE-100011-PSF-model-err-propa-ell
Propagation of PSF model parameter errors from the posterior of the PSF model parameters to galaxy shape and size PDF, effect on ellipticity.

#### Test Procedure:
1. Applied to emulated (HST) Euclid galaxies.
1. Apply shear estimation to galaxies with fiducual PSF parameters.
1. Repeat shear estimation with a range of PSF parameters based in parameter uncertainties.
1. Measure the variance of galaxy ellipticities.
1. Test is variance is with Requirements.

### TC-SHE-100011-PSF-model-err-propa-R2
Propagation of PSF model parameter errors from the posterior of the PSF model param-eters to galaxy shape and size PDF, effect on size.

#### Test Procedure:
As for TC-SHE-100011-PSF-model-err-propa-ell with ellipticity reply red by size.

