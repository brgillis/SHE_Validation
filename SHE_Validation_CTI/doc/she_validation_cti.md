## CTI Validation Test Descriptions

### CTI PSF Validation

#### Requirement: R-SHE-CAL-F-020

*Residual of CTI to PSF ellipticity <1.1x10-4 (1-sigma) per VIS exposure per component.*

#### Requirement Comment from GDPRD

CTI is initially Validated at the pixel level in VIS (R-VIS-PRD-F-196).
In SHE tested on emulated VIS images.
On Euclid data by cross-correlating corrected galaxy ellipticity in image coordinates with e.g. image position, time, object S/N and size, and sky background. The same cross-correlations shall be performed on residuals of stars after subtraction of the PSF model.

#### Validation Test: T-SHE-000009-CTI-PSF

Linear dependence of PSF ellipticity with read-out register distance (slope).

#### Rational

Residual CTI is expected to leave a trail along the Readout direction of the CCD, which will induce an ellipticity signal as a function of distance from the Readout Register. The absolute value of this is degenerate with other effects, so the test is to measure the gradient of the ellipticity as a function of distance from the Readout Register, which would indicate a residual CTI. Note this is not a strong test (compared to eg a chi^2 fit of the PSF), but is a sanity test of the PSF at the Catalogue Level.

#### Test Case : TC-SHE-100024-CTI-PSF-SNR
Linear dependence of residual PSF ellipticity with read-out register distance (slope) in bins of SNR of stars.

##### Test Procedure 

1. This process is carried out on simulated Euclid Observations. 
1. This test is carried out per Observation. 
1. Stars are binned by SNR over the range [TBD] with bin intervals of [TBD]. [Note: what sample of stars?]
1. Each SNR sample is binned in distance from the Readout Register on each CCD. [Note: per pixel? Dont need to bin, but would to plot results? ]
1. The average difference between the Model PSF ellipticity and simulated Stellar image ellipticity calculated, with error. 
1. The linear regression of the slope of the differential ellipticity as a function of readout distance is estimated, with error. 
1. The sloped and its error are compare to a threshold [TBD].
1. If slope or error is larger than threshold, flag Observation. 
1. Results are stored.
1. Results are collated Globally and compared to Simulated distributions. [TBC] 
1. Need to be able to plot results and fit Locally and Globally.
1. Summary Statistics and Figures are produced.

#### Test Case : TC-SHE-100025-CTI-PSF-bg

As for TC-SHE-100024-CTI-PSF-SNR with SNR replaced by Sky Background Level.

#### Test Case : TC-SHE-100025-CTI-PSF-col

As for TC-SHE-100024-CTI-PSF-SNR with SNR replaced by Colour.

#### Test Case : TC-SHE-100025-CTI-PSF-epoch

As for TC-SHE-100024-CTI-PSF-SNR with SNR replaced by Observation Epoch.

### Input Data

#### Shear Star Catalog (SHE)
* **Purpose**: Provides ellipticities of Model PSFs
* **DPDD Description**: https://gitlab.euclid-sgs.uk/msauvage/data-product-doc/-/blob/SHE_SC8/shedpd/dpcards/she_starcatalog.rst
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/she/euc-test-she-StarCatalog.xsd
* **Cardinality**: 1-4 per Observation (one for each exposure)

#### Calibrated Frame Product (VIS)

* **Purpose**: WCS for detectors is needed to convert sky coordinates of stars to detector coordinates; provides observation epoch, and provides background level at any position
* **DPDD Description**: http://euclid.esac.esa.int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/vis/euc-test-vis-CalibratedFrame.xsd
* **Cardinality**: 1-4 per Observation (one for each exposure, same cardinality as Shear Star Catalog)

#### Final Catalog (MER)

* **Purpose**: Provide SNR and colour for each object
* **DPDD Description**: http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/mer/euc-test-mer-FinalCatalog.xsd
* **Cardinality**: 1-12 per Observation (one for each overlapping tile)

