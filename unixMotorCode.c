//for a commented version of this code please see the windows version
//the only difference between the windows code and this is the serial api used
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <stdint.h>
#include <termios.h>

#define TMCL_ROR 1
#define TMCL_ROL 2
#define TMCL_MST 3
#define TMCL_MVP 4
#define TMCL_SAP 5
#define TMCL_GAP 6
#define TMCL_STAP 7
#define TMCL_RSAP 9
#define TMCL_SGP 9
#define TMCL_GGP 10
#define TMCL_STGP 11
#define TMCL_RSGP 12
#define TMCL_RFS 13
#define TMCL_SIO 14
#define TMCL_GIO 15
#define TMCL_SCO 30
#define TMCL_GCO 31
#define TMCL_CCO 32

//Opcodes of TMCL control functions (to be used to run or abort a TMCL program in the module)
#define TMCL_APPL_STOP 128
#define TMCL_APPL_RUN 129
#define TMCL_APPL_RESET 131

//Options for MVP commandds
#define MVP_ABS 0
#define MVP_REL 1
#define MVP_COORD 2

//Options for RFS command
#define RFS_START 0
#define RFS_STOP 1
#define RFS_STATUS 2

#define FALSE 0
#define TRUE 1

//handles for serial ports
int hComm;
int hComm2;
int hComm3;


void openhComm(const char *device);
void openhComm2(const char *device);
void openhComm3(const char *device);
int checkMotorPower();
void setXmotorSpeed();
int YAxismoveToPositionN(int Position);
int XAxismoveToPositionN(int Position);
void openSerialPorts(char comString1[],char comstring2[],char comstring3[]);
void closeSerialPorts();
void checkMotorAssignment();
void SendCmd(int comport,  uint8_t Address, uint8_t Command, uint8_t Type, uint8_t Motor, int Value);
uint8_t GetResult(int Handle, uint8_t *Address, uint8_t *Status, int *Value);
int motorSetup(int motorSpeed);




int main(){
	return 0;
}


int checkMotorPower(){
	uint8_t Type, Motor,Status = 0x00;
	uint8_t Address = 0x01;
	int Value1 = 0;
	int Value2 = 0;
	int Value3 = 0;
	int Position1 = 1;
	int Position0 = 0;
	printf("Moving to position %d \n",Position1);
	SendCmd(hComm,Address,TMCL_MVP,0x00,0x00,Position1);
	GetResult(hComm,&Address,&Status,&Value1);
	if(Status == 6){
		SendCmd(hComm,Address,TMCL_GGP,0x42,0x00,0);
		GetResult(hComm,&Address,&Status,&Value1);
		printf("Issue with motor power on motor id %d, do not proceed \n",Value1);
		return 0;
	}
	SendCmd(hComm,Address,TMCL_MVP,0x00,0x00,Position0);
	GetResult(hComm,&Address,&Status,&Value1);
	SendCmd(hComm2,Address,TMCL_MVP,0x00,0x00,Position1);
	GetResult(hComm2,&Address,&Status,&Value2);
	if(Status == 6){
		SendCmd(hComm,Address,TMCL_GGP,0x42,0x00,0);
		GetResult(hComm,&Address,&Status,&Value2);
		printf("Issue with motor power on motor id %d, do not proceed \n",Value2);
		return 0;
	}
	SendCmd(hComm2,Address,TMCL_MVP,0x00,0x00,Position0);
	GetResult(hComm2,&Address,&Status,&Value2);
	SendCmd(hComm3,Address,TMCL_MVP,0x00,0x00,Position1);
	GetResult(hComm3,&Address,&Status,&Value3);
	if(Status == 6){
		SendCmd(hComm,Address,TMCL_GGP,0x42,0x00,0);
		GetResult(hComm,&Address,&Status,&Value3);
		printf("Issue with motor power on motor id %d, do not proceed \n",Value3);
		return 0;
	}
	SendCmd(hComm3,Address,TMCL_MVP,0x00,0x00,Position0);
	GetResult(hComm3,&Address,&Status,&Value3);
	return 1;

}



