Overview
========

.. contents::

This repository contains code used to run PF-SHE's validation tests.


Software identification
-----------------------

-  Processing Element Name: PF-SHE
-  Project Name: SHE\_Validation
-  Profile: develop
-  Version: 9.0 (14/06/2022)


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

-  `RSD <https://euclid.roe.ac.uk/attachments/download/54815>`__
-  `SDD <https://euclid.roe.ac.uk/attachments/download/54782/EUCL-IFA-DDD-8-002.pdf>`__
-  `VP/STS <https://euclid.roe.ac.uk/attachments/download/54785/EUCL-CEA-PL-8-001_v1.44-Euclid-SGS-SHE-Validation_Plan_STS.pdf>`__
-  `STP/STR <https://euclid.roe.ac.uk/attachments/download/54784/EUCL-IFA-TP-8-002_v1-0-0.pdf>`__
