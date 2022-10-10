.. _SHE_Validation_ValidatePsfModelErr:

SHE_Validation_ValidatePsfModelErr
====================================

**NOTE:** This program is not yet implemented. This documentation represents the intended functionality.

This program performs the PSF Lambda validation test, T-SHE-000004-PSF-model-err-propa, which validates requirements
R-SHE-PRD-F-110 and R-SHE-PRD-F-120. This tests checks that the errors propagated from uncertainty in the PSF to galaxy
size and ellipticity are below requirements.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidatePsfModelErr`` program with Elements, use the following command in an EDEN 3.0
environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidatePsfModelErr --workdir <dir> --star_catalog_listfile <filename>
     --she_validation_test_results_product <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config
     <filename>]

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
     - Name of a filename to store logs in, relative to the workdir. If not provided, logging data will only be output
       to the terminal. Note that this will only contain logs directly from the run of this executable. Logs of
       executables called during the pipeline execution will be stored in the "logs" directory of the workdir.
     - no
     - None
   * - --logdir ``<path>``
     - Path where logging data will be stored. This only has effect if some other option is enabled which produces
       logging data, such as ``--profile``.
     - no
     - ``"."``
   * - --log-level ``<level>``
     - Minimum severity level at which to print logging information. Valid values are DEBUG, INFO, WARNING, and ERROR.
       Note that this will only contain logs directly from the run of this executable. The log level of executables
       called during pipeline execution will be set based on the configuration of the pipeline server (normally INFO).
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
     - ``.json`` listfile of 2 or more ``.xml`` data products of type `DpdSheStarCatalog <https://euclid.esac.esa.int/
       dm/dpdd/latest/shedpd/dpcards/she_starcatalog.html>`__, containing star information based on the results of
       PF-SHE's PSF Fitting program, using multiple realisations of the fitted PSF model's error distribution
     - yes
     - N/A
   * - ``--pipeline_config <filename>``
     - ``.xml`` data product or pointing to configuration file (described below), or .json listfile (Cardinality 0-1)
       either pointing to such a data product, or empty.
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
     - Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.
       int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation
       test
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
     - If set, Python code will be profiled, and the resulting profiling data will be output to a file in the directory
       specified with ``--logdir``.
     - no
     - False
   * - ``--dry_run`` (``store_true``)
     - If set, program will generate dummy output of the correct format and exit, instead of normal execution.
     - no
     - False


Inputs
------

``star_catalog_listfile``:

**Description:** ``.json`` listfile of 2 or more ``.xml`` data products of type `DpdSheStarCatalog <https://euclid.esac.
esa.int/dm/dpdd/latest/shedpd/dpcards/she_starcatalog.html>`__, containing star information based on the results of
PF-SHE's PSF Fitting program, using multiple realisations of the fitted PSF model's error distribution.

**Details:** These data products should all contain information for the same selection of stars, with the only
difference being the realisation of the PSF model's error distribution that was used to generate them and measure the
properties of their model PSFs.

The more realisations provided, the better the results of this test will be.

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
     - If set to "True", Python code will be profiled, and the resulting profiling data will be output to a file in the
       directory specified with ``--logdir``.
     - Profiling will not be enabled
   * - SHE_Validation_snr_bin_limits
     - Either: 1. List of quoted, space-separated values listing the bin limits for when binning by signal-to-noise
       ratio. Or 2. "auto-<N>" where <N> is the number of quantiles (of equal data volume) to automatically divide the
       data into.
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
   helper program, may be created automatically by providing the argument
   ``--config_args ...`` to it (see documentation of that executable for
   further information).


Outputs
-------

.. _test_results_product:

``she_validation_test_results_product``:

**Description:** Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.
esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation
test.

**Details:** This product contains details of the test results in the data product itself. The Data.ValidationTestList
element contains a list of sheSingleValidationTestResult objects, each of which contains the result of a single test
case. For this test, two test cases are reported: TC-SHE-100011-PSF-model-err-propa-ell, for the effect on ellipticity,
and TC-SHE-100012-PSF-model-err-propa-R2, for the effect on size.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the
SupplementaryInformation element. For this test, these details include the expected error in additive or multiplicative
shear measurement bias contributed by uncertainty in the PSF model.

Example
-------

Prepare the required input data in the desired workdir. At the present stage of development, this is not possible. The
instructions below are provided for when this will be possible.

The program can then be run with the following command in an EDEN 3.0 environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidatePsfModelErr --workdir $WORKDIR --star_catalog_listfile $SC_LISTFILE
    --she_validation_test_results_product she_validation_test_results_product.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir, and ``$SC_LISTFILE``
corresponds to the filename of the prepared star catalog listfile.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can be
opened with your text editor of choice to view the validation test results.
