CMAKE_MINIMUM_REQUIRED(VERSION 2.8.12)

#===============================================================================
# Load elements_subdir macro here
# Examples:
#   For declaring a project module:
#         elements_subdir(ElementsExamples)
#===============================================================================
elements_subdir(SHE_Validation_DataQuality)

#===============================================================================
# Load elements_depends_on_subdirs macro here
#   For creating a dependency onto an other accessible module
#         elements_depends_on_subdirs(ElementsKernel)
#===============================================================================
elements_depends_on_subdirs(ElementsKernel)

#===============================================================================
# Add the find_package macro (a pure CMake command) here to locate the
# libraries.
# Examples:
#          find_package(CppUnit)
#===============================================================================

#===============================================================================
# Declare the library dependencies here
# Example:
#         elements_add_library(ElementsExamples src/Lib/*.cpp
#                     INCLUDE_DIRS Boost ElementsKernel
#                     LINK_LIBRARIES Boost ElementsKernel
#                     PUBLIC_HEADERS ElementsExamples)
#===============================================================================

#===============================================================================
# Declare the executables here
# Example:
# elements_add_executable(ElementsProgramExample src/Program/ProgramExample.cpp
#                        INCLUDE_DIRS Boost ElementsExamples
#                        LINK_LIBRARIES Boost ElementsExamples)
#===============================================================================

#===============================================================================
# Declare the Boost tests here
# Example:
# elements_add_unit_test(BoostClassExample tests/src/Boost/ClassExample_test.cpp
#                       EXECUTABLE BoostClassExample_test
#                       INCLUDE_DIRS ElementsExamples
#                       LINK_LIBRARIES ElementsExamples TYPE Boost)
#===============================================================================

#===============================================================================
# Use the following macro for python modules, scripts and aux files:
#  elements_install_python_modules()
#  elements_install_scripts()
#===============================================================================
elements_install_python_modules()

#===============================================================================
# Declare the Python programs here
# Examples :
# elements_add_python_program(PythonProgramExample
#                             ElementsExamples.PythonProgramExample)
#===============================================================================
elements_add_python_program(SHE_Validation_ValidateGalInfo SHE_Validation_DataQuality.ValidateGalInfo)
elements_add_python_program(SHE_Validation_ValidateDataProc SHE_Validation_DataQuality.ValidateDataProc)
elements_add_python_program(SHE_Validation_ValidateSedExist SHE_Validation_DataQuality.ValidateSedExist)

#===============================================================================
# Add the elements_install_conf_files macro
# Examples:
#          elements_install_conf_files()
#===============================================================================
elements_install_conf_files()
