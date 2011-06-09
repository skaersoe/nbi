#!/usr/bin/env python
# encoding: utf-8


import sys
import getopt
import os
import re


import shlex, subprocess
from getpass import getpass

import datetime
import time

from xml.parsers import expat




class xml_process:
    def __init__(self,the_data,fields=[],keep_prefix=0,keep_attr=0):
        self.results=[]
        self.cur_name=None
        self.tmp=[]
        self.the_data=the_data
        self.p=expat.ParserCreate()
        self.p.StartElementHandler=self.start
        self.p.EndElementHandler=self.end
        self.p.CharacterDataHandler=self.data
        self.fields=fields
        self.keep_prefix=keep_prefix
        self.keep_attr=keep_attr
    def clean(self,data):
        tmp=''.join(data)
        return ' '.join(tmp.split())
    def start(self,name,attrs): 
        if not self.cur_name: self.cur_name=name
        tmp_name=self.cur_name
        if not self.keep_prefix:
            if self.cur_name[1]==':': tmp_name=self.cur_name[2:]
        self.attrs=attrs
        if name != self.cur_name:
            if not self.attrs or not self.keep_attr:
                if not self.fields or tmp_name.lower() in self.fields:
                    self.results.append( {tmp_name:self.clean(self.tmp)})
            else:
                if not self.fields or tmp_name.lower() in self.fields:
                 self.results.append( { tmp_name:{self.clean(self.tmp):attrs}})
            self.tmp=[]
            self.cur_name=name
    def data(self,info):  self.tmp.append(info)
    def end(self,name): pass
    def parse(self):
        if 'xml' not in self.the_data[0:50].lower(): return []
        self.p.Parse(self.the_data,1)
        results=self.results
        if self.fields:
            filter_cache={}
            results=[{}]
            
            for i in self.fields: filter_cache[i]=None
            for row in self.results:
                k,v=row.items()[0]
                #check if filter_cache is full
                full=0
                for i in filter_cache:
                    if not filter_cache[i]:
                        filter_cache[i]=1
                        full=0;break
                    full=1
                if full:
                    for i in self.fields: filter_cache[i]=None
                    full=0
                    results.append({})
                if k not in results[-1]:
                    results[-1][k]=v
        return results
        
