 
#include "address.h"



// the main function is not less than 40 lines.  This is for a good reason.  If 
// the user selects an option, the main function runs a few tests before running 
// the program to make sure that it is ok to run the function
// i.e. check to make sure the contacts is not full
int main(){
   
   system("clear");
   mainMenu();
   
   // must forcefully exit the program when done because of the 'exit' 
   // command in the function scanline()
   // (if exit() is not used and the user chooses to exit, then the 
   // program would go back to the newContact function and continue where 
   // it left off.
   exit(0);
}


/************************  FUNCTION DEFINITIONS  ************************/


contact newContact(contact contacts[]){
   contact tempContact;
   char correctData[MAXDATA];
   int redo;
   int index;
   char overwrite[MAXDATA];
   int arrayPlace;
   int delContact = MAXCONTACTS;
   int exit = 0;

   do{
      redo = 0;
      printf("\nPlease enter the following information on the contact:\n\n");
      printf("NOTE: If you leave a field blank (just press enter), then\n");
      printf("'Not Entered' will automatically be placed into the field.\n\n");
      printf("NOTE: Type 'Exit' or 'exit' to exit back to the main menu\n\n");
   
      printf("First Name:  ");
      scanline(tempContact.firstName, MAXDATA);
   
      printf("Last Name:  ");
      scanline(tempContact.lastName, MAXDATA);
   
      // After the user inputs a first and last name, check to see
      // if a contact already exists with the same first and last name
      // If the contact does exists already, ask the user if they want
      // to overwrite it (if not, they are returned to the main function
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(tempContact.firstName, contacts[index].firstName) == 0 && 
          strcmp(tempContact.lastName, contacts[index].lastName) == 0){
            printf("\nA contact already exists with the name: %s %s\n\n", 
             tempContact.firstName, tempContact.lastName);
            printf("If you say yes and change you mind while inputting data,");
            printf("\njust type exit or Exit to cancel\n\n");
            printf("Do you want to overwrite it (y/n)?  ");
            scanline(overwrite, MAXDATA);
            
            if(overwrite[0] == 'y' || overwrite[0] == 'Y'){
               arrayPlace = findEmptySpot(contacts);
               
               for(index = 0; index < MAXCONTACTS; index++){
                  if(strcmp(contacts[index].firstName, tempContact.firstName) == 
                   0 && strcmp(contacts[index].lastName, tempContact.lastName) 
                   == 0){
                     delContact = index;
                     break;
                  }
               }
               if(arrayPlace == 0 || arrayPlace - 1 == delContact){
                  clearContact(contacts, delContact);
               }
               else{
                  contacts[delContact] = contacts[arrayPlace - 1];
                  clearContact(contacts, arrayPlace - 1);
               }
            }
            else{
               exit = 1;
            }
         }        
      }
      
      // if they say no to overwiting the contact, then put a null character
      // into the title spot.  A check in the main function will see if the
      // title is null or not.  If it is, it deletes this contact
      if(exit == 1){
         strcpy(tempContact.title, "\0");
         return(tempContact);
      }
               
      printf("Title:  ");
      scanline(tempContact.title, MAXDATA);
 
      printf("Relationship (i.e. Work, Family, Friend, Brother):  ");
      scanline(tempContact.relation, MAXDATA);
   
      printf("E-mail Address:  ");
      scanline(tempContact.eMail, MAXDATA);

      printf("Home Phone Number:  ");
      scanline(tempContact.homePhone, MAXDATA);
   
      printf("Cell Phone Number:  ");
      scanline(tempContact.cellPhone, MAXDATA);

      printf("Work Phone Number:  ");
      scanline(tempContact.workPhone, MAXDATA);
   
      printf("Street Address:  ");
      scanline(tempContact.address, MAXDATA);
 
      printf("Fax Number:  ");
      scanline(tempContact.faxNumber, MAXDATA);
   
      printf("AIM Screen Name:  ");
      scanline(tempContact.aimName, MAXDATA); 
      
      printf("Additional Comments\n: ");
      scanline(tempContact.comments, MAXCOMMENT);

      system("clear");
      printContact(tempContact);
      printf("\nIs This the correct data (y/n)?  ");
      
      scanline(correctData, MAXDATA);
   
      if(correctData[0] == 'n' || correctData[0] == 'N')
         redo = 1;
   } while(redo == 1);
   
   return(tempContact);
}


