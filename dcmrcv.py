import os
import subprocess

#you will probably make 1 template instance and use it many times

class dcmrcv(object):
    def __init__(self, AETitle, port, RCVDIR, dcmrcvpath='dcmrcv'):
        self.AETitle = AETitle
        self.port = port
        self.RCVDIR = RCVDIR #directory where DICOM images are placed
        self.args = [dcmrcvpath, self.AETitle + ':' + self.port, '-dest', self.RCVDIR, '-rspTO', '6000000', '-requestTO', '6000000', '-acceptTO', '6000000', '-idleTO', '6000000']
        self.__checkdirs__()

    def listen(self):
        #open template and output file

        #execute script
        print "Executing %s" % ' '.join(self.args)
        p = subprocess.Popen(self.args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if stderr != '':
            print "DCMRCV Error: %s" % stderr
        print stdout

    def __checkdirs__(self):
        if not os.path.exists(self.RCVDIR):
            os.makedirs(self.RCVDIR)


    def __str__(self):
        return ' '.join(self.args)
