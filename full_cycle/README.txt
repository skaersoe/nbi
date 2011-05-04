A python script to create a full usable SFrame cycle.

FullCycleCreators.py should be linked or copied to $SFRAME_DIR/python/.
sframe_create_full_cycle.py should be linked or copied to $SFRAME_DIR/bin/.

sframe_create_full_cycle.py:
    This script is able to create a full sframe analysis cycle that can be compiled
    and run right away.  If only the CYCLENAME is given, the produced code is
    essentially the same as that created by sframe_create_cycle.py, except that it
    compiles and runs.  The power of this extended script is that it can read a
    list of variables either directly from a root-file, or from a text file with
    variable declarations.  It can then produce code that uses these variables in
    the sframe cycle.  If the name of an OUTTREE is given, code will be generated
    to copy all input variables to an output tree.
    
The following describes some typical usecases:
==============================================    
    A full analysis can be created like this:
    
    $ sframe_new_package.py TestAnalysis
    $ cd TestAnalysis
    $ sframe_create_full_cycle.py -n MyNewCycle -r ntuple.root
    
    For this to work ntuple.root should contain a TTree. The name of the TTree as 
    well as the list of variables will be read from ntuple.root. Code will be 
    generated to read all the variables in ntuple.root. The config.xml file will 
    also be configured to read this file. By default, the TTree with the largest
    number of branches will be used. If a different TTree should be used, specify 
    with --treename.
    
    If a different set of variables is desired, or no root-file can be supplied,
    the script can be called like this:
    
    $ sframe_create_full_cycle.py -n MyNewCycle -v selection.C
    
    Where selection.C might contain variable declarations like this:
    """"
    //UInt_t RunNumber;
    int i;
    //float f;
    vector<float> *v;/*
    vector<float> *el_eta;
    vector<float> *el_phi;*/
    """"
    As can be seen, c-style comments can be used. Commented out variable
    declarations will be used in commented form. The tree-name and the root-file
    name will be set to default values in the the config.xml file. These need to
    be adjusted for running.

Test Suite
==========
    If you would like to see a full test of sframe_create_full_cycle.py, have a
    look at the test suite located in the folder "test/".
    Inspect the script run_test.sh. It contains examples for how to use the most
    important options that are available in sframe_create_full_cycle.py.
    Run or source the script run_test.sh and inspect the generated code. The 
    generated analysis itself is fairly trivial, but notice that it compiles and 
    runs right out of the box!

The usage of sframe_create_full_cycle.py
========================================
$ sframe_create_full_cycle.py -h
>>
>> sframe_create_full_cycle.py : Analysis cycle torso creator
>>

Usage: sframe_create_full_cycle.py [options]

Options:
  -h, --help            show this help message and exit
  -n CYCLENAME, --name=CYCLENAME
                        Name of the analysis cycle to create
  -l LINKDEF, --linkdef=LINKDEF
                        Name of the LinkDef.h file in the package
  -r ROOTFILE, --rootfile=ROOTFILE
                        Name a rootfile to use as the input. The tree name and
                        the variable list can be read from here.
  -t TREENAME, --treename=TREENAME
                        Name of the tree in the input file
  -v VARLIST, --varlist=VARLIST
                        Name a file containing a list of variable declarations
                        to be used in the cycle. Can contain comments.
  -a ANALYSIS, --analysis=ANALYSIS
                        Name of the analysis package. Defaults to the name of
                        the pwd.
  -o OUTTREE, --outtree=OUTTREE
                        Name of the output tree, if it should be written.
