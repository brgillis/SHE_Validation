# Declare this directory as an Elements module
elements_subdir(SHE_Validation_PSF)

# Declare Elements module dependencies
elements_depends_on_subdirs(ElementsKernel)

# Instruction for Python module installation
elements_install_python_modules()

# Instruction for creating a Python executable
elements_add_python_program(SHE_Validation_ValidatePSFResStarPos SHE_Validation_PSF.ValidatePSFResStarPos)
elements_add_python_program(SHE_Validation_ValidatePSFResInterp SHE_Validation_PSF.ValidatePSFResInterp)
elements_add_python_program(SHE_Validation_ValidatePSFModelErr SHE_Validation_PSF.ValidatePSFModelErr)
elements_add_python_program(SHE_Validation_ValidatePSFLambda SHE_Validation_PSF.ValidatePSFLambda)

# Install the configuration files
# elements_install_conf_files()
elements_install_conf_files()

# Install the auxiliary files
# elements_install_aux_files()