class T3Tools(object):
    """Tier 3 tools for CPH_Storagelemeent"""
    
    BASE_SERVER_URL_XROOT = "root://ftp1.ndgf.org"
    BASE_SERVER_URL = "https://ftp1.ndgf.org:2881"
    BASE_URL = "https://ftp1.ndgf.org:2881/atlas/disk/atlaslocalgroupdisk/dk%s"
    BASE_URL_STR = "https://ftp1.ndgf.org:2881/atlas/disk/atlaslocalgroupdisk/dk"
    BASE_URL_PATH = "/atlas/disk/atlaslocalgroupdisk/dk"
    
    help_message = '''
    List folders on the Tier 3 storage element.
    Author: Morten Dam Jørgensen, 2011.

    Flags: 

        -l :    Print date modified, file size and filenames (default)
        -x :    Print SFrame XML input lines
        -f :    Print full path
        -r :    Print xroot path

    Examples:
    	t3ls /user/username
    	t3ls -f /user/

        Base url: %s
        xroot base: %s
    ''' % (BASE_URL_STR, BASE_SERVER_URL_XROOT + BASE_URL_PATH)
    
    def __init__(self, pw="", auto_completer=False):
		super(T3Tools, self).__init__()
		
		self.auto_completer = auto_completer
		self.flags = ""
		self.homedir = os.path.expanduser('~')
		try:
		    pw_file = open("%s/.globus/t3password" % self.homedir, "r")
		    self.pw = pw_file.read()
		    pw_file.close()
		except:
		    try:
		        if open("%s/.globus/userkey.pem" % self.homedir, "r").read().find("ENCRYPTED") == -1:
		            self.pw = ""
		        else:
		            self.pw = getpass("Enter GRID password: ")
		            
		    except:
		        self.pw = getpass("Enter GRID password: ")
		  


    def t3ls(self, remote ):
        """List Structure"""
        path_org = remote
        path = self.BASE_URL % remote.replace(self.BASE_URL_STR, "")
        
        exe = 'curl -ks --cert %s/.globus/usercert.pem:%s --key %s/.globus/userkey.pem  --data "<xml>" --header "Depth: 1" --header "Content-Type: text/xml" --request PROPFIND %s' % (self.homedir, self.pw, self.homedir, path)
        a = subprocess.Popen(shlex.split(exe), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        text =  a.communicate()[0]

        result=xml_process(text)
        result2=[]

        ou = dict()
        size_buff_len = 0
        for i in result.parse(): ## Loop over parsed data
            if i.has_key('status'):
                ou = {"name" : None, "size" : None, "modified": None}
                ou["status"] = i["status"]
                
            if i.has_key("getcontenttype"):
                ou["contenttype"] = i["getcontenttype"]
        
            if i.has_key('getetag'):
	            ou["etag"] = i["getetag"]
	            result2.append(ou)
                
            if i.has_key('href'):
                ou["name"] = i["href"].replace(path, "").replace("//", "/")    
            if i.has_key("getcontentlength"):
                if not i[u'getcontentlength'] == "":
                    ou["size"] =  int(i[u'getcontentlength'])
                    size_buff_len = max(size_buff_len, len(str(int(i[u'getcontentlength'])/1000000)))
                else:
                    ou["size"] = 0
					
            if i.has_key('getlastmodified'):
			    ou["modified"] = i[u'getlastmodified']

            if i.has_key('creationdate'):
			    ou["creationdate"] = i[u'creationdate']
			                
            
        if self.auto_completer:
            out = []
            out.append(path_org)
            for line in result2:
                l = line["name"].replace(self.BASE_URL_PATH, "")
                l.replace(path_org, "")
                out.append(l)

            return out
            
        for line in result2:
            dm = datetime.datetime.fromtimestamp(time.mktime(time.strptime(line["modified"], "%a, %d %b %Y %H:%M:%S %Z")))

            if "f" in self.flags: # Full path listing
                print "%s%s" % (self.BASE_SERVER_URL, line["name"])
            elif "r" in self.flags: # xpath path listing
                if len(line["name"]) > 1 and not line["name"][-1] == "/":
                    print '%s%s' % (self.BASE_SERVER_URL_XROOT, line["name"])
            
            elif "x" in self.flags or "X" in self.flags:
                if len(line["name"]) > 1 and not line["name"][-1] == "/":
                    print '<In FileName="%s%s" Lumi="1.0" />' % (self.BASE_SERVER_URL_XROOT, line["name"])
            else:

                if hasattr(str(), "format"): # Check if we can use the str.format() method (available in Python > 2.6)
                    print ("{0}  {1:>%d} MB  {2}" % (size_buff_len)).format(str(dm), line["size"]/1000000,line["name"].replace(self.BASE_URL_PATH, ""))# line["name"][line["name"].find("/user/"):])
                else:
                    # Fallback to old string formatting style (ugly)
                    print "%s\t%s MB\t%s" % (str(dm), line["size"]/1000000, line["name"].replace(self.BASE_URL_PATH, "")) 



    def t3get(self, remote, local, overwrite=False):
        """Download file"""

        filename = self.BASE_URL % remote.replace(self.BASE_URL_STR, "")
        
        d = local.split("/")  # In case of . as output, use the input file name (not very safe)
        if d[-1] == ".":
            d[-1] = filename.replace(self.BASE_URL_STR, "").split("/")[-1]
        local = "/".join(d)

        exe = 'curl -k --location-trusted --cert %s/.globus/usercert.pem:%s --key %s/.globus/userkey.pem %s -o %s' % (self.homedir, self.pw, self.homedir, filename, local)

        a = subprocess.Popen(shlex.split(exe), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        resp = a.communicate()[0]

        return resp
    
    
    def local_ls(self, local):
        """Local lookup"""
        # from glob import glob
        # print glob(local)
        # print "local" + str(os.listdir(os.path.expanduser(local)))
        if os.path.isdir(local) or os.path.isfile(local):
            return os.listdir(os.path.expanduser(local))
        else:
            return []
        
    def autocompleter(self, args):
        """docstring for autocompleter"""
        self.auto_completer = True # Override user flags
        
        command = args[1]
        last_complete_string = args[-2]
        second_last_string = args[-1]
            
        args_line = re.sub("\s+", " ", os.environ["COMP_LINE"])
        args_line = args_line.split(" ")
        if command == "t3ls":
            return self.t3ls(last_complete_string[0:last_complete_string.rfind("/")+1])
            
        elif command == "t3get":
            if len(args_line) == 2:
                return self.t3ls(args_line[-1][0:args_line[-1].rfind("/")+1])
            # print args_line
            elif len(args_line) == 3:
                # local completion
                return self.local_ls(args_line[-1][0:args_line[-1].rfind("/")+1])
                
        else:
            return []
        

        # method = getattr(self, command)
        # 
        # method_arguments =  inspect.getargspec(method)
        # n_inp_args =  len(method_arguments.args) -1
        # print n_inp_args, single_input  
        # return method(complete_string[0:complete_string.rfind("/")+1])
        return []

def main():
    inval = sys.argv[-2]

    # args_line = re.sub("\s+", " ", os.environ["COMP_LINE"])
    # args_line = args_line.split(" ")
    # inval = args_line[-1]

    # Initialise T3Tools for autocompletion

    t = T3Tools()
    words = t.autocompleter(sys.argv)
    print words
    possibles = []
    for word in words:
        if word.find(inval) == 0:
	        possibles.append(word)

    if not possibles:
		return

    if len(possibles)==1:
        if not possibles[0][-1] == "/":
            print possibles[0] + " "
        else:
            print possibles[0]            
        return

	
    import os.path
    lcp = os.path.commonprefix(possibles)
    if lcp==inval:
        for word in possibles:
            print word
    else:
        print lcp

if __name__ == '__main__':
    main()