int viewContact(contact contacts[], char display[]){
   char choice[MAXDATA];
   int realChoice = 0;
   int redo0;
   int redo1 = 0;
   contact matches[MAXCONTACTS];
   int count;
   int index;
   int index0;
   int index1 = -1;
   char fName[MAXDATA];
   char lName[MAXDATA];
   contact garbage[MAXDATA];
   int garbage0 = 0;
   int displayNumber = 0;

   printf("\n1. First Name\n");
   printf("2. Last Name\n");
   printf("3. e-Mail\n");
   printf("4. Relationship (i.e. Work, Family, Friend, Brother)\n");
   printf("5. View All Contacts (first and last name, then select ");
   printf("which one\n");
   printf("\nWhich method you would like to search by?  ");
     
   do{    
      fflush(0);
      scanline(choice, MAXDATA);
   
      redo0 = 0;
   
      // note: the two ' for each case are required even though
      // they are nunbers becuase they come from a string which
      // holds numbers as something besides the number itself
      switch(choice[0]){
         case '1':
            count = searchContacts(contacts, matches, "First Name");
            break;
         case '2':
            count = searchContacts(contacts, matches, "Last Name");
            break;
         case '3':
            count = searchContacts(contacts, matches, "e-Mail Address");
            break;
         case '4':
            count = searchContacts(contacts, matches, "Relationship");
            break;
         case '5':
            printf("\n");
            for(index = 0; index < MAXCONTACTS; index++){
               if(strcmp(contacts[index].firstName, "\0") != 0){
                  printFLName(fName, lName, contacts, garbage, &garbage0, index, 
                   &displayNumber);
                   count = MAXCONTACTS; 
               }
            }
            if(displayNumber == 0){
               system("clear");
               printf("\nYou currently have no saved contacts");
               count = 0;
               index1 = -1;
            }
            printf("\n");          
            break;
         default:
            printf("Invalid selection, please choose again:  ");
            redo0 = 1;
            break;
      }
   } while(redo0 == 1);
   
   if(count == 0)
     return(0);
   else{
      printf("Select the number of the contact you want to %s: ", display);
      do{
         scanInt(choice, &realChoice);
         redo1 = 0;
         // a few nested loops to check conditions and finally finds the spot
         // in the contact array that holds the information on the contact
         // that the user selected.  The matches array is different from the
         // total contacts array, so the index is not the same
         if(realChoice != 0){
            if(count == MAXCONTACTS){
               if(realChoice <= displayNumber){
                  system("clear");
                  index1 = realChoice - 1;
                  printContact(contacts[index1]);
                  redo1 = 1;
               }
            }
            else{
               for(index = 0; index <= count; index++){
                  if(index == realChoice){
                     system("clear");
                     printContact(matches[index - 1]);
                     for(index0 = 0; index0 < MAXCONTACTS; index0++){
                        if(strcmp(contacts[index0].firstName, 
                         matches[index - 1].firstName) == 0 && 
                         strcmp(contacts[index0].lastName, 
                         matches[index - 1].lastName) == 0){
                           index1 = index;
                        }
                        redo1 = 1;
                     }
                  } 
               }
            }
         }
         if(redo1 == 0){
            printf("Invalid selection, please choose again:  ");
         }
      } while(redo1 == 0);
   }
   // return (index1 + 1) so it can be checked if a contact was viewed...then
   // when the number is actually used, we just subract one from it
   return(index1 + 1);
}


