from os import listdir
from os import path
import logging
from .filetraversalresult import FileTraversalResult

logger = logging.getLogger("filetraversal")

class FileTraversal:
    '''
    File traversal object that will operate on it's constructed targets.
    '''
    def __init__(self, foldermethod=None, filemethod=None):
        '''
        Constructor. "foldermethod" is the function called on each folder. "filemethod" is the function called on each file.
        '''
        
        if foldermethod is None and filemethod is None:
            logger.warning("No functions defined for folder or file traversal.")

        self.foldermethod = foldermethod
        self.filemethod = filemethod


    def recurse(self, rootpath, depth=0):
        '''
        Recursively traverses the "rootpath" folder, calling the FileTraversal object's "foldermethod" and "filemethod" methods
        as it goes. "depth" is an optional parameter that represents folder depth of the recursive operation.
        '''
        result = FileTraversalResult()
        folderlist = listdir(rootpath)

        #Simple recursive folder and file traversal.
        for entry in folderlist: 
            item = path.join(rootpath, entry)
            if path.isdir(item):
                recursive_result = self.recurse(item, depth + 1)
                result.maximizedepth(depth)
                result.maximizedepth(recursive_result.getmaximumdepth())
                if self.foldermethod is not None:
                    self.foldermethod(item)
                result.addfolders(item)
                result.addfolders(recursive_result.getfolderstraversed())
                result.addfiles(recursive_result.getfilestraversed())
            if path.isfile(item):
                if self.filemethod is not None:
                    self.filemethod(item)
                result.addfiles(item)

        result.maximizedepth(depth)

        #Finally, disable mutability of the result.
        if(depth == 0):
            result.disablemutability()
        return result
