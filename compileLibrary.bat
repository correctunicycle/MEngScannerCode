gcc -c -o motorob.o windowsMotorCode.c
gcc -o firstMotorLib.dll -s -shared motorob.o 
