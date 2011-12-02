class ImportNiiError(Exception):
    def __init__(self, source, dest='', description='ImportNiiError'):
        self.source = source
        self.dest = dest
        self.description = description
    def __str__(self):
        infostring = 'cannot import nii file:\n' + self.source
        if self.dest != '':
            infostring += "\ninto\n" + self.dest
        if (self.description != 'ImportNiiError'):
            infostring += "\n" + self.description
        return infostring

class DeleteNiiError(Exception):
    def __init__(self, niiname, description='DeleteNiiError'):
        self.niiname = niiname
        self.description = description
    def __str__(self):
        infostring = 'cannot delete nii file:\n' + self.niiname
        if (self.description != 'DeleteNiiError'):
            infostring += "\n" + self.description
        return infostring

class UnknownFileException(Exception):
    def __init__(self, file, split=[], description='UnknownFileException: Find Source Data Error'):
        self.file = file
        self.split = split
        self.description = description
    def __str__(self):
        infostring = 'cannot determine file type of:\n' + self.file
        infostring += "\n Split was:\n" + '::'.join(self.split)
        if (self.description != 'UnknownFileException: Find Source Data Error'):
            infostring += "\n" + self.description
        return infostring
#try:
#    raise MyError(2 * 2)
#except MyError as e:
#    print 'My exception occurred, value:', e.value
