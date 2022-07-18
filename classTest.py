#code written by Ollie Church
#legacy file implementing scanner control pre-GUI. The code is outdated and will no longer work
#this could be rewritten in order to play with scanner functioning outside of the GUI in a more manageable way

from datetime import datetime
import cleanScannerCode
import motorWrapper
import time

#gets filename based on current date, may want to change this format to 
#a filename that includes scan parameters
now = datetime.now()



#this is the parameter dictionary that defines the scanning parameters
#frequency is in hertz, amplitude in Vrms, motor speed in the arbitrary tmcl units
#gain refers to the gain set by the jumper on the sensor PCB, was left at 1000 but if changed will need to be changed here too
#captures is a picoscope parameter -see picoscope 5000 series programming guide for more information and for ranges of sampling periods
#resolutions (also can be seen in GUI) and voltage range and timebase

parameterDictionary = {
    "coilFrequency" : 900e3,
    "sensorFrequency" : 55e3,
    "coilAmplitude" :3.8,
    "sensorAmplitude":4,
    "samplingPeriod" :  64,
    "picoTimebase" : 1e-9,
    "motorSpeed" : 200,
    "mmMovedX"   : 70,
    "mmMovedY"   : 80,
    "yResolutionMm"   : 0.5,
    "xResolutionMm"   : 0.1,
    "captures"   : 1,
    "gain"       : 1000,
    "PicoResolution" : "PS5000A_DR_16BIT",
    "PicoVoltageRange" : "PS5000A_5V",
    "PicoTimeBase": "PS5000A_NS",
    "filename" : now.strftime("%d%mFFTOutput%H%M")
}


print(parameterDictionary["filename"])
#this try and except was just to be able to interrupt the scan. Made redundant by the GUI
try:
    
    scanner = cleanScannerCode.scannerControl()
    scanner.startMotors()
    scanner.setScanParams(parameterDictionary)
    #time.sleep(120)
    scanner.Scan()
    scanner.endScan()
        
except KeyboardInterrupt:
    scanner.endScan()
    print ("Shutdown requested...exiting")




