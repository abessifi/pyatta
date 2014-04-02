#!../bin/python
    
import sys
sys.path.append('../')
from ExecFormat import ExecutorFormator

class config_opt():
    execformat=ExecutorFormator()

    def set(self, args):
        self.execformat.call(args,"set")

    def delete(self, args):
        self.execformat.call(args,"delete")
