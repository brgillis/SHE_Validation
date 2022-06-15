.. _SHE_Validation_ValidateGlobalShearBias:

SHE_Validation_ValidateGlobalShearBias
======================================

This program performs the Shear Bias validation test, T-SHE-000006-shear-bias, which validates requirement R-SHE-CAL-F-070. This tests checks the multiplicative and additive shear bias are consistent with requirements. It checks this both for all objects, and for various bins of objects.

This program is functionally identical to `SHE_Validation_ValidateShearBias <prog_shear_bias.html>`__, except it takes as input a listfile of input data products instead of a single file, and performs the validation on data for all of these products. This documentation will be limited to the different aspects; please see `SHE_Validation_ValidateShearBias <prog_shear_bias.html>`__'s documentation for further details.


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_ValidateGlobalShearBias`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 9.0 SHE_Validation_ValidateGlobalShearBias --workdir <dir> --matched_catalog_listfile <filename> --she_validation_test_results_product <filename> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>] [--snr_bin_limits "<value> <value> ..."] [--bg_bin_limits "<value> <value> ..."] [--colour_bin_limits "<value> <value> ..."] [--size_bin_limits "<value> <value> ..."] [--epoch_bin_limits "<value> <value> ..."] [--max_g_in <value>] [--bootstrap_errors <value>] [--require_fitclass_zero <value>]

with the following arguments which differ from ``SHE_Validation_ValidateShearBias``:


Input Arguments
~~~~~~~~~~~~~~~

.. list-table::
   :widths: 15 50 10 25
   :header-rows: 1

   * - Argument
     - Description
     - Required
     - Default
   * - ``--matched_catalog_listfile <filename>``
     - ``.json`` listfile pointing to one or more ``.xml`` data products of type `DpdSheValidatedMeasurements <https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she_measurements.html>`__, containing matched catalogs with both shear estimate information and true universe input information.
     - yes
     - N/A


Inputs
------

``matched_catalog_listfile``:

**Description:** ``.json`` listfile pointing to one or more ``.xml`` data product of type DpdSheValidatedMeasurements, containing matched catalogs with both shear estimate information and true universe input information.

**Source:** This is an intermediate data product, not stored in the EAS. The ``.xml`` data products can be generated through use of the `SHE_Validation_MatchToTU program <prog_match_to_tu.html>`__ - See that program's documentation for details. Once multiple of these have been generated, a ``.json`` listfile can be written which points to them, and provided as input to this program.


Example
-------

Prepare the required input data in the desired workdir. This will require downloading the ``vis_calibrated_frame_listfile``, ``tu_output_product``, and ``she_validated_measurements_product`` data for one or more observations, then running the `SHE_Validation_MatchToTU <prog_match_to_tu.html>`__ program for each observation to generate the ``matched_catalog`` data products, and then writing a ``.json`` listfile pointing to these data products.

The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 9.0 SHE_Validation_ValidateGlobalShearBias --workdir $WORKDIR  --matched_catalog_listfile $MC_LISTFILE --she_validation_test_results_product she_validation_test_results_product.xml

where the variable ``$WORKDIR`` corresponds to the path to your workdir and the variable ``$MC_LISTFILE`` corresponds to the filename of the prepared matched catalog product.

This command will generate a new data product with the filename ``she_validation_test_results_product.xml``. This can be opened with your text editor of choice to view the validation test results. This will also point to a tarball of figures of the regression for each test case, the names of which you can find in the product either by manual inspection or through a command such as ``grep \.tar\.gz she_validation_test_results_product.xml``. After extracting the contents of the tarball (e.g. through ``tar -xvf <filename>.tar.gz``), the figures can opened with your image viewer of choice to see the regression results.
