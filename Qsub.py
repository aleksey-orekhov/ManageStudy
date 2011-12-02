import os
import subprocess

#you will probably make 1 template instance and use it many times

class Qsub(object):
    def __init__(self, templatepath, scriptdir, qsubpath='qsub', command_args=None):
        self.scriptdir = scriptdir #directory where qsub scripts are placed
        self.outfiledir = os.path.join(self.scriptdir, 'logs', 'output')  #directory where stdout outputs will be placed
        self.errfiledir = os.path.join(self.scriptdir, 'logs', 'error')  #directory where error outputs will be placed
        self.donedir = os.path.join(self.scriptdir, 'done') #directory where finished scripts will be placed
        self.templatepath = templatepath #path (string) to template
        self.qsubpath = qsubpath #path to qsub executable
        self.command_args = command_args #stuff preceeded with -l in qsub
        self.__checkdirs__()


    #takes subs,a dictionary that must at least have a mapping {'filename':'scriptname.sh'}
    def submit(self, subs, command_args=None):
        #open template and output file
        templatefile = open(self.templatepath, 'r')
        outscriptpath = os.path.join(self.scriptdir, subs['filename'])
        outscriptfile = open(outscriptpath, 'w')

        #read in template, add bottom line to move script when done, substitute, and write to script
        templatestring = templatefile.read()
        templatestring += '\nmv %(this_script)s %(done_dir)s\n'
        subs['this_script'] = outscriptpath
        subs['done_dir'] = self.donedir
        outscriptfile.write(templatestring % subs)

        #close files
        templatefile.close()
        outscriptfile.close()

        #build args
        args = [self.qsubpath, '-o', self.outfiledir, '-e', self.errfiledir, outscriptpath]
        if command_args != None:
            if command_args != '':
                args = [self.qsubpath, '-o', self.outfiledir, '-e', self.errfiledir, '-l', command_args, outscriptpath]
        elif self.command_args != None:
            args = [self.qsubpath, '-o', self.outfiledir, '-e', self.errfiledir, '-l', self.command_args, outscriptpath]

        #execute script
        print "Executing %s" % ' '.join(args)
        p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        if stderr != '':
            print "Qsub Error: %s" % stderr
        print stdout

    def __checkdirs__(self):
        if not os.path.exists(self.scriptdir):
            os.makedirs(self.scriptdir)
        if not os.path.exists(self.outfiledir):
            os.makedirs(self.outfiledir)
        if not os.path.exists(self.errfiledir):
            os.makedirs(self.errfiledir)
        if not os.path.exists(self.donedir):
            os.makedirs(self.donedir)


    def __str__(self):
        with open(self.templatepath, 'r') as templatefile:
            return templatefile.read()
