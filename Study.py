import os.path
import re
import warnings
import Subject
import string
import tarfile
import datetime
import shutil
from ManageStudyErrors import StudyErrors
#from dcmrcv import dcmrcv
import myutils

#===============================================================================
# Attr:
# study_name     -Overall Study Name
# study_dir      -freesurfer directory (folder in the study folder that contains the FS subjects directory)
# fs_folder      -freesurfer folder (folder in the study folder that contains the FS subjects directory)
# subjects_dir   -freesurfer subjects directory
# subjectlist    -list of FS_Scan objects
# subjects       -dictionary mapping to FS_Scan objects <FS_Scan>.subjects['subid_scanid'] (fs_subid)
# fs_home        -freesurfer home on machine that will be running scripts

# Methods:
# findSubjects   -locates all freesurfer subjects in subjects_dir
#===============================================================================

class Study(object):

    def __init__(self, path, subjectfolderRE='^P[0-9]+$', scanfolderRE='^S[0-9]+$', ignoredirlist=['DICOM', 'Log']):
        self.path = os.path.normpath(path)
        self.name = os.path.basename(self.path)
        self.subjects_dir = os.path.join(self.path, 'Subjects')
        self.EXsubjects_dir = os.path.join(self.path, 'ExcludedSubjects')
        self.Qsubjects_dir = os.path.join(self.path, 'Quarantine', 'Subjects')
        self.IncomingDICOM_dir = os.path.join(self.path, 'Quarantine', 'IncomingDICOM')
        self.nonconformingniilist = []
        self.nonconformingdicomlist = []
        self.__subjectfolderRE__ = subjectfolderRE
        self.__setsubjectfolderRE__(subjectfolderRE) #read in from/update config file
        self.__scanfolderRE__ = scanfolderRE
        self.__setscanfolderRE__(scanfolderRE) #read in from/update config file
        self.__ignoredirlist__ = ignoredirlist
        self.__setexcludedscanfolders__(ignoredirlist)
        self.__imageRE__ = '_'.join(['(' + self.__subjectfolderRE__ + ')', '(' + self.__scanfolderRE__ + ')', '(.*?)$'])
        self.__imageREC__ = re.compile(self.__imageRE__)
        (self.subjectlist, self.subjects) = self.__findSubjects__(self.subjects_dir)
        (self.EXsubjectlist, self.EXsubjects) = self.__findSubjects__(self.EXsubjects_dir)
        (self.Qsubjectlist, self.Qsubjects) = self.__findSubjects__(self.Qsubjects_dir)

#    def setdcmrcv(self, AETitle, port):
#        self.dcmrcv = dcmrcv(AETitle, port, RCVDIR=os.path.join(self.path, 'DICOM'))

    def __setsubjectfolderRE__(self, subjectfolderRE):
        configdir = os.path.join(self.path, 'Config')
        configfile = os.path.join(configdir, 'main.cfg')
        parser = myutils.parseConfig(configdir, configfile)

        if not parser.has_section('Subject'):
            parser.add_section('Subject')
        if not parser.has_option('Subject', 'subjectfolderRE') or subjectfolderRE != self.__subjectfolderRE__:
            parser.set('Subject', 'subjectfolderRE', subjectfolderRE)
            self.__subjectfolderRE__ = subjectfolderRE
        else:
            self.__subjectfolderRE__ = parser.get('Subject', 'subjectfolderRE')
        with open(configfile, 'wb') as mainconfig:
            parser.write(mainconfig)
        self.__subjectfolderREC__ = re.compile(self.__subjectfolderRE__)

