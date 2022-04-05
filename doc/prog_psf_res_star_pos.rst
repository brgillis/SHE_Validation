.. _SHE_Validation_ValidatePSFResStarPos:

SHE_Validation_ValidatePSFResStarPos
====================================

This program performs the PSF Residual at star positions validation test, T-SHE-000001-PSF-res-star-pos, which validates requirement R-SHE-PRD-F-100. This tests checks if the residuals of modelled PSFs compared to observed stars is consistent with the expectation from simulations.

This program is presently under active development, and frequent changes are anticipated.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateCTIGal`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.3 SHE_Validation_ValidatePSFResStarPos --workdir <dir> --star_catalog_product <filename> --she_validation_test_results_product <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>] [--snr_bin_limits "<value> <value> ..."]

with the following arguments:


Common Elements Arguments
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 15 50 10 25
   :header-rows: 1

   * - Argument
     - Description
     - Required
     - Default
   * - --workdir ``<path>``
     - Name of the working directory, where input data is stored and output data will be created.
     - yes
     - N/A
   * - --log-file ``<filename>``
     - Name of a filename to store logs in, relative to the workdir. If not provided, logging data will only be output to the terminal. Note that this will only contain logs directly from the run of this executable. Logs of executables called during the pipeline execution will be stored in the "logs" directory of the workdir.
     - no
     - None
   * - --logdir ``<path>``
     - Path where logging data will be stored. This only has effect if some other option is enabled which produces logging data, such as ``--profile``.
     - no
     - ``"."``
   * - --log-level ``<level>``
     - Minimum severity level at which to print logging information. Valid values are DEBUG, INFO, WARNING, and ERROR. Note that this will only contain logs directly from the run of this executable. The log level of executables called during pipeline execut will be set based on the configuration of the pipeline server (normally INFO).
     - no
     - INFO


Input Arguments
~~~~~~~~~~~~~~~

.. list-table::
   :widths: 15 50 10 25
   :header-rows: 1

   * - Argument
     - Description
     - Required
     - Default
   * - ``--star_catalog_product <filename>``
     - ``.xml`` data product of type `DpdSheStarCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_starcatalog.html>`__, containing star information based on the results of PF-SHE's PSF Fitting program
     - yes
     - N/A
   * - ``--pipeline_config <filename>``
     - ``.xml`` data product or pointing to configuration file (described below), or .json listfile (Cardinality 0-1) either pointing to such a data product, or empty.
     - no
     - None (equivalent to providing an empty listfile)


Output Arguments
~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 15 50 10 25
   :header-rows: 1

   * - Argument
     - Description
     - Required
     - Default
   * - ``--she_validation_test_results_product``
     - Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test
     - yes
     - N/A

Options
~~~~~~~

.. list-table::
   :widths: 15 50 10 25
   :header-rows: 1

   * - Argument
     - Description
     - Required
     - Default
   * - ``--profile`` (``store_true``)
     - If set, Python code will be profiled, and the resulting profiling data will be output to a file in the directory specified with ``--logdir``.
     - no
     - False
   * - ``--dry_run`` (``store_true``)
     - If set, program will generate dummy output of the correct format and exit, instead of normal execution.
     - no
     - False
   * - ``--snr_bin_limits "<value> <value> ..."``
     - List of quoted, space-separated values listing the bin limits for when binning by signal-to-noise ratio.
     - no
     - ``0 3.5 5 7 10 15 30 1e99``

See `the table here <prog_ccvd.html#outputs>`__ for the specific definitions of values used for binning.


Inputs
------

``star_catalog_product``:

**Description:** The filename of a ``.xml`` data product of type `DpdSheStarCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_starcatalog.html>`__ in the workdir. This data product points to a ``.fits`` data table in the workdir with information on stars in a single observation, based on the processing performed by SHE's PSF Fitting program. This table contains the relevant information:

* Object ID
* Updated best-fit positions
* Fit quality information

See the data product information linked above for a detailed description of the data product.

**Source:** At the present stage of development, this product is not yet being produced by PF-SHE's PSF Fitting program. When that program is updated to produce it, instructions for running it will be provided here.

``pipeline_config``:

**Description:** One of the following:

1. The word "None" (without quotes), which signals that default values
   for all configuration parameters shall be used.
2. The filename of an empty ``.json`` listfile, which similarly
   indicates the use of all default values.
3. The filename of a ``.txt`` file in the workdir listing configuration
   parameters and values for executables in the current pipeline run.
   This shall have the one or more lines, each with the format
   "SHE\_MyProject\_config\_parameter = config\_value".
4. The filename of a ``.xml`` data product of format
   DpdSheAnalysisConfig, pointing to a text file as described above. The
   format of this data product is described in detail in the Euclid DPDD
   at
   https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she\_analysisconfig.html.
5. The filename of a ``.json`` listfile which contains the filename of a
   ``.xml`` data product as described above.

Any of the latter three options may be used for equivalent
functionality.

The ``.txt`` pipeline configuration file may have any number of
configuration arguments which apply to other executables, in addition to
optionally any of the following which apply to this executable:

