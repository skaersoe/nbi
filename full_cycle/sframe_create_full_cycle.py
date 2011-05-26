#!/usr/bin/env python
# $Id: sframe_create_cycle.py 120 2009-08-27 12:02:57Z krasznaa $
#***************************************************************************
#* @Project: SFrame - ROOT-based analysis framework for ATLAS
#* @Package: Core
#*
#* @author Stefan Ask             <Stefan.Ask@cern.ch>                     - Manchester
#* @author David Berge            <David.Berge@cern.ch>                    - CERN
#* @author Johannes Haller    <Johannes.Haller@cern.ch>            - Hamburg
#* @author A. Krasznahorkay <Attila.Krasznahorkay@cern.ch> - CERN/Debrecen
#* @author S. Heisterkamp   <heisterkamp@nbi.dk>           - Copenhagen    #
#* For bugs/comments on this particluar script, please contact the last    #
#* autor in the list above                                                 #
#***************************************************************************
#
# This script can be used to quickly create a new analysis cycle in
# the user's package. If it's called in an arbitrary directory, then
# all the created files are put in the current directory. However
# when invoking it in an SFrame package directory (like SFrame/user)
# it will put the files in the correct places and add the entry
# to the already existing LinkDef file.
#

# Import base module(s):
import sys
import os.path
import optparse

## Main function of this script
#
# The executable code of the script is put into this function, much like
# it is done in the case of C++ programs. The main function is then called
# from outside using the usual method. (Which I've seen in various
# places...)
def main():
    # Print some welcome message before doing anything else:
    print ">>"
    print ">> %s : Analysis cycle torso creator" % \
                os.path.basename( sys.argv[ 0 ] )
    print ">>"
    print ""
    
    # Parse the command line parameters:
    parser = optparse.OptionParser( usage="%prog [options]" )
    parser.add_option( "-n", "--name", dest="cycleName", action="store",
                        type="string", default="AnalysisCycle",
                        help="Name of the analysis cycle to create" )
    parser.add_option( "-l", "--linkdef", dest="linkdef", action="store",
                        type="string", default="",
                        help="Name of the LinkDef.h file in the package" )
    parser.add_option( "-r", "--rootfile", dest="rootfile", action="store",
                        type="string", default="",
                        help="Name a rootfile to use as the input. The tree name and the variable list can be read from here." )
    parser.add_option( "-t", "--treename", dest="treename", action="store",
                        type="string", default="",
                        help="Name of the tree in the input file" )
    parser.add_option( "-v", "--varlist", dest="varlist", action="store",
                        type="string", default="",
                        help="Name a file containing a list of variable declarations to be used in the cycle. Can contain comments." )
    parser.add_option( "-a", "--analysis", dest="analysis", action="store",
                        type="string", default="",
                        help="Name of the analysis package. Defaults to the name of the pwd." )
    parser.add_option( "-o", "--outtree", dest="outtree", action="store",
                        type="string", default="",
                        help="Name of the output tree, if it should be written." )
    
    ( options, args ) = parser.parse_args()
    
    # This is where the main function are:
    from FullCycleCreators import FullCycleCreator
    
    # Execute the cycle creation:
    cc = FullCycleCreator()
    cc.CreateCycle( **options.__dict__)


# Call the main function:
if __name__ == "__main__":
    main()
