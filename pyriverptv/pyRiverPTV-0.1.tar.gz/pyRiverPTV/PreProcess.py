import os
import cv2
import numpy as np
from glob import glob
import math
import re

class PreProcess():
    
    """
    Collection of functions useful for processing raw drone video for to perform PTV and other analysis.

    """
    
    def __init__(self,projectPath):
        
        ## path containing video to process and which will contain any processed video frames
        self.projectPath=projectPath
    

    def defineGRP(self):
        """
        Opens ground reference point (GRP) definition window 
        """
        import pyRiverPTV.gdp as gdp



    def getImagesInDirectory(self,path,extension,**kwargs):
        
        imagePaths= [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.%s'%extension))]
        
        if 'sort' in kwargs:
            
            if kwargs['sort'] == True:
                #return imagePaths.sort(key=self.natural_keys)
                return sorted(imagePaths)
        else:
            return imagePaths

    def extractInterval(self,videoPath,interval,out):
        """
        Extract frames from video between times specified in interval variable.
        
        videoPath (str): path to video in .mp4 format
        interval (list): first entry string in "hh:mm:ss" format, second entry in "hh:mm:ss"
        out    (string): name of output video in mp4 format
        """
        
        os.system("ffmpeg -i %s -ss %s -to %s -c:v copy -c:a copy %s.mp4" %(videoPath,interval[0],interval[1],out))


    def extractFrames(self,path,out,fps,nleadingZeros,filetype):
        """
        Extracts the frames of the video at a specified frames per second
        
        path (str): path to video
        out  (str): prefix name for extracted images
        fps  (int): frames per second to extract
        nleadingZeros (int): maximum number of 0s to fill in front of image id
        filetype (str): specify the filetype (e.g. 'jpg', 'png')
        
        -------------
        ***WARNING***
        -------------
        
        Seems to return the wrong number of frames on short videos (i.e. < 10 s?)
        Check to makes sure the correct number of frames are returned. For example,
        on a 10 s video, extracting 10 fps, you would expect 100 frames to be returned.
        """
        os.chdir(self.projectPath)
        
        command="ffmpeg -i %s " % path + "-vf fps=%d " % fps + "%s" % out + "%0" + "%dd.%s" % (nleadingZeros, filetype) 
        os.system(command)
        
    def detectGRPsInImageSequence(self,images,threshValue,areaLimits,searchRadius,baseLocations):
        """
        Calls self.findGRPs() for each image in images and appends the moved GRP locations to movedLocations.
        
        images (list): list of paths (str) to each image in the sequence
        baseLocations (list): list of lists, containing x, y px coordinates of each GRP
        """
        
        movedLocations=[]
        moved=baseLocations
        
        for image in images:
            
            moved=self.findGRPs(image,moved,threshValue,areaLimits,searchRadius,baseLocations)
             
            if not moved:
                print('problem')
                break
            else:
#                print(moved)
                movedLocations.append(moved) 
        
        return movedLocations


    def findGRPs(self,imagePath,lastKnownPositions,threshValue,areaLimits,searchRadius,baseLocations,**kwargs):
        
        """
        Returns locations of ground reference points (GRPs) in image.
        
        GRPs must be between the area (pixel) limits defined in areaLimits and be within the searchRadius of one of the baseLocations
        Some testing of these parameters is needed prior to succesfully using this function.
        
        image (str): path to image
        lastKnownPositions (list): list of lists containing x, y px coordinates of each GRP in last known position
        threshValue (int): grayscale value below which pixels will be made white, value over black
        areaLimits (list): first entry minimum contour area in pixels, second entry maximum contour area
        searchRadius (int): pixel distance to search around lastKnownPositions[i]
        
        returns (list): list of lists, each containing the x,y pixel location of each GRP in the image
        
        """
        
        image = cv2.imread(imagePath)
        
        print("*************************************")
        print("Detecting GRPs in image %s" %os.path.basename(imagePath))
        
        outputImg = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret,threshold = cv2.threshold(gray,threshValue,255,cv2.THRESH_BINARY_INV)
        ret, cnts, hierachy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        nbrGRP=len(baseLocations)
        nbrGRPdetected=0
        
        #populate placeholders for the four GRPs
        locations=[[0,0],[0,0],[0,0],[0,0]]
        displacements_x=[0,0,0,0]
        displacements_y=[0,0,0,0]
        
        for c in cnts:
            
            #size limits
            if areaLimits[0] <= cv2.contourArea(c) <= areaLimits[1]: 
                
                M = cv2.moments(c)
                
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.drawContours(outputImg, [c], -5, (255, 0, 0), 3)
                
                """
                Compares to last detected position of marker (input as a variable)
                Makes algorithm more robust for really shaky videos.
                """
                for count, grp in enumerate(lastKnownPositions):
                    dist=((grp[0]-cx)**2+(grp[1]-cy)**2)**0.5
                    
                    #search area limit
                    if  dist < searchRadius:
                            
                        print('Detected GRP %d' %count)
                        print('Contour area: %d' % cv2.contourArea(c))
                        print('Position: %d, %d' %(cx, cy))
                        

                        locations[count]=[cx,cy]
                        displacements_x[count]=abs(grp[0]-cx)
                        displacements_y[count]=abs(grp[1]-cy)

                        print("Displacement: %d in x and %d in y" %(displacements_x[count],displacements_y[count]))
                        print('---')
                        cv2.circle(outputImg,(cx,cy),2,(0,0,255),-1)
                        
                        nbrGRPdetected = nbrGRPdetected + 1
    
        if nbrGRPdetected == nbrGRP:
            avg_disp_x=sum(displacements_x)/len(displacements_x)
            avg_disp_y=sum(displacements_y)/len(displacements_y)
            
            
            print("Avg x disp: %d" %avg_disp_x)
            print("Avg y disp: %d" %avg_disp_y)
            print("Detection of all %d successful, moving to next image" %nbrGRP)
            return locations
        else:
            
            print("Catastrophic failure: not all GRP detected, returning 0.\n")
            print("Cause: A GRP is being detected more than once.")
            print("Fixes: Refine contour area limits to be closer to the area (pixels) of the GRPs.")
            print("       Reduce the search radius around last known point.")
            print("       Generally a 10 to 20 pixle search radius is appropriate.\n")
            cv2.namedWindow("output", cv2.WINDOW_NORMAL)
            cv2.imshow("output", outputImg)
            cv2.namedWindow("threshold", cv2.WINDOW_NORMAL)
            cv2.imshow("threshold", threshold)
            return 0
        
#    if 'save' in kwargs:
#        
#        if kwargs['save'] == True:
#            outputImgPath='%d_grp.jpg' % 
#            cv2.imwrite(outputImgPath, outputImg)    
#                    (xstart, ystart, w, h) = cv2.boundingRect(c)

        print("*************************************")


    def stabilizeFrames(self,imagePaths,baseLocations,movedLocations,folderName,**kwargs):
        
        for count,image in enumerate(imagePaths):
            
            self.stabilizeFrame(image,baseLocations,movedLocations[count],folderName)

    def stabilizeFrame(self,imagePath,baseLocations,movedLocations,folderName,**kwargs):
        
        """
        Stabilizes the image so that the GRP locations in movedLocations match their baseLocations
        
        imagePath (str): Path to image to stabilize
        baseLocations (list): list of list containing the 'base' locations of each GRP (use calibration module to obtain)
        movedLocations (list): list of lists containing the 'moved' locations of each GRP (result of findGRPs())
        """
    
        img = cv2.imread(imagePath)
        
        rows,cols,ch = img.shape
        pts1 = np.float32(movedLocations)
    
        #where the GRP points will be move to (i.e., desired base positions)
        pts2 = np.float32(baseLocations)
    
        M = cv2.getPerspectiveTransform(pts1,pts2)
        dst = cv2.warpPerspective(img,M,(cols,rows))
    
        stbImagePath='%s\%s\%s_stb.png' %(self.projectPath,folderName, os.path.splitext(os.path.basename(imagePath))[0])
        print(stbImagePath)
        cv2.imwrite(stbImagePath, dst) 

    def writeVideoFromFrames(self,outputName,imagePaths,fps):
        
        """
        Combines images into a .mp4 video
        
        imagePaths (list): paths of individual images in chronological order to combine in video
        outputName (str): name of video that will be output
        fps (int): number of frames per second in video
        """
        
        img_array = []
        for image in imagePaths:
            img = cv2.imread(image)
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)
         
        out = cv2.VideoWriter('%s.mp4' %outputName,cv2.VideoWriter_fourcc(*'MP4V'), fps, size)
         
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()        

    def cropImage(self,extents,imagePath):
        img = cv2.imread(imagePath)   
        crop_img = img[extents[1]:extents[1]+extents[3], extents[0]:extents[0]+extents[2]]