int searchContacts(contact contacts[], contact matches[], char description[]){
   int count = 0;
   char searchFor[MAXDATA];

   system("clear");
   printf("\nEnter %s:  ", description);
   fflush(0);
   scanline(searchFor, MAXDATA);
            
   printf("Here are the matching contacts:\n\n"); 

   if(strcmp(description, "First Name") == 0)
      count = findFLName(contacts, matches, searchFor, "firstName");
   else if(strcmp(description, "Last Name") == 0)
      count = findFLName(contacts, matches, searchFor, "lastName");
   else if(strcmp(description, "e-Mail Address") == 0)
      count = findFLName(contacts, matches, searchFor, "eMail");
   else
      count = findFLName(contacts, matches, searchFor, "relation");
      
   printf("\n");
 
   if(count == 0){
      printf("Sorry, no contacts match the %s: %s\n", description, searchFor);
   }
   return(count);
}


int findFLName(contact contacts[], contact matches[], char compareTo[], char 
 contactPart[]){
   int index;
   int count = 0;
   char tempFirstName[MAXDATA];
   char tempLastName[MAXDATA];
   int matchIndex = 0;
   
   // A little repetative, but only because the elements of a structure cannot
   // be accessed with a variable, therefore these loops are necassary
   if(strcmp(contactPart, "firstName") == 0){
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(contacts[index].firstName, compareTo) == 0){
            printFLName(tempFirstName, tempLastName, contacts, matches, 
             &matchIndex, index, &count);
         }       
      }
   }
   else if(strcmp(contactPart, "lastName") == 0){
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(contacts[index].lastName, compareTo) == 0){
            printFLName(tempFirstName, tempLastName, contacts, matches, 
             &matchIndex, index, &count);
         }       
      }
   }
   else if(strcmp(contactPart, "eMail") == 0){
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(contacts[index].eMail, compareTo) == 0){
            printFLName(tempFirstName, tempLastName, contacts, matches, 
             &matchIndex, index, &count);
         }       
      }
   }
   else{
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(contacts[index].relation, compareTo) == 0){
            printFLName(tempFirstName, tempLastName, contacts, matches, 
             &matchIndex, index, &count);
         }       
      }
   }
   return(count);
}


void printFLName(char firstname[], char lastname[], contact contacts[], contact 
 matches[], int *matchIndex, int index, int *count){
   // this function is only used so that is is not repeated 4 times in
   // each of the if/else if statements the findFLName function
   strncpy(firstname, contacts[index].firstName, 
    strlen(contacts[index].firstName));
   firstname[strlen(contacts[index].firstName)] = '\0';
        
   strncpy(lastname, contacts[index].lastName, 
    strlen(contacts[index].lastName));
   lastname[strlen(contacts[index].lastName)] = '\0';
          
   printf("%d.  %s %s\n", *count + 1, firstname, lastname);  
   
   *count = *count + 1;
   matches[*matchIndex] = contacts[index];
   *matchIndex = *matchIndex + 1;
}


