# Declare this directory as an Elements module
elements_subdir(SHE_Validation_CTI)

# Declare Elements module dependencies
elements_depends_on_subdirs(ElementsKernel SHE_Validation)

# Instruction for Python module installation
elements_install_python_modules()

# Instruction for creating a Python executable
# elements_add_python_program(...)
elements_add_python_program(SHE_Validation_ValidateCTIGal SHE_Validation_CTI.ValidateCTIGal)
elements_add_python_program(SHE_Validation_ValidateCTIPSF SHE_Validation_CTI.ValidateCTIPSF)

# Install the configuration files
# elements_install_conf_files()
elements_install_conf_files()

# Install the auxiliary files
# elements_install_aux_files()
