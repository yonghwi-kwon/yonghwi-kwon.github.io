#include <stdio.h>

main(int argc, char *argv[])
{
	int a;

	a = atoi(argv[1]);

	switch(a){
		case 0:
			printf("Nothin....");
			break;
		case 1:
			printf("Solo....\n");
			break;
		case 2:
			printf("For tea?\n");
			break;
		case 3:
			printf("Not today, thanks\n");
			break;
		case 5:
			printf("Is alive\n");
			break;
		case 433:
			printf("What?\n");
			break;
		case 2001:
			printf("A space oddessy\n");
			break;
		default:
			printf("This is the default\n");
			break;
	}
}

