#include<stdio.h>

typedef struct{
	int a, b, c;
}myStruct;


void addVals(myStruct *s)
{
	s->c = s->a + s->b;
}

int main()
{
	myStruct v;

	v.a = 100;
	v.b = 200;

	addVals(&v);

	printf("Result = %d\n",v.c);
}

