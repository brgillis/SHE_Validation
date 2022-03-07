## Requirement: R-SHE-PRD-F-070 / 080
Parent: Missing Requirement

## Requirement Comment from GDPRD
None, Missing Requirement.  
This Requirement is inferred from R-SHE-PRD-F-070/080, as we need simulations to calibrate shear methods.

## Validation Test: T-SHE-000012-calibr-simul
This test validates the image simulation suites that are used to derive the shear calibration for the shear bias correction.

## Rational:
Simulations for shear calibration need to be highly accurate, or introduce addition bias.

## Input Data
Image simulations of galaxies that are used for shear calibration. These simulations may consist of a suite of simulations, for which a certain effect or parameter p is varied, with the purpose to measure the response of the shear bias ∂m/∂p to that parameter. The range of that parameter shall be informed by prior knowledge on astrophysics, and/or the expected instrumental performance of Euclid. If the astrophysical knowledge is expected to be improved by Euclid, the image simulation suites might be re-created and calibration re-computed over more restricted parameter ranges.

## Analysis Tools
Relative error analysis.

## Test Cases:
### TC-SHE-100034-calibr-simul
Ability of image simulations to provide calibration of shear measurements.

**Purpose:** The variation of the response of the shear bias as function of a simulated parameter.

**Output:** The variation of the response of the shear bias as function of a simulated parameter.

**Pass/Fail criteria:** The response of the shear bias m with a given parameter needs to be such that the inferred bias correction ∆m is smaller than the required value of 5 × 10−4, or even a certain fraction of that value if that parameter represents only a part of the total error budget. This depends on two ingredients: The variation (slope) of the response m(p) over the prior parameter range, and the uncertainty of the bias measurement m for various p. The former is intrinsic to the shape measurement method, and intrinsic properties of galaxies, noise, etc. The latter can be reduced by increasing the number of simulations per p. The value of ∆m can for example be determined by a fit of an appropriate function to m(p) over the prior range (e.g. a constant, or linear function). The uncertainty of the fitted m over the prior range has then to be smaller than the requirement. It is possible that the slope is very large, or cannot be determined (e.g. due to large randomness in the measured m), and the requirement is not reached even when increasing the number of simulations. In that case, the shape measurement method in question cannot be validated, and the algorithm needs to be modified such that there is less sensitivity to input properties.

#### Test Procedure:
This is the SIM Shear Sensitivity Testing programme.
1. Run SIM Shear Sensitivity Testing with TBD variations in input parameters.
1. Calculate slope of m and c bias with respect to variation in input parameter.
1. Test Dm over range is within Requirement.
1. Test error on DM is within Requirement.
1. Report results.

