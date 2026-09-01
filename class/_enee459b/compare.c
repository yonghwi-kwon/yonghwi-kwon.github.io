#include <stdio.h>

int main()
{
	int a, b;
	unsigned int c, d;

	a = 5;
	b = 4;
	
	if(a == b){
		printf("This can't be\n");
	}

	if(a < b){
		printf("Something is wrong\n");
	}

	if(b <= a){
		printf("This is okay\n");
	}

	c = 10;
	d = 20;
	if(c < d){
		printf("Something is right\n");
	}

	if(c != d){
		printf("Something is still right\n");
	} 

}

