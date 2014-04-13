#!/usr/bin/env python
    
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from ExecFormat.execformat import execUtils
from VyosSessionConfig.configsession import ConfigSession
class config_opt():
    exe=execUtils()
    CS=ConfigSession()

    def set(self, args):
        self.CS.setup_config_session()
        args.insert(0,'set')
        self.exe.execmd(args) 
        self.CS.teardown_config_session()

    def delete(self, args):
        self.CS.setup_config_session()
        args.insert(0,'delete')
        self.exe.execmd(args)
        self.CS.teardown_config_session()
