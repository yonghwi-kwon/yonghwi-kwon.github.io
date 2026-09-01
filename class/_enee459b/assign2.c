#include <stdio.h>
#include <stdlib.h>


int main(int argc, char *argv[])
{
	unsigned short int a, b, c, d;
	unsigned long int z;

	z = strtol(argv[1],NULL,16);

	*((unsigned long int *)(&a)) = z;	

	printf("a = %X, b = %X, c = %X, d = %X\n",a,b,c,d);	
}