#### Input PSF Catalog (SIM)
* **Purpose**: Provides ellipticities of input PSFs
* **DPDD Description**: N/A (doesn't exist yet)
* **Data Product**: N/A (doesn't exist yet)
* **Cardinality**: Unknown

Input data for each port will be provided as listfiles of .xml data products. Data may be provided for more than one observation, and ordering cannot be guaranteed, so attention will need to be paid to properly associate files using information in the data products (such as the ObservationId values) to make sure they are all properly associated.

### Output Data

#### Validation Test Results (SHE)
* **Purpose**: Contains name, ID, and result of validation test(s), plus extra data such as plots
* **DPDD Description**: https://gitlab.euclid-sgs.uk/msauvage/data-product-doc/-/blob/SHE_SC8/shedpd/dpcards/she_validationtestresults.rst
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/she/euc-test-she-ValidationTestResults.xsd
* **Cardinality**: 1

---

### CTI Galaxy Validation

#### Requirement: R-SHE-CAL-F-140

Residual of CTI to galaxy multiplicative bias mu <5x10-4 (1-sigma).

Note: There is no equivalent CTI Requirement for Additive Bias. Should there be?

#### Requirement Comment from GDPRD

None.

#### Validation Test: T-SHE-000010-CTI-gal

Linear dependence of galaxy ellipticity with read-out register distance (slope).

#### Rational:

Residual CTI is expected to leave a trail along the Readout direction of the CCD, which will induce a galaxy ellipticity signal as a function of distance from the Readout Register. The absolute value of this is degenerate with other effects, so the test is to measure the gradient of the ellipticity as a function of distance from the Readout Register, which would indicate a residual CTI.

#### Test Case : TC-SHE-100028-CTI-gal-SNR

Linear dependence of residual galaxy ellipticity with read-out register distance (slope) in bins of SNR of galaxies.

##### Test Procedure: 
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

#### Test Case : TC-SHE-100029-CTI-gal-bg

Linear dependence of residual galaxy ellipticity with read-out register distance (slope) in bins of Sky Background Levels.

##### Test Procedure: 
1. This process is carried out on real and simulated Euclid Observations. 
1. This test is carried out per Observation. 
1. Galaxies are binned by Sky Background Level over the range [TBD] with bin intervals of [TBD]. [Note: what sample of galaxies?]
1. Each Sky Background Level sample is binned in distance from the Readout Register on each CCD. [Note: per pixel? Dont need to bin, but would to plot results? ]
1. The average galaxy ellipticity per bin in estimated with error. 
1. The linear regression of the slope of the ellipticity as a function of readout distance is estimated, with error. 
1. The sloped and its error are compare to a threshold [TBD].
1. If slope or error is larger than threshold, flag Observation. 
1. Results are stored.
1. Results are collated Globally and compared to Simulated distributions. [TBC] 
1. Need to be able to plot results and fit Locally and Globally.
1. Summary Statistics and Figures are produced.

#### Test Case : TC-SHE-100030-CTI-gal-col

As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by galaxy Colour.

#### Test Case : TC-SHE-100031-CTI-gal-size

As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by galaxy size.

#### Test Case : TC-SHE-100031-CTI-gal-epoch

As for TC-SHE-100028-CTI-gal-SNR with SNR replaced by Observation Epoch.

### Input Data

#### Validated Shear Measurements (SHE)
* **Purpose**: Provides shear estimates for detected objects, which can be interpreted as ellipticity measurements for the purpose of this test
* **DPDD Description**: https://gitlab.euclid-sgs.uk/msauvage/data-product-doc/-/blob/SHE_SC8/shedpd/dpcards/she_starcatalog.rst
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/she/euc-test-she-StarCatalog.xsd
* **Cardinality**: 1 per Observation

#### Calibrated Frame Product (VIS)
* **Purpose**: WCS for detectors is needed to convert sky coordinates of stars to detector coordinates; provides observation epoch, and provides background level at any position
* **DPDD Description**: http://euclid.esac.esa.int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/vis/euc-test-vis-CalibratedFrame.xsd
* **Cardinality**: 1-4 per Observation (one for each exposure)

#### Final Catalog (MER)
* **Purpose**: Provide SNR, colour, and size for each object
* **DPDD Description**: http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/mer/euc-test-mer-FinalCatalog.xsd
* **Cardinality**: 1-12 per Observation (one for each overlapping tile)

Input data for each port will be provided as listfiles of .xml data products. Data may be provided for more than one observation, and ordering cannot be guaranteed, so attention will need to be paid to properly associate files using information in the data products (such as the ObservationId values) to make sure they are all properly associated.

### Output Data

#### Validation Test Results (SHE)
* **Purpose**: Contains name, ID, and result of validation test(s), plus extra data such as plots
* **DPDD Description**: https://gitlab.euclid-sgs.uk/msauvage/data-product-doc/-/blob/SHE_SC8/shedpd/dpcards/she_validationtestresults.rst
* **Data Product**: https://gitlab.euclid-sgs.uk/ST-DM/ST_DataModel/-/blob/develop/ST_DM_Schema/auxdir/ST_DM_Schema/dpd/she/euc-test-she-ValidationTestResults.xsd
* **Cardinality**: 1
