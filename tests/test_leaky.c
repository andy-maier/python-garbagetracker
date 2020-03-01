// Python extension module in C

#include <Python.h>

// ----------------------------------------------------------------------------
// Python function inccref(obj):
//
// Increase the reference count of the specified Python object by one.
//
// Parameters:
//   obj (object): Python object.
//

static char incref_docs[] =
  "incref(obj): Increase the reference count of the specified Python object "
  "by one.";

static PyObject* incref_func(PyObject* self, PyObject *args, PyObject *kw)
{
  PyObject *obj;
  char *kw_names[] = {"obj", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kw_names, &obj))
  {
    return NULL;
  }

  Py_INCREF(obj);

  Py_RETURN_NONE;
}

// ----------------------------------------------------------------------------
// Python function decref(obj):
//
// Decrease the reference count of the specified Python object by one.
//
// Parameters:
//   obj (object): Python object.
//

static char decref_docs[] =
  "decref(obj): Decrease the reference count of the specified Python object "
  "by one.";

static PyObject* decref_func(PyObject* self, PyObject *args, PyObject *kw)
{
  PyObject *obj;
  char *kw_names[] = {"obj", NULL};

  if (!PyArg_ParseTupleAndKeywords(args, kw, "O", kw_names, &obj))
  {
    return NULL;
  }

  Py_DECREF(obj);

  Py_RETURN_NONE;
}

// ----------------------------------------------------------------------------
// Module definition
//

static char module_name[] = "test_leaky";

static char module_docs[] =
  "A Python extension module in C that can produce memory leaks for test "
  "purposes";

static PyMethodDef module_funcs[] =
{
  {"incref", (PyCFunction)incref_func, METH_VARARGS | METH_KEYWORDS, incref_docs},
  {"decref", (PyCFunction)decref_func, METH_VARARGS | METH_KEYWORDS, decref_docs},
  {NULL}
};

#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef module_def =
{
    PyModuleDef_HEAD_INIT,
    module_name,
    module_docs,
    -1,   /* size of per-interpreter state of the module,
             or -1 if the module keeps state in global variables. */
    module_funcs,
};

PyMODINIT_FUNC PyInit_test_leaky(void)  // must be named PyInit_{module_name}
{
    return PyModule_Create(&module_def);
}

#else  // PY_MAJOR_VERSION < 3

void inittest_leaky(void)  // must be named init{module_name}
{
  Py_InitModule3(
    module_name,
    module_funcs,
    module_docs
  );
}

#endif