#TODO: clean up code..just split this into public and private methods..no one wants to change the regex here anyhow.

    def __setscanfolderRE__(self, scanfolderRE):
        configdir = os.path.join(self.path, 'Config')
        configfile = os.path.join(configdir, 'main.cfg')
        parser = myutils.parseConfig(configdir, configfile)

        if not parser.has_section('Scan'):
            parser.add_section('Scan')
        if not parser.has_option('Scan', 'scanfolderRE') or scanfolderRE != self.__scanfolderRE__:
            parser.set('Scan', 'scanfolderRE', scanfolderRE)
            self.__subjectfolderRE__ = scanfolderRE
        else:
            self.__scanfolderRE__ = parser.get('Scan', 'scanfolderRE')
        with open(configfile, 'wb') as mainconfig:
            parser.write(mainconfig)
        self.__scanfolderREC__ = re.compile(self.__scanfolderRE__)

    def __setexcludedscanfolders__(self, ignoredirlist):
        configdir = os.path.join(self.path, 'Config')
        configfile = os.path.join(configdir, 'main.cfg')
        parser = myutils.parseConfig(configdir, configfile)

        if not parser.has_section('Scan'):
            parser.add_section('Scan')
        if not parser.has_option('Scan', 'ignoredirlist') or ignoredirlist != self.__ignoredirlist__:
            parser.set('Scan', 'ignoredirlist', '|'.join(ignoredirlist))
            self.__ignoredirlist__ = ignoredirlist
        else:
            self.__ignoredirlist__ = parser.get('Scan', 'ignoredirlist').split('|')
        with open(configfile, 'wb') as mainconfig:
            parser.write(mainconfig)

    def __findSubjects__(self, subjects_dir):
        '''takes subjects_dir and returns a list and hash of subject objects for all the folders inside 
        as (subjectlist,subjectdict)=__findSubjects__(subjects_dir)'''

        if not os.path.exists(subjects_dir):
            os.makedirs(subjects_dir)

        try:
            subjectFiles = os.listdir(subjects_dir)
        except:
            warnings.warn("\nCould not list files in: " + self.subjects_dir)
            return

        subjectlist = []
        subjectdict = {}

        for file in subjectFiles:
            fulldir = os.path.join(subjects_dir, file)
            if (not os.path.isdir(fulldir)):
                continue
            m = self.__subjectfolderREC__.match(file)
            if m:
                newsubject = Subject.Subject(self, m.group(0))
            else:
                raise Exception('could not parse ' + file + '\n Should it be in this directory?\n')
            subjectlist.append(newsubject)
            subjectdict[newsubject.subid] = newsubject
        return (subjectlist, subjectdict)


    def addSubjects(self, subids, warn):
        for subid in subids:
            self.addSubject(subid, warn)

    def addSubject(self, subid, warn=False):
        m = self.__subjectfolderREC__.match(subid)
        if not m:
            warnings.warn('Did not create subject with subid ' + subid + '\n::Subject Regex did not match.\n' + 'Regex:: ' + self.__subjectfolderRE__)
            return False
        elif subid not in self.subjects:
            newsubject = Subject.Subject(self, subid)
            self.subjectlist.append(newsubject)
            self.subjects[newsubject.subid] = newsubject
            return True
        elif warn == True:
            warnings.warn('Did not create subject with subid ' + subid + '::Already Exists.')
            return False

    def removeSubject(self, subject):
        '''archives and removes a subject dir'''

        recycledir = os.path.join(self.path, 'Recycling')
        if not os.path.exists(recycledir):
            os.makedirs(recycledir)

        if os.path.exists(subject.path):
            filename = os.path.join(recycledir, 'Subject' + subject.subid + datetime.datetime.now().__str__() + '.tar.gz')
            arcname = os.path.join('Subjects', subject.subid)
            with tarfile.open(filename, "w:gz") as tar:
                tar.add(name=subject.path, arcname=arcname)
            shutil.rmtree(subject.path)
            return True
        else:
            raise StudyErrors.DeleteSubjectError(subid=subject.subid, description="Directory does not exist")
            return False

    def wipenonconformingNiis(self):
        if (raw_input("Are you sure?: ") == 'YES'):
            for niftipath in self.nonconformingniilist:
                print "Deleting %s" % niftipath
                os.unlink(niftipath)
            self.nonconformingniilist = []


    def __str__(self):
        outstring = 'Study: %s\n\t' % self.name
        for subject in self.subjectlist:
            outstring += '%s' % string.replace(subject.__str__(), '\n', '\n\t')
        if len(self.nonconformingniilist) > 0:
            outstring += "\nWARNING: Nonconforming NIfTI File Names Found\n"
            outstring += '\n'.join(self.nonconformingniilist) + '\n'
        if len(self.nonconformingdicomlist) > 0:
            outstring += "\nWARNING: Nonconforming DICOM Folder Names Found\n"
            outstring += '\n'.join(self.nonconformingdicomlist) + '\n'
        return outstring[0:-1]

