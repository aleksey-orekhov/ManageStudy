import os
import warnings
import string
import re
from ManageFreesurferErrors import FSStudyErrors
from ManageStudy.Qsub import Qsub
import FS_Scan

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

class FS_Study(object):


    def __init__(self, study, path, fs_home):
        self.study = study
        self.path = os.path.normpath(path)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.name = study.name + ' : ' + os.path.basename(self.path)
        self.subjects_dir = os.path.normpath(os.path.join(self.path, 'freesurfer'))
        self.fs_home = fs_home
        self.__fsIDRE__ = '(% s)_(% s)' % (study.__subjectfolderRE__, study.__scanfolderRE__)#grab regex from study object
        self.__fsIDREC__ = re.compile(self.__fsIDRE__) #freesurfer subid regular expression compiled
        self.scanlist = []
        self.scans = {}
        self.qsubTemplatesDir = os.path.join(os.path.dirname(FS_Scan.__file__), 'qsubtemplates')
        self.__findScans__()

    def exists(self, scan):
        #regenerate scan list
        self.__findScans__()
        fsID = scan.subject.subid + '_' + scan.scanid
        if fsID in [fsscan.fsID for fsscan in self.scanlist]:
            return True
        return False

    #takes MedImage object, does a reconall import, and creates the FS_Scan object
    def importT1(self, image):
        #do not import image if it already exists
        if self.exists(image.scan):
            return False

        #get subject/scan info & set up template objects
        subid = image.scan.subject.subid
        scanid = image.scan.scanid
        fs_scan = self.__addscan__(subjectid=subid, scanid=scanid)

        #set up args & help text
        helptext = ('#This script was used to import the subject %(subid)s scan %(scanid)s from\n'
                       + '#%s\n' % image.path
                       + '#into FreeSurfer Analysis %(FS_Study_name)s with id %(fsID)s'
                  )
        args = ('-i %s' % image.path)
        self.recon_all(fs_scan=fs_scan, prefix='import', args=args, helptext=helptext)
        return fs_scan.fsID


    #takes MedImage object, does a reconall -all reconstruction
    def recon_all(self, fs_scan, prefix='prefix', args='RECON-ALL ARGS GO HERE!', helptext='#The helptext was not filled in'):

        #set up template objects
        reconalltemplate = os.path.join(self.qsubTemplatesDir, 'reconall.sh')
        qsub = Qsub(templatepath=reconalltemplate, scriptdir=os.path.join(self.path, 'runs_freesurfer'), qsubpath='qsub', command_args='mem_free=3.5G')

        #set up substitution dictionary
        dict = self.__buildGenericDict__(fs_scan=fs_scan, prefix=prefix, args=args, helptext=helptext)

        qsub.submit(dict)
        return True

    def __buildGenericDict__(self, fs_scan, prefix='prefix', args='RECON-ALL ARGS GO HERE!', helptext='#The helptext was not filled in'):
        dict = {'filename':prefix + '_' + fs_scan.fsID + '.sh',
                'helptext':helptext,
                'FS_Study_name':self.name,
                'FREESURFER_HOME':self.fs_home,
                'subjects_dir':self.subjects_dir,
                'recon-all_args': args,
                'subid':fs_scan.subject.subid,
                'scanid':fs_scan.scan.scanid,
                'fsID': fs_scan.fsID
                #'this_script':os.path.join(qsub.scriptdir, prefix + '_' + fs_scan.fsID + '.sh'),
                #'done_dir':os.path.join(qsub.scriptdir, 'done')
                }
        dict['helptext'] = dict['helptext'] % dict
        return dict


    def __findScans__(self):
        'Returns a list of FS_Subject objects at the subject dir'
        if not os.path.exists(self.subjects_dir):
            os.makedirs(self.subjects_dir)

        try:
            fsfiles = os.listdir(self.subjects_dir)
        except:
            warnings.warn("\nCould not list files in: " + self.subjects_dir)
            return

        self.scanlist = []
        self.scans = {}
        knownfsfiles = ['fsaverage', 'lh.EC_average', 'rh.EC_average']

        #I anticipate many subjects/study but relatively few scans per subject
        #and scans need to be run in a loop anyhow
        studysubjects = [subject.subid for subject in self.study.subjectlist]

        for fsfile in fsfiles:
            fulldir = os.path.normpath(os.path.join(self.subjects_dir, fsfile))
            if (not os.path.isdir(fulldir)):
                continue
            m = self.__fsIDREC__.match(fsfile)
            if m:
                subjectid = m.group(1)
                scanid = m.group(2)
                if subjectid in studysubjects:
                    if scanid in [scan.scanid for scan in self.study.subjects[subjectid].scanlist]:
                        self.__addscan__(subjectid=subjectid, scanid=scanid)
                    else:
                        raise FSStudyErrors.NoScanError(fsfile, subjectid, scanid, "Couldn't find Scan")
                else:
                    raise FSStudyErrors.NoSubjectError(fsfile, subjectid, "Couldn't find Subject")
            elif fsfile in knownfsfiles:
                continue
            else:
                raise Exception('could not parse ' + fsfile + '\n Should it be in this directory?\n')



    def __rm_isrunning__(self, fsID):
        isrunningpath = os.path.join(self.subjects_dir, fsID, 'scripts/IsRunning.lh+rh')
        try:
            os.remove(isrunningpath)
            print "Removed %s" % isrunningpath
        except Exception as e:
            print "Failed to remove: %s" % isrunningpath

    def __makefsID__(self, subjectid, scanid):
            return subjectid + '_' + scanid

    def __addscan__(self, subjectid, scanid):
        fsID = self.__makefsID__(subjectid, scanid)

        #get subject and scanid being referenced
        subject = self.study.subjects[subjectid]
        scan = subject.scans[scanid]

        #create new FSscan object
        newFSscan = FS_Scan.FS_Scan(self, fsID=fsID, subject=subject, scan=scan)

        #add scan to list and dictionary
        self.scanlist.append(newFSscan)
        self.scans[fsID] = newFSscan

        return newFSscan

    def __str__(self):
        self.__findScans__()
        outstring = 'Study: %s\n\t ' % self.name
        scanstrings = []
        for scan in self.scanlist:
            scanstrings.append(scan.__str__())
        scanstrings.sort()
        scanstrings = [string.replace(scanstring, '\t', '\t\t') for scanstring in scanstrings]
        outstring += '\t '.join(scanstrings)
        return outstring



