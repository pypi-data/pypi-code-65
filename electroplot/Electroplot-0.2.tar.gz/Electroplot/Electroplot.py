## Electroplot.py
import os
from tifffile import TiffFile
from tkinter import filedialog
import numpy as np
from Functions.dataGrabber import grabMetadata, grabImageJdata, grabData, tif2png
#from Functions.masks import logTransform
from matplotlib import pyplot as plt
from Functions.masks import applyMask
from PIL import Image
import moviepy.editor as mp
import Functions.Arranger as ar
import Functions.maths
import math
from Misc.Errors import DatasetTypeError as DatasetTypeError


# Initialise the data to be analysed. 
# example: condition1 = ep.Dataset('Control', imagetype = 'image')
class Dataset(object):
    def __init__(self, name, path = None, imagetype = 'stack', outputpath = None): 
        self.name = name        #variable name of data set for internal reference
        self.raw = []           #contains raw image data
        self.data = []          #contains pixel values for image(s) as arrays
        
        self.type = imagetype   #property that describes whether dataset is a single image or an entire stack.
        self.metadata = None    #metadata property declaration
        self.outputpath = outputpath

        if path == None:        # if no path to the dataset is specified then a filedialog is automatically created. 
            if self.type == 'stack': 
                self.path = filedialog.askdirectory()                      #if a stack asks to select a folder
            else: 
                self.path = filedialog.askopenfilename()                   #if an image asks to select a file
        else:
            self.path = path                                               #if path argument specified skips above.

        if self.type == 'stack':
            for file in os.listdir(self.path):                              #stack loading cycle
                    try:
                        raw = grabData(str(self.path + '\\' + file))
                        self.raw.append(raw)
                        self.data.append(raw['Pixels'])
                        self.data[~np.isnan(self.data)]                     #removes any None values in stack
                    except TypeError:                                       #anything that does not conform to a pixel value is skipped (is this inherently skipping metadata?)
                        pass
                    try:
                        self.metadata = self.raw['ImageJ']                  #ImageJ metadata stored in self.metadata caught if no metadata present
                    except TypeError:
                        pass
                    
                                            
        else:                                                               # single image loading cycle
            self.raw = grabData(str(self.path))
            for item in self.raw['Pixels']:
                if item == None:                                            #skips Nones
                    pass
                else:
                    self.data.append(item) 
            self.size = len(self.data)
            try:
                self.metadata = self.raw['ImageJ']                          #if 'ImageJ' metadata non-existent, skips this step. 
            except TypeError:
                pass
        
        if self.metadata == None:
            print('Warn: no metadata detected in dataset')        
            
            
        self.size = len(self.data)
        self.data = np.array(self.data)                         #convert self.data from list to numpy array
        self.previous = self.data                               #establish back ups for undo and reset
        self.original = self.data
        
        #Error Catching
        a  = TypeError('the Electroplot dataset <' + str(self.name) + '> is an ' + str(self.type) + ' and cannot be divided.'), 
        self.errorParams = [a]
        
        print('Successfully loaded data at ' + str(self.path) + ' into a dataset object')
    
    
    def mask(self, threshold = 1000, masktype = 'edges' ): 
        self.previous = self.data
        if self.type == 'stack':
            masked = applyMask(self.data, threshold, masktype)
            self.data = masked
            return masked
                
        elif self.type == 'image':
            
            masked = applyMask(self.data, threshold, masktype)
            self.data = masked
            return masked
    #note: on image datasets stacks cannot be passed as operators
    #Divide the dataset by either another stack, another image, or a determined value.
    def divide(self, divider):                              
        self.previous = self.data
        divided = Functions.maths.datasetOperation(self.data, operator = divider, operation='divide' )
        self.data = divided
        return divided
      
    #Multiply the dataset by either another stack, another image, or a determined value.
    def multiply(self, multiplier):
        self.previous = self.data
        multiplied = Functions.maths.datasetOperation(self.data, operator = multiplier, operation = 'multiply')
        self.data = multiplied
        return multiplied
    
    #Add another stack, image or value to the dataset.
    def add(self, multiplier):
        self.previous = self.data
        summed = Functions.maths.datasetOperation(self.data, operator = multiplier, operation = 'addition')
        self.data = summed
        return summed
    
    #Subtract another stack, image or value from the dataset
    def subtract(self, multiplier):
        self.previous = self.data
        subtracted = Functions.maths.datasetOperation(self.data, operator = multiplier, operation = 'subtract')
        self.data = subtracted
        return subtracted
                
    def transform(self, transformer, *args): #need to add rotation
        #add rotation code
        return("transformation code still needs adding.")
    def undo(self):
        self.data = self.previous
        return("Last operation on dataset undone.")
    
    def wipe(self):
        self.data = self.original
        return ("Dataset wiped back to origin.")
    
    def getZprofile(self, plot = True, mask = None):
        zprofile = []
        i = 0
        if self.type == 'stack': 
            if mask == None: 
                for image in self.data: 
                    zprofile.append(np.average(image))
            elif mask == 'log':
                    zprofile.append(logTransform(self.data, 10))
            else: 
                print('bork')
                    #process(self.data['Pixels'], **kwargs           
        else: 
            zprofile = print('getZprofile: This dataset is a' + str(self.type) + ', not a stack!')
        if plot == True:
            plot = plt.plot(zprofile)
            zprofileplot = plt.savefig('zprofile.png')
            return zprofileplot
        else:
            return zprofile
    
    def visualise(self):
        img = Image.fromarray(self.data[0], 'I;16')
        img.show()
    
    def save(self, path = None, format = '.TIF'):
        #if self.outputpath == None: 
        #    self.outputpath = filedialog.askdirectory()
        if path == None:
            path = filedialog.askdirectory()
        try:
            os.makedirs(path)
        except OSError as e:
            #specific error catch
            pass
        if self.type == 'stack':
            iterator = 0
            for array in self.data: 
                iterator +=1
                image = Image.fromarray(array, 'I;16')
                image.save(path + str(self.name) + str(iterator) + str(format))
            return(str(len(self.data)) + '.TIF images were saved at ' + str(self.outputpath))   
        elif self.type == 'image':
            image = Image.fromarray(self.data, 'I;16')
            
        else: 
            raise DatasetTypeError('Dataset type not found! Consider reloading data', self.type)
        return(str(format) + )
        
