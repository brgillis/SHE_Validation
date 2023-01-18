.. _SHE_Validation_ValidatePsfLambda:

SHE_Validation_ValidatePsfLambda
====================================

**NOTE:** This program is not yet implemented. This documentation represents the intended functionality.

This program performs the PSF Lambda validation test, T-SHE-000002-PSF-lambda, which validates requirements
R-SHE-CAL-F-040 and R-SHE-CAL-F-050. This tests checks that PSFs can be adequately approximated from broad-band
magnitudes.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidatePsfLambda`` program with Elements, use the following command in an EDEN 3.0
environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidatePsfLambda --workdir <dir> --reference_star_catalog_product <filename>
     --broadband_star_catalog_product <filename> --she_validation_test_results_product <filename> [--log-file <filename>]
     [--log-level <value>] [--pipeline_config <filename>]

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
   * - ``--reference_star_catalog_product <filename>``
     - ``.xml`` data product of type `DpdSheStarCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/
       she_starcatalog.html>`__, containing star information based on the results of PF-SHE's PSF Fitting program,
       using PSF images generated from full SED information.
     - yes
     - N/A
   * - ``--broadband_star_catalog_product <filename>``
     - ``.xml`` data product of type `DpdSheStarCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/
       she_starcatalog.html>`__, containing star information based on the results of PF-SHE's PSF Fitting program,
       using PSF images generated from broad-band magnitudes.
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

``reference_star_catalog_product``:

**Description:** Filename of ``.xml`` data product of type `DpdSheStarCatalog <https://euclid.esac.esa.int/dm/dpdd/
latest/shedpd/dpcards/she_starcatalog.html>`__, containing star information based on the results of PF-SHE's PSF Fitting
program, using PSF images generated from full SED information.

**Details:** This product may contain data for any number of stars, with a greater number leading to greater accuracy
of this validation test. The stars used should be distributed over ranges of the following values:

* SED
* Position in Field-of-View
* Realisation of telescope model

For example, these values can be drawn from the details of simulated or real Euclid-Wide observations of stars.

``broadband_star_catalog_product``:

**Description:** Filename of ``.xml`` data product of type `DpdSheStarCatalog <https://euclid.esac.esa.int/dm/dpdd/
latest/shedpd/dpcards/she_starcatalog.html>`__, containing star information based on the results of PF-SHE's PSF Fitting
program, using PSF images generated from broad-band magnitudes.

**Details:** This product must represent the same selection of stars as those in the `reference_star_catalog_product`.
The only difference should be that the PSFs were generated using broad-band magnitudes (calculated from the full SED
information) rather than directly from the SED information.

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

Any of the latter three options may be used for equivalent functionality.

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
case. For this test, two test cases are reported: TC-SHE-100003-PSF-lambda-ell, for the effect on ellipticity, and
TC-SHE-100004-PSF-lambda-R2, for the effect on size.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the
SupplementaryInformation element. For this test, these details include the Kolmogorov-Smirnov test statistic (either
from a one-tailed two-sample test, if a ``ref_star_catalog_product`` is provided, or a two-tailed one-sample test if
not), the p-value of this statistic, and the threshold at which this triggers a failure. In the case of the ``tot`` test
case, this is presented for the full data set. For the ``SNR`` test case, this is presented for each bin of data, and
the test case is considered ``FAILED`` if the test fails for any individual bin that has sufficient data in it to run
the test (i.e. bins are ignored if they have no objects in them).

Example
-------

Prepare the required input data in the desired workdir. At the present stage of development, this is not possible. The
instructions below are provided for when this will be possible.

The program can then be run with the following command in an EDEN 3.0 environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidatePsfLambda --workdir $WORKDIR --reference_star_catalog_product
    $RSC_PRODUCT --broadband_star_catalog_product $BSC_PRODUCT --she_validation_test_results_product
    she_validation_test_results_product.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir, and ``$RSC_PRODUCT`` and ``$BSC_PRODUCT``
correspond to the filenames of the prepared reference and broad-band star catalog products.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can be
opened with your text editor of choice to view the validation test results.
