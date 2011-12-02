import os.path

class FS_Scan:

    def __init__(self, fsstudy, fsID, subject, scan):
        self.fsstudy = fsstudy
        self.fsID = fsID
        self.subject = subject #link to related subject object
        self.scan = scan #link to related scan object
        self.path = os.path.join(fsstudy.subjects_dir, fsID)

    def __str__(self):
        outstring = 'FS Scan: %s\n' % self.fsID
        #for scan in self.scanlist:
        #    outstring += '\t %s' % string.replace(scan.__str__(), '\t', '\t\t')
        return outstring


