#Code written by Omri Temkin, David Lam, Ollie Church


from cgi import test
import numpy as np
import pandas as pd
import sys
from matplotlib import pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.fft import rfft, rfftfreq
from scipy.fft import irfft
from scipy.stats import iqr
import csv
from scipy.signal import butter, lfilter
import os
import ctypes
from datetime import datetime
import heapq as hp
import time


class FFTLine:
    def __init__(self,filename,SamplesPerPixel,CoilFrequency,SensorFrequency,SampleFrequency,Gain):
        #save parameters for signal processing (SP) in local variables
        now = datetime.now()
        self.FFTOutFile = f'{filename}.csv'
        self.SamplesPerPixel = SamplesPerPixel
        self.CoilFrequency = CoilFrequency
        self.SensorFrequency = SensorFrequency
        self.SampleFrequency = SampleFrequency
        self.Gain = Gain
        self.firstline = False
        
        

    def FFTData(self,rowCounter,rowArray):
        tic = time.perf_counter()
        #filter functions, commented out as currently unused
        # def butter_bandpass(lowcut, highcut, fs, order=5):
        #     return butter(order, [lowcut, highcut], fs=fs, btype='band')

        # def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
        #     b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        #     y = lfilter(b, a, data)
        #     return y

        # open results file in the write mode
        f = open(f'./Results/{self.FFTOutFile}', 'a') 
        wtr = csv.writer(f, delimiter=',', lineterminator='\n')
        
        #generator function (google it, interesting and useful) that outputs a pixel's worth of data from the picoscope
        #the variable names here are currently very unclear and could do with changing
        def chunks(lst, n): 
                    """Yield successive n-sized chunks from lst."""
                    #print('calling chunks')
                    for i in range(0, len(lst), n):
                        yield lst[i:i + n]   

        sum = 0
        aver = 0     
        a = chunks(rowArray,self.SamplesPerPixel)
        #more unused filtering
        #a = butter_bandpass_filter(a , 360e3,380e3, 1953125, order=9)
        FFTLineabs = []
        FFTLinemax = []
        dt = 1/self.SampleFrequency
        #iterate over generator and perform signal processing on each pixel
        for val in a:
            #perform fft and take the absolute values
            FFTPixel = rfft(val) 
            FFTLineabs = abs(FFTPixel)
            

            #get frequency bins
            freq=rfftfreq(len(val),d=dt)
            
            #signal processing, sets values outside of sum and difference frequencies to zero
            points_per_freq = len(FFTLineabs) / (self.SampleFrequency / 2)
            CoilFreq = int(points_per_freq * self.CoilFrequency)
            upperBandCutoff = int(points_per_freq * (self.CoilFrequency+self.SensorFrequency))
            lowerBandCutoff = int(points_per_freq * (self.CoilFrequency-self.SensorFrequency)) ##get rid of 200KHz
            SensorBias = int(points_per_freq * self.SensorFrequency) ##get rid of 30KHz
            FFTLineabs[CoilFreq - 40 : CoilFreq + 40] = 0 ##Set Freq bin of Coil to 0
            FFTLineabs[SensorBias - 50 : SensorBias + 50] = 0
            FFTLineabs[upperBandCutoff +1: 10000000] = 0 ##Set Sensor Biasing Freq bin to 0
            FFTLineabs[0 :  lowerBandCutoff-1] = 0
            
            #get largest value of secondary mf.
            FFTout =np.amax(FFTLineabs)
            sum = sum+ round(FFTout)
            FFTLinemax.append(FFTout) #add largest absolute value of secondary magnetic field to array
        
        aver = sum /(len(FFTLinemax))

        #code that removes outliers
        

        Q1 = np.quantile(FFTLinemax,0.25)
        Q3 = np.quantile(FFTLinemax,0.75)
        IQR = Q3 - Q1
        low = Q1 - 1.5*IQR
        up = Q3 + 1.5*IQR

        for i in range(len(FFTLinemax)):
            
            if FFTLinemax[i]>up or FFTLinemax[i]<low:
                FFTLinemax[i] = aver
            

            FFTLinemax[i] = FFTLinemax[i] - aver
        
        toc = time.perf_counter()
        #times how long the signal processing takes, could be taken out
        print(f"Time Taken is {toc - tic:0.4f} .")
        #set variables back to zero for next run
        aver = 0
        sum = 0
        #write results of row to results file
        wtr.writerow(FFTLinemax)


      

            
            
        

    






