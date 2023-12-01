#include <windows.h>

struct Yolo
{
	int x;
	float y;
	double* z;
};

int main(int argc, char* argv[])
{
	Yolo y = {1, 2, nullptr};
	return y.x * y.y;
}

