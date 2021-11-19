.. _SHE_Validation_ValidateShearBias:

SHE_Validation_ValidateShearBias
================================

This program performs the Shear Bias validation test, T-SHE-000006-shear-bias, which validates requirement R-SHE-CAL-F-070. This tests checks the multiplicative and additive shear bias are consistent with requirements. It checks this both for all objects, and for various bins of objects.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateShearBias`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_ValidateShearBias --workdir <dir> --matched_catalog <filename> --she_validation_test_results_product <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>] [--snr_bin_limits "<value> <value> ..."] [--bg_bin_limits "<value> <value> ..."] [--colour_bin_limits "<value> <value> ..."] [--size_bin_limits "<value> <value> ..."] [--epoch_bin_limits "<value> <value> ..."] [--max_g_in <value>] [--bootstrap_errors <value>] [--require_fitclass_zero <value>]

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
   * - ``--matched_catalog <filename>``
     - ``.xml`` data product of type `DpdSheValidatedMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_measurements.html>`__, containing matched catalogs with both shear estimate information and true universe input information.
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
     - Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on the observation as a whole.
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
   * - ``--max_g_in <value>``
     - Determines the maximum magnitude of true shear applied to objects, for those objects to be included in the bias regression.
     - no
     - 1.0
   * - ``bootstrap_errors``
     - If set to True, will calculate bias errors through a bootstrap approach. Otherwise, will trust error estimates from shear estimation algorithms and calculate errors based on those.
     - no
     - False
   * - ``require_fitclass_zero``
     - If set to True, will only include for the regression test objects identified as likely galaxies (FITCLASS=0) which match to galaxies. Otherwise, will include all objects which match to galaxies, even if not identified as such.
     - no
     - False


Inputs
------

``matched_catalog``:

**Description:** ``.xml`` data product of type DpdSheValidatedMeasurements, containing matched catalogs with both shear estimate information and true universe input information. The data product uses the type DpdSheValidatedMeasurements (though see note in the paragraph below), which is detailed in full on the DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she\_measurements.html. This product provides the filenames of generated ``.fits`` data tables (one for each shear estimation algorithm) in the attributes Data.<Algorithm>ShearMeasurements.DataStorage.DataContainer.FileName.

The data tables here will include extra columns which are not defined in the Shear Measurements table formats, containing key information on the matched True Universe sources and some calculated information, and will be split into HDUs for tables of objects best matching to galaxies (index 1), objects best matching to stars (index 2), and all objects (index 3). As such, this file isn't fully-compliant with the table format, and should only be used intermediately within a pipeline or for manual analysis, and not ingested into the EAS.

The table for objects best matched to galaxies includes useful additional data. The added columns are:

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - Column Name
     - Data Type
     - Description
   * - ``RA_MAG``
     - 32-bit float
     - From TU Galaxy Catalog: Right ascension (J2000) with lensing in degrees
   * - ``DEC_MAG``
     - 32-bit float
     - From TU Galaxy Catalog: Declination (J2000) with in degrees
   * - ``BULGE_FRACTION``
     - 32-bit float
     - From TU Galaxy Catalog: Ratio of the ﬂux in the bulge component to the total ﬂux (often written B/T)
   * - ``BULGE_R50``
     - 32-bit float
     - From TU Galaxy Catalog: Major-axis half-light radius in arcsec
   * - ``DISK_R50``
     - 32-bit float
     - From TU Galaxy Catalog: For disk-dominated galaxies, the disk_length is the major-axis exponential scalelength in arcsec (is 0 for bulge-dominated galaxies)
   * - ``BULGE_NSERSIC``
     - 32-bit float
     - From TU Galaxy Catalog: Sersic index of the bulge component
   * - ``BULGE_AXIS_RATIO``
     - 32-bit float
     - From TU Galaxy Catalog: Bulge projected axis ratio (b/a)
   * - ``INCLINATION_ANGLE``
     - 32-bit float
     - From TU Galaxy Catalog: Galaxy inclination angle (where 0 degrees = face-on and 90 degrees = edge-on). Galaxy ellipticity for disk and bulge components are computed following the recipe in https://euclid.roe.ac.uk/projects/sgsshear/wiki/SHE-SIM
   * - ``DISK_ANGLE``
     - 32-bit float
     - From TU Galaxy Catalog: Position of the disk rotation axis (degrees) (assumption: bulge\_angle = disk_angle) From North to East, with the major axis aligned in Declination
   * - ``KAPPA``
     - 32-bit float
     - From TU Galaxy Catalog: Lensing convergence
   * - ``GAMMA1``
     - 32-bit float
     - From TU Galaxy Catalog: Lensing shear for axis 1 (using same convention as ``DISK_ANGLE``)
   * - ``GAMMA2``
     - 32-bit float
     - From TU Galaxy Catalog: Lensing shear for axis 2 (using same convention as ``DISK_ANGLE``)
   * - ``Beta_Input_Shear``
     - 32-bit float
     - Calculated: Position angle of true shear value applied, using convention 0 degrees = West on the sky, 90 degrees = North on the sky
   * - ``Mag_Input_Shear``
     - 32-bit float
     - Calculated: Magnitude of true shear value applied
   * - ``SHE_<ALGORITHM>_Beta_Est_Shear``
     - 32-bit float
     - Calculated: Position angle of estimated shear value, using same convention as ``Beta_Input_Shear``
   * - ``SHE_<ALGORITHM>_Mag_Est_Shear``
     - 32-bit float
     - Calculated: Magnitude of estimated shear value
   * - ``Beta_Input_Bulge_Unsheared_Shape``
     - 32-bit float
     - Calculated: Position angle of disk rotation axis, using same convention as ``Beta_Input_Shear``
   * - ``Beta_Input_Disk_Unsheared_Shape``
     - 32-bit float
     - Calculated: Position angle of bulge rotation axis, using same convention as ``Beta_Input_Shear``

**Source:** This is an intermediate data product, not stored in the EAS. It can be generated through use of the `SHE_Validation_MatchToTU program <prog_match_to_tu.html>`__ - See that program's documentation for details.

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
   * - SHE_Validation_ValidateShearBias_max_g_in
     - Determines the maximum magnitude of true shear applied to objects, for those objects to be included in the bias regression.
     - 1.0
   * - SHE_Validation_ValidateShearBias_bootstrap_errors
     - If set to True, will calculate bias errors through a bootstrap approach. Otherwise, will trust error estimates from shear estimation algorithms and calculate errors based on those.
     - False
   * - SHE_Validation_ValidateShearBias_require_fitclass_zero
     - If set to True, will only include for the regression test objects identified as likely galaxies (FITCLASS=0) which match to galaxies. Otherwise, will include all objects which match to galaxies, even if not identified as such.
     - False

If both these arguments are supplied in the pipeline configuration file
and the equivalent command-line arguments are set, the command-line
arguments will take precedence.

**Source:** One of the following:

1. May be generated manually, creating the ``.txt`` file with your text
   editor of choice.
2. Retrieved from the EAS, querying for a desired product of type
   DpdSheAnalysisConfig.
3. If run as part of a pipeline triggered by the
   ``SHE_Pipeline_Run`` <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__
   helper script, may be created automatically by providing the argument
   ``--config_args ...`` to it (see documentation of that executable for
   further information).


Outputs
-------

``she_validation_test_results_product``:

**Description:** Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test on this observation.

**Details:** This product contains details of the test results in the data product itself. The Data.ValidationTestList element contains a list of sheSingleValidationTestResult objects, each of which contains the result of a single test case. For the purpose of results-reporting, a test case is a test on a single shear estimation algorithm, using either all data, or binned by one of signal-to-noise, sky background level, colour, size, or epoch, for each of the multiplicative and additive biases. This results in a total of 48 (4 algorithms times 6 ways to bin times 2 biases) test case results reported.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the SupplementaryInformation element. For this test, these details include the measured multiplicative and additive shear biases, the errors on the measurements, the numbers of standard deviations away from zero these are, and the threshold at which this triggers a failure. In the case of the global test cases, this is presented for the full data set. In other cases, this is presented for each bin of data, and the test case is considered ``FAILED`` if the test fails for any individual bin that has sufficient data in it to run the test (i.e. bins are ignored if they have fewer than three objects in them).

Additionally, the data product contains to a tarball of ``.png`` figures illustrating the regressions for each bin of each test case. The filename of this tarball can most easily be obtained with a command such as ``grep \.tar\.gz she_observation_cti_gal_validation_test_results_product.xml``.


Example
-------

Prepare the required input data in the desired workdir. This will require downloading the ``vis_calibrated_frame_listfile``, ``tu_output_product``, and ``she_validated_measurements_product`` data, and then running the `SHE_Validation_MatchToTU <prog_match_to_tu.html>`__ program to generate the ``matched_catalog`` data product.

The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_ValidateCTIGal --workdir $WORKDIR  --matched_catalog $MC_PRODUCT --she_validation_test_results_product she_validation_test_results_product.xml

where the variable ``$$WORKDIR`` corresponds to the path to your workdir and the variable ``$MC_PRODUCT`` corresponds to the filename of the prepared matched catalog product.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can be opened with your text editor of choice to view the validation test results. This will also point to a tarball of figures of the regression for each test case, the names of which you can find in the product either by manual inspection or through a command such as ``grep \.tar\.gz she_validation_test_results_product.xml``. After extracting the contents of the tarball (e.g. through ``tar -xvf <filename>.tar.gz``), the figures can opened with your image viewer of choice to see the regression results.
