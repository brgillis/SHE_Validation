.. _SHE_Validation_ValidateCTIPSF:

SHE_Validation_ValidateCTIPSF
==============================

This program performs the CTI-PSF validation test, T-SHE-000009-CTI-PSF, which validates requirement R-SHE-CAL-F-020. This tests checks if there is any statistically-significant difference between bins in correlation between model PSF shape and distance of object image from the detector's readout register.

**Note:** This program is still in development, and not yet fully-functional.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateCTIPSF`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 9.0 SHE_Validation_ValidateCTIPSF --workdir <dir> --star_catalog_listfile <filename> --extended_catalog <filename> --she_observation_cti_psf_validation_test_results_product <filename> --she_exposure_cti_psf_validation_test_results_listfile <filename>  [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>] [--snr_bin_limits "<value> <value> ..."] [--bg_bin_limits "<value> <value> ..."] [--colour_bin_limits "<value> <value> ..."] [--size_bin_limits "<value> <value> ..."] [--epoch_bin_limits "<value> <value> ..."]

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
   * - ``--star_catalog_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdSheStarCatalog <hhttps://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_starcatalog.html>`__, containing PF-SHE's updated information on stars fit by the `SHE_PSF_Toolkit_FitPSFs <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_PSFToolkit>`__ program.
     - yes
     - N/A
   * - ``--extended_catalog <filename>``
     - ``.xml`` data product of type `DpdMerFinalCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html>`__, containing a catalog of all objects in the observation, with all columns from the MER object catalogs plus extra columns for calculated data.
     - yes
     - N/A
   * - ``--mdb <filename>``
     - ``.xml`` Mission DataBase file. See https://euclid.roe.ac.uk/projects/missiondatabase/wiki/Wiki for documentation of it.
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
   * - ``--she_observation_cti_psf_validation_test_results_product``
     - Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on the observation as a whole.
     - yes
     - N/A
   * - ``--she_exposure_cti_psf_validation_test_results_listfile``
     - Desired filename of output ``.json`` listfile which will contain the filenames of ``.xml`` data products of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on each exposure.
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
   * - ``--bg_bin_limits "<value> <value> ..."``
     - List of quoted, space-separated values listing the bin limits in ADU for when binning by sky background level.
     - no
     - ``0 30 35 35.25 36 50 1e99``
   * - ``--colour_bin_limits "<value> <value> ..."``
     - List of quoted, space-separated values listing the bin limits for when binning by colour.
     - no
     - ``-1e99 -2.5 -2 -1.5 -1 -0.6 1e99``
   * - ``--size_bin_limits "<value> <value> ..."``
     - List of quoted, space-separated values listing the bin limits in pixels for when binning by size.
     - no
     - ``0 30 45 75 140 300 1e99``
   * - ``--epoch_bin_limits "<value> <value> ..."``
     - List of quoted, space-separated values listing the bin limits for when binning by epoch.
     - no
     - N/A - Not yet implemented


Inputs
------

``star_catalog_listfile``:

**Description:** ``.json`` listfile pointing to ``.xml`` data products of type `DpdSheStarCatalog <hhttps://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_starcatalog.html>`__, containing PF-SHE's updated information on stars fit by the `SHE_PSF_Toolkit_FitPSFs <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_PSFToolkit>`__ program. This contains the following relevant information for stars used in the fitting process:

* Updated world position
* Position on detector
* Shape measurement

**Source:** Unavailable at present; the ``SHE_PSF_Toolkit_FitPSFs`` program has not yet implemented production of this data product.

``extended_catalog``:

**Description:** Desired filename of output ``.xml`` data product of type DpdMerFinalCatalog, containing a catalog of all objects in the observation, with all columns from the MER object catalogs plus extra columns for calculated data.

The generated data product will be of type DpdMerFinalCatalog (though see note in the paragraph below), which is detailed in full on the DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer\_finalcatalog.html. This product provides the filename of a generated ``.fits`` data table in the attribute Data.DataContainer.FileName. This filename is generated to be fully-compliant with Euclid file naming standards. You can easily get this filename from the product with a command such as ``grep \.fits extended_catalog.xml`` (assuming the output data product is named ``extended_catalog.xml``; substitute as necessary).

