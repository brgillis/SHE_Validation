Overview
========

.. contents::

This repository contains code used to run PF-SHE's validation tests.


Software identification
-----------------------

-  Processing Element Name: PF-SHE
-  Project Name: SHE\_Validation
-  Profile: develop
-  Version: 8.2 (17/11/2021)


Contributors
------------

Active Contributors
~~~~~~~~~~~~~~~~~~~

-  Bryan Gillis (b.gillis@roe.ac.uk)

Other Contributors
~~~~~~~~~~~~~~~~~~

-  Rob Blake (rpb@roe.ac.uk)

Purpose
-------

This repository provides code to run OU-SHE's required validation tests. The ``SHE_Validation`` module contains common code and programs for this purpose, and other modules contain code for specific validation tests and programs to perform those tests.

The common programs in the ``SHE_Validation`` module are used to process data to output useful intermediate data products which can be more readily processed by programs provided in other modules to perform validation tests. These latter programs all output one or more DpdSheValidationTestResults data products, which detail the results of the tests performed and optionally contain supplementary figures and textfiles.

Relevant Documents
------------------

-  `RSD <link%20here>`__
-  `SDD <link%20here>`__
-  `VP/STS <link%20here>`__
-  `STP/STR <link%20here>`__
