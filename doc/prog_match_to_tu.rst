.. _SHE_Validation_MatchToTU:

SHE_Validation_MatchToTU
========================

Multiple PF-SHE Validation tests benefit from relating detected objects to the true source objects in PF-SIM's True Universe catalogs, and this is useful for manual analysis as well to assess the performance of shear estimation algorithms.

The Euclid pipeline does not maintain a direct link between true source objects and detected objects, due to a couple of reasons: Firstly, in production, the former will not be available to PF-MER, and so runs on simulations also proceed without this information. Secondly: It is non-trivial to relate the two, given that some sources may be undetected, some sources may be fragmented into multiple detections, and some detections might be spurious and not relate to any source.

This program implements a match between true sources and detected objects, attempting to optimally balance these issues to generate the best possible match. This is done through requiring that all matches are symmetric best matches (i.e. ``A[i]`` matches ``B[j]`` from the other catalog if and only if ``A[i]`` is the closest source to ``B[j]`` and ``B[j]`` is the closest source to ``A[i]``) and that the separation between the matches is below a given threshold.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_MatchToTU`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_MatchToTU --workdir <dir> --she_validated_measurements_product <filename> --tu_output_product <filename> --matched_catalog <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>] [--match_threshold <value>]

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
   * - ``--she_validated_measurements_product <filename>``
     - ``.xml`` data product of type `DpdSheMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_measurements.html>`__, containing shear estimates of all detected objects in an observation.
     - yes
     - N/A
   * - ``--tu_output_product <filename>``
     - ``.xml`` data product of type `DpdTrueUniverseOutput <https://euclid.esac.esa.int/dm/dpdd/latest/simdpd/tu/dpcards/sim_trueuniverseoutput.html>`__, containing PF-SIM's True Universe galaxy and star catalogs for an observation.
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
   * - ``--matched_catalog <filename>``
     - Desired filename of output ``.xml`` data product of type DpdSheValidatedMeasurements, containing matched catalogs with both shear estimate information and true universe input information.
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
   * - ``--match_threshold <value>``
     - Maximum distance in arcsec between a true universe source object and a detected object for an allowable match.
     - no
     - ``0.3`` arcsec


Inputs
------

``she_validated_measurements_product``:

**Description:** The filename of a ``.xml`` data product of type `DpdSheMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_measurements.html>`__  in the workdir, containing catalogs of shear estimates and related data for all objects in the observation from each shear estimation algorithm. This includes the following information:

* Object ID (which can be matched to the Object ID in MER Final Catalogs)
* Flags indicating the status of the fit (bits indicating possible reasons for fitting failure or warnings)
* Best-fit object positions
* Object shear estimates and errors
* Object size estimates and errors
* Object signal-to-noise estimates

See the data product information linked above for a detailed description of the data product.

This information is stored in multiple ``.fits`` files (one for each shear estimation algorithm) associated with the data product, which must be stored in the ``data`` subdirectory of the workdir.

**Source:** A DpdSheMeasurements data product and its associated ``.fits`` files may be downloaded through the EAS, using a desired DataSetRelease and ObservationId to specify which one. The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script ``get_all_she_products.sh`` to aid in the download of these products - see that project's documentation for details on this script. This script can be used to download the desired product to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   OBS_ID=$OBS_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_she_products.sh

where ``$WORKDIR`` is the workdir and ``$OBS_ID`` is the ObservationId of the desired data (e.g. 10351). Note that this script will download both the DpdSheMeasurements and DpdSheLensMcChains data products. If the latter isn't needed, you can comment out this code within the script so that it is not unnecessarily downloaded.

After the data has been downloaded, sort the downloaded ``.fits`` files into the ``data`` subdirectory of the workdir. The filename of the downloaded ``.xml`` data product can then be passed to the ``she_validated_measurements_product`` input argument.

``tu_output_product``:

**Description:** The filename of a ``.xml`` data product of type `DpdTrueUniverseOutput <https://euclid.esac.esa.int/dm/dpdd/latest/simdpd/tu/dpcards/sim_trueuniverseoutput.html>`__  in the workdir, containing catalogs of true input information for galaxies and stars. This includes the following information on galaxies relevant to PF-SHE:

* True apparent position on the sky (accounting for shift due to magnification)
* Inclination angle relative to line-of-sight
* Intrinsic position angle of the galaxy
* Morphological information of the galaxy (e.g. bulge fraction, bulge size, disk size, etc.)
* Shear and magnification values applied to the galaxy image

See the data product information linked above for a detailed description of the data product.

This information is stored in multiple ``.fits`` files (one for the galaxy catalog and one for the star catalog) associated with the data product, which must be stored in the ``data`` subdirectory of the workdir.

**Source:** A DpdTrueUniverseOutput data product and its associated ``.fits`` files may be downloaded through the EAS, using a desired DataSetRelease and EuclidPointingId (same as the ObservationId attribute of other data products) to specify which one. The `SHE_IAL_Pipelines project <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__ provides the helper script ``get_all_sim_products.sh`` to aid in the download of these products - see that project's documentation for details on this script. This script can be used to download the desired product to a workdir with a command such as:

.. code-block:: bash

   cd $WORKDIR
   OBS_ID=$OBS_ID $HOME/Work/Projects/SHE_IAL_Pipelines/SHE_Pipeline/scripts/get_all_sim_products.sh

where ``$WORKDIR`` is the workdir and ``$OBS_ID`` is the ObservationId of the desired data (e.g. 10351).

After the data has been downloaded, sort the downloaded ``.fits`` files into the ``data`` subdirectory of the workdir. The filename of the downloaded ``.xml`` data product can then be passed to the ``tu_output_product`` input argument.

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
   `SHE_Pipeline_Run <https://gitlab.euclid-sgs.uk/PF-SHE/SHE_IAL_Pipelines>`__
   helper script, may be created automatically by providing the argument
   ``--config_args ...`` to it (see documentation of that executable for
   further information).


Outputs
-------

``matched_catalog``:

**Description:** Desired filename of output ``.xml`` data product of type DpdSheValidatedMeasurements, containing matched catalogs with both shear estimate information and true universe input information.

**Details:** The generated data product will be of type DpdSheValidatedMeasurements (though see note in the paragraph below), which is detailed in full on the DPDD at https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she\_measurements.html. This product provides the filenames of generated ``.fits`` data tables (one for each shear estimation algorithm) in the attributes Data.<Algorithm>ShearMeasurements.DataStorage.DataContainer.FileName. These filenames are generated to be fully-compliant with Euclid file naming standards. You can easily get these filenames from the product with a command such as ``grep \.fits matched_catalog.xml`` (assuming the output data product is named ``matched_catalog.xml``; substitute as necessary).

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


Example
-------

Download the required input data into the desired workdir. The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_MatchToTU --she_validated_measurements_product $SVM_PRODUCT --tu_output_product $TU_PRODUCT --matched_catalog matched_catalog.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variables  ``$SVM_PRODUCT`` and ``$TU_PRODUCT`` correspond to the filenames of the prepared downloaded products for each input port.

This command will generate a new data product with the filename ``matched_catalog.xml``. This will point to a fits data table for each shear estimation algorithm, the names of which you can find in the product either by manual inspection or through a command such as ``grep \.fits extended_catalog.xml``. These tables can be opened either through a utility such as TOPCAT or a package such as astropy.
