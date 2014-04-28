#!/usr/bin/env python
    
import sys
import os
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from execformat.executor import execUtils, OperationFailed
from vyos_session.utils import logger
class configOpts():

    def set(self, args):
        exe=execUtils(args)
        args.insert(0,'set')
        try:
            exe.execmd()
            return True
        except OperationFailed, e:
            logger.error(e.message)
            return False

    def delete(self, args):
        exe=execUtils(args)
        args.insert(0,'delete')
        try:
            exe.execmd()
            return True
        except OperationFailed, e:
            logger.error(e.message)
            return False
