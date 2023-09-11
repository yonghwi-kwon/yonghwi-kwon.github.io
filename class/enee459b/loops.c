#include <stdio.h>

int main()
{
	int i, b;

	for(i = 0; i < 10; ++i){
		printf("i = %d\n",i);
	}

	i = 0;

	while( i < 10 ){
		printf("i = %d\n",i);
		++i;
	}

	b = 0;
	i = 0;
	while(!b){
		printf("i = %d\n",i);
		++i;
		if(i >= 10){
			b = 1;
		}
	}
}