#        cv2.imshow("cropped", crop_img)
        return crop_img
    
    def resizeImage(self,percent,image):
        
        width = int(image.shape[1] * percent / 100)
        height = int(image.shape[0] * percent / 100)
        dim = (width, height)
        
        return cv2.resize(image, dim, interpolation = cv2.INTER_AREA) 
        
    def getCV2image(self,imagePath):
        
        return cv2.imread(imagePath)
        
    def stackImages(self,folderName,images,fileName):
        
        """
        Horizontally or vertically stacks input images into a single image.
        """

        max_width = 0 
        total_height = 0 
       
        for image in images:

            height, width, layers = image.shape
            
            if width > max_width:
                max_width = width
                
            total_height += height
            
        final_image = np.zeros((total_height,max_width,3),dtype=np.uint8)
    
        current_y = 0 # keep track of where your current image was last placed in the y coordinate
        for image in images:
            
            final_image[current_y:image.shape[0]+current_y,:image.shape[1],:] = image
            current_y += image.shape[0]

        stackImgPath='%s\%s\%s_stack.png' %(self.projectPath,folderName,fileName)

        cv2.imwrite(stackImgPath, final_image)
        
    def getAvgGrayIntensity(self,image):
        
        """
        Find average grayscale pixel value over image.
        
        Useful for detecting time serie fluctuations of visible suspended sediment in a mixing layer
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        return gray.mean()

    def getAverageOfImages(self, imagePaths, writeName):

        images=[]
        for imagePath in imagePaths:
            image = cv2.imread(imagePath, 1)
            images.append(image)
         
        print('Taking average of %d images ... please wait ...' %len(images))
        # Calculate blended image
        dst = images[0]
        for i in range(len(images)):
            if i == 0:
                pass
            else:
                alpha = 1.0/(i + 1)
                beta = 1.0 - alpha
                dst = cv2.addWeighted(images[i], alpha, dst, beta, 0.0)
         
        # Save blended image
        cv2.imwrite('%s.png' % writeName, dst)

    def grayScaleImage(self,imagePath,folderName):
        image = cv2.imread(imagePath, 1)
        grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayImagePath='%s\%s\%s_gray.png' %(self.projectPath,folderName, os.path.splitext(os.path.basename(imagePath))[0])
        cv2.imwrite(grayImagePath, grayScale) 
        print('Writing grayscale image to %s' % os.path.splitext(os.path.basename(imagePath))[0])

    def binarizeImage(self,imagePath,threshold,inverse,folderName,**kwargs):
        
        image = cv2.imread(imagePath, 1)
        grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if inverse == True:
            ret,thresh=cv2.threshold(grayScale,threshold,255,cv2.THRESH_BINARY_INV)
        if inverse == False:
            ret,thresh=cv2.threshold(grayScale,threshold,255,cv2.THRESH_BINARY)
        
        threshImagePath='%s\%s\%s_tresh.png' %(self.projectPath,folderName, os.path.splitext(os.path.basename(imagePath))[0])
        cv2.imwrite(threshImagePath, thresh) 
        print('Writing thresholded image to %s' % os.path.splitext(os.path.basename(imagePath))[0])
        
        if 'show' in kwargs:
            if kwargs['show']==True:
                cv2.namedWindow("main", cv2.WINDOW_NORMAL)
                cv2.imshow("main",thresh)        


    """
    Orthorectification functionality
    """

    def setupTriangles(self,grpCoords):
        
        """
        Calculates information to complete the two triangles defined by the four GRPs.
        
        grpCoords: list of tuples [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]) for each re
        
        The vector c1 of triangle 1 (T1) is assumed to have the correct orientation on the drone images. 
        c1 is defined by the first two points in grpCoords (0 and 1), a1 points 1 and 2 and b1 points 0 and 2.
        
        The interior angles A1, B1 and C1 are calculated using the law of Cosines knowing the lengths of a1, b1 and c1.
        
               grpCoords[2]         a1             grpCoords[1]
                            *-------------------* 
                            |\C1              B1|
                            | \                 |
                            |  \                |
                            |B2 \       T1      |
                            |    \              |
                            |     \             |
                            |      \            |
                            |       \ b1        | c1
                            |a2      \          |
                            |         \         |
                            |       c2 \        |
                            |           \       |
                            |            \      |
                            |     T2      \     |
                            |              \    |
                            |               \ A1| 
                            |                \  | 
                            | C2           A2 \ |
                            *__________________\*  
               grpCoords[2]         b2             grpCoords[0]
        
        """ 
        
        T1={'A1':None,'B1':None,'C1':None,'a1':0,'b1':None,'c1':None}
        T2={'A2':None,'B2':None,'C2':None,'a2':None,'b2':None,'c2':None}
        
        T1['a1']=self.magnitude(grpCoords[1],grpCoords[2])
        T1['b1']=self.magnitude(grpCoords[0],grpCoords[2])
        T1['c1']=self.magnitude(grpCoords[0],grpCoords[1])
        
        T2['a2']=self.magnitude(grpCoords[2],grpCoords[3])
        T2['b2']=self.magnitude(grpCoords[0],grpCoords[3])
        T2['c2']=self.magnitude(grpCoords[0],grpCoords[2])  
    
        def angles(a,b,c):
            cosA=(b*b+c*c-a*a)/(2*b*c)
            cosB=(c*c+a*a-b*b)/(2*c*a)
            cosC=(a*a+b*b-c*c)/(2*a*b)
            return math.degrees(math.acos(cosA)), math.degrees(math.acos(cosB)), math.degrees(math.acos(cosC))
            
        T1['A1'],T1['B1'],T1['C1']=angles(T1['a1'],T1['b1'],T1['c1'])
        T2['A2'],T2['B2'],T2['C2']=angles(T2['a2'],T2['b2'],T2['c2'])
        
        return T1, T2

    def fitLine(self,p1,p2):
        vx,vy,x,y=cv2.fitLine(np.array([p1,p2]),cv2.DIST_L2,0,0.01,0.01)
        return vx,vy,x,y        
    
    def magnitude(self,p1,p2):
        mag=((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5
        return mag
        
    def getScalingFactor(self,T1,T2,imgPos):
        
        a1_px=self.magnitude(imgPos[1],imgPos[2])
        b1_px=self.magnitude(imgPos[0],imgPos[2])
        c1_px=self.magnitude(imgPos[0],imgPos[1])
    
        a2_px=self.magnitude(imgPos[2],imgPos[3])
        b2_px=self.magnitude(imgPos[0],imgPos[3])
        c2_px=self.magnitude(imgPos[0],imgPos[2])
    
        sf_a1=T1['a1']/a1_px
        sf_b1=T1['b1']/b1_px
        sf_c1=T1['c1']/c1_px
        
        sf_a2=T2['a2']/a2_px
        sf_b2=T2['b2']/b2_px
        sf_c2=T2['c2']/c2_px
        
        scaleFactors=[sf_a1,sf_b1,sf_c1,sf_a2,sf_b2,sf_c2]
        sf_mean=np.asanyarray(scaleFactors).mean()
        
        return scaleFactors, sf_mean

    def getOrthorectificationParameters(self,imagePath,T1,T2,GRPpos,imgPos,writeImage):
        
        """
        Determines orthorectified image coordinates for the GRPs. Scales GRP positions with a 
        uniform scaling factor calculated as the mean side length in measurment units / mean side length in pixels.
        
        imagePath (str): path to base image
        T1 (dict): interior angles and lengths of the upper triangle between points 0, 1 and 2
        T2 (dict): interior angles and lengths of the lower triangle between points 0, 2 and 3
        GRPpos (list of tuples): realworld coordinates of the GRPs
        imgPos (list of tuples): orginal pixel coordinates of GRP in base image
    
        returns:
        list of tuples containing orthorectified pixel locations of the GRPs
        scaling factor (measurement units/pixel)
        
        """
        
        #path to base image
        image = cv2.imread(imagePath, 1)
        
        #draw origin (GRP 0, always lower right in image)
        cv2.circle(image,imgPos[0],3,(0,255,0),-1)
        cv2.circle(image,imgPos[0],20,(0,255,0),3)
        
        def drawLine(p1,p2):
            vx,vy,x,y=self.fitLine(p1,p2)
            left_pt = int((-p1[0]*vy/vx) + p1[1])
            right_pt = int(((image.shape[1]-x)*vy/vx)+y)
            cv2.line(image,(image.shape[1]-1,right_pt),(0,left_pt),(0,0,255),2)
    
        def drawGRPcorr(x_corr,y_corr):
            imgPos_corr=(x_corr,y_corr)
            cv2.circle(image,imgPos_corr,3,(0,255,0),-1)
            cv2.circle(image,imgPos_corr,20,(0,255,0),3)
        
        #draw lines joining non-corrected GRP pixel coordinates
        drawLine(imgPos[0],imgPos[1])
        drawLine(imgPos[1],imgPos[2])
        drawLine(imgPos[2],imgPos[3])
        drawLine(imgPos[3],imgPos[0])
    
        sfs,sfmean=self.getScalingFactor(T1,T2,imgPos)
        
        #correct GRP1
        c1_corr_px=self.magnitude(GRPpos[0],GRPpos[1])/sfmean
        
        if imgPos[0][0]>imgPos[1][0]:
            x_corr1=int(imgPos[0][0]-c1_corr_px*math.sin(self.fitLine(imgPos[0],imgPos[1])[0]))
            y_corr1=int(imgPos[0][1]-c1_corr_px*math.cos(self.fitLine(imgPos[0],imgPos[1])[0]))
            drawGRPcorr(x_corr1,y_corr1)
            cv2.line(image,imgPos[0],(x_corr1, y_corr1),(0,255,0))
        else:
            x_corr1=int(imgPos[0][0]+c1_corr_px*math.sin(self.fitLine(imgPos[0],imgPos[1])[0]))
            y_corr1=int(imgPos[0][1]-c1_corr_px*math.cos(self.fitLine(imgPos[0],imgPos[1])[0]))
            drawGRPcorr(x_corr1,y_corr1)
            cv2.line(image,imgPos[0],(x_corr1, y_corr1),(0,255,0))
    
    
        #correct GRP2
        #angle for A1' which is used to calculate dx_px and dy_px
        b1_corr_px=self.magnitude(GRPpos[0],GRPpos[2])/sfmean
        Aprime=90-T1['A1']-math.degrees(math.tan(self.fitLine(imgPos[0],imgPos[1])[0]/self.fitLine(imgPos[0],imgPos[1])[1]))
        dpx_x=b1_corr_px*math.cos(math.radians(Aprime))
        dpx_y=b1_corr_px*math.sin(math.radians(Aprime))
        x_corr2=int(imgPos[0][0]-dpx_x)
        y_corr2=int(imgPos[0][1]-dpx_y)
        drawGRPcorr(x_corr2,y_corr2)
        cv2.line(image,(x_corr1,y_corr1),(x_corr2, y_corr2),(0,255,0))
    
        #correct GRP3
        b2_corr_px=self.magnitude(GRPpos[0],GRPpos[3])/sfmean
        Aprime=90-T1['A1']-T2['A2']-math.degrees(math.tan(self.fitLine(imgPos[0],imgPos[1])[0]/self.fitLine(imgPos[0],imgPos[1])[1]))
        dpx_x=b2_corr_px*math.cos(math.radians(Aprime))
        dpx_y=b2_corr_px*math.sin(math.radians(Aprime))
        x_corr3=int(imgPos[0][0]-dpx_x)
        y_corr3=int(imgPos[0][1]-dpx_y)
        drawGRPcorr(x_corr3,y_corr3)
        cv2.line(image,(x_corr2,y_corr2),(x_corr3, y_corr3),(0,255,0))
        cv2.line(image,imgPos[0],(x_corr3, y_corr3),(0,255,0))
    
        cv2.namedWindow("output", cv2.WINDOW_NORMAL)
        cv2.imshow("output", image)
        
        if writeImage==True:
            cv2.imwrite('rectifiedPositions.png', image) 
        
        return [imgPos[0],(x_corr1,y_corr1),(x_corr2,y_corr2),(x_corr3,y_corr3)], sfmean




    def rotateImage(self,imagePath,degree,folderName,write):
        
#        image = cv2.imread(imagePath, 1)
#        grayScale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#        
#        if inverse == True:
#            ret,thresh=cv2.threshold(grayScale,threshold,255,cv2.THRESH_BINARY_INV)
#        if inverse == False:
#            ret,thresh=cv2.threshold(grayScale,threshold,255,cv2.THRESH_BINARY)
#        
#        threshImagePath='%s\%s\%s_tresh.png' %(self.projectPath,folderName, os.path.splitext(os.path.basename(imagePath))[0])
#        cv2.imwrite(threshImagePath, thresh) 
#        print('Writing thresholded image to %s' % os.path.splitext(os.path.basename(imagePath))[0])
#        
#        if 'show' in kwargs:
#            if kwargs['show']==True:
#                cv2.namedWindow("main", cv2.WINDOW_NORMAL)
#                cv2.imshow("main",thresh)        


        image = cv2.imread(imagePath, 1)
        (h, w) = image.shape[:2]
        center = (w / 2, h / 2)
        # rotate the image by x degrees
        M = cv2.getRotationMatrix2D(center, degree, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h))
        
        
        if write==True:
        
            rotatedImagePath='%s\%s\%s_rot.png' %(self.projectPath,folderName, os.path.splitext(os.path.basename(imagePath))[0])
            print(rotatedImagePath)
            cv2.imwrite(rotatedImagePath, rotated) 
            print('Writing rotated image to %s' % os.path.splitext(os.path.basename(imagePath))[0])
            
        else:
            return rotated
        
#        cv2.namedWindow("rotated", cv2.WINDOW_NORMAL)
#        cv2.imshow("rotated", rotated)


    def getRealWorldCoords(self,imgCoords,rwCoords,points,sf):
        
        """
        Given two points of known real-world coordinates
        and corresponding image coordinates, return real-world 
        coordinates of a list of pixel points on image.
        """
        
        #angle of rw points with rw x axis
        rw_vx,rw_vy,rw_x,rw_y=self.fitLine(rwCoords[0],rwCoords[1])
        
        #angle between img x axis and image point 2
        img_vx,img_vy,img_x,img_y=self.fitLine(imgCoords[0],imgCoords[1])
        
        #angle between img x-axis and rw x-axis
        angleWithXaxis=math.degrees(math.asin(img_vy))+math.degrees(math.asin(rw_vy))
        
        x=[]
        y=[]
        for point in points:
            p_vx,p_vy,p_x,p_y=self.fitLine(imgCoords[0],point)
            
            #angle between point and img x-axis
            angle=math.degrees(math.asin(p_vy))
            
            #angle between rw x-axis and point
            interiorAngle=angleWithXaxis-angle
            
            #pixel magnitude between origin and point
            mag=self.magnitude(imgCoords[0],point)
            
            x.append(rwCoords[0][0]+mag*math.cos(math.radians(interiorAngle))*sf)
            y.append(rwCoords[0][1]+mag*math.sin(math.radians(interiorAngle))*sf)
               
        return x, y, angleWithXaxis



# #start calibration window, use to

        
# path=r"C:\Users\Jason\Google Drive\PythonTools\RiverPTV\StabilizeTests\dots.mp4"
# preProc=Preprocess(path)

# #user variables
# threshValue = 100

# #input variables
# path=r"C:\Users\Jason\Google Drive\PythonTools\RiverPTV\StabilizeTests\frames"

# #paths to images
# images= [y for x in os.walk(path) for y in glob(os.path.join(x[0], '*.png'))]

# #pixel locations of GRPs
# areaLimits=[5000,9000]
# baseLocations=[[702,797],[1062,733],[1097,243],[718,237]]
# lastKnownPositions=[[702,797],[1062,733],[1097,243],[718,237]]
# searchRadius=150

# movedLocations=[]
# new=lastKnownPositions
# for image in images:
    
#     new=findGRPs(image,new,100,areaLimits,searchRadius,baseLocations)
     
#     if not new:
#         break
#     else:
#         movedLocations.append(new)
    
    
# def findGRPs(imagePath,lastKnownPositions,threshValue,areaLimits,searchRadius,baseLocations,**kwargs):
    
#     """
#     Returns locations of ground reference points (GRPs) in image.
    
