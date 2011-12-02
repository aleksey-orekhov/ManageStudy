import os
from MedImage import MedImage
import string
#A NIfTI image, this adds two extensions (.nii,.nii.gz) to the MedImage class
#ToDo: more info (say from a call wrapper call to fslhd may be added)

class NIfTIImage(MedImage):

    def __init__(self, scan, folder, filename):
        super(NIfTIImage, self).__init__(scan=scan, folder=folder, filename=filename)
        self.extension = '.'.join(string.split(filename, '.')[1:])



    def __str__(self):
        outstring = 'NIfTI: %s\\%s\n' % (self.folder, self.filename)
        return outstring
