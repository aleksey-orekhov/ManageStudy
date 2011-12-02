
class DeleteSubjectError(Exception):
    def __init__(self, subid, description='DeleteSubjectError'):
        self.subid = subid
        self.description = description
    def __str__(self):
        infostring = 'cannot delete subject:\n' + self.subid
        if (self.description != 'DeleteSubjectError'):
            infostring += "\n" + self.description
        return infostring

