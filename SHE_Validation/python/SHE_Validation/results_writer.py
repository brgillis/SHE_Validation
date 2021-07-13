""" @file results_writer.py

    Created 17 December 2020

    (Base) classes for writing out results of validation tests
"""

__updated__ = "2021-07-13"

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

from SHE_PPT import file_io
from SHE_PPT.logging import getLogger
from future.builtins.misc import isinstance

from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
from ST_DataModelBindings.sys.dss_stub import dataContainer

from . import __version__
from .test_info import RequirementInfo, TestCaseInfo


logger = getLogger(__name__)

# Constants related to writing directory files

DEFAULT_DIRECTORY_FILENAME = "SheAnalysisResultsDirectory.txt"
DEFAULT_DIRECTORY_HEADER = "### OU-SHE Analysis Results File Directory ###"
TEXTFILES_SECTION_HEADER = "# Textfiles:"
FIGURES_SECTION_HEADER = "# Figures:"
DIRECTORY_KEY = "Directory"


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

    # Attrs set at init
    _key = None
    _description = None
    _message = None

    def __init__(self,
                 key: str = KEY_INFO,
                 description: str = DESC_INFO,
                 message: str = MSG_NO_INFO):
        self._key = key
        self._description = description
        self._message = message

    # Getters/setters for attrs set at init
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

    # Attrs set at init
    _parent_test_case_writer = None
    _requirement_object = None
    _requirement_info = None

    def __init__(self,
                 parent_test_case_writer: "TestCaseWriter" = None,
                 requirement_object=None,
                 requirement_info: RequirementInfo = None):

        self._parent_test_case_writer = parent_test_case_writer
        self._requirement_object = requirement_object
        self._requirement_info = requirement_info

    # Getters/setters for attrs set at init
    @property
    def requirement_object(self):
        return self._requirement_object

    @property
    def requirement_info(self):
        return self._requirement_info

    # Public methods
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

    # Attributes set at init
    _parent_test_case_writer = None
    _analysis_object = None
    _product_type = None
    _workdir = None

    # Attributes set when requested
    _textfiles_filename = None
    _qualified_textfiles_filename = None
    _figures_filename = None
    _qualified_figures_filename = None

    # Attributes set when write is called
    _directory_filename = None
    _qualified__directory_filename = None

    def __init__(self,
                 parent_test_case_writer: "TestCaseWriter" = None,
                 product_type="UNKNOWN-TYPE"):

        # Set attrs from command-line
        self._product_type = product_type

        # Get info from parent
        self._parent_test_case_writer = parent_test_case_writer
        if self.parent_test_case_writer is not None:
            self._workdir = self.parent_test_case_writer.workdir
            self._analysis_object = self.parent_test_case_writer.analysis_object
        else:
            logger.debug("AnalysisWriter.parent_test_case_writer not set at init - attrs will need to be set " +
                         "manually.")

    # Getters/setters for attributes set at init
    @property
    def parent_test_case_writer(self):
        return self._parent_test_case_writer

    @property
    def analysis_object(self):
        return self._analysis_object

    @analysis_object.setter
    def analysis_object(self, a):
        self._analysis_object = a

    @property
    def product_type(self):
        return self._product_type

    @property
    def workdir(self):
        return self._workdir

    @workdir.setter
    def workdir(self, a):
        self._workdir = a

    # Getters/setters for attributes set when requested
    @property
    def textfiles_filename(self):
        if self._textfiles_filename is None:
            self._textfiles_filename = file_io.get_allowed_filename(type_name=self.product_type, instance_id="TEXTFILES",
                                                                    extension=".tar.gz",
                                                                    version=__version__)
        return self._textfiles_filename

    @property
    def qualified_textfiles_filename(self):
        if self._qualified_textfiles_filename is None:
            if self.workdir is not None:
                self._qualified_textfiles_filename = os.path.join(self.workdir, self.textfiles_filename)
            else:
                raise ValueError("Qualified textfile filename cannot be determined when workdir is None.")
        return self._qualified_textfiles_filename

    @property
    def figures_filename(self):
        if self._figures_filename is None:
            self._figures_filename = file_io.get_allowed_filename(type_name=self.product_type, instance_id="FIGURES",
                                                                  extension=".tar.gz",
                                                                  version=__version__)
        return self._figures_filename

    @property
    def qualified_figures_filename(self):
        if self._qualified_figures_filename is None:
            if self.workdir is not None:
                self._qualified_figures_filename = os.path.join(self.workdir, self.figures_filename)
            else:
                raise ValueError("Qualified figures filename cannot be determined when workdir is None.")
        return self._qualified_figures_filename

    @property
    def directory_filename(self):
        return self._directory_filename

    @directory_filename.setter
    def directory_filename(self, directory_filename):

        # Unset _qualified_directory_filename
        self._qualified_directory_filename = None

        self._directory_filename = directory_filename

    @property
    def qualified_directory_filename(self):
        if self.directory_filename is None:
            return None
        if self._qualified_directory_filename is None:
            if self.workdir is not None:
                self._qualified_directory_filename = os.path.join(self.workdir, self.directory_filename)
            else:
                raise ValueError("Qualified directory filename cannot be determined when workdir is None.")
        return self._qualified_directory_filename

    # Private and protected methods
    def _generate_directory_filename(self):
        """ Overridable method to generate a filename for a directory file.
        """
        self.directory_filename = DEFAULT_DIRECTORY_FILENAME

    def _get_directory_header(self):
        """ Overridable method to get the desired header for a directory file.
        """
        return DEFAULT_DIRECTORY_HEADER

    def _write_filenames_to_directory(self, fo, filenames):
        """ Write a dict or list of filenames to an open, writable directory file,
            with different functionality depending on if a list or dict is passed.
        """

        if isinstance(filenames, dict):
            # Write out the key for each file and its filename
            for key, filename in filenames.items():
                fo.write(f"{key}: {filename}\n")
        else:
            # Write the string representation of each filename
            for filename in filenames:
                fo.write(f"{filename}\n")

    def _write_directory(self, textfiles, figures):

        # Generate a filename for the directory if needed
        if self._directory_filename is None:
            self._generate_directory_filename()

        # Write out the directory file
        with open(self.qualified_directory_filename, "w") as fo:

            # Write the header using the possible-overloaded method self._get_directory_header()
            fo.write(f"{self._get_directory_header()}\n")

            # Write a comment for the start of the textfiles section, then write out the textfile filenames
            fo.write(f"{TEXTFILES_SECTION_HEADER}\n")
            self._write_filenames_to_directory(fo, textfiles)

            # Write a comment for the start of the figures section, then write out the figure filenames
            fo.write(f"{FIGURES_SECTION_HEADER}\n")
            self._write_filenames_to_directory(fo, figures)

    def _add_directory_to_textfiles(self, textfiles):
        """ Adds the directory filename to a dict or list of textfiles.
        """

        if isinstance(textfiles, dict):
            textfiles[DIRECTORY_KEY] = self.directory_filename
        else:
            textfiles.append(self.directory_filename)

    @staticmethod
    def _write_dummy_data(qualified_filename):
        """ Write dummy data to a file.
        """
        with open(qualified_filename, "w") as fo:
            fo.write("Dummy data")
        return fo

    def _tar_files(self, qualified_tarball_filename, filenames, delete_files):
        """ Tar the set of files in {files} into the tarball {qualified_filename}. Optionally delete these files
            afterwards.
        """

        # Get a list of the files
        if isinstance(filenames, dict):
            l_filenames = list(filenames.values())
        else:
            l_filenames = filenames

        # Get a list of the qualified files to be tarred, and write it in a space-separated string
        l_qualified_filenames = [None] * len(l_filenames)
        for i, filename in enumerate(l_filenames):
            l_qualified_filenames[i] = os.path.join(self.workdir, filename)

        # Tar the files into the desired tarball
        file_io.tar_files(qualified_tarball_filename=qualified_tarball_filename,
                          l_qualified_filenames=l_qualified_filenames,
                          delete_files=delete_files)

    def _write_files(self,
                     files,
                     tarball_filename,
                     qualified_tarball_filename,
                     data_container_attr,
                     write_dummy_files,
                     delete_files):
        """ Tar a set of files and update the data product with the filename of the tarball. Optionally delete
            files now included in the tarball.
        """

        # Check if we will be creating a file we want to point the data product to
        if len(files) > 0 or write_dummy_files:
            getattr(self.analysis_object, data_container_attr).FileName = tarball_filename
            if len(files) == 0:
                self._write_dummy_data(qualified_tarball_filename)
            else:
                self._tar_files(qualified_tarball_filename=qualified_tarball_filename,
                                filenames=files,
                                delete_files=delete_files)
        else:
            # No file for the data product, so set the attribute to None
            setattr(self.analysis_object, data_container_attr, None)

    # Public methods

    def write(self,
              textfiles=None,
              figures=None,
              write_directory=True,
              write_dummy_files=False,
              delete_files=True) -> str:
        """ Writes analysis data in the data model object for one or more items, modifying self._analysis_object and
            writing files to disk, which the data model object will point to.

            'textfiles' and 'figures' should either be None (for no files), lists of filenames, or dicts. A directory
            is written if desired; if dicts are passed, the keys will be written in the directory along with filenames.
        """

        if textfiles is None:
            textfiles = []
        if figures is None:
            figures = []

        # Create a directory if desired
        if write_directory:
            self._write_directory(textfiles, figures)
            self._add_directory_to_textfiles(textfiles)

        # Write out textfiles and figures
        self._write_files(files=textfiles,
                          tarball_filename=self.textfiles_filename,
                          qualified_tarball_filename=self.qualified_textfiles_filename,
                          data_container_attr="TextFiles",
                          write_dummy_files=write_dummy_files,
                          delete_files=delete_files)

        self._write_files(files=figures,
                          tarball_filename=self.figures_filename,
                          qualified_tarball_filename=self.qualified_figures_filename,
                          data_container_attr="Figures",
                          write_dummy_files=write_dummy_files,
                          delete_files=delete_files)


