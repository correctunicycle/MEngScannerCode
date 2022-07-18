import csv
import time
import ctypes
import numpy as np
import threading
#from multiprocessing import Process
import pandas as pd
import asyncio
from picosdk.ps5000a import ps5000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok



#Function to get values from picoscope, based off example code that can be found on the Picosdk python wrappers github
#Written by Ollie Church and David Lam


thread_local = threading.local()

class StreamData:
    def __init__(self,BitRes,VoltRange,SampInterval,SampIntUnit,BuffSize,Caps):
        #import parameters from scanner control file
        self.BitRes = BitRes
        self.VoltRange = VoltRange
        self.SampInterval = SampInterval
        self.SampIntUnit = SampIntUnit
        self.BuffSize = BuffSize
        self.Caps = Caps
        self.firstline = False

        self.chandle = ctypes.c_int16()
        self.status = {}

        

        # Open PicoScope 5000 Series device
        # Resolution set to 16 Bit
        
        self.resolution =ps.PS5000A_DEVICE_RESOLUTION[self.BitRes] ## 16bits needed
        # Returns handle to chandle for use in future API functions
        self.status["openunit"] = ps.ps5000aOpenUnit(ctypes.byref(self.chandle), None, self.resolution)

        try:
            assert_pico_ok(self.status["openunit"])
        except: # PicoNotOkError:

            self.powerStatus = self.status["openunit"]

            if self.powerStatus == 286:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, self.powerStatus)
            elif self.powerStatus == 282:
                self.status["changePowerSource"] = ps.ps5000aChangePowerSource(self.chandle, self.powerStatus)
            else:
                raise

            self.assert_pico_ok(self.status["changePowerSource"])


        enabled = 1
        disabled = 0
        analogue_offset = 0.0

        # Set up channel A
        # handle = chandle
        # channel = PS5000A_CHANNEL_A = 0
        # enabled = 1
        # coupling type = PS5000A_DC = 1
        # range = PS5000A_2V = 7
        # analogue offset = 0 V
        self.channel_range = ps.PS5000A_RANGE[VoltRange]
        self.status["setChA"] = ps.ps5000aSetChannel(self.chandle,
                                                ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],
                                                enabled,
                                                ps.PS5000A_COUPLING['PS5000A_DC'],
                                                self.channel_range,
                                                analogue_offset)
                                                
        assert_pico_ok(self.status["setChA"])

        # Size of capture
        self.sizeOfOneBuffer = BuffSize #64M
        self.numBuffersToCapture = Caps #maximum captures 250K

        self.totalSamples = self.sizeOfOneBuffer * self.numBuffersToCapture

        # Create buffers ready for assigning pointers for data collection
        global bufferAMax
        bufferAMax = np.zeros(shape=self.sizeOfOneBuffer, dtype=np.int16)
        self.memory_segment = 0

        # Set data buffer location for data collection from channel A
        # handle = chandle
        # source = PS5000A_CHANNEL_A = 0
        # pointer to buffer max = ctypes.byref(bufferAMax)
        # pointer to buffer min = ctypes.byref(bufferAMin)
        # buffer length = maxSamples
        # segment index = 0
        # ratio mode = PS5000A_RATIO_MODE_NONE = 0

        self.status["setDataBuffersA"] = ps.ps5000aSetDataBuffers(self.chandle,
                                                            ps.PS5000A_CHANNEL['PS5000A_CHANNEL_A'],
                                                            bufferAMax.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                            None,
                                                            self.sizeOfOneBuffer,
                                                            self.memory_segment,
                                                            ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status["setDataBuffersA"])

    #this is the function that is attached to the picoscope thread in the main scanning loop.        
    def GetVal(self,userSamples,rowCounter,fft):
         tic = time.perf_counter()
         if(userSamples !=0):
            #if user sets a value for the number of samples they want to collect then this value will be used
            #although actually this part is now automatically set when the user enters their desired scanning parameters anyway
            #to ensure that the number of values taken will be in time with the movement of the motors.
            #otherwise equal to value set in constructor. The != 0 could be changed to None.
            self.totalSamples = userSamples
        
         
         sampleInterval = ctypes.c_int32(self.SampInterval) ## sample frequency
         self.sampleUnits = ps.PS5000A_TIME_UNITS[self.SampIntUnit] #set timebase
        # We are not triggering:
         self.maxPreTriggerSamples = 0
         self.autoStopOn = 1
        # No downsampling:
         self.downsampleRatio = 1
         global bufferCompleteA
         bufferCompleteA = np.zeros(shape=self.totalSamples,dtype=np.int16)
         
         global nextSample
         nextSample = 0
         self.autoStopOuter = False
         wasCalledBack = False
         
         def streaming_callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
            global nextSample, autoStopOuter, wasCalledBack, sourceEnd, destEnd
            wasCalledBack = True
            destEnd = nextSample + noOfSamples
            sourceEnd = startIndex + noOfSamples
            bufferCompleteA[nextSample:destEnd] = bufferAMax[startIndex:sourceEnd]
            nextSample += noOfSamples
            if autoStop:
                autoStopOuter = True


        # Convert the python function into a C function pointer.
         print('starting getting values')
         cFuncPtr = ps.StreamingReadyType(streaming_callback)
         self.status["runStreaming"] = ps.ps5000aRunStreaming(self.chandle,                    ######### read a second time
                                                        ctypes.byref(sampleInterval),
                                                        self.sampleUnits,
                                                        self.maxPreTriggerSamples,
                                                        self.totalSamples,
                                                        self.autoStopOn,
                                                        self.downsampleRatio,
                                                        ps.PS5000A_RATIO_MODE['PS5000A_RATIO_MODE_NONE'],
                                                        self.sizeOfOneBuffer)
         assert_pico_ok(self.status["runStreaming"])

         actualSampleInterval = sampleInterval.value
         actualSampleIntervalNs = actualSampleInterval ## sample frequency
        
         while nextSample < self.totalSamples and not self.autoStopOuter:
            wasCalledBack = False
            self.status["getStreamingLastestValues"] = ps.ps5000aGetStreamingLatestValues(self.chandle, cFuncPtr, None)
            if not wasCalledBack:
                # If we weren't called back by the driver, this means no data is ready. Sleep for a short while before trying
                # again.
                    time.sleep(0.01)
         toc = time.perf_counter()
         #another bit of timing that could be taken out
         print(f'Finished Getting Values in {toc - tic:0.4f} seconds')
         
         filename = f'Row{rowCounter}'
         #string1 : ctypes.Array[ctypes.c_char] = ctypes.create_string_buffer(bytes(filename,'utf-8'))
         #bufferConversion = (ctypes.c_int16 * len(bufferCompleteA))(*bufferCompleteA)
         #arrayPointer = ctypes.POINTER(ctypes.c_int16)
         #There was a line here where the raw ADC values were converted into mV values
         #it was taken out to increase speed as it was found that the raw values worked equally well.
         #start signal processing thread.
         fftT1 = threading.Thread(target=fft.FFTData,args=(rowCounter,bufferAMax,))
         fftT1.start()
         
        
         
         
        

         
    def ClosePico (self):
        # Stop the scope
        # handle = chandle
        self.status["stop"] = ps.ps5000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

        # Disconnect the scope
        # handle = chandle
        self.status["close"] = ps.ps5000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])
        print("Picoscope Closed")

