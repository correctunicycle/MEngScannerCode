# MEngScannerCode
Final version of code for MEng scanner project. Operation of the software is shown in the video below:


https://user-images.githubusercontent.com/54482145/179558570-3a4a8fc3-f7d2-4690-bdd6-dd51211e6dd6.mp4

This software was made completely from scratch. Code written by myself unless otherwise mentioned. The following code files perform the following functions:

* DIP.py: Image processing software, written by Yuntao Zhang 
* FFTLinePixels.py: Signal processing written by David Lam, Omri Temkin, and myself.
* NewUnixMotors.so: Shared library for motor control for Unix-like machines (Should work for MacOS and Linux).
* PicoScopewithFFT.py: Collects values from PicoScope 5442D ADC and passes data to signal processing
* classTest.py: an example of how to use the code without the GUI
* cleanScannerCode.py: where all modules are collected for overall scanner control.
* compileLib.sh: Compile shared library for Unix motor code
* compileLibrary.bat: Compile shared library for Windows motor code
* fGenControl.py : Function generator control using PyVisa
* firstMotorLib.dll : Shared library for motor control for Windows machines
* scanParams.py : Calcualtes secondary scanning parameters (See software report for more information)
* scannerGUI2.py : PyQt GUI code
* simpleIP : Some very basic Matplotlib image processing code
* unixMotorCode : Source file for unix motor code 
* unixMotorWrapper : Wrapper for unix motor code, will also work with the windows code, just need to change the imported library. Code could very easily be added to do this automatically. 
* windowsMotorCode : Source file for unix motor code

There are a number of things that could be improved about this code, most urgently that little addition to the motor wrapper. It should also be packaged as an executable but there was not time. To understand the methodology and design process please see the software report PDF. The GUI is not mentioned in the report as it was created afterwards.