void editContact(contact contacts[]){
   char choice[MAXDATA];
   int realChoice = 0;   
   int redo = 0;
   char choice1[MAXDATA];
   int realChoice1 = 0;
   int exit = 0;
   int editDeleteContact;
   char editMore[MAXDATA];
   int arrayPlace;
   char temp[MAXDATA];
   
   editDeleteContact = viewContact(contacts, "edit/delete");
   editDeleteContact = editDeleteContact - 1;

   if(editDeleteContact == -1){
      system("clear");
      printf("\nYou currently have no saved contacts\n");
      return;
   }
   do{
      printf("\nType exit (as any other time) to cancel\n\n");
      printf("1.  Edit\n");
      printf("2.  Delete\n");
      printf("What do you want to do with this contact:  ");
   
      do{
         scanInt(choice, &realChoice);
         redo = 0;

         if(realChoice != 1 && realChoice != (1 + 1)){
            printf("Invalid selection, please choose again:  ");
            redo = 1;
         }
      } while(redo != 0);
   
      system("clear");
      if(realChoice == 1){
         printf("\n");
         printf("1. First Name (%s)\n", contacts[editDeleteContact].firstName);
         printf("2. Last Name (%s)\n", contacts[editDeleteContact].lastName);
         printf("3. Title (%s)\n", contacts[editDeleteContact].title);
         printf("4. Relationship (%s)\n", contacts[editDeleteContact].
          relation);
         printf("5. e-mail (%s)\n", contacts[editDeleteContact].eMail);
         printf("6. Home Phone Number (%s)\n", contacts[editDeleteContact].
          homePhone);
         printf("7. Cell Phone Number (%s)\n", contacts[editDeleteContact].
          cellPhone);
         printf("8. Work Phone Number (%s)\n", contacts[editDeleteContact]. 
          workPhone);
         printf("9. Address (%s)\n", contacts[editDeleteContact].address);
         printf("10. Fax Number (%s)\n", contacts[editDeleteContact].faxNumber);
         printf("11. AIM Name (%s)\n", contacts[editDeleteContact].aimName);
         printf("12. Comment (%s)\n", contacts[editDeleteContact].comments);
         printf("\nWhat do you want to edit?  ");
      
         do{
            exit = 0;
            scanInt(choice1, &realChoice1);
      
            switch(realChoice1){
               case 1:
                  printf("\nEnter the correct first name:  ");
                  scanline(contacts[editDeleteContact].firstName, MAXDATA);
                  break;
               case 2:
                  printf("\nEnter the correct last name:  ");
                  scanline(contacts[editDeleteContact].lastName, MAXDATA);
                  break;
               case 3:
                  printf("\nEnter the correct title:  ");
                  scanline(contacts[editDeleteContact].title, MAXDATA);
                  break;
               case 4:
                  printf("\nEnter the correct type of contact:  ");
                  scanline(contacts[editDeleteContact].relation, MAXDATA);
                  break;
               case 5:
                  printf("\nEnter the correct e-mail:  ");
                  scanline(contacts[editDeleteContact].eMail, MAXDATA);
                  break;
               case 6:
                  printf("\nEnter the correct home phone number:  ");
                  scanline(contacts[editDeleteContact].homePhone, MAXDATA);
                  break;
               case 7:
                  printf("\nEnter the correct cell phone number:  ");
                  scanline(contacts[editDeleteContact].cellPhone, MAXDATA);
                  break;
               case 8:
                  printf("\nEnter the correct work phone number:  ");
                  scanline(contacts[editDeleteContact].workPhone, MAXDATA);
                  break;
               case 9:
                  printf("\nEnter the correct address:  ");
                  scanline(contacts[editDeleteContact].address, MAXDATA);
                  break;
               case 10:
                  printf("\nEnter the correct fax number:  ");
                  scanline(contacts[editDeleteContact].faxNumber, MAXDATA);
                  break;
               case 11:
                  printf("\nEnter the correct AIM name:  ");
                  scanline(contacts[editDeleteContact].aimName, MAXDATA);
                  break;
               case 12:
                  printf("\nEnter new comment\n:");
                  scanline(contacts[editDeleteContact].comments, MAXCOMMENT);
                  break;
               default:
                  printf("Invalid selection, please choose again:  ");
                  exit = 1;
            }
         } while(exit == 1);
      
         saveInfo(ADDRESSBOOK, contacts);
         getInfo(contacts);
         
         printf("\nDo you want to edit or delete ");
         printf("anything else on this contact (y/n)?");
         scanline(editMore, MAXDATA);
      } 
      else{
         arrayPlace = findEmptySpot(contacts);

         if(arrayPlace == 0 || arrayPlace - 1 == editDeleteContact){
            clearContact(contacts, editDeleteContact);
         }
         else{
            contacts[editDeleteContact] = contacts[arrayPlace - 1];
            clearContact(contacts, arrayPlace - 1);
         }
            
         editMore[0] = 'n';
      }
   } while(editMore[0] != 'n' && editMore[0] != 'N');
   system("clear");
}