#     GRPs must be between the area (pixel) limits defined in areaLimits and be within the searchRadius of one of the baseLocations
    
#     image (str): path to image
#     lastKnownPositions (list): list of lists containing x, y px coordinates of each GRP
#     threshValue (int): grayscale values below will be made white, value over black
#     areaLimits (list): first entry minimum contour area in pixels, second maximum contour area
#     searchRadius (int): pixel distance to search around baseLocation
    
#     returns (list): list of lists, each containing the x,y pixel location of each GRP
    
#     """
    
#     image = cv2.imread(imagePath)
    
#     print("*************************************")
#     print("Detecting GRP in image %s" %os.path.basename(imagePath))
    
#     outputImg = image.copy()
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     ret,threshold = cv2.threshold(gray,threshValue,255,cv2.THRESH_BINARY_INV)
#     ret, cnts, hierachy = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
#     nbrGRP=len(baseLocations)
#     nbrGRPdetected=0
    
#     movedLocations=[]
#     for c in cnts:
        
#         if areaLimits[0] <= cv2.contourArea(c) <= areaLimits[1]: 
            
#             M = cv2.moments(c)
            
#             cx = int(M['m10']/M['m00'])
#             cy = int(M['m01']/M['m00'])
#             cv2.drawContours(outputImg, [c], -5, (255, 0, 0), 1)
            
            
#             """
#             Compares to last detected position of marker (input as a variable)
#             Makes algorithm more robust for really shaky videos.
#             """
#             for count, grp in enumerate(lastKnownPositions):

