import os
from MedImage import MedImage
import string
#A NIfTI image, this adds two extensions (.nii,.nii.gz) to the MedImage class
#ToDo: more info (say from a call wrapper call to fslhd may be added)

class NIfTIImage(MedImage):

    def __init__(self, scan, folder, filename):
        filenamesplit = string.split(filename, '.')
        if filenamesplit[-1] == 'nii':
            self.extension = filenamesplit[-1]
            basename = '.'.join(filenamesplit[:-1])
        else:   #.nii.gz
            self.extension = '.'.join(filenamesplit[-2:])
            basename = '.'.join(filenamesplit[:-2])
        super(NIfTIImage, self).__init__(scan=scan, folder=folder, filename=filename, basename=basename)



    def __str__(self):
        outstring = 'NIfTI: %s\\%s\n' % (self.folder, self.filename)
        return outstring
