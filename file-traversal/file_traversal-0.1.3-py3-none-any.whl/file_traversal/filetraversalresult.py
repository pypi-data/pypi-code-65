class FileTraversalResult:
    '''
    Holds result of file traversal.
    '''
    def __init__(self):
        super()
        self.folderstraversed = list()
        self.filestraversed = list()
        self.maximumfolderdepth = 0
        self.__ismutable = True
    
    def addfolders(self, folders):
        '''
        Appends traversed folders to the result list.
        '''
        if self.__ismutable:
            self.folderstraversed.append(folders)

    def addfiles(self, files):
        '''
        Appends traversed files to the result list.
        '''
        if self.__ismutable:
            self.filestraversed.append(files)

    def maximizedepth(self, depth):
        '''
        Sets maximum depth of traversal.
        '''
        if self.__ismutable:        
            if depth > self.maximumfolderdepth:
                self.maximumfolderdepth = depth

    def disablemutability(self):
        '''
        Sets the mutability if possible, will return the post-assignment mutability status (True/False).
        '''
        if self.__ismutable:
            self.__ismutable = False

    def getfolderstraversed(self):
        '''
        Returns folders traversed.
        '''
        return self.folderstraversed

    def getfilestraversed(self):
        '''
        Returns files traversed.
        '''
        return self.filestraversed

    def getmaximumdepth(self):
        '''
        Returns the maximum folder depth reached.
        '''
        return self.maximumfolderdepth