void checkMotorAssignment(){
 	uint8_t Type, Motor,Status = 0x00;
	uint8_t Address = 0x01;
 	int Value = 0;
	SendCmd(hComm3,Address,TMCL_GGP,0x42,0x00,0);
	GetResult(hComm3,&Address,&Status,&Value);
	printf("Value returned by hcomm3 is %d \n",Value);
	if(Value != 2){
		printf("Something has gone terribly wrong with motor assignment \n");
	}
}







void openhComm(const char *device){
	
	 hComm = open(device, O_RDWR | O_NOCTTY);
  if (hComm == -1)
  {
    printf("Opening hcomm failed \n");
    
  }
 
 
}

void openhComm2(const char *device){
	hComm2 = open(device, O_RDWR | O_NOCTTY);
  if (hComm2 == -1)
  {
    printf("Opening hcomm2 failed \n");
  }
 
 
}

void openhComm3(const char *device){
	hComm3 = open(device, O_RDWR | O_NOCTTY);
  if (hComm3 == -1)
  {
    printf("Opening hcomm3 failed \n");
  }
 
 
}



void openSerialPorts(char comstring1[],char comstring2[],char comstring3[]){
	
	uint8_t Address = 0x01;
 	uint8_t Type, Motor,Status = 0x00;
 	int Value = 0;
	printf("Comstring1 is %s \n",comstring1);
	
	openhComm(comstring1);

	SendCmd(hComm,Address,TMCL_GGP,0x42,0x00,0);
	GetResult(hComm,&Address,&Status,&Value);
	printf("Value returned by hcomm is %d \n",Value);

	if(Value == 2){
		printf("X motor found, closing hComm, opening hComm3 \n");
		close(hComm);
		openhComm3(comstring1);
		openhComm2(comstring2);
		openhComm(comstring3);
	}


	else{
		openhComm2(comstring2);
		SendCmd(hComm2,Address,TMCL_GGP,0x42,0x00,0);
		GetResult(hComm2,&Address,&Status,&Value);
		printf("Value returned by hcomm2 is %d \n",Value);
		if(Value == 2){
			printf("X motor found, closing hComm2, opening hComm3 \n");
			close(hComm2);
			openhComm3(comstring2);
			openhComm2(comstring3);
	}

 
	else{
		openhComm3(comstring3);
	
	}
	}
	
}

void closeSerialPorts(){
	close(hComm);
  	close(hComm2);
  	close(hComm3);
}


void setXmotorSpeed(int speed){
	uint8_t Address = 0x01;
 	uint8_t Type, Motor,Status = 0x00;
 	int Value = 0;
	SendCmd(hComm3,Address,TMCL_SAP,0x04,0x00,speed);
	GetResult(hComm3,&Address,&Status,&Value);

}


// int open_serial_port(const char * device)
// {
//   printf("getting here in open serial port \n");
//   int fd = open(device, O_RDWR | O_NOCTTY);
//   if (fd == -1)
//   {
//     perror(device);
//     return -1;
//   }
 
 
 
//   return fd;
// }

//size of windows UCHAR is: 1 byte
//size of 




// int main(){
//     printf("hello world \n");
//     const char * device = "/dev/cu.usbmodemTMCSTEP1";
//     uint32_t baud_rate = 9600;
//     uint8_t Address = 0x01;
//     uint8_t Type, Motor,Status = 0x00;
// 	int Value = 0;
//     printf("getting here \n");
//     int fd = open_serial_port(device);
//     motorSetup(500,fd);
//     printf("getting here 2 \n");
//     //SendCmd(fd,0x01,TMCL_SAP,0x01,0x00,0);
//     //GetResult(fd,&Address,&Status,&Value);
//     printf("Command Sent \n");
//     SendCmd(fd,Address,TMCL_MVP,0x00,0x00,20000);
//     GetResult(fd,&Address,&Status,&Value);
//     // SendCmd(fd,0x01,TMCL_MVP,0x01,0x00,0);
//     // GetResult(fd,&Address,&Status,&Value);
//     printf("Axis position is: %d \n",Value);
//     close(fd);
//     return 0;
// }


