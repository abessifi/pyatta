#!/usr/bin/env python
    
import sys
import os
import logging
topdir = os.path.dirname(os.path.realpath(__file__)) + "../.."
topdir = os.path.realpath(topdir)
sys.path.insert(0, topdir)
from execformat.executor import execUtils, OperationFailed
from vyos_session import utils 

logger = logging.getLogger(__name__)
utils.init_logger(logger)

class configOpts():

    def set(self, args):
        args.insert(0,'set')
        exe=execUtils(list(args))
        try:
            exe.execmd()
            return True
        except OperationFailed, e:
            logger.error(e.message)
            return False

    def delete(self, args):
        args.insert(0,'delete')
        exe=execUtils(list(args))
        try:
            exe.execmd()
            return True
        except OperationFailed, e:
            logger.error(e.message)
            return False
