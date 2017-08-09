# -*- coding: utf-8 -*-

#
# Author: water - waterlzj@gmail.com
#
# Last modified: 2017-07-31 06:19 +0800
#
# Description: 
#

import logging
import logging.handlers

logger = logging.getLogger()

def initLogger():
    global logger

    # fmt = logging.Formatter("%(asctime)s - %(pathname)s - %(filename)s - %(funcName)s - %(lineno)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")  
    fmt = logging.Formatter("[%(asctime)s] %(levelname)s [%(filename)s,line%(lineno)s,%(funcName)s] %(message)s", "%Y-%m-%d %H:%M:%S")

    fileHandler = logging.handlers.TimedRotatingFileHandler("../log/worker", 'H', 1, 0)
    fileHandler.suffix = "%Y%m%d-%H:%M.log"
    fileHandler.setFormatter(fmt)
    logger.addHandler(fileHandler)
    
    #cnslHandler = logging.StreamHandler()
    #cnslHandler.setFormatter(fmt)
    #logger.addHandler(cnslHandler)

    logger.setLevel(logging.DEBUG)
    logger.debug("logger init")




