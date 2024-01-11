#include <windows.h>
#include <stdio.h>

int global_variable = 0;

int main(int argc, char* argv[])
{
	global_variable = 2;
	char* p1 = (char*)(&global_variable);
	char* p2 = (char*)GetModuleHandle(0);
	printf("%p\n", p1 - p2);
	
	return global_variable;
}

