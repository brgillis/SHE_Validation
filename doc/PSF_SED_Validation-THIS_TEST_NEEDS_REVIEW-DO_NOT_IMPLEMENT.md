## Requirement: R-SHE-CAL-F-040 / R-SHE-CAL-F-050:
Parent: R-GDP-CAL-025 / R-GDP-CAL-035
The bias caused in the ellipticity of an object arising from the transfer of the VIS PSF ellipticity model to the weak-lensing objects shall be smaller than 3.5x10-5 (1 sigma TBC).

[ANT: TBD to be removed in SHE RSD]

## Requirement Comment from GDPRD
This shall be demonstrated on emulated Euclid images with realistic SEDs for stars and galaxies. [Note a proposed revision of this Requirement to an error has been proposed by SHE.]

Requirements Chain:

## Validation Test: T-SHE-000002-PSF-lambda
Estimate PSF model residuals at star positions and compare with suitable expected distribution (eg chi^2) with eg KL test (ANT: should this be KS-test?)

This test is defined in the WL Validation doc in VAL-WL-SHE-0020.

## Rational:
Ensures that the object PSF model model captures the correct wavelength dependence for stars.

## Test Cases:
### TC-SHE-100003-PSF-lambda-ell
Approximate PSF from broad-band magnitudes compared to precise PSF from spectroscopic data, effect on ellipticity.

#### Test Procedure:
**[Major concern raised over this test as checking wavelength dependence.]**
1. For every star i, use the spectral information to create the precise reference PSF Ipsf,i(⃗x) as function of position ⃗x for the star SED and the star position.
1. Emulate broad-band magnitudes of the star by utilising the star SED and the broad-band filter curves.
1. Construct an approximate, interpolated PSF model Iˆ (⃗x) of the star by making use of psf ,i
the emulated broad-band magnitudes only.
1. Compute the unweighted quadrupole moments Q and Qˆ from I kl,i kl,i
respectively; k, l = 1, 2 are the components of the 2D tensor Qkl,i.
1. Compute from Qkl,i, Qˆkl,i, respectively:
(⃗x) and Iˆ psf,i psf,i
(⃗x),
• the ellipticity components eij , eˆij j = 1, 2 are the ellipticity components.
1. Obtain difference between reference and estimated, approximate quantities, and their scatter (around zero by construction).

## Issues:

* For running on emulated images, precise input SEDs are needed. This will require a data product providing this from somewhere (EXT, SPE, SIR?).
* Unweighted moments might not be the best choice