The data table here will include extra columns which are not defined in the MER Final Catalog, containing the calculated data for each object (S/N, colour, etc.). As such, this table isn't fully-compliant with MER Final Catalog table format. This product is used only intermediately within SHE pipelines, and so this non-compliance is not expected to pose any issues.

The added columns are:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Column Name
     - Data Type
     - Description
   * - SNR
     - 32-bit float
     - Signal-to-noise ratio of the object, using the flux and its error in the VIS filter as determined by PF-MER
   * - BG
     - 32-bit float
     - Sky background level at the object position in ADU, from PF-VIS's background maps
   * - COLOUR
     - 32-bit float
     - Colour of the object, defined as ``2.5*log10(FLUX_VIS_APER/FLUX_NIR_STACK_APER)``, using PF-MER's measured flux values
   * - SIZE
     - 32-bit float
     - Size of the object, defined as the size in pixels of PF-MER's segmentation map for it
   * - EPOCH
     - 32-bit float
     - Time at which the object was observed. Currently unused, and filled with dummy data

**Source:** This is a product purely intermediate to pipelines, and as such is not stored in the EAS. It can be generated by running the ``SHE_Validation_CalcCommonValData`` task. See `that task's documentation <prog_ccvd.html#SHE_Validation_CalcCommonValData>`__ for details.

``mdb``:

**Description:** ``.xml`` Mission DataBase file. See https://euclid.roe.ac.uk/projects/missiondatabase/wiki/Wiki for documentation of it. Note that despite also being in ``.xml`` format, this file is not readable or writable as a "data product" like other ``.xml`` files used as input and output.

This file contains various parameters describing various specifics of the Euclid telescope and mission, such as the dimensions of the detectors in the VIS instrument. Some of this data is stored directly in the MDB ``.xml`` file, while other data is stored in ``.fits`` files linked to by it. Similar to ``.xml`` data products, these ``.fits`` files should be stored in the ``data`` subdirectory of the workdir. Given the large number of ``.fits`` files associated with the MDB, only those which are expected to be accessed are generally downloaded.

For the purposes used within PF-SHE, the needed ``.fits`` files are those for the parameters:

* SpaceSegment.Instrument.VIS.ReadoutNoiseTable
* SpaceSegment.Instrument.VIS.GainCoeffs

**Source:** The Euclid MDB's present and historical versions can be viewed online at https://euclid.esac.esa.int/epdb/. From here, it is possible to download the MDB ``.xml`` file of a given version by selecting that version using the version tree in the left panel. Once the desired version is selected, the MDB ``.xml`` file can be downloaded through the link at the top of the right panel.

Next, the required ``.fits`` files should be downloaded. For each parameter where this is required (see list in the Description), select this parameter from the tree in the left panel. This will bring up the parameter's information in the right panel, which will include a link to the ``.fits`` file. Download the file from this link and store it in the ``data`` subdirectory of the workdir.

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
   * - SHE_Pipeline_profile
     - If set to "True", Python code will be profiled, and the resulting profiling data will be output to a file in the directory specified with ``--logdir``.
     - Profiling will not be enabled
   * - SHE_Validation_snr_bin_limits
     - List of quoted, space-separated values listing the bin limits for when binning by signal-to-noise ratio.
     - Will use default bin limits, as listed above in the `Options`_ section above.
   * - SHE_Validation_bg_bin_limits
     - List of quoted, space-separated values listing the bin limits in ADU for when binning by sky background level.
     - Will use default bin limits, as listed above in the `Options`_ section above.
   * - SHE_Validation_colour_bin_limits
     - List of quoted, space-separated values listing the bin limits for when binning by colour.
     - Will use default bin limits, as listed above in the `Options`_ section above.
   * - SHE_Validation_size_bin_limits
     - List of quoted, space-separated values listing the bin limits in pixels for when binning by size.
     - Will use default bin limits, as listed above in the `Options`_ section above.
   * - SHE_Validation_epoch_bin_limits
     - List of quoted, space-separated values listing the bin limits for when binning by epoch.
     - Will use default bin limits, as listed above in the `Options`_ section above.


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
   helper script, may be created automatically by providing the argument
   ``--config_args ...`` to it (see documentation of that executable for
   further information).


Outputs
-------

.. _obs_test_results_product:

``she_observation_cti_psf_validation_test_results_product``:

**Description:** Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on the observation as a whole.

