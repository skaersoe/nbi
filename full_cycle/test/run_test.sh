#!/bin/bash

echo "
    ==============================
    Creating new analysis package.
    ==============================
"

sframe_new_package.sh TestAnalysis
cd TestAnalysis

echo "
    ====================================
    Creating MyFirstCycle analysis cycle
    ====================================
"

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

sframe_create_full_cycle.py -n MySecondCycle -v ../TestVariableList.C -r MyFirstCycle.DATA.V1.root -t OutTree

echo "
    =========================================
    Now compiling and running the second cycle
    =========================================
"

make
sframe_main config/MyFirstCycle_config.xml
