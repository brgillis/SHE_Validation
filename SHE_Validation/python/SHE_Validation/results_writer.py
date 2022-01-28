""" @file results_writer.py

    Created 17 December 2020

    (Base) classes for writing out results of validation tests
"""

__updated__ = "2021-08-27"

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

import os
from copy import deepcopy
from typing import Any, Callable, Dict, IO, List, Optional, Sequence, Set, Union

import numpy as np
import scipy.stats

from SHE_PPT import file_io
from SHE_PPT.logging import getLogger
from SHE_PPT.pipeline_utility import ConfigKeys, ValidationConfigKeys
from SHE_PPT.product_utility import coerce_no_include_data_subdir
from SHE_PPT.utility import any_is_inf_or_nan, coerce_to_list
from ST_DataModelBindings.dpd.she.validationtestresults_stub import dpdSheValidationTestResults
from ST_DataModelBindings.sys.dss_stub import dataContainer
from . import __version__
from .constants.default_config import DEFAULT_BIN_LIMITS, ExecutionMode, FailSigmaScaling
from .constants.test_info import BinParameters, RequirementInfo, TestCaseInfo

# Set up a custom type definition for when either a dict or list is accepted
StrDictOrList = Union[Dict[str, str], List[str]]

logger = getLogger(__name__)

# Constants related to writing directory files

DEFAULT_DIRECTORY_FILENAME: str = "SheAnalysisResultsDirectory.txt"
DEFAULT_DIRECTORY_HEADER: str = "### OU-SHE Analysis Results File Directory ###"
TEXTFILES_SECTION_HEADER: str = "# Textfiles:"
FIGURES_SECTION_HEADER: str = "# Figures:"
DIRECTORY_KEY: str = "Directory"

# Define constants for various messages

RESULT_PASS: str = "PASSED"
RESULT_FAIL: str = "FAILED"

COMMENT_LEVEL_INFO: str = "INFO"
COMMENT_LEVEL_WARNING: str = "WARNING"
COMMENT_MULTIPLE: str = "Multiple notes; see SupplementaryInformation."

INFO_MULTIPLE: str = f"{COMMENT_LEVEL_INFO}: {COMMENT_MULTIPLE}"

WARNING_TEST_NOT_RUN: str = "WARNING: Test not run."
WARNING_MULTIPLE: str = f"{COMMENT_LEVEL_WARNING}: {COMMENT_MULTIPLE}"
WARNING_BAD_DATA: str = "WARNING: Bad data; see SupplementaryInformation"

KEY_REASON: str = "REASON"
KEY_INFO: str = "INFO"

DESC_NOT_RUN_REASON: str = "Why the test was not run."
DESC_INFO: str = "Information about the results of the test."

MSG_BAD_DATA: str = "Test failed due to NaN results for measured parameter."
MSG_NO_DATA: str = "No data is available for this test."
MSG_NOT_IMPLEMENTED: str = "This test has not yet been implemented."
MSG_NO_INFO: str = "No supplementary information available."

MEASURED_VAL_BAD_DATA = 1e99


# Utility functions


def check_test_pass(val: float, val_err: float, val_z: float, val_target: float) -> bool:
    """ Check if a given test has good data and passes.
    """
    if ((val_err == 0.) or
            (any_is_inf_or_nan([val, val_err])) or
            (val_z > val_target)):
        return False
    return True


def check_test_pass_if_data(val: float, val_err: float, val_z: float, val_target: float,
                            good_data: bool) -> bool:
    """ Check if a test either doesn't have good data, or does and passes.
    """
    if not good_data:
        return True
    return check_test_pass(val, val_err, val_z, val_target)


def get_result_string(test_pass: bool):
    """ Get the appropriate result string depending on if the test passed.
    """
    if test_pass:
        return RESULT_PASS
    return RESULT_FAIL


# Classes