int motorSetup(int motorSpeed){
	uint8_t Address = 0x01;
 	uint8_t Type, Motor,Status = 0x00;
 	int Value = 0;
SendCmd(hComm,Address,TMCL_SAP,0x9A,0x00,4);
GetResult(hComm,&Address,&Status,&Value);  //Set Pulse divisor
SendCmd(hComm2,Address,TMCL_SAP,0x9A,0x00,4);
GetResult(hComm2,&Address,&Status,&Value);
SendCmd(hComm3,Address,TMCL_SAP,0x9A,0x00,4);
GetResult(hComm3,&Address,&Status,&Value);


SendCmd(hComm,Address,TMCL_SAP,0x99,0x00,6);
GetResult(hComm,&Address,&Status,&Value); //Set Ramp divisor
SendCmd(hComm2,Address,TMCL_SAP,0x99,0x00,6);
GetResult(hComm2,&Address,&Status,&Value);
SendCmd(hComm3,Address,TMCL_SAP,0x99,0x00,6);
GetResult(hComm3,&Address,&Status,&Value);

SendCmd(hComm,Address,TMCL_SAP,0x8C,0x00,3);
GetResult(hComm,&Address,&Status,&Value);  //Set Microstep Resolution
SendCmd(hComm2,Address,TMCL_SAP,0x8C,0x00,3);
GetResult(hComm2,&Address,&Status,&Value);
SendCmd(hComm3,Address,TMCL_SAP,0x8C,0x00,3);
GetResult(hComm3,&Address,&Status,&Value);

SendCmd(hComm,Address,TMCL_SAP,0x04,0x00,100);
GetResult(hComm,&Address,&Status,&Value);  //Set Maximum positioning speed
SendCmd(hComm2,Address,TMCL_SAP,0x04,0x00,100);
GetResult(hComm2,&Address,&Status,&Value);
SendCmd(hComm3,Address,TMCL_SAP,0x04,0x00,motorSpeed);
GetResult(hComm3,&Address,&Status,&Value);

SendCmd(hComm,Address,TMCL_SAP,0x05,0x00,200);
GetResult(hComm,&Address,&Status,&Value);  //Set Maximum acceleration
SendCmd(hComm2,Address,TMCL_SAP,0x05,0x00,200);
GetResult(hComm2,&Address,&Status,&Value);
SendCmd(hComm3,Address,TMCL_SAP,0x05,0x00,200);
GetResult(hComm3,&Address,&Status,&Value);
if(XAxismoveToPositionN(1) == 1 && YAxismoveToPositionN(1)== 1){
	XAxismoveToPositionN(0);
	YAxismoveToPositionN(0);
	printf("Motor Check returning 1 \n");
	return 1;
}
else{
	return 0;
}


}



int YAxismoveToPositionN(int Position){
	
	
	uint8_t Address = 0x01;
	uint8_t Type, Motor,Status = 0x00;
	int Value1 = 0;
	int Value2 = 0;
	//printf("Moving to position %d \n",Position);
	SendCmd(hComm,Address,TMCL_MVP,0x00,0x00,Position);
	GetResult(hComm,&Address,&Status,&Value1);
	if(Status == 6){
		printf("Issue with motor power, do not proceed \n");
		return 0;
	}
	SendCmd(hComm2,Address,TMCL_MVP,0x00,0x00,Position);
	GetResult(hComm2,&Address,&Status,&Value2);
	if(Status == 6){
		printf("Issue with motor power, do not proceed \n");
		return 0;
	}
	SendCmd(hComm,Address,TMCL_GAP,0x08,0x00,0);
	GetResult(hComm,&Address,&Status,&Value1);
	SendCmd(hComm2,Address,TMCL_GAP,0x08,0x00,0);
	GetResult(hComm2,&Address,&Status,&Value2);
	
	

	while(Value1 != 1 && Value2 != 1 ){
		//printf("y motors looping to position %d \n",Position);
		SendCmd(hComm,Address,TMCL_GAP,0x08,0x00,0);
		GetResult(hComm,&Address,&Status,&Value1);
		SendCmd(hComm2,Address,TMCL_GAP,0x08,0x00,0);
		GetResult(hComm2,&Address,&Status,&Value2);
		
	
	}
	return 1;

}


