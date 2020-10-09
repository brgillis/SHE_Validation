## Requirement: R-SHE-PRD-F-070 / R-SHE-PRD-F-080
Parent: R-GDP-CAL-070 / R-GDP-CAL-072

R-SHE-PRD-F-070: The average error on the multiplicative bias (μ) intrinsic to the ellipticity measurement per galaxy, accounting for the weak lensing weights, shall be less than 2×10-3 (1 sigma) for the ensemble of galaxies used for weak lensing.

R-SHE-PRD-F-080: The average error on the additive bias (c) intrinsic to the ellipticity measurement method, accounting for the weak lensing weights, shall be known to better than 5×10-4 (1 sigma) for the ensemble of galaxies used for weak lensing.

## Requirement Comment from GDPRD
This shall be demonstrated on emulated Euclid images based on processed HST images for stars and galaxies.

[ANT: The Requirement and test refer to ellipticities, but methods have evolved to estimate unbiased shear, so this should be used. ]

Requirements Chain:

## Validation Test: T-SHE-000006-shear-bias

## Rational:
Measure multiplicative and additive biases from HST images with known shear, to check they and their error are within Requirements.

## Test Cases:
### TC-SHE-100017-shear-bias-m
Measure the multiplicative bias (along with additive bias) from a linear regression of estimated shear from input shear for a sample of HST emulated Euclid images.

#### Test Procedure:
1. Emulated galaxy images with known shear, based on deep HST data, are generated.
1. A subset of those emulated HST galaxy images is used to train the shape measurement method, i.e. to derive and apply the bias correction and calibration. The fraction of the data allowed for this training is TBD. ANT: An alternative is that realistic simulated data is used for Calibration and the HST sample is used for Validation.
1. From the remaining HST data construct a test data set upon which the validation test is run.
1. The measured shear from the emulated images is plotted against the true input shear.
1. Derive m and c measured from a straight line fit. Note that both parameters are correlated and have to be estimated jointly using their covariance.

### TC-SHE-100017-shear-bias-m-SNR

#### Test Procedure:
1. Emulated galaxy images with known shear, based on deep HST data, are generated.
1. A subset of those emulated HST galaxy images is used to train the shape measurement method, i.e. to derive and apply the bias correction and calibration. The fraction of the data allowed for this training is TBD. ANT: An alternative is that realistic simulated data is used for Calibration and the HST sample is used for Validation.
1. From the remaining HST data construct a test data set upon which the validation test is run.
1. Generate subsets according to galaxy SNR over range TBD and bin width TBD.
1. The measured shear from the emulated images is plotted against the true input shear.
1. Derive m and c measured from a straight line fit. Note that both parameters are correlated and have to be estimated jointly using their covariance.

### TC-SHE-100017-shear-bias-m-bg
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy background.

### TC-SHE-100017-shear-bias-m-size
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy size.

### TC-SHE-100017-shear-bias-m-col
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy colour.

### TC-SHE-100017-shear-bias-m-epoch
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy epoch.

### TC-SHE-100017-shear-bias-c
Measure the additive bias (along with multiplicative bias) from a linear regression of estimated shear from input shear for a sample of HST emulated Euclid images.

#### Test Procedure:
1. Emulated galaxy images with known shear, based on deep HST data, are generated.
1. A subset of those emulated HST galaxy images is used to train the shape measurement method, i.e. to derive and apply the bias correction and calibration. The fraction of the data allowed for this training is TBD. ANT: An alternative is that realistic simulated data is used for Calibration and the HST sample is used for Validation.
1. From the remaining HST data construct a test data set upon which the validation test is run.
1. The measured shear from the emulated images is plotted against the true input shear.
1. Derive m and c measured from a straight line fit. Note that both parameters are correlated and have to be estimated jointly using their covariance.

### TC-SHE-100017-shear-bias-c-SNR

#### Test Procedure:
1. Emulated galaxy images with known shear, based on deep HST data, are generated.
1. A subset of those emulated HST galaxy images is used to train the shape measurement method, i.e. to derive and apply the bias correction and calibration. The fraction of the data allowed for this training is TBD. ANT: An alternative is that realistic simulated data is used for Calibration and the HST sample is used for Validation.
1. From the remaining HST data construct a test data set upon which the validation test is run.
1. Generate subsets according to galaxy SNR over range TBD and bin width TBD.
1. The measured shear from the emulated images is plotted against the true input shear.
1. Derive m and c measured from a straight line fit. Note that both parameters are correlated and have to be estimated jointly using their covariance.

### TC-SHE-100017-shear-bias-c-bg
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy background.

### TC-SHE-100017-shear-bias-c-size
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy size.

### TC-SHE-100017-shear-bias-c-col
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy colour.

### TC-SHE-100017-shear-bias-c-epoch
As for TC-SHE-100017-shear-bias-m-SNR with SNR replaced by galaxy epoch.

## Issues:

Need to make sure that epoch information is properly propagated through all data products.