class FailSigmaCalculator:
    """Class to calculate the fail sigma, scaling properly for number of bins and/or/nor test cases.
    """

    # Attributes set from args at init
    global_fail_sigma: float
    local_fail_sigma = float
    fail_sigma_scaling: FailSigmaScaling
    mode: ExecutionMode = ExecutionMode.LOCAL
    s_test_case_info: Set[TestCaseInfo]

    # Attributes determined at init
    bin_parameters: List[BinParameters]
    num_test_cases: int = 1
    num_test_case_bins: int = 1
    d_num_bins: Dict
    num_test_case_bin_parameters_bins: int

    # Attributes determined on demand
    _d_scaled_global_sigma: Optional[Dict[str, float]] = None
    _d_scaled_local_sigma: Optional[Dict[str, float]] = None

    def __init__(self,
                 pipeline_config: Dict[ConfigKeys, Any],
                 l_test_case_info: List[TestCaseInfo],
                 d_l_bin_limits: Dict[BinParameters, np.ndarray] = None,
                 mode: ExecutionMode = ExecutionMode.LOCAL, ):

        # Set attributes directly from args
        self.global_fail_sigma = pipeline_config[ValidationConfigKeys.VAL_GLOBAL_FAIL_SIGMA]
        self.local_fail_sigma = pipeline_config[ValidationConfigKeys.VAL_LOCAL_FAIL_SIGMA]
        self.fail_sigma_scaling = pipeline_config[ValidationConfigKeys.VAL_FAIL_SIGMA_SCALING]
        self.mode = mode
        self.s_test_case_info = set(l_test_case_info)

        # Get a set of all bin parameters in the test cases
        s_bin_parameters: Set[BinParameters] = set()
        for test_case_info in self.s_test_case_info:
            s_bin_parameters.add(test_case_info.bins)

        # Create a default list of bin limits if necessary
        if d_l_bin_limits is None:
            d_l_bin_limits = {}
            for bin_parameter in s_bin_parameters:
                d_l_bin_limits[bin_parameter] = DEFAULT_BIN_LIMITS

        # Calculate the number of bins for each test case, and in total

        self.d_num_bins = {}

        bin_parameter: BinParameters
        for bin_parameter in s_bin_parameters:
            self.d_num_bins[bin_parameter] = len(d_l_bin_limits[bin_parameter]) - 1

        self.num_test_cases = len(self.s_test_case_info)
        self.num_test_case_bins = 0

        test_case_info: TestCaseInfo
        for test_case_info in self.s_test_case_info:
            bin_parameter: BinParameters = test_case_info.bins
            self.num_test_case_bins += self.d_num_bins[bin_parameter]

    @property
    def d_scaled_global_sigma(self) -> Dict[str, float]:
        if self._d_scaled_global_sigma is None:
            self._d_scaled_global_sigma = self._calc_d_scaled_sigma(self.global_fail_sigma)
        return self._d_scaled_global_sigma

    @property
    def d_scaled_local_sigma(self) -> Dict[str, float]:
        if self._d_scaled_local_sigma is None:
            self._d_scaled_local_sigma = self._calc_d_scaled_sigma(self.local_fail_sigma)
        return self._d_scaled_local_sigma

    @property
    def d_scaled_sigma(self) -> Dict[str, float]:
        if self.mode == ExecutionMode.LOCAL:
            return self.d_scaled_local_sigma
        return self.d_scaled_global_sigma

    def _calc_d_scaled_sigma(self, base_sigma: float) -> Dict[str, float]:

        d_scaled_sigma: Dict[str, float] = {}

        test_case_info: TestCaseInfo
        for test_case_info in self.s_test_case_info:

            # Get the number of tries depending on scaling type
            num_tries: int
            if self.fail_sigma_scaling == FailSigmaScaling.NONE:
                num_tries = 1
            elif self.fail_sigma_scaling == FailSigmaScaling.BINS:
                num_tries = self.d_num_bins[test_case_info.bins]
            elif self.fail_sigma_scaling == FailSigmaScaling.TEST_CASES:
                num_tries = self.num_test_cases
            elif self.fail_sigma_scaling == FailSigmaScaling.TEST_CASE_BINS:
                num_tries = self.num_test_case_bins
            else:
                raise ValueError(f"Unexpected fail sigma scaling: {self.fail_sigma_scaling}")

            d_scaled_sigma[test_case_info.name] = self._calc_scaled_sigma_from_tries(base_sigma = base_sigma,
                                                                                     num_tries = num_tries)

        return d_scaled_sigma

    @classmethod
    def _calc_scaled_sigma_from_tries(cls,
                                      base_sigma: float,
                                      num_tries: int) -> float:
        # To avoid numeric error, don't calculate if num_tries==1
        if num_tries == 1:
            return base_sigma

        p_good: float = (1 - 2 * scipy.stats.norm.cdf(-base_sigma))
        return -scipy.stats.norm.ppf((1 - p_good ** (1 / num_tries)) / 2)


class SupplementaryInfo:
    """ Data class for supplementary info for a test case.
    """

    # Attrs set at init
    _key: str = KEY_INFO
    _description: str = DESC_INFO
    _message: str = MSG_NO_INFO

    def __init__(self,
                 key: str = KEY_INFO,
                 description: str = DESC_INFO,
                 message: str = MSG_NO_INFO):
        self._key = key
        self._description = description
        self._message = message

    # Getters/setters for attrs set at init
    @property
    def key(self) -> str:
        return self._key

    @property
    def description(self) -> str:
        return self._description

    @property
    def message(self) -> str:
        return self._message


