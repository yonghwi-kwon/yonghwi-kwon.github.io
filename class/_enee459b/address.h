
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <ctype.h>
#include <stdlib.h>
#include <unistd.h>


#define MAXDATA 50
#define MAXCONTACTS 100
#define INTCONVERSION 48
#define ADDRESSBOOK ".addressbook"
#define MAXCOMMENT 300
#define BASETEN 10


typedef struct{
   char firstName[MAXDATA];
   char lastName[MAXDATA];
   char title[MAXDATA];
   char relation[MAXDATA];
   char eMail[MAXDATA];
   char homePhone[MAXDATA];
   char cellPhone[MAXDATA];
   char workPhone[MAXDATA];
   char address[MAXDATA];
   char faxNumber[MAXDATA];
   char aimName[MAXDATA];
   char comments[MAXCOMMENT];
} contact;


contact newContact(contact contacts[]);
int viewContact(contact contacts[], char display[]);
int searchContacts(contact contacts[], contact matches[], char description[]);
int findFLName(contact contacts[], contact matches[], char compareTo[], char 
 contactPart[]);
void printFLName(char firstname[], char lastname[], contact contacts[], contact 
 matches[], int *matchindex, int index, int *count);
void editContact(contact contacts[]);
void scanline(char input[], int maxInputLength);
void scanInt(char scan[], int *integer);
void saveInfo(char filename[], contact contacts[]);
void getInfo(contact contacts[]);
int getFileLine(char contactPiece[], int maxData, FILE* ptr);
int findEmptySpot(contact contacts[]);
void printContact(contact cont);
void clearContact(contact contacts[], int index);
void executeOrder66();
void mainMenu();

