.. _SHE_Validation_CalcCommonValData:

SHE_Validation_CalcCommonValData
================================

Multiple PF-SHE Validation tests rely on the same data, such as parameters used to bin objects: S/N, colour, size, sky background level, etc. It is most convenient and efficient to calculate these in a single executable tasked for that purpose, rather than in each test individually. This executable serves that purpose, calculating all data which is used by multiple tests and passing it on to them.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_CalcCommonValData`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_CalcCommonValData --workdir <dir> --vis_calibrated_frame_listfile <filename> --mer_final_catalog_listfile <filename> --she_validated_measurements_product <filename> --extended_catalog <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>]

with the arguments and options as defined in the following sections:


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
   * - ``--vis_calibrated_frame_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdVisCalibratedFrame <https://euclid.esac.esa.int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html>`__, containing VIS science images for each exposure in an observation.
     - yes
     - N/A
   * - ``--mer_final_catalog_listfile <filename>``
     - ``.json`` listfile pointing to ``.xml`` data products of type `DpdMerFinalCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html>`__, containing MER object catalogs for all tiles overlapping an observation.
     - yes
     - N/A
   * - ``--she_validated_measurements_product <filename>``
     - ``.xml`` data product of type `DpdSheMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_measurements.html>`__, containing shear estimates of all detected objects in an observation.
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
   * - ``--extended_catalog <filename>``
     - Desired filename of output ``.xml`` data product of type DpdMerFinalCatalog, containing a catalog of all objects in the observation, with all columns from the MER object catalogs plus extra columns for calculated data.
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


Inputs
------

``vis_calibrated_frame_listfile``:

**Description:** The filename of a ``.json`` listfile which contains the filenames of 1-4 ``.xml`` data products of type `DpdVisCalibratedFrame <https://euclid.esac.esa.int/dm/dpdd/latest/visdpd/dpcards/vis_calibratedframe.html>`__ in the workdir, corresponding to each exposure of the observation being analysed. This data product contains the science images made available by PF-VIS, containing the following data relevant to PF-SHE:

* Science images
* Masks
* Noise maps
* Background maps
* Weight maps
* WCS solutions

See the data product information linked above for a detailed description of the data product.

This information is stored in multiple Multi-HDU ``.fits`` files associated with each data product, which must be stored in the ``data`` subdirectory of the workdir.

**Source:** The DpdVisCalibratedFrame data products and their associated ``.fits`` files may be downloaded through the EAS, using a desired DataSetRelease and ObservationId to specify which ones. The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script ``get_all_vis_products.sh`` to aid in the download of these products - see that project's documentation for details on this script. This script can be used to download the desired products to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   OBS_ID=$OBS_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_vis_products.sh

where ``$WORKDIR`` is the workdir and ``$OBS_ID`` is the ObservationId of the desired data (e.g. 10351). Note that this script will download both the DpdVisCalibratedFrame and DpdVisStackedFrame data products. If the latter isn't needed, you can comment out this code within the script so that it is not unnecessarily downloaded.

After the data has been downloaded, sort the downloaded ``.fits`` data products into the ``data`` subdirectory of the workdir. Next, write a ``.json`` listfile containing the filenames of the downloaded ``.xml`` data products with your text editor of choice. It should look something like:

.. code-block:: text

   ["DpdCalibratedFrame1.xml","DpdCalibratedFrame2.xml","DpdCalibratedFrame3.xml","DpdCalibratedFrame4.xml"]

except with the actual filenames of the downloaded data products. The filename of this ``.json`` listfile can then be passed to the ``vis_calibrated_frame_listfile`` input argument.

``mer_final_catalog_listfile``:

**Description:** The filename of a ``.json`` listfile which contains the filenames of 1-12 ``.xml`` data products of type `DpdMerFinalCatalog <https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_finalcatalog.html>`__  in the workdir, corresponding to catalogs for each tile which overlaps the observation being analysed. This data product contains the object detections catalogue provided by MER, containing the following information relevant to PF-SHE:

* Object ID assignments
* Object positions
* Object fluxes in various filters
* Object segmentation map ID
* Object segmentation map size

See the data product information linked above for a detailed description of the data product.

This information is stored in one ``.fits`` file associated with each data product, which must be stored in the ``data`` subdirectory of the workdir.

**Source:** The DpdMerFinalCatalog data products and their associated ``.fits`` files may be downloaded through the EAS, using a desired DataSetRelease and multiple TileIndex values to specify which ones. These TileIndex values should correspond to the tiles which overlap the observation being analysed. These are most easily determined through using the online EAS viewer available at https://eas-dps-cus.test.euclid.astro.rug.nl/ to query for DpdMerFinalCatalog products whose ObservationIdList contains the ID of this observation, and which match the DataSetRelease in use.

