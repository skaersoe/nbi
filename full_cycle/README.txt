Python script to create a full usable SFrame cycle.

FullCycleCreators.py should be linked or copied to $SFRAME_DIR/python/.
sframe_create_full_cycle.py should be linked or copied to $SFRAME_DIR/bin/.

sframe_create_full_cycle.py:
	This script is able to create a full sframe analysis cycle that can
	be compiled and run right away.
	If only the CYCLENAME is given, the produced code is essentially the
	same as that created by sframe_create_cycle.py, except that it compiles
	and runs.
	The power of this extended script is that it can read a list of variables
	either directly from a root-file, or from a textile with variable declarations.
	It can then produce code that uses these variables in the sframe cycle.
	If the name of an OUTTREE is given, code will be generated to copy all input
	variables to an output tree.

The usage of sframe_create_full_cycle.py is:
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
  --analysis=ANALYSIS   Name of the analysis package. Defaults to the name of
                        the pwd.
  --outtree=OUTTREE     Name of the output tree, if it should be written.
