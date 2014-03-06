#!../bin/python

import os
import logging
import ConfigParser
#import ExecuterFormatter

class sessionconfig:

	shell_api_path = set_config_params('bin','shell_api_path')

	def set_config_params(self,tag,key):
		config = ConfigParser.SafeConfigParser()
		config.readfp(open('../VyosApi.conf'))
		return config.get(tag,key)

	def setup_config_session(self):
                return ("""
			session_env=$(%s getSessionEnv $PPID) 
			eval $session_env 
			%s setupSession

			%s inSession
			if [ $? -ne 0 ]; then
        		echo "Something went wrong!"
			fi
		""" % (self.shell_api_path,self.shell_api_path,self.shell_api_path))

	def commit(self):
                call([], name="commit")

	def save(self):
                call([], name="save")

	def discard():
		call([], name="discard")
