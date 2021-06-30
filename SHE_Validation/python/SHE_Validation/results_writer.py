""" @file results_writer.py

    Created 17 December 2020

    (Base) classes for writing out results of validation tests
"""

__updated__ = "2021-06-30"

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from copy import deepcopy
import os
from typing import List, Union, Dict, Any, Callable

from SHE_PPT.file_io import get_allowed_filename
from SHE_PPT.logging import getLogger

from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
from ST_DataModelBindings.sys.dss_stub import dataContainer

from . import __version__
from .test_info import RequirementInfo, TestCaseInfo


logger = getLogger(__name__)

# Define constants for various messages

RESULT_PASS = "PASSED"
RESULT_FAIL = "FAILED"

COMMENT_LEVEL_INFO = "INFO"
COMMENT_LEVEL_WARNING = "WARNING"
COMMENT_MULTIPLE = "Multiple notes; see SupplementaryInformation."

INFO_MULTIPLE = COMMENT_LEVEL_INFO + ": " + COMMENT_MULTIPLE

WARNING_TEST_NOT_RUN = "WARNING: Test not run."
WARNING_MULTIPLE = COMMENT_LEVEL_WARNING + ": " + COMMENT_MULTIPLE
WARNING_BAD_DATA = "WARNING: Bad data; see SupplementaryInformation"

KEY_REASON = "REASON"
KEY_INFO = "INFO"

DESC_NOT_RUN_REASON = "Why the test was not run."
DESC_INFO = "Information about the results of the test."

MSG_BAD_DATA = "Test failed due to NaN results for measured parameter."
MSG_NO_DATA = "No data is available for this test."
MSG_NOT_IMPLEMENTED = "This test has not yet been implemented."
MSG_NO_INFO = "No supplementary information available."


class SupplementaryInfo():
    """ Data class for supplementary info for a test case.
    """

    def __init__(self,
                 key: str = KEY_INFO,
                 description: str = DESC_INFO,
                 message: str = MSG_NO_INFO):
        self._key = key
        self._description = description
        self._message = message

    @property
    def key(self):
        return self._key

    @property
    def description(self):
        return self._description

    @property
    def message(self):
        return self._message


