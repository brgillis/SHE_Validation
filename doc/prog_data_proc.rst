.. _SHE_Validation_ValidateDataProc:

SHE_Validation_ValidateDataProc
===============================

This program performs the Data Proc validation test, T-SHE-000013-data-proc, which validates requirement
R-SHE-PRD-F-010. This tests checks that all required Level-2 data is produced by PF-SHE pipelines. This test does not
perform any quality checks on the data; it only checks that the data is provided in the expected format. Basic quality
checks are performed by the program SHE_Validation_ValidateGalInfo, which performs the validation test
T-SHE-000008-gal-info.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateDataProc`` program with Elements, use the following command in an EDEN 3.0
environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidateDataProc --workdir <dir> --reconciled_catalog <filename>
    --she_validation_test_results_product <filename> [--log-file <filename>] [--log-level <value>] [--reconciled_chains
    <filename>] [--pipeline_config <filename>]

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
   * - ``--reconciled_catalog <filename>``
     - ``.xml`` data product of type `DpdSheReconciledMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/
       dpcards/she_reconciledmeasurements.html>`__ pointing to ``.fits`` table(s) of shear measurements for a given
       spatial tile.
     - yes
     - N/A
   * - ``--reconciled_chains <filename>``
     - ``.xml`` data product of type `DpdSheReconciledLensMCChains <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/
       dpcards/she_reconciledlensmcchains.html>`__ pointing to a ``.fits`` table of shear measurement MCMC chains for a
       given spatial tile.
     - no
     - None
   * - ``--pipeline_config <filename>``
     - ``.xml`` data product pointing to configuration file (described below), or .json listfile (Cardinality 0-1)
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
     - Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa
       .int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation
       test.
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

``reconciled_catalog``:

**Description:** ``.xml`` data product of type `DpdSheReconciledMeasurements <https://euclid.esac.esa.int/dm/dpdd/
latest/shedpd/dpcards/she_reconciledmeasurements.html>`__ pointing to ``.fits`` table(s) of shear measurements for a
given spatial tile. This product will be checked to confirm that it points to at least one valid table of shear
measurements.

**Source:** This product is produced by the ``SHE_CTE_ReconcileShear`` program within the SHE Reconciliation pipeline.
See that program's documentation in the `SHE_CTE <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_CTE>`__ project for more
details. This product is archived in the EAS at the end of execution of the SHE Reconciliation pipeline when it is
triggered via PPO or COORS. Archived instances of this product may be downloaded through the EAS, using a desired
DataSetRelease and TileIndex to specify which one.

``reconciled_chains``:

**Description:** ``.xml`` data product of type `DpdSheReconciledLensMCChains <https://euclid.esac.esa.int/dm/dpdd/
latest/shedpd/dpcards/she_reconciledlensmcchains.html>`__ pointing to a ``.fits`` table of shear measurement MCMC
chains for a given spatial tile. If provided, this product will be checked to confirm that it points to a valid table
of shear measurement MCMC chains.

**Source:** This product is produced by the ``SHE_CTE_ReconcileShear`` program within the SHE Reconciliation pipeline.
See that program's documentation in the `SHE_CTE <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_CTE>`__ project for more
details. This product is archived in the EAS at the end of execution of the SHE Reconciliation pipeline when it is
triggered via PPO or COORS. Archived instances of this product may be downloaded through the EAS, using a desired
DataSetRelease and TileIndex to specify which one.

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
case.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the
SupplementaryInformation element. For this test, these details include whether any expected file was missing or empty.

Example
-------

Prepare the required input data in the desired workdir. This will require downloading the reconciled catalog and chains
data for a selected spatial tile.

The program can then be run with the following command in an EDEN 3.0 environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidateDataProc --workdir $WORKDIR --reconciled_catalog $REC_CAT
    --reconciled_chains $REC_CHAINS --she_validation_test_results_product she_validation_test_results_product.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variables ``$REC_CAT`` and
``$REC_CHAINS`` correspond to the filenames of the prepared downloaded products for each input port.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can
be opened with your text editor of choice to view the validation test results.
