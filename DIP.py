#Code written by Yuntao Zhang 


import numpy as np
import csv
import cv2
from skimage import morphology
from skimage import measure
import time

class TI():
    def __init__(self,filename):
        tt=time.time()
        millis=int(round(tt*1000))
        self.inputpath= f'./Results/{filename}.csv' #source of data, must be .csv
        self.outputimagname=['./Results/TIrawimage_'+str(filename)+'.jpg','./Results/TIpreprocessed_'+str(filename)+'.jpg','./Results/TIbinarized_'+str(filename)+'.jpg','./Results/TIlabel_'+str(filename)+'.jpg'] #filename can be renamed
        self.imx=-1 #x direction in DIP
        self.imy=-1 #y direction in DIP
        self.resizeratio=1.0 #record ratio of scaling if zoomin is called
        self.defectno=-1 #record number of defects
        self.step = -1  # means mm per pixel
        self.labels=None


    def loadcsv(self):
        with open(self.inputpath, 'r') as csvfile:
            tempfile = csv.reader(csvfile)
            data_raw = []
            for row in tempfile:
                data_raw.append(list(map(float, row)))
        (self.imx, self.imy) = (len(data_raw), len(data_raw[0]))

        mn = min(min(rrow) for rrow in data_raw)
        mx = max(max(rrow) for rrow in data_raw)
        for i in range(self.imx):
            for j in range(self.imy):
                data_raw[i][j] = ((data_raw[i][j] - mn) / (mx - mn)) * 255
                data_raw[i][j] = int(data_raw[i][j])
        # change to np type so cv2 can read it as an image
        data_raw = np.array(data_raw)
        cv2.imwrite(self.outputimagname[0], data_raw)

    def dimensionfit(self,dimy,dimx):
        src=cv2.imread(self.outputimagname[0])
        self.imy = int(dimy * self.imx / dimx)
        # 86/140=x/200
        src = cv2.resize(src, (self.imy, self.imx), interpolation=cv2.INTER_AREA)
        cv2.imwrite(self.outputimagname[0], src)

    def zoomin(self,imylength=600):
        resizeimy, resizeimx = imylength, int(imylength / self.imy * self.imx)
        self.resizeratio = resizeimy / self.imy
        # resizeimy,resizeimx=imy,imx
        src = cv2.imread(self.outputimagname[0])
        src = cv2.resize(src, (resizeimy, resizeimx), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(self.outputimagname[0], src)

    def preprocess(self,medianksize=5,cliplim=4.0,gridsize=(8,8)):
        src = cv2.imread(self.outputimagname[0])
        src = cv2.medianBlur(src, medianksize)
        cv2.imwrite(self.outputimagname[1], src)
        img = cv2.imread(self.outputimagname[1], 0)
        clahe = cv2.cv2.createCLAHE(clipLimit=cliplim, tileGridSize=gridsize)
        cl1 = clahe.apply(img)
        cv2.imwrite(self.outputimagname[1], cl1)

    def morphology(self,thresh,ksize_OPEN=(15,15),ksize_CLOSE=(20,20)):
        binarized = cv2.imread(self.outputimagname[1], cv2.IMREAD_GRAYSCALE)
        ret, binarized = cv2.threshold(binarized, thresh, 255, cv2.THRESH_BINARY)
        cv2.imwrite(self.outputimagname[2], binarized)

        # use open operation to delete existing small blocks
        kel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize_OPEN)
        binarized = cv2.morphologyEx(binarized, cv2.MORPH_OPEN, kel_open)
        cv2.imwrite(self.outputimagname[2], binarized)
        # use close operation to smooth edges
        kel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize_CLOSE)
        binarized = cv2.morphologyEx(binarized, cv2.MORPH_CLOSE, kel_close)
        cv2.imwrite(self.outputimagname[2], binarized)

        for i in range(int(self.imx*self.resizeratio)):
            for j in range(int(self.imy*self.resizeratio)):
                if binarized[i][j] == 255:
                    binarized[i][j] = 1
                else:
                    binarized[i][j] = 0
        return binarized

    def skeletonize(self,binarized):
        # perform skeleton operation
        skeleton = morphology.skeletonize(binarized)
        # connectivity measure
        self.labels = measure.label(skeleton)
        # labels is a ndarray of same shape of skeleton image, but use 1~N to mark skeleton
        self.defectno = max(max(rrow) for rrow in self.labels)  # get number of defects
        # bool list cannot be iterated, so mark the points to pre-processed image
        # each element in defectinfo stores imx & imy defect coordinates of a label number
        '''
        defectinfo looks like
        ([ [imx coords of label 1][imx coords of label 2][imx coords of label 3][imx coords of label 4] ], 
         [ [imy coords of label 1][imy coords of label 2][imy coords of label 3][imy coords of label 4] ])
        '''
        defectinfo = ([[] for _ in range(self.defectno)], [[] for _ in range(self.defectno)])
        imskeleton = cv2.imread(self.outputimagname[0])
        # remind labels start from 1
        for i in range(self.defectno):
            for x in range(int(self.imx*self.resizeratio)):
                for y in range(int(self.imy*self.resizeratio)):
                    if self.labels[x][y] == i + 1:
                        # save location imformation of defects
                        defectinfo[0][i].append(x)
                        defectinfo[1][i].append(y)
                        # mark defect points, note xy coorindates are opposite with DIP form
                        cv2.circle(imskeleton, (y, x), 1, (0, 255, 0), 1)
                        cv2.imwrite(self.outputimagname[3], imskeleton)

        # label the number of defects

        for i in range(self.defectno):
            cv2.putText(imskeleton, str(i + 1),
                        (defectinfo[1][i][len(defectinfo[1][i]) // 2], defectinfo[0][i][len(defectinfo[0][i]) // 2])
                        , cv2.FONT_HERSHEY_SIMPLEX, 0.6
                        , (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imwrite(self.outputimagname[3], imskeleton)

        return defectinfo




    def realcenter(self,defectcenter):

        reszieddim = (int(self.imy * self.resizeratio), int(self.imx * self.resizeratio))
        #print(defectcenter)
        coords=[]
        for i in range(len(defectcenter)):

            coords.append((round(defectcenter[i][1]/reszieddim[0]*self.imy,0),round((reszieddim[1] - defectcenter[i][0])/reszieddim[1]*self.imx,0)))


        return coords

    def reallength(self,defectarea):
        for i in range(len(defectarea)):
            defectarea[i] = round(defectarea[i] / self.resizeratio, 1)

        return defectarea

    def defectinfo(self):
        defectarea = []
        defectcenter = []
        props = measure.regionprops(self.labels)
        for i in range(self.defectno):
            defectarea.append(props[i].area)
            defectcenter.append(props[i].centroid)

        return defectarea,defectcenter

class CFRP():
    def __init__(self,inputpath):
        tt=time.time()
        millis=int(round(tt*1000))
        self.inputpath = inputpath  # source of data, must be .csv
        self.outputimagname = ['CFRPrawimage_' + str(millis) + '.jpg', 'CFRPpreprocessed_' + str(millis) + '.jpg',
                               'CFRPbinarized_' + str(millis) + '.jpg',
                               'CFRPlabel_' + str(millis) + '.jpg']  # filename can be renamed

        self.imx = -1  # x direction in DIP
        self.imy = -1  # y direction in DIP
        self.resizeratio = 1.0  # record ratio of scaling if zoomin is called
        self.defectno = -1  # record number of defects
        self.step = -1  # means mm per pixel
        self.labels = None

    def loadcsv(self):
        with open(self.inputpath, 'r') as csvfile:
            tempfile = csv.reader(csvfile)
            data_raw = []
            for row in tempfile:
                data_raw.append(list(map(float, row)))
        (self.imx, self.imy) = (len(data_raw), len(data_raw[0]))

        mn = min(min(rrow) for rrow in data_raw)
        mx = max(max(rrow) for rrow in data_raw)
        for i in range(self.imx):
            for j in range(self.imy):
                data_raw[i][j] = ((data_raw[i][j] - mn) / (mx - mn)) * 255
                data_raw[i][j] = int(data_raw[i][j])
        # change to np type so cv2 can read it as an image
        data_raw = np.array(data_raw)
        cv2.imwrite(self.outputimagname[0], data_raw)

    def dimensionfit(self,dimy,dimx):
        src=cv2.imread(self.outputimagname[0])
        self.imy = int(dimy * self.imx / dimx)
        # 86/140=x/200
        src = cv2.resize(src, (self.imy, self.imx), interpolation=cv2.INTER_AREA)
        cv2.imwrite(self.outputimagname[0], src)

    def zoomin(self,imylength=600):
        resizeimy, resizeimx = imylength, int(imylength / self.imy * self.imx)
        self.resizeratio = resizeimy / self.imy
        # resizeimy,resizeimx=imy,imx
        src = cv2.imread(self.outputimagname[0])
        src = cv2.resize(src, (resizeimy, resizeimx), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(self.outputimagname[0], src)

    def preprocess(self,medianksize=5,cliplim=3.0,gridsize=(8,8)):
        src = cv2.imread(self.outputimagname[0])
        src = cv2.medianBlur(src, medianksize)
        cv2.imwrite(self.outputimagname[1], src)
        img = cv2.imread(self.outputimagname[1], 0)
        clahe = cv2.cv2.createCLAHE(clipLimit=cliplim, tileGridSize=gridsize)
        cl1 = clahe.apply(img)
        cv2.imwrite(self.outputimagname[1], cl1)

    def morphology(self, thresh=147, ksize_OPEN=(25, 25), ksize_CLOSE=(50, 50)):
        binarized = cv2.imread(self.outputimagname[1], cv2.IMREAD_GRAYSCALE)
        ret, binarized = cv2.threshold(binarized, thresh, 255, cv2.THRESH_BINARY)  # 83 #255-int(0.43*255)
        cv2.imwrite(self.outputimagname[2], binarized)

        # use open operation to delete existing small blocks
        kel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize_OPEN)
        binarized = cv2.morphologyEx(binarized, cv2.MORPH_OPEN, kel_open)
        cv2.imwrite(self.outputimagname[2], binarized)
        # use close operation to smooth edges
        kel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize_CLOSE)
        binarized = cv2.morphologyEx(binarized, cv2.MORPH_CLOSE, kel_close)
        cv2.imwrite(self.outputimagname[2], binarized)
        cv2.bitwise_not(binarized, binarized)
        cv2.imwrite(self.outputimagname[2], binarized)

        kel_ero = [[1] * 55 for _ in range(4)]
        kel_ero = np.array(kel_ero).T
        binarized = cv2.erode(binarized, kel_ero)
        cv2.imwrite(self.outputimagname[2], binarized)
        self.labels = measure.label(binarized)

    def skimeasure(self,binarized):
        #self.labels = measure.label(binarized)  # labels is a ndarray of same shape of skeleton image, but use 1~N to mark skeleton
        self.defectno = max(max(rrow) for rrow in self.labels)

        defectarea = []
        defectcenter = []
        defectecc = []
        props = measure.regionprops(self.labels)
        for i in range(self.defectno):
            defectarea.append(props[i].area)
            defectcenter.append(props[i].centroid)
            defectecc.append(props[i].eccentricity)



        prev_defectno = self.defectno

        popindex=[]
        for i in range(prev_defectno):
            if defectarea[i]>(min(defectarea)*20) and defectecc[i]>0.9:
                popindex.append(i)
                self.defectno =self.defectno - 1

        for i in range(len(popindex)):
            defectarea.remove(defectarea[i])
            defectcenter.remove(defectcenter[i])

        x = []
        y = []
        for i in range(len(defectcenter)):
            x.append(int(defectcenter[i][0]))
            y.append(int(defectcenter[i][1]))

        imskeleton = cv2.imread(self.outputimagname[0])

        for i in range(self.defectno):
            cv2.circle(imskeleton, (y[i], x[i]), 20, (0, 255, 0), 3)
            cv2.putText(imskeleton, str(i + 1)
                        , (y[i], x[i])
                        , cv2.FONT_HERSHEY_SIMPLEX, 0.6
                        , (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imwrite(self.outputimagname[3], imskeleton)

        return defectarea,defectcenter

    def realcenter(self,defectcenter):

        reszieddim = (int(self.imy * self.resizeratio), int(self.imx * self.resizeratio))
        #print(defectcenter)
        realcoords=[]
        for i in range(len(defectcenter)):
            realcoords.append((round(defectcenter[i][1]/reszieddim[0]*self.imy,0),round((reszieddim[1] - defectcenter[i][0])/reszieddim[1]*self.imx,0)))

        return realcoords

    def realarea(self,defectarea):
        realarea=[0]*len(defectarea)
        for i in range(len(defectarea)):
            realarea[i] = round(defectarea[i] / self.resizeratio, 1)

        return realarea





