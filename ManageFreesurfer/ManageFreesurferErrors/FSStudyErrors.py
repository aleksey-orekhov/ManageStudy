
class NoSubjectError(Exception):
    def __init__(self, fsfile, subid, description='NoSubjectError'):
        self.fsfile = fsfile
        self.subid = subid
        self.description = description
    def __str__(self):
        infostring = "%s: Couldn't find subject %s for fsfile %s" % (self.description, self.subid, self.fsfile)
        return infostring

class NoScanError(Exception):
    def __init__(self, fsfile, subid, scanid, description='NoScanError'):
        self.fsfile = fsfile
        self.subid = subid
        self.scanid = scanid
        self.description = description
    def __str__(self):
        infostring = "%s: Couldn't find scanid %s in scanlist of subject %s for fsfile %s" % (self.description, self.scanid, self.subid, self.fsfile)
        return infostring