#                 if  grp[0] - searchRadius <= cx <= grp[0] + searchRadius and grp[1] - searchRadius <= cy <= grp[1] + searchRadius:

#                     print('Detected GRP %d' %count)
    
#                     movedLocations.append([cx,cy])
#                     cv2.circle(outputImg,(cx,cy),2,(0,0,255),-1)
                    
#                     nbrGRPdetected = nbrGRPdetected + 1


#     if nbrGRPdetected == nbrGRP:
        
#         print("Detection of all %d successful, moving to next image" %nbrGRP)
#         return movedLocations
#     else:
        
#         print("Catastrophic failure: not all GRP detected, returning 0.")
#         cv2.imshow("output", outputImg)
#         cv2.imshow("threshold", threshold)
#         return 0
        
# #    if 'save' in kwargs:
# #        
# #        if kwargs['save'] == True:
# #            outputImgPath='%d_grp.jpg' % 
# #            cv2.imwrite(outputImgPath, outputImg) 

                         
# #                    (xstart, ystart, w, h) = cv2.boundingRect(c)
#     print("*************************************")


 
    

# def stabilizeFrames(imagePath,baseLocations,imgLocations,**kwargs):

#     img = cv2.imread(imagePath)
#     rows,cols,ch = img.shape
#     pts1 = np.float32(imgLocations)

