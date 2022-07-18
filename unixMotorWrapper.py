#imports C functions into python functions, in order to neated up the code
#hopefully there will be no issues with speed.

#just need function to do setup and motor parameter and then functions to move x and y
from logging import exception
import ctypes as  pyC
import serial
import sys
import glob

motordll = pyC.CDLL("./unixMotors.so")


#example mac serial ports: 
#['/dev/cu.usbmodem3', '/dev/cu.usbmodem4', '/dev/cu.usbmodemTMCSTEP1']

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.usbmodem*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result




def MotorStartup(speed):
    try:
        SerialPortsList = serial_ports()
        print(SerialPortsList)
        

        #motordll.openSerialPorts(f"\\\\\\\.\\\{SerialPortsList[0]}",f"\\\\\\\.\\\{SerialPortsList[1]}",f"\\\\\\\.\\\{SerialPortsList[2]}")

        string1 : pyC.Array[pyC.c_char] = pyC.create_string_buffer(bytes(SerialPortsList[0],'utf-8'))
        string2 : pyC.Array[pyC.c_char] = pyC.create_string_buffer(bytes(SerialPortsList[1],'utf-8'))
        string3 : pyC.Array[pyC.c_char] = pyC.create_string_buffer(bytes(SerialPortsList[2],'utf-8'))
        
        motordll.openSerialPorts(string1,string2,string3)

        motordll.checkMotorAssignment()
        checkMotors = motordll.motorSetup(speed)
        if checkMotors != 1:
            
            raise Exception ("Motor Failure")
    except:
        print("Motors not found")
        return 0
    
        

        
def setXspeed(speed):
    print(f'setting x speed to {speed}')
    motordll.setXmotorSpeed(int(speed))

def moveX(stepsToMove):
    motordll.XAxismoveToPositionN(int(stepsToMove))

def moveY(stepsToMove):
    motordll.YAxismoveToPositionN(int(stepsToMove))


def closePorts():
    motordll.closeSerialPorts()

def checkMotorPower():
    checkMotors = motordll.checkMotorPower()
    
    if checkMotors != 1:
        return 1
    else:
        return 0