class RequirementWriter:
    """ Class for managing reporting of results for a single test case.
    """

    # Attrs set at init
    _parent_test_case_writer: Optional["TestCaseWriter"] = None
    _requirement_object: Optional[Any] = None
    _requirement_info: Optional[RequirementInfo] = None

    def __init__(self,
                 parent_test_case_writer: Optional["TestCaseWriter"] = None,
                 requirement_object = None,
                 requirement_info: RequirementInfo = None):

        self._parent_test_case_writer = parent_test_case_writer
        self._requirement_object = requirement_object
        self._requirement_info = requirement_info

    # Getters/setters for attrs set at init
    @property
    def requirement_object(self) -> Optional[Any]:
        return self._requirement_object

    @property
    def requirement_info(self) -> Optional[RequirementInfo]:
        return self._requirement_info

    # Public methods
    def add_supplementary_info(self,
                               l_supplementary_info: Union[None, SupplementaryInfo, Sequence[SupplementaryInfo]] = None
                               ) -> None:
        """ Fills out supplementary information in the data model object for one or more items,
            modifying self._requirement_object.
        """

        # Silently coerce single item into list
        l_supplementary_info = coerce_to_list(l_supplementary_info, keep_none = True)

        # Use defaults if None provided
        if l_supplementary_info is None:
            l_supplementary_info = [SupplementaryInfo()]

        base_supplementary_info_parameter: Any = self.requirement_object.SupplementaryInformation.Parameter[0]

        l_supplementary_info_parameter: List[str] = [""] * len(l_supplementary_info)

        i: int
        supplementary_info: SupplementaryInfo
        for i, supplementary_info in enumerate(l_supplementary_info):
            supplementary_info_parameter: Any = deepcopy(base_supplementary_info_parameter)

            supplementary_info_parameter.Key = supplementary_info.key
            supplementary_info_parameter.Description = supplementary_info.description
            supplementary_info_parameter.StringValue = supplementary_info.message

            l_supplementary_info_parameter[i] = supplementary_info_parameter

        self.requirement_object.SupplementaryInformation.Parameter = l_supplementary_info_parameter

    def report_bad_data(self,
                        l_supplementary_info: Union[None, SupplementaryInfo, Sequence[SupplementaryInfo]] = None
                        ) -> None:
        """ Reports bad data in the data model object for one or more items, modifying self._requirement_object.
        """

        # Report the special value as the measured value for this test
        self.requirement_object.MeasuredValue[0].Value.FloatValue = MEASURED_VAL_BAD_DATA

        self.requirement_object.Comment = WARNING_BAD_DATA

        # Add a supplementary info key for each of the slope and intercept, reporting details
        self.add_supplementary_info(l_supplementary_info = l_supplementary_info)

    def report_good_data(self,
                         measured_value: float = -99.,
                         warning: bool = False,
                         l_supplementary_info: Union[None, SupplementaryInfo, Sequence[SupplementaryInfo]] = None
                         ) -> None:
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
        self.add_supplementary_info(l_supplementary_info = l_supplementary_info)

    def report_test_not_run(self,
                            reason: str = "Unspecified reason."
                            ) -> None:
        """ Fills in the data model with the fact that a test was not run and the reason.
        """

        self.requirement_object.MeasuredValue[0].Parameter = WARNING_TEST_NOT_RUN
        self.requirement_object.MeasuredValue[0].Value.FloatValue = MEASURED_VAL_BAD_DATA
        self.requirement_object.ValidationResult = RESULT_PASS
        self.requirement_object.Comment = WARNING_TEST_NOT_RUN

        supplementary_info_parameter: Any = self.requirement_object.SupplementaryInformation.Parameter[0]
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


