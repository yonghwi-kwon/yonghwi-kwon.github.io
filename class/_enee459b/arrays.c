#include <stdio.h>

int main()
{
	int a[5] = {0, 1, 2, 3, 4};
	unsigned char b[5] = {0, 1, 2, 3, 4};
	int i;
	int total_a = 0;
	unsigned char total_b = 0;

	for(i = 0; i < 5; ++i){
		total_a = total_a + a[i];
		total_b = total_b + b[i];
	}

	printf("Total a = %d, total b = %d\n",total_a,total_b);
}