class RequirementWriter():
    """ Class for managing reporting of results for a single test case.
    """

    _parent_test_case_writer = None
    _requirement_object = None
    _requirement_info = None

    def __init__(self,
                 parent_test_case_writer: "TestCaseWriter",
                 requirement_object,
                 requirement_info: RequirementInfo):

        self._parent_test_case_writer = parent_test_case_writer
        self._requirement_object = requirement_object
        self._requirement_info = requirement_info

    @property
    def requirement_object(self):
        return self._requirement_object

    @property
    def requirement_info(self):
        return self._requirement_info

    def add_supplementary_info(self,
                               l_supplementary_info: Union[SupplementaryInfo, List[SupplementaryInfo]] = None):
        """ Fills out supplementary information in the data model object for one or more items,
            modifying self._requirement_object.
        """

        # Silently coerce single item into list
        if isinstance(l_supplementary_info, SupplementaryInfo):
            l_supplementary_info = [l_supplementary_info]
        # Use defaults if None provided
        elif l_supplementary_info is None:
            l_supplementary_info = [SupplementaryInfo()]

        base_supplementary_info_parameter = self.requirement_object.SupplementaryInformation.Parameter[0]

        l_supplementary_info_parameter = [None] * len(l_supplementary_info)
        for i, supplementary_info in enumerate(l_supplementary_info):
            supplementary_info_parameter = deepcopy(base_supplementary_info_parameter)

            supplementary_info_parameter.Key = supplementary_info.key
            supplementary_info_parameter.Description = supplementary_info.description
            supplementary_info_parameter.StringValue = supplementary_info.message

            l_supplementary_info_parameter[i] = supplementary_info_parameter

        self.requirement_object.SupplementaryInformation.Parameter = l_supplementary_info_parameter

    def report_bad_data(self,
                        l_supplementary_info: Union[SupplementaryInfo, List[SupplementaryInfo]] = None):
        """ Reports bad data in the data model object for one or more items, modifying self._requirement_object.
        """

        # Report -1 as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = -1.0

        self.requirement_object.Comment = WARNING_BAD_DATA

        # Add a supplementary info key for each of the slope and intercept, reporting details
        self.add_supplementary_info(l_supplementary_info=l_supplementary_info)

    def report_good_data(self,
                         measured_value: float = -99.,
                         warning: bool = False,
                         l_supplementary_info: Union[SupplementaryInfo, List[SupplementaryInfo]] = None):
        """ Reports good data in the data model object for one or more items, modifying self._requirement_object.
        """

        # Report the maximum slope_z as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = measured_value

        # If the slope passes but the intercept doesn't, we should raise a warning
        if warning:
            comment_level = COMMENT_LEVEL_WARNING
        else:
            comment_level = COMMENT_LEVEL_INFO

        self.requirement_object.Comment = f"{comment_level}: " + COMMENT_MULTIPLE

        # Add supplementary info
        self.add_supplementary_info(l_supplementary_info=l_supplementary_info)

    def report_test_not_run(self,
                            reason: str = "Unspecified reason."):
        """ Fills in the data model with the fact that a test was not run and the reason.
        """

        self.requirement_object.MeasuredValue[0].Parameter = WARNING_TEST_NOT_RUN
        self.requirement_object.ValidationResult = RESULT_PASS
        self.requirement_object.Comment = WARNING_TEST_NOT_RUN

        supplementary_info_parameter = self.requirement_object.SupplementaryInformation.Parameter[0]
        supplementary_info_parameter.Key = KEY_REASON
        supplementary_info_parameter.Description = DESC_NOT_RUN_REASON
        supplementary_info_parameter.StringValue = reason

    def write(self,
              result: str = RESULT_PASS,
              report_method: Callable[[Any], None] = None,
              report_kwargs: Dict[str, Any] = None) -> str:
        """ Reports data in the data model object for one or more items, modifying self._requirement_object.

            report_method is called as report_method(self, *args, **kwargs) to handle the data reporting.
        """

        # Default to report good data method
        if report_method is None:
            report_method = self.report_good_data

        # Default to empty dict for report_kwargs
        if report_kwargs is None:
            report_kwargs = {}

        # Report the result
        self.requirement_object.Id = self.requirement_info.id
        self.requirement_object.ValidationResult = result
        self.requirement_object.MeasuredValue[0].Parameter = self.requirement_info.parameter
        report_method(**report_kwargs)

        return result


class AnalysisWriter():
    """ Class for managing writing of analysis data for a single test case
    """

    _parent_test_case_writer = None
    _analysis_object = None
    _l_requirement_info = None
    _qualified_textfiles_filename = None
    _qualified_figures_filename = None

    def __init__(self,
                 parent_test_case_writer: "TestCaseWriter",
                 product_type="UNKNOWN-TYPE"):

        # Get info from parent
        self._parent_test_case_writer = parent_test_case_writer
        self._workdir = self._parent_test_case_writer.workdir
        self._analysis_object = self._parent_test_case_writer.analysis_object

        # Determine appropriate filenames
        textfiles_filename = get_allowed_filename(type_name=product_type,
                                                  instance_id="TEXTFILES",
                                                  extension=".tar.gz",
                                                  version=__version__)
        self._qualified_textfiles_filename = os.path.join(self.workdir, textfiles_filename)
        self.analysis_object.TextFiles.FileName = textfiles_filename

        figures_filename = get_allowed_filename(type_name=product_type,
                                                instance_id="FIGURES",
                                                extension=".tar.gz",
                                                version=__version__)
        self._qualified_figures_filename = os.path.join(self.workdir, figures_filename)
        self.analysis_object.Figures.FileName = textfiles_filename

    @property
    def analysis_object(self):
        return self._analysis_object

    @property
    def requirement_info(self):
        return self._l_requirement_info

    @property
    def workdir(self):
        return self._workdir

    @property
    def qualified_textfiles_filename(self):
        return self._qualified_textfiles_filename

    @property
    def qualified_figures_filename(self):
        return self._qualified_figures_filename

    def write(self,
              write_dummy_files=True) -> str:
        """ Writes analysis data in the data model object for one or more items, modifying self._analysis_object and
            writing files to disk, which the data model object will point to.
        """

        if write_dummy_files:
            os.makedirs(os.path.split(self.qualified_textfiles_filename)[0], exist_ok=True)
            with open(self.qualified_textfiles_filename, "w") as fo:
                fo.write("Dummy data")
            with open(self.qualified_figures_filename, "w") as fo:
                fo.write("Dummy data")


