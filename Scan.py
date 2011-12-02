import os
import shutil #for file copying
from ManageStudyErrors import ScanErrors
import tarfile
import datetime
from NIfTIImage import NIfTIImage
from DICOMImage import DICOMImage
import string
import warnings
from collections import defaultdict

class Scan(object):

    def __init__(self, subject, scanid):
        self.subject = subject
        self.scanid = scanid
        self.path = os.path.join(self.subject.path, scanid)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.niftilist = []
        self.niftis = defaultdict(dict)
        self.__checkdirs__()
        self.__findNIfTIData__()
        self.dicomlist = []
        self.dicoms = {}
        self.__findDICOMData__()


    def __checkdirs__(self):
        self.logdir = os.path.join(self.path, 'logs')
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)
        Quarantine = os.path.join(self.path, 'Quarantine')
        if not os.path.exists(Quarantine):
            os.makedirs(Quarantine)


    def __findNIfTIData__(self):
        'Returns a list of Scan objects at the subject dir'

        try:
            Files = os.listdir(self.path)
            Files = [folder for folder in Files if folder not in self.subject.study.__ignoredirlist__]
        except:
            warnings.warn("\nCould not list files in: " + self.path)
            return

        self.niftilist = []
        self.niftis = defaultdict(dict)

        for folder in Files:
            folderdir = os.path.join(self.path, folder)
            if (not os.path.isdir(folderdir)):
                continue
            try:
                seriesfiles = os.listdir(folderdir)
            except:
                warnings.warn("\nCould not list files in: " + folderdir)
                return

            for seriesfile in seriesfiles:
                fullseriespath = os.path.join(folderdir, seriesfile)
                if (not os.path.isfile(fullseriespath)):
                    continue
                else:
                    filenamesplit = string.split(seriesfile, '.')
                    if filenamesplit[1].lower() != 'nii':
                        continue
                    elif self.subject.study.__imageREC__.match(filenamesplit[0]):
                        newimage = NIfTIImage(self, folder=folder, filename=seriesfile)
                        self.niftilist.append(newimage)
                        self.niftis[folder][newimage.series] = newimage
                    else:
                        self.subject.study.nonconformingniilist.append(fullseriespath)

    def __findDICOMData__(self):
        'Returns a list of Scan objects at the subject dir'

        self.dicomdir = os.path.join(self.path, 'DICOM')
        if not os.path.exists(self.dicomdir):
            os.makedirs(self.dicomdir)

        self.dicomlist = []
        self.dicoms = {}

        dicomdir = os.path.join(self.path, 'DICOM')
        try:
            seriesfolders = os.listdir(dicomdir)
        except:
            warnings.warn("\nCould not list files in: " + dicomdir)
            return

        for seriesfolder in seriesfolders:
            fullseriespath = os.path.join(dicomdir, seriesfolder)
            if (not os.path.isdir(fullseriespath)):
                continue
            elif self.subject.study.__imageREC__.match(seriesfolder):
                newimage = DICOMImage(self, folder='DICOM', filename=seriesfolder)
                self.dicomlist.append(newimage)
                self.dicoms[newimage.series] = newimage
            else:
                self.subject.study.nonconformingdicomlist.append(fullseriespath)



    #===========================================================================
    # Utility Methods
    #===========================================================================

    def importNii(self, niftilocation, folder, series, override=False):
        '''Imports *.nii file into current scan's source folder
        folder => T1,T2,PET,CT
        series => V1,V2,PET,CT,Sternberg,etc'''

        #check niftilocation to make sure file is nii
        locationsplit = string.split(os.path.basename(os.path.normpath(niftilocation)), '.')
        if len(locationsplit) < 2:
            raise ScanErrors.UnknownFileException(niftilocation, locationsplit, "niftilocation: nifti filename is too short:: length is %d:: %g Too Short!" % (len(locationsplit)))
        if locationsplit[1].lower() != 'nii':
            raise ScanErrors.ImportNiiError(niftilocation, description="File is not a nii")

        #make destination dir if needed
        destdir = os.path.join(self.path, folder)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        filename = NIfTIImage.makebasename(self, series) + '.' + '.'.join(locationsplit[1:])
        destfile = os.path.join(destdir, filename)
        print "\nSOURCEFILE::::" + niftilocation
        print "DESTFILE::::" + destfile
        if (override == True) or not os.path.exists(destfile):
            shutil.copyfile(niftilocation, destfile)
            newimage = NIfTIImage(self, folder=folder, filename=filename)
            self.niftilist.append(newimage)
            self.niftis[folder][series] = newimage
            return True
        else:
            raise ScanErrors.ImportNiiError(niftilocation, destfile, "File exists and override False")
            return False



    def removeNii(self, folder, series):
        '''
        Removes all Nii Files matching type (now folder) and basename (now filename)
        for the given scan
        '''
        recycledir = os.path.join(self.subject.study.path, 'Recycling')
        if not os.path.exists(recycledir):
            os.makedirs(recycledir)
        mydatetime = datetime.datetime.now().__str__()
        matchfound = False
        deleted = False
        newimagelist = []
        for image in self.niftilist:
            deleted = False
            if image.folder == folder and image.series == series:
                matchfound = True
                tarpath = os.path.join(recycledir, 'nii' + self.subject.subid + self.scanid + folder + series + mydatetime + '.tar.gz')
                filenameinarchive = os.path.join('Subjects', self.subject.subid , self.scanid, image.folder, image.basename)
                with tarfile.open(tarpath, "w:gz") as tar:
                    if os.path.exists(image.path):
                        tar.add(name=image.path, arcname=filenameinarchive)
                        os.unlink(image.path)
                        del self.image[image.folder][image.series]
                        deleted = True
                    else:
                        raise ScanErrors.DeleteNiiError(niiname=image.path, description="File does not exist")
            if not deleted:
                newimagelist.append(image)
                self.image[image.folder][image.series] = image
        if not matchfound:
            raise ScanErrors.DeleteNiiError(niiname=image.path, description="No matching Images found")
        self.niftilist = newimagelist

    def importDICOM(self, dicomlocation, series, override=False):

        dicomfilename = os.path.basename(os.path.normpath(dicomlocation))

        #make destination dir if needed
        destdir = os.path.join(self.path, 'DICOM')
        foldername = DICOMImage.makebasename(self, series)
        destfolder = os.path.join(destdir, foldername)
        destfile = os.path.join(destfolder, dicomfilename)
        if not os.path.exists(destfolder):
            print "Making dir %s" % destfolder
            os.makedirs(destfolder)
            newimage = DICOMImage(self, folder='DICOM', filename=foldername)
            self.dicomlist.append(newimage)
            self.dicoms[series] = newimage
        if (override == True) or not os.path.exists(destfile):
            shutil.copyfile(dicomlocation, destfile)
            return True
        else:
            print "File %s exists and override False" % destfile
            return False

    def __str__(self):
        outstring = 'Scan: %s\n\t' % self.scanid
        for image in self.niftilist:
            outstring += '%s' % string.replace(image.__str__(), '\n', '\n\t')
        for image in self.dicomlist:
            outstring += '%s' % string.replace(image.__str__(), '\n', '\n\t')
        return outstring[0:-1]


