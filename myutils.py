import os
from ConfigParser import SafeConfigParser


def parseConfig(configdir, configfile): #configfile=main.cfg
    if not os.path.exists(configdir):
        os.makedirs(configdir)
    if not os.path.exists(configfile): #create config file if it doesn't exist
        f = open(configfile, 'w')
        f.close()

    parser = SafeConfigParser()
    confighandle = open(configfile, 'r')
    parser.readfp(confighandle, configfile)
    confighandle.close()

    return parser
