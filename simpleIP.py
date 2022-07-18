import pandas as pd
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
#very simple image processing code that normalises the pixel values
#and reduces the X dimension by a factor of 10.
#this code could be modified so that the image can be scaled down by a factor of the users  choice


def showImage(filename,colourmap):
    

        img = pd.read_csv(f'./Results/{filename}.csv')
        imgArray = np.asarray(img)
        print(imgArray.shape)
        rows, columns = imgArray.shape
        maxVal = np.max(imgArray)
        minVal = np.min(imgArray)


        resized = np.zeros((rows,int(columns/10)))
        print(f'shape of output image is: {resized.shape}')
        for row in range(rows):
            for column in range(0,(int(columns)-10),10):
                upperLimit = column +9
                PixelSum = np.sum(imgArray[row,column:upperLimit])
                PixelAverage = PixelSum/10
                normalised = (PixelAverage-minVal)/(maxVal-minVal)
                finalValue = normalised
                resized[row,int(column/10)] = finalValue






        plt.imshow(resized,cmap=colourmap)
        plt.savefig(f'./Results/{filename}.png')


    

