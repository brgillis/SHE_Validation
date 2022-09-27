.. _SHE_Validation_ValidateSedExist:

SHE_Validation_ValidateSedExist
===============================

**WARNING:** This executable is presently under construction. This documentation reflects the intended functionality of
it.

This program performs the SED-Exist validation test, T-SHE-000011-star-SED-exist, which validates requirement
R-SHE-CAL-F-060. This tests checks that SEDs are provided for a number of stars sufficient to adequately constrain the
PSF model for a given observation.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateSedExist`` program with Elements, use the following command in an EDEN 3.0
environment:

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
   * - ``--phz_catalog_listfile <filename>``
     - `.json`` listfile, containing the filenames of ```.xml`` data products of type `PhzPfOutputCatalog <https:/
       euclid.esac.esa.int/dm/dpdd/latest/phzdpd/dpcards/phz_phzpfoutputcatalog.html>`__, which contain the photo-z,
       template, and SED information for galaxies in each tile overlapping an observation.
     - yes
     - N/A
   * - ``--vis_calibrated_frame_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdVisCalibratedFrame <https://euclid.esac.esa
       .int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html>`__, containing VIS science images for each exposure
       in an observation.
     - yes
     - N/A
   * - ``--mer_final_catalog_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdMerFinalCatalog <https://euclid.esac.esa
       .int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html>`__, containing MER object catalogs for all tiles
       overlapping an observation.
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

``phz_catalog_listfile``:

**Description:** The filename of a `.json`` listfile, containing the filenames of ```.xml`` data products of type
`PhzPfOutputCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/phzdpd/dpcards/phz_phzpfoutputcatalog.html>`__, which
contain the photo-z, template, and SED information for galaxies in each tile overlapping an observation. For the
purpose of this validation test, only the SED information from the stars table is used.

See the data product information linked above for a detailed description of the data product.

**Source:** The PhzPfOutputCatalog data products and their associated ``.fits`` files may be downloaded through the
EAS, using a desired DataSetRelease and multiple TileIndex values to specify which ones. These TileIndex values should
correspond to the tiles which overlap the observation being analysed. These are most easily determined through using
the online EAS viewer available at https://eas-dps-cus.test.euclid.astro.rug.nl/ to query for DpdMerFinalCatalog
products whose ObservationIdList contains the ID of this observation, and which match the DataSetRelease in use. The
TileIndex values for these can then be used to download the PhzPfOutputCatalog data products for the same tiles.

The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script
``get_all_phz_products.sh`` to aid in the download of these products - see that project's documentation for details on
this script. This script can be used to download the desired products to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   TILE_ID=$TILE_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_phz_products.sh

where ``$WORKDIR`` is the workdir and ``$TILE_ID`` is the TileIndex of each overlapping tile (e.g. 90346, repeat for
the TileIndex of each overlapping tile).

After the data has been downloaded, sort the downloaded ``.fits`` files into the ``data`` subdirectory of the workdir.
Next, write a ``.json`` listfile containing the filenames of the downloaded ``.xml`` data products with your text
editor of choice. It should look something like:

.. code-block:: text

   ["PhzPfOutputCatalog-0.xml", "PhzPfOutputCatalog-1.xml", ...]

except with the actual filenames of the downloaded data products. The filename of this ``.json`` listfile can then be
passed to the ``phz_catalog_listfile`` input argument.

``vis_calibrated_frame_listfile``:

**Description:** The filename of a ``.json`` listfile which contains the filenames of 1-4 ``.xml`` data products of
type `DpdVisCalibratedFrame <https://euclid.esac.esa.int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html>`__ in
the workdir, corresponding to each exposure of the observation being analysed. This data product contains the science
images made available by PF-VIS, containing the following data relevant to PF-SHE:

* Science images
* Masks
* Noise maps
* Background maps
* Weight maps
* WCS solutions

See the data product information linked above for a detailed description of the data product.

This information is stored in multiple Multi-HDU ``.fits`` files associated with each data product, which must be
stored in the ``data`` subdirectory of the workdir.