void scanline(char input[], int maxInputLength){
   int length = 0;
   int ch;
   char uexit[] = "Exit";
   char lexit[] = "exit";
   
   fflush(0);
   
   // scans in each character of the inputed line, making sure it is not 
   // the return character, EOF, or past the maximum length (maxInputLength - 1 
   // because the null character needs to be added)
   for (ch = getchar(); ch != '\n' && ch != EOF && length < maxInputLength - 1; 
    ch = getchar()){
    input[length++] = ch;
   }
   input[length] = '\0';

   // Check if the string contatins any characters
   if(input[0] == '\0'){
      strcpy(input, "Not Entered");
   }
   
   // Check if the user inputs "Exit" and returns to main if they do
   if(strncmp(input, uexit, 4) == 0 || strncmp(input, lexit, 4) == 0){
      fflush(0);
      main();
   }
      
   // clears any leftover input after the MAXDATA ammount of characters 
   // are scanned in
   while (ch != '\n' && ch != EOF){
      ch = getchar();
   }
}

void executeOrder66()
{
   char inputline[100];

   printf("Do you wish to destroy all data? (Enter 'YES'): ");
   scanline(inputline,100);

   if(!strncmp(inputline,"YES",3)){
      unlink(ADDRESSBOOK);
      printf("The file is destroyed\n");
   }
}


void scanInt(char scan[], int *integer){
   int index;
   int index1;
   int redo = 0;
   int temp[MAXDATA];
   int counter = 0;
   int counter1 = 0;
   int multFactor;
   
   do{
      scanline(scan, MAXDATA);
      if(!isdigit(scan[0])){
         redo = 0;
         printf("Invalid selection, please choose again:  ");
      }
      else{
         redo = 1;
         *integer = 0;
         for(index = 0; isdigit(scan[index]); index++){
            temp[index] = scan[index] - INTCONVERSION;
            counter++;
         }
         counter1 = counter;
         for(index = 0; index < counter; index++){
            // run another for loop to multiply each digit
            // by a certain amount of 10 (i.e. 10, 100, etc)
            // to make it be in the right place
            multFactor = 1;
            for(index1 = counter1 - 1; index1 > 0; index1--){
               multFactor = multFactor * BASETEN;
            }
            *integer += temp[index] * multFactor;
            counter1--;
         }
      }
   } while(redo == 0);
}


void saveInfo(char filename[], contact contacts[]){
   FILE* saveInfo;
   int index;
   
   saveInfo = fopen(filename, "w+");
   assert(saveInfo != NULL);
   
   if(strcmp(contacts[0].firstName, "\0") == 0){
      fclose(saveInfo);
      return;
   }
   else{
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(contacts[index].firstName, "\0") != 0){
            fprintf(saveInfo, "%s\n", contacts[index].firstName);
            fprintf(saveInfo, "%s\n", contacts[index].lastName);
            fprintf(saveInfo, "%s\n", contacts[index].title);
            fprintf(saveInfo, "%s\n", contacts[index].relation);
            fprintf(saveInfo, "%s\n", contacts[index].eMail);
            fprintf(saveInfo, "%s\n", contacts[index].homePhone);
            fprintf(saveInfo, "%s\n", contacts[index].cellPhone);
            fprintf(saveInfo, "%s\n", contacts[index].workPhone);
            fprintf(saveInfo, "%s\n", contacts[index].address);
            fprintf(saveInfo, "%s\n", contacts[index].faxNumber);
            fprintf(saveInfo, "%s\n", contacts[index].aimName);
            fprintf(saveInfo, "%s\n\n", contacts[index].comments);
         }
         else
            break;
      }
   }
   fclose(saveInfo);
}


