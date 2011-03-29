#!/usr/bin/env bash


#Set up the environment variables needed by xrootd
function gridenv {
	export X509_CERT_DIR=/opt/local/nordugrid/etc/grid-security/certificates/
	export X509_USER_PROXY=$(arcproxy -I|grep ^Proxy | head -1 |sed 's/Proxy .*: //')
}

#make a new gridproxy.
#This may require user input if the userkey is encrypted.
#user key encryption can be removed by:
#	openssl rsa -in userkey.pem -out userkey.pem.new
function gridproxy {
	if ! test -d $HOME/.arc/vomses
	then
		echo \"atlas\" \"voms.cern.ch\" \"15001\" \"/DC=ch/DC=cern/OU=computers/CN=voms.cern.ch\" \"atlas\" > $HOME/.arc/vomses
	fi
	arcproxy -S atlas
	gridenv
}

#check if a new grid proxy is needed
#if there already is a proxy, just set up the environment.
function gridcheck {
	if [ "x$(arcproxy -I 2>&1|grep ^ERROR)" = x ]
	then
		echo $(arcproxy -I 2>&1|grep ^Timeleft | sed 's/Timeleft for AC: /Grid Proxy expires in /')
		gridenv
	else
		if [ x"$(grep ENCRYPTED $HOME/.globus/userkey.pem)" = x ]
		then
			echo "No Grid Proxy found. Making one."
			gridproxy
			gridenv
		else
			echo "No Grid Proxy found. Make one by typing \"gridproxy\""
		fi		
	fi
}

