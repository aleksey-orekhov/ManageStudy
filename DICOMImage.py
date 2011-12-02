import os
from MedImage import MedImage

#A dicom image, in this case, is actual a folder containing the dicoms.
#It retains a count of the number of dicoms, in addition to it's other functionality

class DICOMImage(MedImage):

    def __init__(self, scan, folder, filename):
        super(DICOMImage, self).__init__(scan=scan, folder=folder, filename=filename)
        self.numdicoms = len(os.listdir(self.path))

    def __str__(self):
        outstring = 'DICOM: %4d files at %s%s%s\n' % (self.numdicoms, self.folder, os.sep, self.filename)
        return outstring
