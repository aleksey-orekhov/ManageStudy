import os
import string


class MedImage(object):

    def __init__(self, scan, folder, filename):
        self.scan = scan
        self.folder = folder
        self.basename = string.split(filename, '.')[0]
        self.series = string.replace(self.basename, self.scan.subject.subid + '_' + self.scan.scanid + '_', '')
        self.filename = filename
        self.path = os.path.join(self.scan.path, self.folder, self.filename)

    @staticmethod
    def makebasename(scan, series):
        return '_'.join([scan.subject.subid, scan.scanid, series])

    def __str__(self):
        outstring = 'Image: %s\\%s\n' % (self.folder, self.filename)
        return outstring