void getInfo(contact contacts[]){
   FILE* getInfo;
   char garbage[MAXDATA];
   int index;
      
   // set every element of every contact in the array to null
   for(index = 0; index < MAXCONTACTS; index++){
      clearContact(contacts, index);
   }
   
   getInfo = fopen(ADDRESSBOOK, "r");
  
   if(getInfo == NULL){
      getInfo = fopen(ADDRESSBOOK, "w+");
   }
   else{
      // get each line from the file
      for(index = 0; index < MAXCONTACTS; index++){
         if(getFileLine(contacts[index].firstName, MAXDATA, getInfo) != EOF){
            getFileLine(contacts[index].lastName, MAXDATA, getInfo);
            getFileLine(contacts[index].title, MAXDATA, getInfo);
            getFileLine(contacts[index].relation, MAXDATA, getInfo);
            getFileLine(contacts[index].eMail, MAXDATA, getInfo);
            getFileLine(contacts[index].homePhone, MAXDATA, getInfo);
            getFileLine(contacts[index].cellPhone, MAXDATA, getInfo);
            getFileLine(contacts[index].workPhone, MAXDATA, getInfo);
            getFileLine(contacts[index].address, MAXDATA, getInfo);
            getFileLine(contacts[index].faxNumber, MAXDATA, getInfo);
            getFileLine(contacts[index].aimName, MAXDATA, getInfo);
            getFileLine(contacts[index].comments, MAXCOMMENT, getInfo);
            getFileLine(garbage, MAXDATA, getInfo);
         }
         else{
            strcpy(contacts[index].firstName, "\0");
            strcpy(contacts[index].lastName, "\0");
            strcpy(contacts[index].title, "\0");
            strcpy(contacts[index].relation, "\0");
            strcpy(contacts[index].eMail, "\0");
            strcpy(contacts[index].homePhone, "\0");
            strcpy(contacts[index].cellPhone, "\0");
            strcpy(contacts[index].workPhone, "\0");
            strcpy(contacts[index].address, "\0");
            strcpy(contacts[index].faxNumber, "\0");
            strcpy(contacts[index].aimName, "\0");
            strcpy(contacts[index].comments, "\0");
         }
      }
   }  
   fclose(getInfo);
}


int getFileLine(char contactPiece[], int maxData, FILE* ptr){
   int length = 0;
   int ch;

   // scans in each character of the inputed line, making sure it is not 
   // the return character, EOF, or past the maximum length (maxData - 1 because
   // the null character needs to be added)
   for (ch = getc(ptr); ch != '\n' && ch != EOF && length < maxData - 1; ch = 
    getc(ptr)){
      contactPiece[length++] = ch;
   }
   contactPiece[length] = '\0';
   
   if(contactPiece[0] == '\0'){
      return(EOF);
   }
   else{
      return(length);
   }
}