class AnalysisWriter:
    """ Class for managing writing of analysis data for a single test case
    """

    # Attributes set at init
    _parent_test_case_writer: Optional["TestCaseWriter"] = None
    _product_type: str = "UNKNOWN-TYPE"
    _dl_l_textfiles: Optional[StrDictOrList] = None
    _dl_l_figures: Optional[StrDictOrList] = None
    filename_tag: Optional[str] = None

    # Attributes determined at init
    _workdir: str
    _analysis_object: Any

    # Attributes set when requested
    _textfiles_filename: Optional[str] = None
    _qualified_textfiles_filename: Optional[str] = None
    _figures_filename: Optional[str] = None
    _qualified_figures_filename: Optional[str] = None

    # Attributes set when write is called
    _directory_filename: Optional[str] = None
    _qualified_directory_filename: Optional[str] = None

    def __init__(self,
                 parent_test_case_writer: "TestCaseWriter" = None,
                 product_type: str = "UNKNOWN-TYPE",
                 dl_l_textfiles: Optional[StrDictOrList] = None,
                 dl_l_figures: Optional[StrDictOrList] = None,
                 filename_tag: Optional[str] = None):

        # Set attrs from kwargs
        self._product_type = product_type
        if dl_l_textfiles is not None:
            self._dl_l_textfiles = dl_l_textfiles
        else:
            self._dl_l_textfiles = []
        if dl_l_figures is not None:
            self._dl_l_figures = dl_l_figures
        else:
            self._dl_l_figures = []
        if filename_tag is not None:
            self.filename_tag = filename_tag

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

    @property
    def dl_l_textfiles(self):
        return self._dl_l_textfiles

    @property
    def dl_l_figures(self):
        return self._dl_l_figures

    # Getters/setters for attributes set when requested
    @property
    def textfiles_filename(self) -> str:
        if self._textfiles_filename is None:
            instance_id_tail: str
            if self.filename_tag is None:
                instance_id = ""
            else:
                instance_id = f"{self.filename_tag.upper()}"

            self._textfiles_filename = file_io.get_allowed_filename(type_name = self.product_type + "-TEXTFILES",
                                                                    instance_id = instance_id_tail,
                                                                    extension = ".tar.gz",
                                                                    version = __version__)
        return self._textfiles_filename

    @property
    def qualified_textfiles_filename(self) -> str:
        if self._qualified_textfiles_filename is None:
            if self.workdir is not None:
                self._qualified_textfiles_filename = os.path.join(self.workdir, self.textfiles_filename)
            else:
                raise ValueError("Qualified textfile filename cannot be determined when workdir is None.")
        return self._qualified_textfiles_filename

    @property
    def figures_filename(self) -> str:
        if self._figures_filename is None:
            if self.filename_tag is None:
                instance_id = ""
            else:
                instance_id = f"{self.filename_tag.upper()}"

            self._textfiles_filename = file_io.get_allowed_filename(type_name = self.product_type + "-FIGURES",
                                                                    instance_id = instance_id_tail,
                                                                    extension = ".tar.gz",
                                                                    version = __version__)
        return self._figures_filename

    @property
    def qualified_figures_filename(self) -> str:
        if self._qualified_figures_filename is None:
            if self.workdir is not None:
                self._qualified_figures_filename = os.path.join(self.workdir, self.figures_filename)
            else:
                raise ValueError("Qualified figures filename cannot be determined when workdir is None.")
        return self._qualified_figures_filename

    @property
    def directory_filename(self) -> Optional[str]:
        return self._directory_filename

    @directory_filename.setter
    def directory_filename(self, directory_filename: Optional[str]):

        # Unset _qualified_directory_filename
        self._qualified_directory_filename = None

        self._directory_filename = directory_filename

    @property
    def qualified_directory_filename(self) -> Optional[str]:
        if self.directory_filename is None:
            return None
        if self._qualified_directory_filename is None:
            if self.workdir is not None:
                self._qualified_directory_filename = os.path.join(self.workdir, self.directory_filename)
            else:
                raise ValueError("Qualified directory filename cannot be determined when workdir is None.")
        return self._qualified_directory_filename

    # Private and protected methods

    def _generate_directory_filename(self) -> None:
        """ Overridable method to generate a filename for a directory file.
        """
        self.directory_filename = DEFAULT_DIRECTORY_FILENAME

    def _get_directory_header(self) -> str:
        """ Overridable method to get the desired header for a directory file.
        """
        return DEFAULT_DIRECTORY_HEADER

    @staticmethod
    def _write_filenames_to_directory(fo: IO,
                                      filenames: Optional[StrDictOrList]) -> None:
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

    def _write_directory(self,
                         dl_l_textfiles: Optional[StrDictOrList],
                         dl_l_figures: Optional[StrDictOrList]) -> None:

        # Generate a filename for the directory if needed
        if self._directory_filename is None:
            self._generate_directory_filename()

        # Write out the directory file
        with open(self.qualified_directory_filename, "w") as fo:

            # Write the header using the possible-overloaded method self._get_directory_header()
            fo.write(f"{self._get_directory_header()}\n")

            # Write a comment for the start of the textfiles section, then write out the textfile filenames
            fo.write(f"{TEXTFILES_SECTION_HEADER}\n")
            self._write_filenames_to_directory(fo, dl_l_textfiles)

            # Write a comment for the start of the figures section, then write out the figure filenames
            fo.write(f"{FIGURES_SECTION_HEADER}\n")
            self._write_filenames_to_directory(fo, dl_l_figures)

    def _add_directory_to_textfiles(self, dl_l_textfiles: Optional[StrDictOrList]) -> None:
        """ Adds the directory filename to a dict or list of textfiles.
        """

        if isinstance(dl_l_textfiles, dict):
            dl_l_textfiles[DIRECTORY_KEY] = self.directory_filename
        else:
            dl_l_textfiles.append(self.directory_filename)

    @staticmethod
    def _write_dummy_data(qualified_filename: str) -> None:
        """ Write dummy data to a file.
        """
        with open(qualified_filename, "w") as fo:
            fo.write("Dummy data")

    def _tar_files(self,
                   tarball_filename: str,
                   filenames: Optional[StrDictOrList],
                   delete_files: bool = False) -> None:
        """ Tar the set of files in {files} into the tarball {qualified_filename}. Optionally delete these files
            afterwards.
        """

        # Get a list of the files
        if isinstance(filenames, dict):
            l_filenames = list(filenames.values())
        else:
            l_filenames = filenames

        # Prune any Nones from the list
        l_filenames = [filename for filename in l_filenames if filename is not None]

        if len(l_filenames) == 0:
            return

        # Tar the files into the desired tarball
        file_io.tar_files(tarball_filename = tarball_filename,
                          l_filenames = l_filenames,
                          workdir = self.workdir,
                          delete_files = delete_files)

    def _write_files(self,
                     files: Optional[StrDictOrList],
                     tarball_filename: str,
                     data_container_attr: str,
                     write_dummy_files: bool = False,
                     delete_files: bool = False) -> None:
        """ Tar a set of files and update the data product with the filename of the tarball. Optionally delete
            files now included in the tarball.
        """

        # Check if we will be creating a file we want to point the data product to
        if len(files) > 0 or write_dummy_files:
            getattr(self.analysis_object, data_container_attr).FileName = coerce_no_include_data_subdir(
                tarball_filename)
            if len(files) == 0:
                self._write_dummy_data(os.path.join(self.workdir, tarball_filename))
            else:
                self._tar_files(tarball_filename = tarball_filename,
                                filenames = files,
                                delete_files = delete_files)
        else:
            # No file for the data product, so set the attribute to None
            setattr(self.analysis_object, data_container_attr, None)

    # Public methods

    def write(self,
              write_directory: bool = True,
              write_dummy_files: bool = False,
              delete_files: bool = True) -> None:
        """ Writes analysis data in the data model object for one or more items, modifying self._analysis_object and
            writing files to disk, which the data model object will point to.
        """

        # Create a directory if desired
        if write_directory and len(self.dl_l_textfiles) + len(self.dl_l_figures) > 0:
            self._write_directory(self.dl_l_textfiles, self.dl_l_figures)
            self._add_directory_to_textfiles(self.dl_l_textfiles)

        # Write out textfiles and figures
        self._write_files(files = self.dl_l_textfiles,
                          tarball_filename = self.textfiles_filename,
                          data_container_attr = "TextFiles",
                          write_dummy_files = write_dummy_files,
                          delete_files = delete_files)

        self._write_files(files = self.dl_l_figures,
                          tarball_filename = self.figures_filename,
                          data_container_attr = "Figures",
                          write_dummy_files = write_dummy_files,
                          delete_files = delete_files)