class TestCaseWriter():
    """ Base class to handle the writing out of validation test results for an individual test case.
    """

    # Attributes set at init
    _parent_validation_writer = None
    _test_case_object = None
    _test_case_info = None
    _l_requirement_writers = None
    _l_requirement_objects = None
    _analysis_writer = None
    _analysis_object = None
    _workdir = None

    def __init__(self,
                 parent_validation_writer: "ValidationWriter" = None,
                 test_case_object=None,
                 test_case_info: TestCaseInfo = None,
                 num_requirements: int = None,
                 l_requirement_info: Union[RequirementInfo, List[RequirementInfo]] = None):

        if (num_requirements is None) == (l_requirement_info is None):
            raise ValueError("Exactly one of num_requirements or l_requirement_info must be provided " +
                             "to TestCaseWriter().")

        # Get attributes from parent
        self._parent_validation_writer = parent_validation_writer
        if self.parent_validation_writer is not None:
            self._workdir = self.parent_validation_writer.workdir
        else:
            logger.debug("TestCaseWriter.parent_validation_writer not set at init - attrs will need to be set " +
                         "manually.")

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

    # Getters/setters for attributes set at init
    @property
    def parent_validation_writer(self):
        return self._parent_validation_writer

    @property
    def test_case_object(self):
        return self._test_case_object

    @property
    def test_case_info(self):
        return self._test_case_info

    @property
    def workdir(self):
        return self._workdir

    @workdir.setter
    def workdir(self, a):
        self._workdir = a

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

    # Private methods
    def _init_requirement_writer(self, **kwargs):
        """ Method to initialize a requirement writer, which we use to allow inherited classes to override this.
        """
        return RequirementWriter(self, **kwargs)

    def _init_analysis_writer(self, **kwargs):
        """ Method to initialize an analysis writer, which we use to allow inherited classes to override this.
        """
        return AnalysisWriter(self, **kwargs)

    # Public methods
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

    # Attrs set at init
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

    # Getters/setters for attrs set at init
    @property
    def test_object(self):
        return self._test_object

    @property
    def workdir(self):
        return self._workdir

    @workdir.setter
    def workdir(self, a):
        self._workdir = a

    @property
    def l_test_case_writers(self):
        return self._l_test_case_writers

    @property
    def l_test_case_objects(self):
        return self._l_test_case_objects

    # Private methods
    def _init_test_case_writer(self, **kwargs) -> TestCaseWriter:
        """ Method to initialize a test case writer, which we use to allow inherited classes to override this.
        """
        return TestCaseWriter(self, **kwargs)

    # Public methods
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