class Figure(): 
    def __init__(self, name, *datasets, rows = None, columns = None, duration = None ):
        #initialise containers for subfigure objects and positional array
        subfigures = []                                         
        positions = []
        total = int
        
        #automatically calculate rows and columns if none specified
        if rows == None:
            rows = len(datasets) 
        if columns == None: 
            columns = 1
        if total != rows * columns:
            Exception('the total number of subfigures is out of bounds!')
        
        #create subfigures from datasets, and append to array
        for i in datasets:
            subfigure = ar.subFigure(i, i.name, 
                                i.data, 
                                i.metadata,
                                )
            subfigures.append(subfigure)
        self.subfigures = np.array(subfigures)
        
        #figure parameter dictionary (base)
        self.figureParams = {   'name' : name,
                                'total': int(len(datasets)),
                                'rows' : rows,
                                'cols' : columns,
                                'duration' : duration,
                                'valid' : 0
                            }
        #set positional layout for subfigures, labelled 0 - 1 left to right, rows -> columns
        c = 0
        for i in subfigures:
            i.position = c
            c+=1
            positions.append(i.position)
        positions = np.asarray(positions)
        self.figureParams['positions'] = np.array(positions.reshape(self.figureParams['rows'], self.figureParams['cols']))
        #print("Sucessfully made subfigures, access datasets " + str(subfigures.names))
        
    #arrange the layout of subfigures.
    def arrange(self, cols, rows): #arranges the grid to accomodate for electrodes with 
        self.figureParams['rows'] = rows
        self.figureParams['cols'] = cols
        if cols + rows != self.figureParams['total']:
            raise Exception('the number of columns and rows must equal the total number of datasets!')
        else:
            #self.layout = self.subfigures.reshape(self.figureParams['rows'], self.figureParams['cols'])
            self.figureParams['positions']=self.figureParams['positions'].reshape(self.figureParams['rows'], self.figureParams['cols'])
            return print ('Set figure to have ' + str(cols) + ' columns, and ' + str(rows) + ' rows:' ), print(self.figureParams['positions'])
    
    #def makeClip(self, subfigure, )
    #joins two datasets into a single subfigure
    def pairSubfigures(self, subfigures):
        #pairingcode
        return None
    def setFPS(self, fps):
        self.figureParams['fps'] = fps
        return print ('fps:' + str(self.figureParams['fps']))
    #prints the current positional layout of the Figure. 
    def showlayout(self):
        print(self.figureParams['positions'])
        
    # assign figure types to subfigures. Available types are 'image', 'movie' and 'graph'
    #for graph types, animation must be specified as true or false
    # all subfigures must be assigned before a plot can be valid
    def assignSubfigures(self, *subtypesPositions, animation = None):
        c = 0
        for i in subtypesPositions:
            position = i[0]
            self.subfigures[position].subtype = i[1]
            if self.subfigures[position].subtype == 'graph':
                self.subfigures[position].animation = i[2]
        
        '''
        for i in self.subfigures:
            i.subtype = subtypesPositions[c]
            c+=1
        '''
        self.figureParams['valid'] = True
        return print(subtypesPositions)
    
    #print the type of subfigure, at specified position
    def checkSubtype(self, position):
        if self.subfigures[position].subtype == 'graph':
            return print(self.subfigures[position].subtype), print('animated: ' + str(self.subfigures[position].animation) )
        else:
            return print(self.subfigures[position].subtype)
    
    #preview the specified subfigures before figure compilation
    def previewSubfigures(self, *subFigures):
        previews = []
        for i in subFigures:
            i.makeSubfigure()
            previews.append(i.clip)
        return previews
        
    #compiles, and outputs the animated figure
    def renderFigure(self, fps, output = '.mp4', preview = True ):
        figure = []
        cliparray = []
        c = 0
        if self.figureParams['valid'] == True:
            cliparray = []
            for subfigure in self.subfigures:
                if subfigure.subtype == 'image':
                    subfigure.makeSubfigure(fps, self.figureParams['duration'])
                
                elif subfigure.subtype == 'movie':
                    subfigure.makeSubfigure(fps)
                
                elif subfigure.subtype == 'graph':
                    subfigure.makeSubfigure(fps)
                
                else: 
                    raise Exception("< subtype = " + str(subfigure.subtype) + " >, assing subtypes with Figure.assignSubtypes()")
            cliparray.append(i.clip)
            print(i)
                
            cliparray = np.asarray(cliparray)
            cliparray = np.array(cliparray.reshape(self.figureParams['rows'], self.figureParams['cols']))
            figure = mp.clips_array(cliparray)

            figure.resize(width = 480).write_videofile(self.figureParams['name'] + output, fps = fps)
            figure.resize(width=480).preview()

        else:
            raise Exception("invalid or missing figure parameters!")
        return figure
        