class TestCaseWriter:
    """ Base class to handle the writing out of validation test results for an individual test case.
    """

    # Types of child objects, which can be overridden by derived classes
    requirement_writer_type = RequirementWriter
    analysis_writer_type = AnalysisWriter

    # Attributes set from kwargs at init
    _parent_val_results_writer: Optional["ValidationResultsWriter"] = None
    _test_case_object: Optional[Any] = None
    _test_case_info: Optional[TestCaseInfo] = None
    _l_requirement_writers: Optional[List[Optional[RequirementWriter]]] = None
    _l_requirement_objects: Optional[List[Any]] = None

    # Attributes determined at init
    _analysis_writer: Optional[AnalysisWriter] = None
    _analysis_object: Optional[Any] = None
    _workdir: Optional[str] = None

    # Attributes set when writing
    global_result: Optional[str] = None

    def _init_analysis_object(self,
                              analysis_object: Any,
                              dl_l_textfiles,
                              dl_l_figures):

        analysis_textfiles_object: Any = dataContainer(filestatus = "PROPOSED")
        analysis_object.TextFiles = analysis_textfiles_object

        analysis_figures_object: Any = dataContainer(filestatus = "PROPOSED")
        analysis_object.Figures = analysis_figures_object

        self._analysis_object = analysis_object
        filename_tag = self.test_case_info.name.upper().replace("SHE-", "").replace("CTI-GAL", "").replace("CTI-PSF",
                                                                                                           "")
        self._analysis_writer = self._make_analysis_writer(dl_l_textfiles = dl_l_textfiles,
                                                           dl_l_figures = dl_l_figures,
                                                           filename_tag = filename_tag)

    def __init__(self,
                 parent_val_results_writer: Optional["ValidationResultsWriter"] = None,
                 test_case_object: Optional[Any] = None,
                 test_case_info: TestCaseInfo = None,
                 num_requirements: int = None,
                 l_requirement_info: Union[None, RequirementInfo, List[RequirementInfo]] = None,
                 dl_l_textfiles: Optional[StrDictOrList] = None,
                 dl_l_figures: Optional[StrDictOrList] = None):

        if (num_requirements is None) == (l_requirement_info is None):
            raise ValueError("Exactly one of num_requirements or l_requirement_info must be provided " +
                             "to TestCaseWriter().")

        # Get attributes from parent
        self._parent_val_results_writer = parent_val_results_writer
        if self.parent_val_results_writer is not None:
            self._workdir = self.parent_val_results_writer.workdir
        else:
            logger.debug("TestCaseWriter.parent_val_results_writer not set at init - attrs will need to be set " +
                         "manually.")

        # Get attributes from arguments
        self._test_case_object = test_case_object
        self._test_case_info = test_case_info

        # Init l_requirement_writers etc. always as lists
        base_requirement_object: Any = test_case_object.ValidatedRequirements.Requirement[0]
        analysis_object: Any = test_case_object.AnalysisResult.AnalysisFiles

        if isinstance(l_requirement_info, RequirementInfo):
            # Init writer using the pre-existing requirement object in the product
            requirement_object: Any = base_requirement_object
            self._l_requirement_writers = [self._make_requirement_writer(requirement_object = requirement_object,
                                                                         requirement_info = l_requirement_info)]
            self._l_requirement_objects = [requirement_object]

        else:

            if l_requirement_info is not None:
                num_requirements = len(l_requirement_info)

            self._l_requirement_writers = [None] * num_requirements
            self._l_requirement_objects = [None] * num_requirements

            for i in range(num_requirements):

                requirement_info: Optional[RequirementInfo] = None
                if l_requirement_info:
                    requirement_info: RequirementInfo = l_requirement_info[i]

                requirement_object = deepcopy(base_requirement_object)
                self.l_requirement_objects[i] = requirement_object
                self.l_requirement_writers[i] = self._make_requirement_writer(requirement_object = requirement_object,
                                                                              requirement_info = requirement_info)

            test_case_object.ValidatedRequirements.Requirement = self.l_requirement_objects

        # Set up the Analysis Writer
        self._init_analysis_object(analysis_object,
                                   dl_l_textfiles,
                                   dl_l_figures)

    # Getters/setters for attributes set at init
    @property
    def parent_val_results_writer(self) -> Optional["ValidationResultsWriter"]:
        return self._parent_val_results_writer

    @property
    def test_case_object(self) -> Any:
        return self._test_case_object

    @property
    def test_case_info(self) -> Optional[TestCaseInfo]:
        return self._test_case_info

    @property
    def workdir(self) -> Optional[str]:
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: Optional[str]):
        self._workdir = workdir

    @property
    def l_requirement_writers(self) -> List[RequirementWriter]:
        return self._l_requirement_writers

    @property
    def l_requirement_objects(self) -> List[Any]:
        return self._l_requirement_objects

    @property
    def analysis_writer(self) -> Optional[AnalysisWriter]:
        return self._analysis_writer

    @property
    def analysis_object(self) -> Any:
        return self._analysis_object

    # Private and protected methods
    def _make_requirement_writer(self, **kwargs) -> RequirementWriter:
        """ Method to initialize a requirement writer, which we use to allow inherited classes to override this
            in case they need to alter the kwargs in any way..
        """
        return self.requirement_writer_type(self, **kwargs)

    def _make_analysis_writer(self, **kwargs) -> AnalysisWriter:
        """ Method to initialize an analysis writer, which we use to allow inherited classes to override this
            in case they need to alter the kwargs in any way..
        """
        return self.analysis_writer_type(self,
                                         **kwargs)

    # Public methods
    def write_meta(self) -> None:
        """ Fill in metadata about the test case, modifying self._test_case_object.
        """
        self.test_case_object.TestId = self.test_case_info.id
        self.test_case_object.TestDescription = self.test_case_info.description

    def write_requirement_objects(self, **kwargs) -> None:
        """ Writes all data for each requirement subobject, modifying self._test_case_object.
        """
        all_requirements_pass = True
        requirement_writer: RequirementWriter
        for requirement_writer in self.l_requirement_writers:
            requirement_result = requirement_writer.write(**kwargs)
            all_requirements_pass = all_requirements_pass and (requirement_result == RESULT_PASS)

        if all_requirements_pass:
            self.test_case_object.GlobalResult = RESULT_PASS
        else:
            self.test_case_object.GlobalResult = RESULT_FAIL

        self.global_result = self.test_case_object.GlobalResult

    def write_analysis_files(self, **kwargs) -> None:
        """ Method to write any desired analysis files. Subclasses may override this with a method
            which writes out desired files, or leave this empty if no files need to be written.
        """

        # Write the global result, using what was determined for writing requirements
        if self.global_result is None:
            raise ValueError("self.global_results is not set when self.write_analysis_files method is called.")
        self.test_case_object.AnalysisResult.Result = self.global_result

        self.analysis_writer.write(**kwargs)

    def write(self, requirements_kwargs = None, analysis_kwargs = None) -> None:
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


