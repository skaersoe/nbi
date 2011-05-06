###########################################################################
# @Project: SFrame - ROOT-based analysis framework for ATLAS              #
#                                                                         #
# @author Stefan Ask        <Stefan.Ask@cern.ch>            - Manchester  #
# @author David Berge      <David.Berge@cern.ch>          - CERN          #
# @author Johannes Haller  <Johannes.Haller@cern.ch>      - Hamburg       #
# @author A. Krasznahorkay <Attila.Krasznahorkay@cern.ch> - CERN/Debrecen #
#                                                                         #
###########################################################################

## @package FullCycleCreators
#    @short Functions for creating a new analysis cycle torso
#
# This package collects the functions used by sframe_create_full_cycle.py
# to create the torso of a new analysis cycle. Apart from using
# sframe_create_full_cycle.py, the functions can be used in an interactive
# python session by executing:
#
# <code>
#  >>> import FullCycleCreators
# </code>

## @short Class creating analysis cycle templates
#
# This class can be used to create a template cycle inheriting from
# SCycleBase. It is quite smart actually. If you call CycleCreator.CreateCycle
# from inside an "SFrame package", it will find the right locations for the
# created files and extend an already existing LinkDef.h file with the
# line for the new cycle.

import re

class FullCycleCreator:
    
    ## @short Function creating a configuration file for the new cycle
    #
    # This function is supposed to create an example configuration file
    # for the new cycle. It uses PyXML to write the configuration, and
    # exactly this causes a bit of trouble. PyXML is about the worst
    # XML implementation I ever came accross... There are tons of things
    # that it can't do. Not to mention the lack of any proper documentation.
    #
    # All in all, the resulting XML file is not too usable at the moment, 
    # it's probably easier just copying one of the example cycles from
    # SFrame/user/config and adjusting it to the user's needs...
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param fileName  Optional parameter with the configuration file name
    class Variable( object ):
        """
        One of the variables that will be used in the cycle.
        A variable has a name and a typename.
        A variable can be and stl-container where the input declaration must be a pointer etc.
        A variable can be commented out, in which case it will be included in the cycle, 
        but as being commented out.
        
        A list of variables is assembled either by the TreeReader directly from a root-file, 
        or by the VariableSelectionReader from a C-like file with variable declarations.
        """
        
        def __init__( self, name, typename, commented, pointer ):
            super( FullCycleCreator.Variable, self ).__init__()
            self.name = name
            self.typename = typename
            self.pointer = pointer
            self.commented = commented
            # Sanitize the name. Root names can be anything.
            # We must be careful to have a valid C++ variable name in front of us
            import re
            self.cname = re.sub("""[ :.,;\\/|`'"()\[\]{}<>~?!@#$%^&*+=\-]""","_",name) 
        
        def __repr__(self):
            return "%s%s %s%s" % (self.commented, self.typename, self.pointer, self.name )
        def __str__(self):
            return self.__repr__()
        
        # End of Class Variable
    
    ## @short Function creating a configuration file for the new cycle
    #
    # This function is supposed to create an example configuration file
    # for the new cycle. It uses PyXML to write the configuration, and
    # exactly this causes a bit of trouble. PyXML is about the worst
    # XML implementation I ever came accross... There are tons of things
    # that it can't do. Not to mention the lack of any proper documentation.
    #
    # All in all, the resulting XML file is not too usable at the moment, 
    # it's probably easier just copying one of the example cycles from
    # SFrame/user/config and adjusting it to the user's needs...
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param fileName  Optional parameter with the configuration file name
    def ReadVariableSelection( self, filename ):
        """
        Reads a list of variable declarations from file into a structured format.
        From there they can be used to create the declarations and 
        connect-statements necessary to use the variables in a cycle.
        """
        varlist = []
        try:
            text = open( filename ).read()
        except:
            print "Unable to open variable selection file", "\"%s\"" % filename
            return varlist
        
        # Use some regexp magic to change all /*...*/ style comments to // style comments
        text = re.sub( """\*/[^\n]""", "*/\n", text ) # append newline to every */ that isn't already followed by one
        while re.search( """/\*""", text ):  # While ther still are /* comments
            text = re.sub( """/\*(?P<line>.*?)(?P<end>\n|\*/)""", """// \g<line>/*\g<end>""", text ) # move the /* to the next newline or */
            text = re.sub( """/\*\*/""", "", text )  # remove zero content comments
            text = re.sub( """/\*\n""", "\n/*", text ) # move the /* past the newline
        
        text = re.sub("""(?<!\n)//""","\n//", text ) # Make sure // always starts a new line
        text = re.sub("""\n(\s)*""","\n", text ) # clean up any sequence of successive whitespaces starting with a newline
        text = re.sub("""^(\s)*""","", text ) # clean up any sequence of successive whitespaces at the start of the file
        text = re.sub("""(\s)*\n""","\n", text ) # clean up any sequence of successive whitespaces at line endings
        
        # the text should now be quite tidy and ready for parsing.
        
        # Find every variable definition.
        # Definitions may start with a //.
        # After that I expect there to be a typename of the form UInt_t or int or std::vector<double> etc.
        # then a name, 
        # and finally a;
        query="""(?P<comment>(?://)?)[ \t]*""" # First find out if the line is commented
        # next is the typename which starts with a word chracter [a-zA-Z_]
        query+="""(?P<type>[a-zA-Z_][a-zA-Z_0-9:]*(?:[ \t]*<.+>)?)""" 
        # but can from there on also contain numbers [a-zA-Z_0-9:]*
        # finally it may contain a template structure (?:[ \t]*<.+>)?
        # next comes the issue of pointers. 
        query+="""(?:(?:[ \t]*(?P<point>\*)[ \t]*)|(?:(?<!\*)[ \t]+(?!\*)))"""
        # if there is a star, it can have whitespaces before or after.
        # if there is no star, there must be some whitespace.
        # and now for the name
        query+="""(?P<name>[a-zA-Z_][a-zA-Z_0-9]*)[ \t]*;[ \t;]*"""
        for match in re.finditer( query, text ):
            varargs = {}
            varargs[ "commented" ] = match.group( "comment" ) # whether the variable was commented out. Will be '//' if it was
            varargs[ "typename" ] = match.group( "type" )
            varargs[ "name" ] = match.group( "name" )
            varargs[ "pointer" ] = match.group( "point" )
            if not varargs[ "pointer" ]:
                varargs[ "pointer" ] = "" # just in case there was no poiner to match.
            varlist.append( self.Variable( **varargs ) )
        
        return varlist
    
    ## @short Function creating a configuration file for the new cycle
    #
    # This function is supposed to create an example configuration file
    # for the new cycle. It uses PyXML to write the configuration, and
    # exactly this causes a bit of trouble. PyXML is about the worst
    # XML implementation I ever came accross... There are tons of things
    # that it can't do. Not to mention the lack of any proper documentation.
    #
    # All in all, the resulting XML file is not too usable at the moment, 
    # it's probably easier just copying one of the example cycles from
    # SFrame/user/config and adjusting it to the user's needs...
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param fileName  Optional parameter with the configuration file name
    class ROOT_Access:
        """
        A class that contains all the pyROOT related tasks.
        It will try to import pyROOT only once, and tell you if
        it failed. After that it will simply shut up and return
        empty objects if ROOT was't imported properly.
        """
        def __init__( self ):
            self.intitalized = 0
        
        
        def Initalize( self ):
            if self.intitalized:
                return bool( self.ROOT )
            
            try:
                import ROOT
                self.ROOT = ROOT
            except ImportError, e:
                print "ERROR: pyROOT could not be loaded. Unable to access root-file"
                print "ERROR: You will need to supply the treename and variable list."
                print "ERROR: use -h or --help to get help."
                self.ROOT = 0
            
            return bool( self.ROOT )
        
        
        def TCollIter( self, tcoll ):
            """Gives an iterator over anything that the ROOT.TIter can iterate over."""
            if not self.Initalize():
                return
            it = self.ROOT.TIter( tcoll )
            it.Reset()
            item = it.Next()
            while item:
                yield item
                item = it.Next()
            return
        
        
        def GetTreeName( self, rootfile ):
            """
            Get the name of the treename in the file named rootfile.
            Or just return 'TreeName' if any errors show up.
            If several trees are present, get the one with the largest number
            of branches.
            """
            treename = "TreeName"
            if not self.Initalize():
                return treename
            
            if not rootfile:
                print "No rootfile given. Using default tree name:", treename
                return treename
            
            f = self.ROOT.TFile.Open( rootfile )
            if not f:
                print rootfile, "could not be opened. Using default tree name:", treename
                return treename
            # Get a list of all TKeys to TTrees
            trees = [ key for key in self.TCollIter( f.GetListOfKeys() ) if key.GetClassName() == "TTree" ]
            if len( trees ) == 1:
                # Just 1? Use it
                treename = trees[ 0 ].GetName()
            elif len( trees ) > 1:
                print "Avaliable tree names:", ", ".join( [ key.GetName() for key in trees ] )
                # Find the tree with the largest number of branches.
                nbranch = -1;
                for key in trees:
                    tree = key.ReadObj()
                    if tree.GetNbranches() > nbranch:
                        nbranch = tree.GetNbranches()
                        treename = tree.GetName()
            print "Using treename:", treename
            f.Close()
            
            return treename
        
        
        def ReadVars( self, rootfile, treename ):
            """
            Reads a list of variables from a root-file into a structured 
            format. From there they can be used to create the declarations and connect
            statements necessary to use the variables in a cycle.
            """
            varlist = []
            if not self.Initalize():
                return varlist
            ROOT = self.ROOT
            
            if not rootfile or not treename:
                print "Incomplete arguments. Cannot get tree named \"%s\" from rootfile \"%s\"" % ( treename, rootfile )
                return varlist
            
            f = ROOT.TFile.Open( rootfile )
            if not f:
                print "Could not open root file \"%s\"" % rootfile
                return varlist
            
            tree = f.Get( treename )
            if not tree:
                print "Could not get tree \"%s\"" % treename
                f.Close()
                return varlist
            
            for branch in self.TCollIter( tree.GetListOfBranches() ):
                for leaf in self.TCollIter( branch.GetListOfLeaves() ):
                    varargs = {}
                    varargs[ "commented" ] = ""
                    varargs[ "typename" ] = leaf.GetTypeName()
                    varargs[ "name" ] = leaf.GetName()
                    #varargs[ "pointer" ] = FullCycleCreator.Is_stl_like( leaf.GetTypeName() )
                    if type( leaf ) in (ROOT.TLeafElement, ROOT.TLeafObject):
                        varargs[ "pointer" ] = "*"
                    else:
                        varargs[ "pointer" ] = ""
                    varlist.append( FullCycleCreator.Variable( **varargs ) )
            f.Close()
            return varlist
        
        #End of Class ROOT_Access
    
    
    ## @short Determine whether the type named by typename is an stl_container
    # That should be cleared at the start of the event execution
    @staticmethod
    def Is_stl_like( typename ):

        #stl_like = "vector" in typename
        #stl_like = bool( re.search( """<.+>""", typename ) ) or bool( "vector" in typename )
        import re
        # Check if the typename contains structures like "vector <int>" or similar for list, map or set 
        stl_like = bool( re.search( "(vector|list|set|map)\s*<.*>", typename ) )
        # May want to include other stl_containers here, but I don't expect others to be used.
        # ... and really there is only so far you can go with automatic gode generation.
        if stl_like:
            return "*"
        else:
            return ""
    
    ## @short Indent a text body for inserting into a namespace
    def Indent( self, text ):
        return re.sub( """(?<=:^|\n)(?=.)""", """%s\g<0>""" % self._tab, text )
    
    # See end of class definition for string literals
    
    def __init__( self ):
        self._headerFile = ""
        self._sourceFile = ""
        self.pyROOT = self.ROOT_Access()
    
    ## @short Function creating a configuration file for the new cycle
    #
    # This function is supposed to create an example configuration file
    # for the new cycle. It uses PyXML to write the configuration, and
    # exactly this causes a bit of trouble. PyXML is about the worst
    # XML implementation I ever came accross... There are tons of things
    # that it can't do. Not to mention the lack of any proper documentation.
    #
    # All in all, the resulting XML file is not too usable at the moment, 
    # it's probably easier just copying one of the example cycles from
    # SFrame/user/config and adjusting it to the user's needs...
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param fileName  Optional parameter with the configuration file name
    def SplitCycleName( self, cycleName ):
        """
        splits the cycleName into a class name and a namespace name
        returns a tuple of (namespace, className )
        """
        namespace = ""
        className = cycleName
        if re.search( "::", cycleName ):
            m = re.match( "(.*)::(.*)", cycleName )
            namespace = m.group( 1 )
            className = m.group( 2 )
        
        return ( namespace, className )
    
    ## @short Function creating a configuration file for the new cycle
    #
    # This function is supposed to create an example configuration file
    # for the new cycle. It uses PyXML to write the configuration, and
    # exactly this causes a bit of trouble. PyXML is about the worst
    # XML implementation I ever came accross... There are tons of things
    # that it can't do. Not to mention the lack of any proper documentation.
    #
    # All in all, the resulting XML file is not too usable at the moment, 
    # it's probably easier just copying one of the example cycles from
    # SFrame/user/config and adjusting it to the user's needs...
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param fileName  Optional parameter with the configuration file name
    def Backup( self, filename ):
        """
        Check if the file exists. If it does, beck it up to file+".backup"
        """
        import os.path
        if os.path.exists( filename ):
            print "WARNING:: File \"%s\" already exists" % filename
            print "WARNING:: Moving \"%s\" to \"%s.backup\"" % ( filename, filename )
            import shutil
            shutil.move( filename, filename + ".backup" )
            

    ## @short Function creating an analysis cycle header
    #
    # This function can be used to create the header file for a new analysis
    # cycle.
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param fileName  Optional parameter with the output header file name
    # @param namespace  Optional parameter with the name of the namespace to use
    # @param varlist  Optional parameter with a list of "Variable" objects for which to create declarations
    # @param create_output  Optional parameter for whether to create declarations for output variables
    def CreateHeader( self, className, headerName = "" , namespace = "", varlist = [], create_output = False, **kwargs):
        # Construct the file name if it has not been specified:
        if  not headerName:
            headerName = className + ".h"
        
        fullClassName = className
        if namespace:
            fullClassName = namespace + "::" + className
        formdict = { "tab":self._tab, "class":className, "namespace":namespace, "fullClassName":fullClassName }

        # Now create all the lines to declare the input and output variables
        inputVariableDeclarations = ""
        outputVariableDeclarations = ""

        for var in varlist:
            subs_dict = dict( formdict )
            subs_dict.update( var.__dict__ )
            inputVariableDeclarations += "%(tab)s%(commented)s%(typename)s\t%(pointer)s%(cname)s;\n" % subs_dict

            if create_output:
                outputVariableDeclarations += "%(tab)s%(commented)s%(typename)s\tout_%(cname)s;\n" % subs_dict
        
        formdict[ "inputVariableDeclarations" ] = inputVariableDeclarations
        formdict[ "outputVariableDeclarations" ] = outputVariableDeclarations
        # Some printouts:
        print "CreateHeader:: Cycle name     = " + className
        print "CreateHeader:: File name      = " + headerName
        self._headerFile = headerName

        # Create a backup of an already existing header file:
        self.Backup( headerName )
        
        # Construct the contents:
        body = self._Template_header_Body % formdict
        if namespace:
            ns_body = self._Template_namespace % { "namespace":namespace, "body": self.Indent( body ) }
        else:
            ns_body = body
        
        full_contents = self._Template_header_Frame % {"body":ns_body, "capclass":( namespace+"_"+className ).upper(), "fullClassName":namespace+"::"+className}

        # Write the header file:
        output = open( headerName, "w" )
        output.write( full_contents )
        output.close()
        
        return headerName
    
    
    ## @short Function creating the analysis cycle source file
    #
    # This function creates the source file that works with the header created
    # by CreateHeader. It is important that CreateHeader is executed before
    # this function, as it depends on knowing where the header file is
    # physically. (To include it correctly in the source file.)
    #
    # @param className Name of the analysis cycle
    # @param fileName  Optional parameter with the output source file name
    # @param namespace  Optional parameter with the name of the namespace to use
    # @param varlist  Optional parameter with a list of "Variable" objects to be used by the cycle
    # @param create_output  Optional parameter for whether to produce code for output variables
    def CreateSource( self, className, sourceName = "", namespace = "", varlist = [], create_output = False, header = "", **kwargs ):
        # Construct the file name if it has not been specified:
        if sourceName == "":
            sourceName = className + ".cxx"
        
        if not header:
            header = className + ".h"
        
        fullClassName = className
        if namespace:
            fullClassName = namespace + "::" + className
        formdict = { "tab":self._tab, "class":className, "namespace":namespace, "fullClassName":fullClassName }
        
        # Determine the relative path of the header
        import os
        headpath = os.path.dirname( os.path.abspath( header ) ).split( os.sep )
        srcpath = os.path.dirname( os.path.abspath( sourceName ) ).split( os.sep )
        #find the index from which the paths differ:
        index = 0
        while index < min( len( headpath ), len( srcpath ) ) and headpath[index] == srcpath[index]:
            # find the highest index to which the paths are equal
            index += 1
        
        if index == 0:
            # no common path
            include = os.path.abspath( header )
        else:
            # Step down the path of the Source-file
            path = [ ".." for directory in srcpath[index:] ]
            # and up the path of the header
            path += headpath[index:]
            path.append( os.path.basename( header ) )
            include = os.sep.join( path )
        
        # Now create all the lines to handle the variables
        inputVariableConnections = ""
        outputVariableConnections = ""
        outputVariableClearing = ""
        outputVariableFilling = ""

        for var in varlist:
            subs_dict =dict( formdict )
            subs_dict.update( var.__dict__ )

            inputVariableConnections += "%(tab)s%(commented)sConnectVariable( InTreeName.c_str(), \"%(name)s\", %(cname)s );\n" % subs_dict

            if create_output:
                outputVariableConnections += "%(tab)s%(commented)sDeclareVariable( out_%(cname)s, \"%(name)s\" );\n" % subs_dict
                outputVariableFilling += "%(tab)s%(commented)sout_%(cname)s = %(pointer)s%(cname)s;\n" % subs_dict
                if var.pointer and self.Is_stl_like( var.typename ):
                    # Not all pointer-accessed types can do this, only stl-vectors
                    outputVariableClearing += "%(tab)s%(commented)sout_%(cname)s.clear();\n" % subs_dict
        
        formdict[ "inputVariableConnections" ] = inputVariableConnections
        formdict[ "outputVariableConnections" ] = outputVariableConnections
        formdict[ "outputVariableClearing" ] = outputVariableClearing
        formdict[ "outputVariableFilling" ] = outputVariableFilling
        
        # Some printouts:
        print "CreateSource:: Cycle name     =", className
        print "CreateSource:: File name      =", sourceName
        self._sourceFile = sourceName

        
        # Create a backup of an already existing source file:
        self.Backup( sourceName )
        
        #Construct the contents of the source file:
        body = self._Template_source_Body % formdict
        if namespace:
            ns_body = self._Template_namespace % { "namespace":namespace, "body":self.Indent( body ) }
        else:
            ns_body = body
        full_contents = self._Template_source_Frame % { "body":ns_body, "fullClassName":fullClassName, "header":include }
        
        
        # Write the source file:
        output = open( sourceName, "w" )
        output.write( full_contents )
        output.close()
        return
    
    
    ## @short Function adding link definitions for rootcint
    #
    # Each new analysis cycle has to declare itself in a so called "LinkDef
    # file". This makes sure that rootcint knows that a dictionary should
    # be generated for this C++ class.
    #
    # This function is also quite smart. If the file name specified does
    # not yet exist, it creates a fully functionaly LinkDef file. If the
    # file already exists, it just inserts one line declaring the new
    # cycle into this file.
    #
    # @param className Name of the analysis cycle. Can contain the namespace name.
    # @param linkdefName  Optional parameter with the LinkDef file name
    # @param namespace  Optional parameter with the name of the namespace to use
    def AddLinkDef( self, className, linkdefName = "LinkDef.h" , namespace = "", varlist = [], **kwargs):
        
        cycleName = className
        if namespace:
            cycleName = namespace + "::" + className
        
        new_lines = "#pragma link C++ class %s+;\n" %  cycleName
        
        # Find all object-like variable types and make pragma lines for them
        # This is unnecessary for many simple vectors, but since it doesn't
        # do any harm, We might as well include it for all object types
        types = set()
        for var in varlist:
            if var.pointer:
                types.add( var.typename )
        
        for typename in types:
            new_lines += "#pragma link C++ class %s+;\n" % typename
        
        import os.path
        if os.path.exists( linkdefName ):
            print "AddLinkDef:: Extending already existing file \"%s\"" % linkdefName
            # Read in the already existing file:
            infile = open( linkdefName, "r" )
            text =infile.read()
            infile.close()

            # Find the "#endif" line:
            if not re.search( """#endif""", text ):
                print "AddLinkDef:: ERROR File \"%s\" is not in the right format!" % linkdefName
                print "AddLinkDef:: ERROR Not adding link definitions!"
                return
            
            # Overwrite the file with the new contents:
            output = open( linkdefName, "w" )
            #Insert the newlines before the #endif
            # """(?=\n#endif)""" matches the empty string that is immediately succeded by \n#endif
            output.write( re.sub( """(?=\n#endif)""", new_lines+"\n", text ) )
            output.close()

        else:
            # Create a new file and fill it with all the necessary lines:
            print "AddLinkDef:: Creating new file called \"%s\"" % linkdefName
            output = open( linkdefName, "w" )
            output.write( self._Template_LinkDef %{ "new_lines":new_lines } )

        return
    
    
    ## @short Function creating a configuration file for the new cycle
    #
    # This function uses the configuration file in $SFRAME_DIR/user/config/FirstCycle_config.xml
    # and adapts it for this analysis using PyXML. As this file is expected to
    # change in future updates this function may break. It may therefore be better to create something from scratch.
    # The advantage of this approach is that the resulting xml file works, and still
    # contains all the comments of FirstCycle_config.xml, making it more usable.
    # 
    #
    # @param className Name of the analysis cycle
    # @param configName  Optional parameter with the output config file name
    # @param namespace  Optional parameter with the name of the namespace to use
    # @param analysis  Optional parameter with the name of the analysis package
    # @param rootfile  Optional parameter with the name of an input root-file
    # @param treename  Optional parameter with the name of the input tree
    # @param outtree  Optional parameter with the name of the output tree if desired
    def CreateConfig( self, className, configName = "" , namespace = "", analysis = "MyAnalysis", rootfile = "my/root/file.root", treename = "InTreeName", outtree = "", **kwargs):
        # Construct the file name if it has not been specified:
        if configName == "":
            configName = className + "_config.xml"
        self.Backup( configName )
        
        cycleName = className
        if namespace:
            cycleName =namespace + "::" + cycleName
        
        # Some printouts:
        print "CreateConfig:: Cycle name     =", className
        print "CreateConfig:: File name      =", configName

        # Use the configuration file FirstCycle_config.xml as a basis:
        import os
        xmlinfile = os.path.join( os.getenv( "SFRAME_DIR" ), "user/config/FirstCycle_config.xml" )
        if not os.path.exists( xmlinfile ):
            print "ERROR: Expected to find example configuration at", xmlinfile
            print "ERROR: No configuration file will be written."
            return
        
        #Make changes to adapt this file to our purposes
        try:
            import xml.dom.minidom
            dom = xml.dom.minidom.parse( open( xmlinfile ) )
            
            nodes = dom.getElementsByTagName( "JobConfiguration" )
            # If more than one Job configuration exists, crash
            if not len( nodes ) == 1: raise AssertionError
            JobConfiguration = nodes[ 0 ]
            JobConfiguration.setAttribute( "JobName", className + "Job" )
            JobConfiguration.setAttribute( "OutputLevel", "INFO" )
            
            #Find the libSFrameUser library and change it to ours
            for node in dom.getElementsByTagName( "Library" ):
                if node.getAttribute( "Name" ) == "libSFrameUser":
                    node.setAttribute( "Name", "lib" + analysis )
            
            #Find the SFrameUser package and change it to ours
            for node in dom.getElementsByTagName( "Package" ):
                if node.getAttribute( "Name" ) == "SFrameUser.par":
                    node.setAttribute( "Name", analysis + ".par" )

            nodes = dom.getElementsByTagName( "Cycle" )
            #There should be exactly one cycle
            if not len( nodes ) == 1: raise AssertionError
            cycle = nodes[ 0 ]
            cycle.setAttribute( "Name", cycleName )
            cycle.setAttribute( "RunMode", "LOCAL" )
            
            #Remove all but one input data
            while len( dom.getElementsByTagName( "InputData" ) ) > 1:
                cycle.removeChild( dom.getElementsByTagName( "InputData" )[ -1 ] )
            inputData = dom.getElementsByTagName( "InputData" )[ 0 ]
            
            for i in range( inputData.attributes.length ):
                inputData.removeAttribute( inputData.attributes.item( 0 ).name )
            
            inputData.setAttribute( "Lumi", "1.0" )
            inputData.setAttribute( "Version", "V1" )
            inputData.setAttribute( "Type", "DATA" )
            # inputData.setAttribute( "Cacheable", "False" )
            # inputData.setAttribute( "NEventsMax", "-1" )
            # inputData.setAttribute( "NEventsSkip", "0" )
            
            # Remove all but one input files
            while len( inputData.getElementsByTagName( "In" ) ) > 1:
                inputData.removeChild( inputData.getElementsByTagName( "In" )[ -1 ] )
            In = inputData.getElementsByTagName( "In" )[ 0 ]
            
            In.setAttribute( "Lumi", "1.0" )
            In.setAttribute( "FileName", rootfile )
            
            # Remove all but one input trees
            while len( inputData.getElementsByTagName( "InputTree" ) ) > 1:
                inputData.removeChild( inputData.getElementsByTagName( "InputTree" )[ -1 ] )
            InputTree = inputData.getElementsByTagName( "InputTree" )[ 0 ]
            
            InputTree.setAttribute( "Name", treename )
            
            # Remove the MetadataOutputTrees
            while len( inputData.getElementsByTagName( "MetadataOutputTree" ) ):
                inputData.removeChild( inputData.getElementsByTagName( "MetadataOutputTree" )[ 0 ] )
            
            # Remove all but one output Trees
            while len( inputData.getElementsByTagName( "OutputTree" ) )>1:
                inputData.removeChild( inputData.getElementsByTagName( "OutputTree" )[ -1 ] )
            outtreenode = inputData.getElementsByTagName( "OutputTree" )[ 0 ]
            
            if not outtree:
                # No output is desired, remove this node
                inputData.removeChild( outtreenode )
            else:
                outtreenode.setAttribute( "Name", outtree )
            
            nodes = cycle.getElementsByTagName( "UserConfig" )
            # We expect one UserConfig section
            if not len( nodes ) == 1: raise AssertionError
            UserConfig = nodes[ 0 ]
            
            # Remove all but one item
            while len( UserConfig.getElementsByTagName( "Item" ) ) > 1:
                UserConfig.removeChild( UserConfig.getElementsByTagName( "Item" )[ -1 ] )
            Item = UserConfig.getElementsByTagName( "Item" )[ 0 ]
            
            Item.setAttribute( "Name", "InTreeName" )
            Item.setAttribute( "Value", treename )
            
        except AssertionError:
            # If any exceptions were raised, the FirstCycle_config.xml file
            # has probably changed. In that case this function should be 
            # updated to reflect that change.
            print "ERROR: ", xmlinfile, "has an unexpected structure."
            print "ERROR: No configuration file will be written."
            return
        
        # For some reason toprettyxml inserts lines of whitespaces.
        # Use some regexp to get rid of those
        text = re.sub( """(?<=\n)([ \t]*\n)+""", "", dom.toprettyxml( encoding ="UTF-8" ) )
        outfile =open( configName, "w" )
        outfile.write( text )
        outfile.close()
        return
    
    
    ## @short Function to add a JobConfig file to the analysis
    #
    # A JobConfig.dtd file is necessary for parsing the config xml files.
    # Use the one from the $SFRAME_DIR/user/ example if there isn't one 
    # here already.
    #
    # @param directory The name of the directory where the file should be
    def AddJobConfig( self, config_directory, **kwargs):
        import os.path
        newfile = os.path.join( config_directory, "JobConfig.dtd" )
        if os.path.exists( newfile ):
            print "Keeping existing JobConfig.dtd"
            return
        
        oldfile = os.path.join( os.getenv( "SFRAME_DIR" ), "user/config/JobConfig.dtd" )
        if not os.path.exists( oldfile ):
            print "ERROR: Expected JobConfig.dtd file at", oldfile
            print "ERROR: JobConfig.dtd file not copied"
            return
            
        import shutil
        shutil.copy( oldfile, newfile )
        print "Using a copy of", oldfile
    
    
    ## @short Main analysis cycle creator function
    #
    # The users of this class should normally just use this function
    # to create a new analysis cycle.
    #
    # It only really needs to receive the name of the new cycle, it can guess
    # the values of all the oter parameters. It calls all the
    # other functions of this class to create all the files for the new
    # cycle.
    #
    # @param cycleName Name of the analysis cycle. Can contain the namespace name.
    # @param linkdef Optional parameter with the name of the LinkDef file
    # @param rootfile Optional parameter with the name of a rootfile containing a TTree
    # @param treename Optional parameter with the name of the input TTree
    # @param varlist Optional parameter with a filename for a list of desired variable declarations
    # @param outtree Optional parameter with the name of the output TTree
    # @param analysis Optional parameter with the name of analysis package
    def CreateCycle( self, cycleName, linkdef = "", rootfile = "", treename = "", varlist = "", outtree = "", analysis = "" ):
        
        namespace, className = self.SplitCycleName( cycleName )
        
        # Make sure analysis is set
        if not analysis:
            import os
            analysis = os.path.basename( os.getcwd() )
            print "Using analysis name", "\"%s\"" % analysis
        
        #First we take care of all the variables that the user may want to have read in.
        # If treename wasn't given, it can be read from the rootfile if it exits.
        if not treename:
            treename = self.pyROOT.GetTreeName( rootfile ) # gives default if rootfile is empty
        
        # The three parameters related to the input variables are varlist, treename and rootfile.
        # if neither rootfile or varlist are given, no input variable code will be written.
        cycle_variables = []
        # Prefer to read the input from the varlist
        if varlist:
            cycle_variables = self.ReadVariableSelection( varlist )
        elif rootfile:
            cycle_variables = self.pyROOT.ReadVars( rootfile, treename )
        
        # The list of input variables is now contained in cycle_variables
        # if this list is empty, the effect of this class should be identical to that of the old CycleCreators
        
        #From now on rootfile is only used in the config file:
        if not rootfile:
            rootfile ="your/input/file.root"
        
        # Check if a directory called "include" exists in the current directory.
        # If it does, put the new header in that directory, otherwise, put it in the current directory
        import os.path
        include_dir = "include/"
        if not os.path.exists( include_dir ):
            include_dir = ""
            
        if not linkdef:
            import glob
            filelist = glob.glob( include_dir+"*LinkDef.h" )
            if len( filelist ) == 0:
                print "CreateCycle:: WARNING There is no LinkDef file under", include_dir
                linkdef = include_dir+"LinkDef.h"
                print "CreateCycle:: WARNING Creating one with the name", linkdef
            elif len( filelist ) == 1:
                linkdef = filelist[ 0 ]
            else:
                print "CreateCycle:: ERROR Multiple header files ending in LinkDef.h"
                print "CreateCycle:: ERROR I don't know which one to use..."
                return
        
        # Check if a directory called "src" exists in the current directory.
        # If it does, put the new source in that directory, otherwise, put it in the current directory
        src_dir = "src/"
        if not os.path.exists( src_dir ):
            src_dir = ""

        # Check if a directory called "config" exists in the current directory.
        # If it does, put the new configuration in that directory. Otherwise leave it up
        # to the CreateConfig function to put it where it wants.
        config_dir = "config/"
        if not os.path.exists( config_dir ):
            config_dir = ""
        
        
        # All options seem to be in order. Generate the code.
        options = dict()
        options[ "className" ]=className
        options[ "namespace" ] = namespace
        options[ "varlist" ] = cycle_variables
        options[ "create_output" ] = bool( outtree )
        options[ "headerName" ] = include_dir + className + ".h"
        options[ "linkdefName" ] = linkdef
        options[ "sourceName" ] = src_dir + className + ".cxx"
        options[ "configName" ] = config_dir + className + "_config.xml"
        options[ "analysis" ] = analysis
        options[ "rootfile" ] = rootfile
        options[ "treename" ] = treename
        options[ "outtree" ] = outtree
        options[ "config_directory" ] = config_dir
        options[ "header" ] = self.CreateHeader( **options )
        self.AddLinkDef( **options )
        self.CreateSource( **options )
        self.CreateConfig( **options )
        self.AddJobConfig( **options )
        return
    
    # End of function declarations
    # From now on there are declarations of the string templates that produce the code.
    
    ## @short The Tab character
    #
    # Define the tab character to be used during code gerneration
    # may be, for example, "\t", "  ", "   " or "    "
    # Note: If you want to change the indentation of all the genrated code
    # you also need to change it in all the following templates.
    _tab = " " * 4 # four spaces
    # _headerFile = ""
    # _sourceFile = ""
    
    ## @short Template for namespaced code
    #
    # This string is used to enclose code bodys in a namespace
    _Template_namespace = "namespace %(namespace)s {\n\n%(body)s\n} // of namespace %(namespace)s\n"

    ## @short Template for the body of a header file
    #
    # This string is used by CreateHeader to create the body of a header file
    _Template_header_Body = """
/**
 *    @short Put short description of class here
 *
 *          Put a longer description over here...
 *
 *  @author Put your name here
 * @version $Revision: 173 $
 */
class %(class)-s : public SCycleBase {

public:
    /// Default constructor
    %(class)-s();
    /// Default destructor
    ~%(class)-s();

    /// Function called at the beginning of the cycle
    virtual void BeginCycle() throw( SError );
    /// Function called at the end of the cycle
    virtual void EndCycle() throw( SError );

    /// Function called at the beginning of a new input data
    virtual void BeginInputData( const SInputData& ) throw( SError );
    /// Function called after finishing to process an input data
    virtual void EndInputData  ( const SInputData& ) throw( SError );

    /// Function called after opening each new input file
    virtual void BeginInputFile( const SInputData& ) throw( SError );

    /// Function called for every event
    virtual void ExecuteEvent( const SInputData&, Double_t ) throw( SError );

private:
    //
    // Put all your private variables here
    //
    string InTreeName;
    
    // Input Variables
%(inputVariableDeclarations)s

    //Output Variables
%(outputVariableDeclarations)s

    // Macro adding the functions for dictionary generation
    ClassDef( %(fullClassName)s, 0 );

}; // class %(class)-s
"""

    ## @short Template for a header file
    #
    # This string is used by CreateHeader to create a header file
    # once the body has already been generated
    _Template_header_Frame = """// Dear emacs, this is -*- c++ -*-
#ifndef %(capclass)-s_H
#define %(capclass)-s_H

// SFrame include(s):
#include \"core/include/SCycleBase.h\"
#include <vector>
#include <string>
using namespace std;

%(body)s

#endif // %(capclass)-s_H

"""
    ## @short Template for the body of a source file
    #
    # This string is used by CreateSource to create the body of a source file
    _Template_source_Body = """
%(class)-s::%(class)-s()
    : SCycleBase() {
    
    DeclareProperty("InTreeName", InTreeName );
    SetLogName( GetName() );
}

%(class)-s::~%(class)-s() {

}

void %(class)-s::BeginCycle() throw( SError ) {

    return;

}

void %(class)-s::EndCycle() throw( SError ) {

    return;

}

void %(class)-s::BeginInputData( const SInputData& ) throw( SError ) {

%(outputVariableConnections)s
    return;

}

void %(class)-s::EndInputData( const SInputData& ) throw( SError ) {

    return;

}

void %(class)-s::BeginInputFile( const SInputData& ) throw( SError ) {

%(inputVariableConnections)s
    return;

}

void %(class)-s::ExecuteEvent( const SInputData&, Double_t ) throw( SError ) {

%(outputVariableClearing)s

    // The main part of your analysis goes here
    
%(outputVariableFilling)s

    return;

}
"""

    ## @short Template for the frame of a source file
    #
    # This string is used by CreateSource to create a source file
    # once the main body has already been generated
    _Template_source_Frame = """
// Local include(s):
#include \"%(header)s\"

ClassImp( %(fullClassName)s );

%(body)s
"""
    _Template_LinkDef = """// Dear emacs, this is -*- c++ -*-

#ifdef __CINT__

#pragma link off all globals;
#pragma link off all classes;
#pragma link off all functions;
#pragma link C++ nestedclass;

%(new_lines)s
#endif // __CINT__
"""