class TestCaseWriter():
    """ Base class to handle the writing out of validation test results for an individual test case.
    """

    _parent_validation_writer = None
    _test_case_object = None
    _test_case_info = None
    _l_requirement_writers = None
    _l_requirement_objects = None
    _analysis_writer = None
    _analysis_object = None
    _workdir = None

    def __init__(self,
                 parent_validation_writer: "ValidationWriter",
                 test_case_object,
                 test_case_info: TestCaseInfo,
                 num_requirements: int = None,
                 l_requirement_info: Union[RequirementInfo, List[RequirementInfo]] = None):

        if (num_requirements is None) == (l_requirement_info is None):
            raise ValueError("Exactly one of num_requirements or l_requirement_info must be provided " +
                             "to TestCaseWriter().")

        # Get attributes from parent
        self._parent_validation_writer = parent_validation_writer
        self._workdir = self._parent_validation_writer.workdir

        # Get attributes from arguments
        self._test_case_object = test_case_object
        self._test_case_info = test_case_info

        # Init l_requirement_writers etc. always as lists
        base_requirement_object = test_case_object.ValidatedRequirements.Requirement[0]
        analysis_object = test_case_object.AnalysisResult.AnalysisFiles

        if isinstance(l_requirement_info, RequirementInfo):
            # Init writer using the pre-existing requirement object in the product
            requirement_object = base_requirement_object
            self._l_requirement_writers = [self._init_requirement_writer(requirement_object=requirement_object,
                                                                         requirement_info=l_requirement_info)]
            self._l_requirement_objects = [requirement_object]

        else:

            if l_requirement_info is not None:
                num_requirements = len(l_requirement_info)

            self._l_requirement_writers = [None] * num_requirements
            self._l_requirement_objects = [None] * num_requirements

            for i, requirement_info in enumerate(l_requirement_info):

                requirement_object = deepcopy(base_requirement_object)
                self.l_requirement_objects[i] = requirement_object
                self.l_requirement_writers[i] = self._init_requirement_writer(requirement_object=requirement_object,
                                                                              requirement_info=requirement_info)

            test_case_object.ValidatedRequirements.Requirement = self.l_requirement_objects

        analysis_textfiles_object = dataContainer(filestatus="PROPOSED")
        analysis_object.TextFiles = analysis_textfiles_object

        analysis_figures_object = dataContainer(filestatus="PROPOSED")
        analysis_object.Figures = analysis_figures_object

        self._analysis_object = analysis_object
        self._analysis_writer = self._init_analysis_writer()

    @property
    def test_case_object(self):
        return self._test_case_object

    @property
    def test_case_info(self):
        return self._test_case_info

    @property
    def workdir(self):
        return self._workdir

    @property
    def l_requirement_writers(self):
        return self._l_requirement_writers

    @property
    def l_requirement_objects(self):
        return self._l_requirement_objects

    @property
    def analysis_writer(self):
        return self._analysis_writer

    @property
    def analysis_object(self):
        return self._analysis_object

    def _init_requirement_writer(self, **kwargs):
        """ Method to initialize a requirement writer, which we use to allow inherited classes to override this.
        """
        return RequirementWriter(self, **kwargs)

    def _init_analysis_writer(self, **kwargs):
        """ Method to initialize an analysis writer, which we use to allow inherited classes to override this.
        """
        return AnalysisWriter(self, **kwargs)

    def write_meta(self):
        """ Fill in metadata about the test case, modifying self._test_case_object.
        """
        self.test_case_object.TestId = self.test_case_info.id
        self.test_case_object.TestDescription = self.test_case_info.description

    def write_requirement_objects(self, **kwargs):
        """ Writes all data for each requirement subobject, modifying self._test_case_object.
        """
        all_requirements_pass = True
        for requirement_writer in self.l_requirement_writers:
            requirement_result = requirement_writer.write(**kwargs)
            all_requirements_pass = all_requirements_pass and (requirement_result == RESULT_PASS)

        if all_requirements_pass:
            self.test_case_object.GlobalResult = RESULT_PASS
        else:
            self.test_case_object.GlobalResult = RESULT_FAIL

        self.global_result = self.test_case_object.GlobalResult

    def write_analysis_files(self, **kwargs):
        """ Method to write any desired analysis files. Subclasses may override this with a method
            which writes out desired files, or leave this empty if no files need to be written.
        """

        # Write the global result, using what was determined for writing requirements
        if self.global_result is None:
            raise ValueError("self.global_results is not set when self.write_analysis_files method is called.")
        self.test_case_object.AnalysisResult.Result = self.global_result

        self.analysis_writer.write(**kwargs)

    def write(self, requirements_kwargs=None, analysis_kwargs=None):
        """ Fills in metadata of the test case object and writes all data for each requirement subobject, modifying
            self._test_case_object.
        """

        # Replace default None args with empty dicts
        if requirements_kwargs is None:
            requirements_kwargs = {}
        if analysis_kwargs is None:
            analysis_kwargs = {}

        self.write_meta()
        self.write_requirement_objects(**requirements_kwargs)

        # Write out analysis information
        self.write_analysis_files(**analysis_kwargs)


