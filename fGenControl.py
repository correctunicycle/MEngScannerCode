#functions for function generator control using pyvisa, as well as pyvisa the appropriate backend will need to be installed
#see pyvisa documentation for more information
#code written by Ollie Church
import pyvisa 

def turnFgenOn():
    #find pyvisa resources connected
    rm = pyvisa.ResourceManager()
    #if you don't know the ID of your specific resource then you can use the print statement to see.
    #print(rm.list_resources())
    #open function generator, the ID of the string is specific to the instrument in question,
    #the one below is specific to the instrument we were using and would have to be updated if a 
    #different function generator was used
    #The string can be changed to something more phonetically comfortable - see pyvisa docs
    my_instrument = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA190300033::0::INSTR')
    my_instrument.read_termination = '\n'
    my_instrument.write_termination = '\n'
    #turn both output channels on
    my_instrument.write(':OUTP1 ON')
    my_instrument.write(':OUTP2 ON')
    #close resource object
    my_instrument.close()



def setFgenParams(coilFrequency, coilAmplitude,sensorFrequency, sensorAmplitude):
    #same process as for first function
    rm = pyvisa.ResourceManager()
    #print(rm.list_resources())
    my_instrument = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA190300033::0::INSTR')

    my_instrument.read_termination = '\n'
    my_instrument.write_termination = '\n'
    #set voltage unit of both channels to RMS
    my_instrument.write(':SOUR1:VOLT:UNIT VRMS')
    my_instrument.write(':SOUR2:VOLT:UNIT VRMS')
    #set output of both channels to sin wave of desired frequency and amplitude
    #(Frequency in hertz.)
    my_instrument.write(f':SOUR1:APPL:SIN {coilFrequency},{coilAmplitude},0,0')
    my_instrument.write(f':SOUR2:APPL:SIN {sensorFrequency},{sensorAmplitude},0,0')
    my_instrument.close()




def turnFgenOff():
    #turn both channels off.
    rm = pyvisa.ResourceManager()
    my_instrument = rm.open_resource('USB0::0x1AB1::0x0642::DG1ZA190300033::0::INSTR')
    my_instrument.write(':OUTP1 OFF')
    my_instrument.write(':OUTP2 OFF')
    my_instrument.close()
