## Requirement: R-SHE-CAL-F-030 / R-SHE-PRD-F-090
Parent: R-GDP-CAL-020
The r.m.s. of the ensemble averaged ΔQij/R2 (where ΔQij is the quadrupole moment of the residual after the linearity correction) for each subset (TBD) of stars in the useful dynamic range, shall be:  
<3.0x10-5 (1-sigma) per moment if i=j  
and  
<1.75x10-5 (1sigma) if i≠j

## Requirement Comment from GDPRD
This shall be demonstrated on emulated Euclid stellar images.  
[ANT - availability of emulated Euclid stars? - Gaia?]

Requirements Chain:

## Validation Test: T-SHE-000003-PSF-res-interp-star-pos
Compare the PSF at a stellar position for a star **not** used in the PSF Fitting.

This test is defined in the [WL Validation](https://euclid.roe.ac.uk/attachments/download/21974/EUCL-UBN-TS-8-001_WLValidation_2018-06-18.pdf) doc in VAL-WL-SHE-0020.

## Rational:
To test accuracy of the effective PSF model (i.e., the spatial interpolation of the object PSF model model).  

[ANT - the spatial interpolation test is no longer appropriate with the wavefront model.]

## Test Cases:
### TC-SHE-100005-PSF-res-interp-star-pos-tot

### TC-SHE-100006-PSF-res-interp-star-pos-SNR

### TC-SHE-100006-PSF-res-interp-star-pos-SED

### TC-SHE-100006-PSF-res-interp-star-pos-coord

### TC-SHE-100006-PSF-res-interp-star-pos-epoch

### TC-SHE-100006-PSF-res-interp-star-pos-aspect