class ValidationResultsWriter:
    """ Base class to handle the writing out of validation test results.
    """

    # Types of child classes, which can be overridden by derived classes
    test_case_writer_type = TestCaseWriter

    # Attributes set at init from arguments
    _test_object: dpdSheValidationTestResults
    _workdir: str
    dl_l_textfiles: Optional[StrDictOrList] = None
    dl_l_figures: Optional[StrDictOrList] = None
    num_test_cases: Optional[int] = None
    l_test_case_info: Optional[List[Optional[TestCaseInfo]]] = None
    dl_num_requirements: Union[None, Dict[str, int], List[int]] = None
    dl_l_requirement_info: Union[None, Dict[str, int], List[int]] = None
    _dl_l_textfiles: Optional[StrDictOrList] = None
    _dl_l_figures: Optional[StrDictOrList] = None

    # Attributes determined at init
    _l_test_case_writers: List[Optional[TestCaseWriter]]
    _l_test_case_objects: List[Any]
    test_case_keys: List[str]

    def __init__(self,
                 test_object: dpdSheValidationTestResults,
                 workdir: str,
                 dl_l_textfiles: Optional[StrDictOrList] = None,
                 dl_l_figures: Optional[StrDictOrList] = None,
                 num_test_cases: Optional[int] = None,
                 l_test_case_info: Union[None, TestCaseInfo, List[TestCaseInfo]] = None,
                 dl_num_requirements: Union[None, Dict[str, int], List[int]] = None,
                 dl_l_requirement_info: Union[None, Dict[str, List[RequirementInfo]],
                                              List[List[RequirementInfo]]] = None) -> None:

        # Init attributes directly from arguments
        self.dl_l_textfiles = dl_l_textfiles
        self.dl_l_figures = dl_l_figures
        self.num_test_cases = num_test_cases
        self.l_test_case_info = coerce_to_list(l_test_case_info, keep_none = True)
        self.dl_num_requirements = dl_num_requirements
        self.dl_l_requirement_info = dl_l_requirement_info
        self._test_object = test_object
        self._workdir = workdir

        # Check validity of input args and process them to calculate derivative values

        self._check_test_case_input()
        self._check_requirements_input()

        self._process_test_case_input()
        self._process_requirements_input()

        # Initialise test case objects and writers
        self._l_test_case_objects = [None] * self.num_test_cases
        self._l_test_case_writers = [None] * self.num_test_cases

        base_test_case_object = self.test_object.Data.ValidationTestList[0]

        for i, test_case_info in enumerate(self.l_test_case_info):
            self._init_test_case_writer(test_case_info = test_case_info,
                                        i = i,
                                        base_test_case_object = base_test_case_object, )

        self.test_object.Data.ValidationTestList = self.l_test_case_objects

    # Getters/setters for attrs set at init
    @property
    def test_object(self) -> Any:
        return self._test_object

    @property
    def workdir(self) -> str:
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: str):
        self._workdir = workdir

    @property
    def l_test_case_writers(self) -> List[TestCaseWriter]:
        return self._l_test_case_writers

    @property
    def l_test_case_objects(self) -> List[Any]:
        return self._l_test_case_objects

    # Private methods - used when initialized

    def _check_test_case_input(self) -> None:
        """ Checks that input related to test cases is valid.
        """

        if (self.num_test_cases is None) == (self.l_test_case_info is None):
            raise ValueError("Exactly one of num_test_cases or l_test_case_info must be provided "
                             "to ValidationResultsWriter().")

    def _check_requirements_input(self) -> None:
        """ Checks that input related to requirements is valid.
        """

        if self.dl_num_requirements and self.dl_l_requirement_info:
            raise ValueError("Only one of dl_num_requirements and dl_l_requirement_info may be "
                             "provided to ValidationResultsWriter.")

        # If we're using default values for requirements, we can return here
        if not self.dl_num_requirements or not self.dl_l_requirement_info:
            return

        # Check that the format is consistent with test case input
        if self.num_test_cases and not (isinstance(self.dl_num_requirements, list) and
                                        isinstance(self.dl_l_requirement_info, list)):
            raise ValueError("If num_test_cases is provided, dl_num_requirements and dl_l_requirement_info must be "
                             "provided as lists.")
        if self.l_test_case_info and not (isinstance(self.dl_num_requirements, list) and
                                          isinstance(self.dl_l_requirement_info, list)):
            raise ValueError("If l_test_case_info is provided, dl_num_requirements and dl_l_requirement_info must be "
                             "provided as dicts.")

    def _process_test_case_input(self) -> None:
        """ Determines all necessary data related to test cases.
        """

        # Align l_test_case_info and num_test_cases based on which was supplied
        if self.l_test_case_info:
            self.num_test_cases = len(self.l_test_case_info)
            self.test_case_keys = [test_case_info.name for test_case_info in self.l_test_case_info]
        else:
            self.l_test_case_info = [None] * self.num_test_cases
            self.test_case_keys = list(range(self.num_test_cases))

    def _init_like(self, a: Union[Dict[Any, Any], List[Any]]) -> Union[Dict[Any, Any], List[Any]]:
        """ Creates a dict or list like the passed dict or list, ready to assign elements by key/index.
        """

        b: Union[Dict[Any, Any], List[Any]]
        if isinstance(a, list):
            b = [None] * self.num_test_cases
        else:
            b = {}
        return b

    def _process_requirements_input(self) -> None:
        """ Determines all necessary data related to requirements.
        """

        if (self.dl_num_requirements is None) and (self.dl_l_requirement_info is None):
            # Assume one requirement if no info provided
            if self.l_test_case_info:
                self.dl_num_requirements = {}
                for test_case in self.test_case_keys:
                    self.dl_num_requirements[test_case] = 1
            else:
                self.dl_num_requirements = [1] * self.num_test_cases

        # Align dl_l_requirement_info and dl_num_requirements based on which was provided
        if self.dl_l_requirement_info:
            self.dl_num_requirements = self._init_like(self.dl_l_requirement_info)
        else:
            self.dl_l_requirement_info = self._init_like(self.dl_num_requirements)

    @staticmethod
    def _get_item_from_dl(dl: Optional[StrDictOrList],
                          key: Union[Any, int]) -> Any:
        """ Get an item out of a list or dictionary depending on the type. If not found, returns None instead of
            raising an exception
        """

        if not dl:
            return None

        item = None
        try:
            item = dl[key]
        except (IndexError, KeyError):
            pass
        return item

    def _init_test_case_writer(self,
                               test_case_info: TestCaseInfo,
                               i: int,
                               base_test_case_object: Any,
                               ) -> None:
        """ Initializes a single test case object and writer.
        """

        # Get the proper textfiles and figures for this test case
        key = self.test_case_keys[i]
        test_case_textfiles = self._get_item_from_dl(self.dl_l_textfiles, key)
        test_case_figures = self._get_item_from_dl(self.dl_l_figures, key)
        num_requirements = self._get_item_from_dl(self.dl_num_requirements, key)
        l_requirement_info = self._get_item_from_dl(self.dl_l_requirement_info, key)

        # Create a test case writer and keep it in the list of writers
        test_case_object = deepcopy(base_test_case_object)
        self.l_test_case_writers[i] = self._make_test_case_writer(test_case_object = test_case_object,
                                                                  test_case_info = test_case_info,
                                                                  dl_l_textfiles = test_case_textfiles,
                                                                  dl_l_figures = test_case_figures,
                                                                  num_requirements = num_requirements,
                                                                  l_requirement_info = l_requirement_info)
        self.l_test_case_objects[i] = test_case_object

    def _make_test_case_writer(self, **kwargs) -> TestCaseWriter:
        """ Method to initialize a test case writer, which we use to allow inherited classes to override this,
            in case they need to change the kwargs in any way.
        """
        return self.test_case_writer_type(self, **kwargs)

    # Public methods
    def add_test_case_writer(self,
                             test_case_writer: TestCaseWriter) -> None:
        self._l_test_case_writers.append(test_case_writer)
        self.l_test_case_objects.append(test_case_writer.test_case_object)

    def write_meta(self) -> None:
        """ Fill in metadata about the test, modifying self._test_object.
        """
        pass

    def write_test_case_objects(self) -> None:
        """ Writes all data for each requirement subobject, modifying self._test_object.
        """
        for test_case_writer in self.l_test_case_writers:
            test_case_writer.write()

    def write(self) -> None:
        """ Fills in metadata of the validation test results object and writes all data for each test case to the
            validation test results object, self._test_object.
        """
        self.write_meta()
        self.write_test_case_objects()