.. list-table::
   :widths: 20 50 30
   :header-rows: 1

   * - Option
     - Description
     - Default Behaviour
   * - SHE_Pipeline_profile
     - If set to "True", Python code will be profiled, and the resulting profiling data will be output to a file in the directory specified with ``--logdir``.
     - Profiling will not be enabled
   * - SHE_Validation_snr_bin_limits
     - List of quoted, space-separated values listing the bin limits for when binning by signal-to-noise ratio.
     - Will use default bin limits, as listed above in the `Options`_ section above.

See `Bin Definitions <bin_definitions>`_ for the spefic definitions of values used for binning.

If both these arguments are supplied in the pipeline configuration file
and the equivalent command-line arguments are set, the command-line
arguments will take precedence.

**Source:** One of the following:

1. May be generated manually, creating the ``.txt`` file with your text
   editor of choice.
2. Retrieved from the EAS, querying for a desired product of type
   DpdSheAnalysisConfig.
3. If run as part of a pipeline triggered by the
   `SHE_Pipeline_Run <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__
   helper program, may be created automatically by providing the argument
   ``--config_args ...`` to it (see documentation of that executable for
   further information).


Outputs
-------

.. _obs_test_results_product:

``she_observation_cti_gal_validation_test_results_product``:

**Description:** Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on the observation as a whole.

**Details:** This product contains details of the test results in the data product itself. The Data.ValidationTestList element contains a list of sheSingleValidationTestResult objects, each of which contains the result of a single test case. For the purpose of results-reporting, a test case is a test on a single shear estimation algorithm, using either all data, or binned by one of signal-to-noise, sky background level, colour, size, or epoch. This results in a total of 24 (4 algorithms times 6 ways to bin) test case results reported.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the SupplementaryInformation element. For this test, these details include the measured slope, the error on the measurement, the number of standard deviations away from zero this is, and the threshold at which this triggers a failure. In the case of the tot test cases, this is presented for the full data set. In other cases, this is presented for each bin of data, and the test case is considered ``FAILED`` if the test fails for any individual bin that has sufficient data in it to run the test (i.e. bins are ignored if they have fewer than three objects in them).

Regression results are reported for each bin of data. In the case that a bin contains no data points with positive weight which aren't flagged as failed measurements, the results will be reported as ``NaN`` for slope and intercept, and ``Inf`` for errors. Unless another error is reported, the presence of these values should be taken to indicate that a bin is empty.

Additionally, the data product contains to a tarball of ``.png`` figures illustrating the regressions for each bin of each test case. The filename of this tarball can most easily be obtained with a command such as ``grep \.tar\.gz she_observation_cti_gal_validation_test_results_product.xml``.

For this particular product, the data points used are combined from all available exposures. For instance, if an object appears in four observations, four data points will be used in the analysis, for the four different distances to the readout register in each exposure it appears in. The single measured shear value will be attached to each data point, and they will all be binned similarly. Compared to `the test results on individual exposures <exp_test_results_listfile_>`_, this test has higher statistical power, but is more likely to miss issues that occur only in a single exposure.


.. _exp_test_results_listfile:

``she_exposure_cti_gal_validation_test_results_listfile``:

**Description:** Desired filename of output ``.json`` listfile which will contain the filenames of ``.xml`` data products of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on each exposure.

**Details:** See `the above section <obs_test_results_product_>`_ for the description of the data product structure and contents.

For these products, each exposure is tested separately. Each detected object appears once in the dataset for each exposure, with the readout register distance for that exposure and the single measured shear value. The regression tests are then performed independently on each exposure. Compared to `the test results on the observation as a whole <obs_test_results_product_>`_, this test has lower statistical power, but is more likely to catch issues that occur only in a single exposure.

Example
-------

Prepare the required input data in the desired workdir. This will require downloading the ``vis_calibrated_frame_listfile``, ``mer_final_catalog_listfile``, and ``she_validated_measurements_product`` data for a selected observation (in the case of the DpdMerFinalCatalog products, these must be downloaded for all tiles which overlap this observation), and then running the `SHE_Validation_CalcCommonValData <prog_ccvd.html#SHE_Validation_CalcCommonValData>`__ program to generate the ``extended_catalog`` data product.

The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.3 SHE_Validation_ValidateCTIGal --workdir $WORKDIR  --vis_calibrated_frame_listfile $VCF_LISTFILE --extended_catalog $EXC_PRODUCT --she_validated_measurements_product $SVM_PRODUCT --she_observation_cti_gal_validation_test_results_product she_observation_cti_gal_validation_test_results_product.xml --she_exposure_cti_gal_validation_test_results_listfile she_exposure_cti_gal_validation_test_results_listfile.json

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variables  ``$VCF_LISTFILE``, ``$EXC_PRODUCT``, and ``$SVM_PRODUCT`` correspond to the filenames of the prepared listfiles and downloaded products for each input port.

This command will generate a new data product with the filename ``she_observation_cti_gal_validation_test_results_product.xml``. This can be opened with your text editor of choice to view the validation test results. This will also point to a tarball of figures of the regression for each test case, the names of which you can find in the product either by manual inspection or through a command such as ``grep \.tar\.gz she_observation_cti_gal_validation_test_results_product.xml``. After extracting the contents of the tarball (e.g. through ``tar -xvf <filename>.tar.gz``), the figures can opened with your image viewer of choice to see the regression results.

The same procedure can be used to analyse the data products pointed to by the newly-created listfile ``she_exposure_cti_gal_validation_test_results_listfile.json``.
