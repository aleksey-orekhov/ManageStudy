import Scan
import os.path
import warnings

import string

class Subject(object):

    def __init__(self, study, subid):
        self.study = study
        self.subid = subid
        self.path = os.path.join(self.study.subjects_dir, subid)
        self.scanlist = []
        self.scans = {}
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.findScans()

    def findScans(self):
        'Returns a list of Scan objects at the subject dir'

        try:
            scanFiles = os.listdir(self.path)
        except:
            warnings.warn("\nCould not list files in: " + self.path)
            return

        for file in scanFiles:
            fulldir = os.path.join(self.path, file)
            if (not os.path.isdir(fulldir)):
                continue
            m = self.study.__scanfolderREC__.match(file)
            if m:
                newscan = Scan.Scan(self, m.group(0))
            else:
                raise Exception('could not parse ' + fulldir + '\n with regex\n' + self.study.scanfolderRE + '\n Should it be in this directory?\n')
            self.scanlist.append(newscan)
            self.scans[newscan.scanid] = newscan

    def addScan(self, scanid, warn=False):
        m = self.study.__scanfolderREC__.match(scanid)
        if not m:
            warnings.warn('Did not create scan with scanid ' + scanid + '\n::Scan Regex did not match.\n' + 'Regex:: ' + self.study.scanfolderRE)
            return False
        if (scanid not in self.scans):
            newscan = Scan.Scan(self, scanid)
            self.scanlist.append(newscan)
            self.scans[newscan.scanid] = newscan
            return True
        elif warn == True:
            warnings.warn('Did not create scan with scanid ' + scanid + '::Already Exists.')
            return False


    def __str__(self):
        outstring = 'Subject: %s\n\t' % self.subid
        for scan in self.scanlist:
            outstring += '%s' % string.replace(scan.__str__(), '\n', '\n\t')
        return outstring[0:-1]