**Details:** This product contains details of the test results in the data product itself. The Data.ValidationTestList element contains a list of sheSingleValidationTestResult objects, each of which contains the result of a single test case. For the purpose of results-reporting, a test case is a test on a single shear estimation algorithm binned by one of signal-to-noise, sky background level, colour, size, or epoch. This results in a total of 20 (4 algorithms times 5 ways to bin) test case results reported.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the SupplementaryInformation element. For this test, these details include the measured slope in each bin, the error on the measurement of slope, the difference between the measurements of slope in each consecutive pair of bins and the errors on this value, the number of standard deviations away from zero this value is, and the threshold at which this triggers a failure. This is presented for each bin of data (except the first bin in the case of bin differences), and the test case is considered ``FAILED`` if the test fails for any pair of bins that has sufficient data in both bins to run the test (i.e. pairs of bins are ignored if they have fewer than three objects in either of them).

Regression results are reported for each bin of data. In the case that a bin contains no data points with positive weight which aren't flagged as failed measurements, the results will be reported as ``NaN`` for slope and intercept differences with neighboring bins, and ``Inf`` for errors. Unless another error is reported, the presence of these values should be taken to indicate that a bin is empty.

Additionally, the data product contains to a tarball of ``.png`` figures illustrating the regressions for each bin of each test case. The filename of this tarball can most easily be obtained with a command such as ``grep \.tar\.gz she_observation_cti_psf_validation_test_results_product.xml``.

For this particular product, the data points used are combined from all available exposures. For instance, if an object appears in four observations, four data points will be used in the analysis, for the four different distances to the readout register in each exposure it appears in and the four different ellipticities for each of these exposures. Compared to `the test results on individual exposures <exp_test_results_listfile_>`_, this test has higher statistical power, but is more likely to miss issues that occur only in a single exposure.


.. _exp_test_results_listfile:

``she_exposure_cti_psf_validation_test_results_listfile``:

**Description:** Desired filename of output ``.json`` listfile which will contain the filenames of ``.xml`` data products of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on each exposure.

**Details:** See `the above section <obs_test_results_product_>`_ for the description of the data product structure and contents.

For these products, each exposure is tested separately. Each detected object appears once in the dataset for each exposure, with the readout register distance and ellipticity for that exposure. The regression tests are then performed independently on each exposure. Compared to `the test results on the observation as a whole <obs_test_results_product_>`_, this test has lower statistical power, but is more likely to catch issues that occur only in a single exposure.


Example
-------

**Note:** This program is still in development, and it is not yet possible to generate the needed ``star_catalog`` input data products. This example is provided to illustrate the intended functionality of this program.

Prepare the required input data in the desired workdir. This will require downloading the ``vis_calibrated_frame_listfile``, ``mer_final_catalog_listfile``, and ``she_validated_measurements_product`` data, and then running the `SHE_Validation_CalcCommonValData <prog_ccvd.html#SHE_Validation_CalcCommonValData>`__ program to generate the ``extended_catalog`` data product, and also the `SHE_PSF_Toolkit_FitPSFs <phttps://gitlab.euclid-sgs.uk/PF-SHE/SHE_PSFToolkit>`__ program to generate the ``star_catalog_listfile`` and the data products it points to.

The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 9.0 SHE_Validation_ValidatePSFGal --workdir $WORKDIR  --star_catalog_listfile $SC_LISTFILE --extended_catalog $EXC_PRODUCT --she_observation_cti_psf_validation_test_results_product she_observation_cti_psf_validation_test_results_product.xml --she_exposure_cti_psf_validation_test_results_listfile she_exposure_cti_psf_validation_test_results_listfile.json

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variables  ``$SC_LISTFILE`` and ``$EXC_PRODUCT`` correspond to the filenames of the prepared listfiles and downloaded products for each input port.

This command will generate a new data product with the filename ``she_observation_cti_psf_validation_test_results_product.xml``. This can be opened with your text editor of choice to view the validation test results. This will also point to a tarball of figures of the regression for each test case, the names of which you can find in the product either by manual inspection or through a command such as ``grep \.tar\.gz she_observation_cti_psf_validation_test_results_product.xml``. After extracting the contents of the tarball (e.g. through ``tar -xvf <filename>.tar.gz``), the figures can opened with your image viewer of choice to see the regression results.

The same procedure can be used to analyse the data products pointed to by the newly-created listfile ``she_exposure_cti_psf_validation_test_results_listfile.json``.