int XAxismoveToPositionN(int Position){
	
	//printf("X Motors Moving to position %d \n", Position);
	uint8_t Address = 0x01;
	uint8_t Type, Motor,Status = 0x00;
	int Value = 0;
	
	SendCmd(hComm3,Address,TMCL_MVP,0x00,0x00,Position);
	GetResult(hComm3,&Address,&Status,&Value);
	
	if(Status == 6){
		printf("Issue with motor power, do not proceed \n");
		return 0;
	}
	
	SendCmd(hComm3,Address,TMCL_GAP,0x08,0x00,0);
	GetResult(hComm3,&Address,&Status,&Value);
	

	
	

	while(Value != 1){
		//printf("X motor Looping  to position %d\n",Position);
		SendCmd(hComm3,Address,TMCL_GAP,0x08,0x00,0);
		GetResult(hComm3,&Address,&Status,&Value);
		//printf("moving to desired position \n");
		

	}
	
	return 1;
	
}



int write_port(int fd, uint8_t * buffer, size_t size)
{
  ssize_t result = write(fd, buffer, size);
  if (result != (ssize_t)size)
  {
    perror("failed to write to port");
    return -1;
  }
  return 0;
}



void SendCmd(int comport,  uint8_t Address, uint8_t Command, uint8_t Type, uint8_t Motor, int Value)
{
	uint8_t TxBuffer[9];
	uint8_t i;

	TxBuffer[0]=Address;
	TxBuffer[1]=Command;
	TxBuffer[2]=Type;
	TxBuffer[3]=Motor;
	TxBuffer[4]=Value >> 24;
	TxBuffer[5]=Value >> 16;
	TxBuffer[6]=Value >> 8;
	TxBuffer[7]=Value & 0xff;
	TxBuffer[8]=0;
	for(i=0; i<8; i++)
		TxBuffer[8]+=TxBuffer[i];
	//Now, send the 9 bytes stored in TxBuffer to the module
  //(this is MCU specific) 
	ssize_t Status = 0 ;
	Status = write(comport,TxBuffer,9);
    printf("Status us %zd \n",Status);

	
}


uint8_t GetResult(int Handle, uint8_t *Address, uint8_t *Status, int *Value)
{
	uint8_t RxBuffer[9], Checksum;
	
	int i;
	

  //First, get 9 bytes from the module and store them in RxBuffer[0..8]
  //(this is MCU specific)
	ssize_t ReadStatus = 0 ;
	ReadStatus = read(Handle,RxBuffer,9);
	//printf("Read File Status is: %d \n",ReadStatus);
	//Check the checksum
	Checksum=0;
	for(i=0; i<8; i++)
		//printf("%d \n",RxBuffer[i]);
		Checksum+=RxBuffer[i];

	//printf("checksum is %d, should be %d \n",Checksum,RxBuffer[8]);
	if(Checksum!=RxBuffer[8]){ 
		//printf("checksum returning false");
		return 0;
	}
	//printf("Status before assignment is %d \n",*Status);
	//Decode the datagram
	*Address=RxBuffer[0];
	*Status=RxBuffer[2];
	//printf("Status returned by Motor is %d \n",*Status);
	*Value=(RxBuffer[4] << 24) | (RxBuffer[5] << 16) | (RxBuffer[6] << 8) | RxBuffer[7];
	/*
	if (*Value == 6){
		printf("Motor Error - Likely Power");
	}
	*/
	return 1;
}