**Source:** The DpdVisCalibratedFrame data products and their associated ``.fits`` files may be downloaded through the
EAS, using a desired DataSetRelease and ObservationId to specify which ones. The `SHE_IAL_Pipelines project <https://
gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script ``get_all_vis_products.sh`` to aid in the
download of these products - see that project's documentation for details on this script. This script can be used to
download the desired products to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   OBS_ID=$OBS_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_vis_products.sh

where ``$WORKDIR`` is the workdir and ``$OBS_ID`` is the ObservationId of the desired data (e.g. 10351). Note that this
script will download both the DpdVisCalibratedFrame and DpdVisStackedFrame data products. If the latter isn't needed,
you can comment out this code within the script so that it is not unnecessarily downloaded.

After the data has been downloaded, sort the downloaded ``.fits`` files into the ``data`` subdirectory of the workdir.
Next, write a ``.json`` listfile containing the filenames of the downloaded ``.xml`` data products with your text
editor of choice. It should look something like:

.. code-block:: text

   ["DpdCalibratedFrame1.xml","DpdCalibratedFrame2.xml","DpdCalibratedFrame3.xml","DpdCalibratedFrame4.xml"]

except with the actual filenames of the downloaded data products. The filename of this ``.json`` listfile can then be
passed to the ``vis_calibrated_frame_listfile`` input argument.

``mer_final_catalog_listfile``:

**Description:** The filename of a ``.json`` listfile which contains the filenames of 1-12 ``.xml`` data products of
type `DpdMerFinalCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html>`__  in the
workdir, corresponding to catalogs for each tile which overlaps the observation being analysed. This data product
contains the object detections catalogue provided by MER, containing the following information relevant to PF-SHE:

* Object ID assignments
* Object positions
* Object fluxes in various filters
* Object segmentation map ID
* Object segmentation map size

See the data product information linked above for a detailed description of the data product.

This information is stored in one ``.fits`` file associated with each data product, which must be stored in the
``data`` subdirectory of the workdir.

**Source:** The DpdMerFinalCatalog data products and their associated ``.fits`` files may be downloaded through the
EAS, using a desired DataSetRelease and multiple TileIndex values to specify which ones. These TileIndex values should
correspond to the tiles which overlap the observation being analysed. These are most easily determined through using
the online EAS viewer available at https://eas-dps-cus.test.euclid.astro.rug.nl/ to query for DpdMerFinalCatalog
products whose ObservationIdList contains the ID of this observation, and which match the DataSetRelease in use.

The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script
``get_all_mer_products.sh`` to aid in the download of these products - see that project's documentation for details on
this script. This script can be used to download the desired products to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   TILE_ID=$TILE_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_mer_products.sh

where ``$WORKDIR`` is the workdir and ``$TILE_ID`` is the TileIndex of each overlapping tile (e.g. 90346, repeat for
the TileIndex of each overlapping tile). Note that this script will download both the DpdMerFinalCatalog and
DpdMerSegmentationMap data products. If the latter aren't needed, you can comment out this code within the script so
that these are not unnecessarily downloaded.

After the data has been downloaded, sort the downloaded ``.fits`` files into the ``data`` subdirectory of the workdir.
Next, write a ``.json`` listfile containing the filenames of the downloaded ``.xml`` data products with your text
editor of choice. It should look something like:

.. code-block:: text

   ["DpdMerFinalCatalog__EUC_MER_???-final_catalog-0.xml", "DpdMerFinalCatalog__EUC_MER_???-final_catalog-0.xml", ...]

except with the actual filenames of the downloaded data products. The filename of this ``.json`` listfile can then be
passed to the ``mer_final_catalog_listfile`` input argument.

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
SupplementaryInformation element. For this test, these details include the ratio of the number of stars with SEDs to
the required number.

Example
-------

Prepare the required input data in the desired workdir. This will require downloading the PHZ output, VIS calibrated
frames, and MER final catalog data for a selected observation.

The program can then be run with the following command in an EDEN 3.0 environment:

.. code:: bash

    E-Run SHE_Validation 9.1 SHE_Validation_ValidateSedExist --workdir $WORKDIR --phz_catalog_listfile $PHZ_LISTFILE
    --vis_calibrated_frame_listfile $VCF_LISTFILE --mer_final_catalog_listfile $MFC_LISTFILE
    --she_validation_test_results_product she_validation_test_results_product.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variables ``$PHZ_LISTFILE``,
``$VCF_LISTFILE`` and ``$MFC_LISTFILE`` correspond to the filenames of the prepared listfiles and downloaded products
for each input port.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can
be opened with your text editor of choice to view the validation test results.
