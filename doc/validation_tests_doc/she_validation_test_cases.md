## Validation Test Cases

Each Validation Test is composed of a set of Validation Test Cases, the
completion of which fulfils the Validation Test. Below is a table of
Shear Validation Test corresponding to the above table, a short
descriptor of the test, the Validation Test Case, the allocated SHE PF,
and a Status Report.

The Status Report is:

|   |   |
|---|---|
| Red | Not Implemented in the SGS |
| Yellow | Implementation in Progress |
| Green | Implemented in the SGS Pipeline |


|                                      |                                                                                  |                                              |        |                       |
|--------------------------------------|----------------------------------------------------------------------------------|----------------------------------------------|--------|-----------------------|
| **Shear Validation Test**            | **Short Descriptor**                                                             | **Test Case**                                | **PF** | **Status**            |
| T-SHE-000001-PSF-res-star-pos        | χ2 distribution of PSF residuals at star positions                               | TC-SHE-100001-PSF-res-star-pos-tot           | PSF    | Yellow                |
|                                      |                                                                                  | TC-SHE-100002-PSF-res-star-pos-SNR           | PSF    | Yellow                |
|                                      |                                                                                  | TC-SHE-100901-PSF-res-star-pos-SED           | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100902-PSF-res-star-pos-pix           | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100903-PSF-res-star-pos-epoch         | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100904-PSF-res-star-pos-solaspang     | PSF    | Red                   |
| T-SHE-000002-PSF-lambdas             | PSF from broadband magnitudes compared to precise PSF from spectroscopic data    | TC-SHE-100003-PSF-lambda-ell                 | PSF    | Red Test needs review |
|                                      |                                                                                  | TC-SHE-100004-PSF-lambda-R2                  | PSF    | Red Test needs review |
| T-SHE-000003-PSF-res-interp-star-pos | Residual of PSF at galaxy                                                        | TC-SHE-100005-PSF-res-interp-star-pos-tot    | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100006-PSF-res-interp-star-pos-SNR    | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100007-PSF-res-interp-star-pos-SED    | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100008-PSF-res-interp-star-pos-coord  | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100009-PSF-res-interp-star-pos-epoch  | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100010-PSF-res-interp-star-pos-aspect | PSF    | Red                   |
| T-SHE-000004-PSF-model-err-propa     | PSF wavelength interpolation                                                     | TC-SHE-100011-PSF-model-err-propa-ell        | PSF    | Red                   |
|                                      |                                                                                  | TC-SHE-100012-PSF-model-err-propa-R2         | PSF    | Red                   |
| T-SHE-000005-colgrad-emul            | Accuracy of emulated Euclid Deep Survey data obtained from multi-colour HST data | TC-SHE-100013-colgrad-emul-A                 | Shear  | Red                   |
|                                      |                                                                                  | TC-SHE-100014-colgrad-emul-B                 | Shear  | Red                   |
|                                      |                                                                                  | TC-SHE-100015-colgrad-emul-C                 | Shear  | Red                   |
|                                      |                                                                                  | TC-SHE-100016-colgrad-emul-D                 | Shear  | Red                   |
| T-SHE-000006-shear-bias              | Shear bias residuals                                                             | TC-SHE-100017-shear-bias-m                   | Shear  | Green                 |
|                                      |                                                                                  | TC-SHE-100018-shear-bias-c                   | Shear  | Green                 |
| T-SHE-000007-pdf-eps-s               | Moments of intrinsic galaxy ellipticities                                        | TC-SHE-100019-pdf-eps-s-m2                   | Shear  | Red                   |
|                                      |                                                                                  | TC-SHE-100020-pdf-eps-s-m3                   | Shear  | Red                   |
|                                      |                                                                                  | TC-SHE-100021-pdf-eps-s-m4                   | Shear  | Red                   |
| T-SHE-000008-gal-info                |                                                                                  | TC-SHE-100022-gal-N-out                      | Shear  | Yellow                |
|                                      |                                                                                  | TC-SHE-100023-gal-info-out                   | Shear  | Yellow                |
| T-SHE-000009-CTI-PSF                 | Linear dependence of PSF ellipticity with read-out register distance (slope)     | TC-SHE-100024-CTI-PSF-SNR                    | CTI    | Yellow                |
|                                      |                                                                                  | TC-SHE-100025-CTI-PSF-bg                     | CTI    | Yellow                |
|                                      |                                                                                  | TC-SHE-100026-CTI-PSF-col                    | CTI    | Yellow                |
|                                      |                                                                                  | TC-SHE-100027-CTI-PSF-epoch                  | CTI    | Yellow                |
| T-SHE-000010-CTI-gal                 | Linear dependence of galaxy ellipticity with read-out register distance (slope)  | TC-SHE-100028-CTI-gal-SNR                    | CTI    | Green                 |
|                                      |                                                                                  | TC-SHE-100029-CTI-gal-bg                     | CTI    | Green                 |
|                                      |                                                                                  | TC-SHE-100030-CTI-gal-size                   | CTI    | Green                 |
|                                      |                                                                                  | TC-SHE-100031-CTI-gal-col                    | CTI    | Green                 |
|                                      |                                                                                  | TC-SHE-100032-CTI-gal-epoch                  | CTI    | Green                 |
|                                      |                                                                                  | TC-SHE-100900-CTI-gal-tot                    | CTI    | Green                 |
| T-SHE-000011-star-SED-exist          | SEDs provided from PHZ data products                                             | TC-SHE-100033-star-SED-exist                 | PSF    | Yellow                |
| T-SHE-000012-calibr-simul            | Ability of image simulations to provide calibration of shear measurements        | TC-SHE-100034-calibr-simul                   | Shear  | Yellow                |
