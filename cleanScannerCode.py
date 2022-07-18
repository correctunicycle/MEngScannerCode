#code written by Ollie Church
#the hardware control and signal processing are unified in this class
#you could also take the image processing out of the GUI and put it here

#imports
import unixMotorWrapper as motorWrapper
import fGenControl
import PicoScopewithFFT as pico
import FFTLinePixels as FFTLinePixels
import threading
import time
import json
from datetime import datetime
import simpleIP

thread_local = threading.local()





class scannerControl:
    def startMotors(self):
        #runs startup and checks power;
        #motor power should no longer be a problem, somewhat of a legacy check because the power connecters used to be really dodgy
        #and if one motor wasn't on the scanner could try and rip itself apart
        motorWrapper.MotorStartup(100)
        motorStatus = motorWrapper.checkMotorPower()
        return motorStatus
    def setScanParams(self,parameterDictionary):
    
        #parameter dictionary passed from GUI
        #explained in scannerGUI2 file and classtest
        self.parameterDictionary = parameterDictionary
        
        

        #initialise motors ready for scan
        self.startMotors() 

        #pass parameters from dictionary to function generator code
        fGenControl.setFgenParams(self.parameterDictionary["coilFrequency"],self.parameterDictionary["coilAmplitude"],
                                self.parameterDictionary["sensorFrequency"],self.parameterDictionary["sensorAmplitude"])
        #turn function generator on
        fGenControl.turnFgenOn()

        #set x speed as desired by user
        #set y speed was never implemented, was not required with our motor movement method
        #but if you wanted to experiment with different motor movements it would be useful.
        #you'd have to edit the C and recompile the dll to do this, the function itself should be trivial to write.
        motorWrapper.setXspeed(self.parameterDictionary["motorSpeed"])
        
        # initialise signal processing with appropriate parameters
        self.fft = FFTLinePixels.FFTLine(self.parameterDictionary["filename"],
                                    self.parameterDictionary["samplesPerPixel"],
                                    self.parameterDictionary["coilFrequency"],
                                    self.parameterDictionary["sensorFrequency"],
                                    self.parameterDictionary["samplingFrequency"],
                                    self.parameterDictionary["gain"])

        # initialise picoscope with appropriate parameters
        
        self.picoOb = pico.StreamData(self.parameterDictionary["PicoResolution"],
                                self.parameterDictionary["PicoVoltageRange"],
                                self.parameterDictionary["samplingPeriod"],
                                self.parameterDictionary["PicoTimeBase"],
                                self.parameterDictionary["bufferSize"],
                                self.parameterDictionary["captures"])
        print('finished setup')
    




    
    #simpleIP.showImage(parameterDictionary["filename"])



        


    def endScan(self):
        #saves parameter dictionary to json file for records. 
        with open(f'./Results/{self.parameterDictionary["filename"]}.json','w') as fp:
            json.dump(self.parameterDictionary,fp)
        #send everything back to zero
        motorWrapper.setXspeed(500)
        motorWrapper.moveX(0)
        motorWrapper.moveY(0)
        motorWrapper.closePorts()
        
        self.picoOb.ClosePico()
        fGenControl.turnFgenOff()

    

    def Scan(self,row):
            #main scanning loop. 
            #create picoscope thread
            picoT1 = threading.Thread(target=self.picoOb.GetVal,args=(self.parameterDictionary["bufferSize"],row,self.fft))
            
            

            
            #send y motors to next row
            motorWrapper.moveY(self.parameterDictionary["yIncrement"]*row)
            #set X speed for scanning, required due to change in speed for drawback
            motorWrapper.setXspeed(self.parameterDictionary["motorSpeed"])
            #start collecting values from the picoscope and send the motors across the material
            picoT1.start()
            motorWrapper.moveX(self.parameterDictionary["xStepRange"])

            picoT1.join()
            #resume once picoscope done, although should be in time with the motors anyway
            #set speed for drawback, a parameter that may want to be added to scanning parameters and in turn the GUI
            #send motors back to zero.
            motorWrapper.setXspeed(1000)
            motorWrapper.moveX(0)
        
        
        
        
       
    







            
       
                                
    