.. _SHE_Validation_ValidateSedExist:

SHE_Validation_ValidateSedExist
===============================

This program performs the SED-Exist validation test, T-SHE-000011-star-SED-exist, which validates requirement
R-SHE-CAL-F-060. This tests checks that SEDs are provided for a number of stars sufficient to adequately constrain the
PSF model for a given observation.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateSedExist`` program with Elements, use the following command in an EDEN 3.0 environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidateSedExist --workdir <dir> --phz_catalog_listfile <filename>
    --vis_calibrated_frame_listfile <filename> --mer_final_catalog_listfile <filename>
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
     - Name of a filename to store logs in, relative to the workdir. If not provided, logging data will only be output to the terminal. Note that this will only contain logs directly from the run of this executable. Logs of executables called during the pipeline execution will be stored in the "logs" directory of the workdir.
     - no
     - None
   * - --logdir ``<path>``
     - Path where logging data will be stored. This only has effect if some other option is enabled which produces logging data, such as ``--profile``.
     - no
     - ``"."``
   * - --log-level ``<level>``
     - Minimum severity level at which to print logging information. Valid values are DEBUG, INFO, WARNING, and ERROR. Note that this will only contain logs directly from the run of this executable. The log level of executables called during pipeline execution will be set based on the configuration of the pipeline server (normally INFO).
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
   * - ``--phz_catalog_listfile <filename>``
     - `.json`` listfile, containing the filenames of ```.xml`` data products of type `PhzPfOutputCatalog <https://
       euclid.esac.esa.int/dm/dpdd/latest/phzdpd/dpcards/phz_phzpfoutputcatalog.html>`__, which contain the photo-z,
       template, and SED information for galaxies in each tile overlapping an observation.
     - yes
     - N/A
   * - ``--vis_calibrated_frame_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdVisCalibratedFrame <https://euclid.esac.esa.int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html>`__, containing VIS science images for each exposure in an observation.
     - yes
     - N/A
   * - ``--mer_final_catalog_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdMerFinalCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html>`__, containing MER object catalogs for all tiles
       overlapping an observation.
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
     - Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation
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

**Description:** Desired filename of output ``.xml`` data product of type `DpdSheValidationTestResults <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_validationtestresults.html>`__, containing the results of the validation test.

**Details:** This product contains details of the test results in the data product itself. The Data.ValidationTestList element contains a list of sheSingleValidationTestResult objects, each of which contains the result of a single test case.

Each of these results objects lists the result of the test (``PASSED`` or ``FAILED``) and details of it in the SupplementaryInformation element. For this test, these details include ...

Example
-------

Prepare the required input data in the desired workdir. This will require downloading the ... data for a selected ... .

The program can then be run with the following command in an EDEN 3.0 environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidateSedExist --workdir $WORKDIR
    --she_validation_test_results_product she_validation_test_results_product.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variables  ... correspond to the filenames of the prepared listfiles and downloaded products for each input port.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can be opened with your text editor of choice to view the validation test results.
