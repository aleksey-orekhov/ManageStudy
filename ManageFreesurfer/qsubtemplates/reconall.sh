#!/bin/bash
#%(filename)s
#%(helptext)s
FREESURFER_HOME=%(FREESURFER_HOME)s  #/usr/local/freesurfer #derived from run<study>.py file
source $FREESURFER_HOME/SetUpFreeSurfer.sh  #/usr/local/freesurfer/SetUpFreeSurfer.sh  
export SUBJECTS_DIR=%(subjects_dir)s
recon-all %(recon-all_args)s -subjid %(fsID)s

