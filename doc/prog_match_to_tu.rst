.. _SHE_Validation_MatchToTU:

SHE_Validation_MatchToTU
========================

    ``(Optional) a more careful description of what the program does``


Running the Program on EDEN/LODEEN
----------------------------------

To run the ``SHE_Validation_...`` program with Elements, use the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_... --workdir <dir> [--log-file <filename>] [--log-level <value>] [--pipeline_config <filename>]

with the following options:


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
   * - ``--pipeline_config <filename>``
     - ``.xml`` data product or pointing to configuration file (described below), or .json listfile (Cardinality 0-1) either pointing to such a data product, or empty.
     - no
     - None (equivalent to providing an empty listfile)
   * -
     -
     -
     -


Output Arguments
~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 15 50 10 25
   :header-rows: 1

   * - Argument
     - Description
     - Required
     - Default
   * -
     -
     -
     -

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
   * -
     -
     -
     -


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
   * -
     -
     -


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

``cat_pic``:

**Description:** The desired filename of the data product for the output
cat image. The data product will be an ``.xml`` file, so this filename
should end with ``.xml``.

**Details:** The generated data product will be of type DpdSheCatImage,
which is detailed in full on the DPDD at
https://euclid.esac.esa.int/dm/dpdd/latest/shedpd/dpcards/she\_catimage.html.
This product provides the filename of a generated ``.png`` cat image in
the attribute Data.DataContainer.FileName. This filename is generated to
be fully-compliant with Euclid file naming standards. You can easily get
this filename from the product with a command such as
``grep \.png cat_pic.xml``.


Example
-------

Download the required input data into the desired workdir, which we will call ``$WORKDIR``. The program can then be run with the following command in an EDEN 2.1 environment:

.. code:: bash

    E-Run SHE_Validation 8.2 SHE_Validation_... --workdir $WORKDIR

This command will...