#     #where the GRP points will be move to (i.e., desired base positions)
#     pts2 = np.float32(baseLocations)

#     M = cv2.getPerspectiveTransform(pts1,pts2)
#     dst = cv2.warpPerspective(img,M,(cols,rows))

#     stbImagePath='./stabilized/%s_stb.png' % os.path.splitext(os.path.basename(imagePath))[0]
#     cv2.imwrite(stbImagePath, dst) 


# for count,frame in enumerate(newlocs):
    
#     img = cv2.imread(frameNames[count])
#     rows,cols,ch = img.shape
#     pts1 = np.float32(frame)

#     #where you want the points to be (i.e. original position)
#     pts2 = np.float32([[702,797],[1062,733],[1097,243],[718,237]])

#     M = cv2.getPerspectiveTransform(pts1,pts2)
#     dst = cv2.warpPerspective(img,M,(cols,rows))

#     binaryImagePath='%d_binary.jpg' % count
#     cv2.imwrite(binaryImagePath, dst)    

# plt.subplot(121),plt.imshow(base),plt.title('Input')
# plt.subplot(122),plt.imshow(dst),plt.title('Output')
# plt.show()




# #preProc.extractInterval(["00:00:00","00:00:13"],"frames")   
# #preProc.extractFrames('dots.mp4','./frames/frame',10,4) 
# preProc.detectGRP(300,"./frame0001.png")
# #preProc.getVideoInfo('bob.mp4')
# image = cv2.imread("./frame0001.png")

# proc=Process("./extracts/magog/*.png")
# proc.ptv()