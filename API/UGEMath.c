#include <Python.h>

/*
 * Function to be called from Python
 */
 
const float infinity =  *(float *) &hex_7F800000;
const float min_float = *(float *) &hex_00800000;

static PyObject* InverseSqrt(PyObject* self, PyObject* args) {
	const float x;
	PyArg_ParseTuple(args, "f", &x);
	
	if (x < min_float)
	{
		return (infinity);
	}

	float r = __frsqrte(x);
	r = 0.5F * r * (3.0F - x * r * r);
	r = 0.5F * r * (3.0F - x * r * r);
	
	return Py_BuildValue("f", r); }

// Tcll - this may not be as fast as CPU-based sincos, but it's still faster than doing this with python alone.
static PyObject* SinCos(PyObject* self, PyObject* args) {
	const float x;
	PyArg_ParseTuple(args, "f", &x);

	PyObject *t = PyTuple_New(2);
	PyTuple_SetItem(t, 0, Py_BuildValue("f", __fsin(x)));
	PyTuple_SetItem(t, 1, Py_BuildValue("f", __fcos(x)));
	
	return t; }

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef module_methods[] = {
    {"isqrt", InverseSqrt, METH_VARARGS},
    {"sincos", SinCos, METH_VARARGS},
    {NULL, NULL}
};

/*
 * Python calls this to let us initialize our module
 */
void initcmathext()
{
    (void) Py_InitModule("UGEMath", module_methods);
};