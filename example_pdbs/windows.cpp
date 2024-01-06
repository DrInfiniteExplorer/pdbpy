//#include <windows.h>

extern "C"
{
	int _fltused;
}

struct Yolo
{
	int x;
	float y;
	double* z;
};


int __stdcall WinMainCRTStartup()
{
	Yolo y = {1, 2, nullptr};
    return y.x * y.y;
}

