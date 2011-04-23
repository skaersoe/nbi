#!/bin/bash

sframe_new_package.sh TestAna
cd TestAna
sframe_create_full_cycle.py -n MyCycle -v ../TestVariableList.C -o OutTree