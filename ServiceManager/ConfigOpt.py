#!../bin/python

import sys
sys.path.append('../')
from ExecFormat import ExecutorFormator

class config_opt():
	execformat=ExecutorFormator()

	def set(self, args):
                self.execformat.call(args, name="set")
		#self.execformat.commit()
		#self.execformat.show(["service","dhcp-server","shared-network-name POOL3"])

        def delete(self, args):
                self.execformat.call(args, name="delete")
		#self.execformat.commit()
		#self.execformat.show(["service","dns"])