class ValidationResultsWriter():
    """ Base class to handle the writing out of validation test results.
    """

    _test_object = None
    _l_test_case_writers = None
    _l_test_case_objects = None
    _workdir = None

    def __init__(self,
                 test_object: dpdSheValidationTestResults,
                 workdir: str,
                 num_test_cases: int = 1,
                 l_test_case_info: Union[TestCaseInfo, List[TestCaseInfo]] = None):

        if (num_test_cases is None) == (l_test_case_info is None):
            raise ValueError("Exactly one of num_test_cases or l_test_case_info must be provided " +
                             "to ValidationResultsWriter().")

        self._test_object = test_object
        self._workdir = workdir

        base_test_case_object = self.test_object.Data.ValidationTestList[0]

        # Init l_test_case_writers always as a list

        if isinstance(l_test_case_info, TestCaseInfo):
            l_test_case_info = [l_test_case_info]

        elif l_test_case_info is not None:
            num_test_cases = len(l_test_case_info)

        else:
            l_test_case_info = [None] * num_test_cases

        # Initialise test case objects and writers
        self._l_test_case_objects = [None] * num_test_cases
        self._l_test_case_writers = [None] * num_test_cases

        for i, test_case_info in enumerate(l_test_case_info):

            test_case_object = deepcopy(base_test_case_object)
            self.l_test_case_writers[i] = self._init_test_case_writer(test_case_object=test_case_object,
                                                                      test_case_info=test_case_info)

            self.l_test_case_objects[i] = test_case_object

        self.test_object.Data.ValidationTestList = self.l_test_case_objects

    @property
    def test_object(self):
        return self._test_object

    @property
    def workdir(self):
        return self._workdir

    @property
    def l_test_case_writers(self):
        return self._l_test_case_writers

    @property
    def l_test_case_objects(self):
        return self._l_test_case_objects

    def _init_test_case_writer(self, **kwargs) -> TestCaseWriter:
        """ Method to initialize a test case writer, which we use to allow inherited classes to override this.
        """
        return TestCaseWriter(self, **kwargs)

    def add_test_case_writer(self,
                             test_case_writer: TestCaseWriter):
        self._l_test_case_writers.append(test_case_writer)
        self.l_test_case_objects.append(test_case_writer.test_case_object)

    def write_meta(self):
        """ Fill in metadata about the test, modifying self._test_object.
        """
        pass

    def write_test_case_objects(self):
        """ Writes all data for each requirement subobject, modifying self._test_object.
        """
        for test_case_writer in self.l_test_case_writers:
            test_case_writer.write()

    def write(self):
        """ Fills in metadata of the validaiton test results object and writes all data for each test case to the
            validation test results object, self._test_object.
        """
        self.write_meta()
        self.write_test_case_objects()
