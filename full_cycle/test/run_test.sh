#!/bin/bash
# run_test.sh
# Create a new package with two analysis cycles.
# The first cycle copies the TTree in myfile.root to its output file.
# The second analysis reads in a subset of the variables in this 
# output file. The subset is specified in VariableList.C
echo "
    ==========================================
    Creating new analysis package TestAnalysis
    ==========================================
"
sframe_new_package.sh TestAnalysis
cd TestAnalysis
echo "
    ====================================
    Creating MyFirstCycle analysis cycle
    ====================================
"
# This analyis will be called MyFirstCycle
# It will read it's variable list and the tree name from ../myfile.root,
# and will alse be configured to run over ../myfile.root.
# Output variables will be declared, connected to the output tree OutTree,
# and the input will be copied to the output tree
sframe_create_full_cycle.py -n MyFirstCycle -r ../myfile.root -o OutTree
echo "
    =========================================
    Now compiling and running the first cycle
    =========================================
"
make
sframe_main config/MyFirstCycle_config.xml
echo "
    ======================================
    Now generating code for a second cycle
    ======================================
"
# This analysis cycle will be called MySecondCycle. It will reside within the 
# namespace my_namespace. It will be configured to run over the file
# MyFirstCycle.DATA.V1.root and read the tree named OutTree (given by -t).
# Its list of variables will be read from VariableList.C.
sframe_create_full_cycle.py -n my_namespace::MySecondCycle -v ../VariableList.C \
    -r MyFirstCycle.DATA.V1.root -t OutTree
# Note: PyRoot is not required for this usage. The name of the ROOT-file will only 
# be used in the config.xml
echo "
    =========================================
    Now compiling and running the second cycle
    =========================================
"
make
sframe_main config/MySecondCycle_config.xml