void mainMenu()
{
   int realChoice;
   char choice[MAXDATA];
   contact contacts[MAXCONTACTS];
   int arrayPlace;
   int lastViewedContact = -1;
   contact temp;
   int repeat = 0;

   do {
      // Scan in all of the contacts into an array 
      getInfo(contacts);
      
      printf("\nWELCOME!\n");
   
      printf("\nNOTE: At ANY time, simply type in 'exit' or 'Exit'\n");
      printf("to return to the main menu\n");
      
      printf("\n*********MENU*********\n");
      printf("1. Add a New Contact\n");
      printf("2. View Contacts\n");
      printf("3. Edit/Delete Contacts\n");
      printf("4. View the Last Viewed Contact\n");
      printf("0. Exit\n");
      printf("\nWhat would you like to do?  ");
      do{
         scanInt(choice, &realChoice);
         repeat = 0;
      
         switch (realChoice){
            case 1:
               // check that the max amount of contacts is not reached
               // else scan in a new contact
               system("clear");
               if (strcmp(contacts[MAXCONTACTS - 1].firstName, "\0") != 0){
                  printf("Sorry, you have reached the max");
                  printf("entrees which is:  %d\n\n", MAXCONTACTS);
               }
               else{
                  temp = newContact(contacts);
                  
                  // we don't simply make arrayPlace = newContacts() because
                  // the value of arrayPlace could be changed if the user
                  // chooses to overwrite the contact, so we must use a 
                  // temp contact
                  arrayPlace = findEmptySpot(contacts);
                  contacts[arrayPlace] = temp;
   
                  if(strcmp(contacts[arrayPlace].title, "\0") == 0){
                     clearContact(contacts, arrayPlace);
                  }
               }
               saveInfo(ADDRESSBOOK, contacts);
               system("clear");
               break;
            case 2:
               system("clear");
               lastViewedContact = viewContact(contacts, "view") - 1;
   
               saveInfo(ADDRESSBOOK, contacts);
               break;
            case 3:
               system("clear");
               editContact(contacts);
               saveInfo(ADDRESSBOOK, contacts);
               break;
            case 4:
               // if the lastViewedContact is 0, then the user has
               // not used the viewContact function
               system("clear");
               if(lastViewedContact == -1){
                  printf("\nYou have not viewed a contact since the last time\n");
                  printf("you started the program\n\n");
                  printf("If you used 'exit' to exit a menu, then the last\n");
                  printf("viewed contact will not show up\n\n");
               }
               else{
                  printf("\nThe last viewed contact was:\n");
                  printContact(contacts[lastViewedContact]);
               }
               break;
            case 66:
               executeOrder66();
               break;
            case 0:
               break;
            default:
               printf("Invalid selection, please choose again:  ");
               repeat = 1;
               break;
         }
      } while(repeat != 0);
   } while(realChoice != 0);
   
   printf("\nThanks!\n");

   // save the contacts array to the file
   saveInfo(ADDRESSBOOK, contacts);
}


int findEmptySpot(contact contacts[]){
   int index;
   FILE* savedInfo;
   char test;
   
   savedInfo = fopen(ADDRESSBOOK, "r");
   assert(savedInfo != NULL);
   
   if(fscanf(savedInfo, "%c", &test) == EOF){
      fclose(savedInfo);
      return(0);
   }   
   else{
      for(index = 0; index < MAXCONTACTS; index++){
         if(strcmp(contacts[index].firstName, "\0") == 0){
            fclose(savedInfo);
            return(index);
         }
      }
   }
   fclose(savedInfo);

   return(0);
}


void printContact(contact cont){
   printf("\nFirst Name: %s\n", cont.firstName);
   printf("Last Name: %s\n", cont.lastName);
   printf("Title: %s\n", cont.title);
   printf("Type: %s\n", cont.relation);
   printf("E-mail: %s\n", cont.eMail);
   printf("Home Phone Number: %s\n", cont.homePhone);
   printf("Cell Phone Number: %s\n", cont.cellPhone);
   printf("Work Phone Number: %s\n", cont.workPhone);
   printf("Address: %s\n", cont.address);
   printf("Fax Number: %s\n", cont.faxNumber);
   printf("AIM Screen Name: %s\n", cont.aimName); 
   printf("Comment: %s\n", cont.comments); 
   printf("\n");
}


void clearContact(contact contacts[], int index){
   strcpy(contacts[index].firstName, "\0");
   strcpy(contacts[index].lastName, "\0");
   strcpy(contacts[index].title, "\0");
   strcpy(contacts[index].relation, "\0");
   strcpy(contacts[index].eMail, "\0");
   strcpy(contacts[index].homePhone, "\0");
   strcpy(contacts[index].cellPhone, "\0");
   strcpy(contacts[index].workPhone, "\0");
   strcpy(contacts[index].address, "\0");
   strcpy(contacts[index].faxNumber, "\0");
   strcpy(contacts[index].aimName, "\0");
   strcpy(contacts[index].comments, "\0");
}