The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script ``get_all_mer_products.sh`` to aid in the download of these products - see that project's documentation for details on this script. This script can be used to download the desired products to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   TILE_ID=$TILE_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_mer_products.sh

where ``$WORKDIR`` is the workdir and ``$TILE_ID`` is the TileIndex of each overlapping tile (e.g. 90346, repeat for the TileIndex of each overlapping tile). Note that this script will download both the DpdMerFinalCatalog and DpdMerSegmentationMap data products. If the latter aren't needed, you can comment out this code within the script so that these are not unnecessarily downloaded.

After the data has been downloaded, sort the downloaded ``.fits`` data products into the ``data`` subdirectory of the workdir. Next, write a ``.json`` listfile containing the filenames of the downloaded ``.xml`` data products with your text editor of choice. It should look something like:

.. code-block:: text

   ["DpdMerFinalCatalog__EUC_MER_???-final_catalog-0.xml", "DpdMerFinalCatalog__EUC_MER_???-final_catalog-0.xml", ...]

except with the actual filenames of the downloaded data products. The filename of this ``.json`` listfile can then be passed to the ``mer_final_catalog_listfile`` input argument.

``she_validated_measurements_product``:

**Description:** The filename of a ``.xml`` data product of type `DpdSheMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_measurements.html>`__  in the workdir, containing catalogs of shear estimates and related data for all objects in the observation from each shear estimation algorithm. This includes the following information:

* Object ID (which can be matched to the Object ID in MER Final Catalogs)
* Flags indicating the status of the fit (bits indicating possible reasons for fitting failure or warnings)
* Best-fit object positions
* Object shear estimates and errors
* Object size estimates and errors
* Object signal-to-noise estimates

See the data product information linked above for a detailed description of the data product.

This information is stored in multiple ``.fits`` files (one for each shear estimation algorithm) associated with each data product, which must be stored in the ``data`` subdirectory of the workdir.

**Source:** A DpdSheMeasurements data product and its associated ``.fits`` files may be downloaded through the EAS, using a desired DataSetRelease and ObservationId to specify which one. The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script ``get_all_she_products.sh`` to aid in the download of these products - see that project's documentation for details on this script. This script can be used to download the desired product to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   OBS_ID=$OBS_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_she_products.sh

where ``$WORKDIR`` is the workdir and ``$OBS_ID`` is the ObservationId of the desired data (e.g. 10351). Note that this script will download both the DpdSheMeasurements and DpdSheLensMcChains data products. If the latter isn't needed, you can comment out this code within the script so that it is not unnecessarily downloaded.

After the data has been downloaded, sort the downloaded ``.fits`` data products into the ``data`` subdirectory of the workdir. The filename of the downloaded ``.xml`` data product can then be passed to the ``she_validated_measurements_product`` input argument.

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

``extended_catalog``:

**Description:** Desired filename of output ``.xml`` data product of type DpdMerFinalCatalog, containing a catalog of all objects in the observation, with all columns from the MER object catalogs plus extra columns for calculated data.

**Details:** The generated data product will be of type DpdMerFinalCatalog (though see note in the paragraph below), which is detailed in full on the DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer\_finalcatalog.html. This product provides the filename of a generated ``.fits`` data table in the attribute Data.DataContainer.FileName. This filename is generated to be fully-compliant with Euclid file naming standards. You can easily get this filename from the product with a command such as ``grep \.fits extended_catalog.xml`` (assuming the output data product is named ``extended_catalog.xml``; substitute as necessary).

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


Example
-------

Download the required input data into the desired workdir. The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_CalcCommonValData --workdir $WORKDIR  --vis_calibrated_frame_listfile $VCF_LISTFILE --mer_final_catalog_listfile $MFC_LISTFILE --she_validated_measurements_product $SVM_PRODUCT --extended_catalog extended_catalog.xml

where the variable ``$$WORKDIR`` corresponds to the path to your workdir and the variables  ``$VCF_LISTFILE``, ``$MFC_LISTFILE``, and ``$SVM_PRODUCT`` correspond to the filenames of the prepared listfiles and downloaded products for each input port.

This command will generate a new data product with the filename ``extended_catalog.xml``. This will point to a fits data table, the name of which you can find in the product either by manual inspection or through a command such as ``grep \.fits extended_catalog.xml``. This table can be opened either through a utility such as TOPCAT or a package such as astropy. The final few columns of the table will contain the newly-added, calculated data.
