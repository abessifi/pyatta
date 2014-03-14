#!../bin/python

import sys
sys.path.append('../')
import subprocess
from subprocess import CalledProcessError
import os
import logging
from  VyosSessionConfig import sessionconfig


class EmptyName(Exception): pass

class ExecutorFormator():
	
	SessConf = sessionconfig()
	shell_api_path = SessConf.set_config_params('bin','shell_api_path')
	vyatta_sbindir = SessConf.set_config_params('bin','vyatta_sbindir')
	logfile=SessConf.set_config_params('log','filename')
	logging.basicConfig(filename=logfile, level=logging.DEBUG)
	
	def join_args(self,args,sep=" "):
                return sep.join(args)

	def call(self, args, name=""):
                if len(name) == 0:
                        raise EmptyName("ERROR: operation name is required !")

                if name=="save":
                        cmd1 = os.path.join(self.vyatta_sbindir,"vyatta-save-config.pl")

                else:
                        cmd1 = os.path.join(self.vyatta_sbindir,"my_"+name)+" "+self.join_args(args)

		cmd = self.SessConf.setup_config_session(self.shell_api_path)+cmd1+"\n"+self.shell_api_path+" teardownSession"
		logging.debug("current cmd = \n%s" % cmd)
                try:
			subprocess.check_output(cmd, shell=True)
		except CalledProcessError:
			logging.debug("""ERROR:  invalid operation \ncheck session\'s 
state or the operation format """)

	def show(self,args):
                cmd = self.shell_api_path+" showCfg"+" "+self.join_args(args)
		output=subprocess.check_output(cmd, shell=True)
                logging.debug("\n%s" % output)
                return output


	def parse_show(self):
		pass


	def commit(self):
                self.call([], name="commit")

        def save(self):
                self.call([], name="save")

        def discard(self):
                self.call([], name="discard")



#obj = ExecutorFormator()
#def set(args):
#       	obj.call(args, name="set")
	
#set(["service", "dns", "forwarding","listen-on", "eth0" ])
#obj.commit()
#obj.show(["service","dns"])

