//#include <windows.h>

extern "C"
{
	int _fltused;
}

char** global_char_ptr_ptr;
char** static_global_char_ptr_ptr;
namespace {
	char** namespaced_global_char_ptr_ptr;
}
__declspec(dllexport) char** export_global_char_ptr_ptr;


struct Yolo
{
	int x;
	float y;
	double* z;
};


int __stdcall WinMainCRTStartup()
{
	Yolo y = {1, 2, nullptr};
	global_char_ptr_ptr = (char**)1;
	static_global_char_ptr_ptr = (char**)2;
	namespaced_global_char_ptr_ptr = (char**)3;
	export_global_char_ptr_ptr = (char**)4;

    return y.x * y.y;
}

