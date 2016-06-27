/*
 * rrdtool-py3k, rrdtool bindings for Python 3.
 * Based on the rrdtool Python bindings for Python 2 from
 * Hye-Shik Chang <perky@fallin.lv>.
 *
 * Copyright 2012 Christian Jurk <commx@commx.ws>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as 
 * published by the Free Software Foundation; either version 3 of the 
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */

#include <Python.h>
#include <rrd.h>

static const char *_version = "0.1.0";

/* Exception types */
static PyObject *rrdtool_OperationalError;
static PyObject *rrdtool_ProgrammingError;

static char **rrdtool_argv = NULL;
static int rrdtool_argc = 0;

static void
destroy_args(void)
{
    PyMem_Del(rrdtool_argv);
    rrdtool_argv = NULL;
}

/* Helper function to convert Python objects into a representation that the
 * rrdtool functions can work with.
 */
static int
convert_args(char *command, PyObject *args)
{
    PyObject *o, *lo;
    int i, j, args_count, argv_count, element_count;

    args_count = PyTuple_Size(args);
    element_count = 0;
    for (i = 0; i < args_count; i++)
    {
        o = PyTuple_GET_ITEM(args, i);
        if (PyUnicode_Check(o) || PyBytes_Check(o))
            element_count++;
        else if (PyList_CheckExact(o))
            element_count += PyList_Size(o);
        else {
            PyErr_Format(rrdtool_ProgrammingError,
                         "Argument %d must be string, bytes or list of " \
                         "string/bytes", i);
            return -1;
        }
    }

    rrdtool_argv = PyMem_New(char *, element_count + 1);

    if (rrdtool_argv == NULL)
        return -1;

    argv_count = 0;
    for (i = 0; i < args_count; i++) {
        o = PyTuple_GET_ITEM(args, i);

        if (PyUnicode_Check(o))
            rrdtool_argv[++argv_count] = PyBytes_AsString(
              PyUnicode_AsUTF8String(o));
        else if (PyBytes_Check(o))
            rrdtool_argv[++argv_count] = PyBytes_AS_STRING(o);
        else if (PyList_CheckExact(o)) {
            for (j = 0; j < PyList_Size(o); j++) {
                lo = PyList_GetItem(o, j);
                if (PyUnicode_Check(lo))
                    rrdtool_argv[++argv_count] = PyBytes_AS_STRING(
                      PyUnicode_AsUTF8String(lo));
                else if (PyBytes_Check(lo))
                    rrdtool_argv[++argv_count] = PyBytes_AS_STRING(lo);
                else {
                    PyMem_Del(rrdtool_argv);
                    PyErr_Format(rrdtool_ProgrammingError,
                      "Element %d in argument %d must be string", j, i);
                    return -1;
                }
            }
        } else {
            PyMem_Del(rrdtool_argv);
            PyErr_Format(rrdtool_ProgrammingError,
              "Argument %d must be string or list of strings", i);
            return -1;
        }
    }

    rrdtool_argv[0] = command;
    rrdtool_argc = element_count + 1;

    return 0;
}

static PyObject *
_rrdtool_util_info2dict(const rrd_info_t *data)
{
    PyObject *dict, *val;

    dict = PyDict_New();

    while (data) {
        val = NULL;

        switch (data->type) {
            case RD_I_VAL:
                if (isnan(data->value.u_val)) {
                    Py_INCREF(Py_None);
                    val = Py_None;
                } else
                    PyFloat_FromDouble(data->value.u_val);
                break;

            case RD_I_CNT:
                val = PyLong_FromUnsignedLong(data->value.u_cnt);
                break;

            case RD_I_INT:
                val = PyLong_FromLong(data->value.u_int);
                break;

            case RD_I_STR:
                val = PyUnicode_FromString(data->value.u_str);
                break;

            case RD_I_BLO:
                val = PyUnicode_FromStringAndSize(
                  (char *)data->value.u_blo.ptr, data->value.u_blo.size);
                break;
            default:
                break;
        }

        if (val != NULL) {
            PyDict_SetItemString(dict, data->key, val);
            Py_DECREF(val);
        }

        data = data->next;
    }

    return dict;
}

static char _rrdtool_create__doc__[] = "Create a new Round Robin Database.\n\n\
  Usage: create(args...)\n\
  Arguments:\n\n\
    filename\n\
    [--start|-b start time]\n\
    [--step|-s step]\n\
    [DS:ds-name:DST:heartbeat:min:max]\n\
    [RRA:CF:xff:steps:rows]\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdcreate.en.html";

static PyObject *
_rrdtool_create(PyObject *self, PyObject *args)
{
    PyObject *ret;

    if (convert_args("create", args) == -1)
        return NULL;

	if (rrd_create(rrdtool_argc, rrdtool_argv) == -1) {
		PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
		rrd_clear_error();
		ret = NULL;
	} else {
        Py_INCREF(Py_None);
        ret = Py_None;
    }

	destroy_args();
    return ret;
}

static char _rrdtool_update__doc__[] = "Store a new set of values into\
 the RRD.\n\n\
 Usage: update(args..)\n\
 Arguments:\n\n\
   filename\n\
   [--template|-t ds-name[:ds-name]...]\n\
   N|timestamp:value[:value...]\n\
   [timestamp:value[:value...] ...]\n\n\
   Full documentation can be found at:\n\
   http://oss.oetiker.ch/rrdtool/doc/rrdupdate.en.html";

static PyObject *
_rrdtool_update(PyObject *self, PyObject *args)
{
    PyObject *ret;

    if (convert_args("update", args) == -1)
        return NULL;

    if (rrd_update(rrdtool_argc, rrdtool_argv) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        Py_INCREF(Py_None);
        ret = Py_None;
    }

	destroy_args();
    return ret;
}

static char _rrdtool_updatev__doc__[] = "Store a new set of values into "\
  "the Round Robin Database and return an info dictionary.\n\n\
  This function works in the same manner as 'update', but will return an\n\
  info dictionary instead of None.";

static PyObject *
_rrdtool_updatev(PyObject *self, PyObject *args)
{
    PyObject *ret;
    rrd_info_t *data;

    if (convert_args("updatev", args) == -1)
        return NULL;

    if ((data = rrd_update_v(rrdtool_argc, rrdtool_argv)) == NULL) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        ret = _rrdtool_util_info2dict(data);
        rrd_info_free(data);
    }

	destroy_args();
    return ret;
}

static char _rrdtool_xport__doc__[] =
    "xport(args..): dictionary representation of data stored in RRDs\n"
    "    [-s|--start seconds] [-e|--end seconds] [-m|--maxrows rows]"
    "[--step value] [--daemon address] [DEF:vname=rrd:ds-name:CF]"
    "[CDEF:vname=rpn-expression] [XPORT:vname[:legend]]";

static PyObject *
_rrdtool_xport(PyObject *self, PyObject *args)
{
    PyObject *r;
    int       argc, xsize;
    char    **argv, **legend_v;
    time_t    start, end;
    unsigned long step, col_cnt;
    rrd_value_t *data, *datai;

    if (convert_args("xport", args) == -1)
        return NULL;

    if (rrd_xport(rrdtool_argc, rrdtool_argv, &xsize, &start, &end,
                  &step, &col_cnt, &legend_v, &data) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        r = NULL;
    } else {
        PyObject *meta_dict, *data_list, *legend_list, *t;
        unsigned long i, j;
        rrd_value_t dv;

        unsigned long row_cnt = ((end - start) / step);

        r = PyDict_New();
        meta_dict = PyDict_New();
        legend_list = PyList_New(col_cnt);
        data_list = PyList_New(row_cnt);
        PyDict_SetItem(r, PyUnicode_FromString("meta"), meta_dict);
        PyDict_SetItem(r, PyUnicode_FromString("data"), data_list);

        datai = data;

        PyDict_SetItem(meta_dict, PyUnicode_FromString("start"), PyLong_FromLong((long) start));
        PyDict_SetItem(meta_dict, PyUnicode_FromString("end"), PyLong_FromLong((long) end));
        PyDict_SetItem(meta_dict, PyUnicode_FromString("step"), PyLong_FromLong((long) step));
        PyDict_SetItem(meta_dict, PyUnicode_FromString("rows"), PyLong_FromLong((long) row_cnt));
        PyDict_SetItem(meta_dict, PyUnicode_FromString("columns"), PyLong_FromLong((long) col_cnt));
        PyDict_SetItem(meta_dict, PyUnicode_FromString("legend"), legend_list);

        for (i = 0; i < col_cnt; i++) {
            PyList_SET_ITEM(legend_list, i, PyUnicode_FromString(legend_v[i]));
        }

        for (i = 0; i < row_cnt; i++) {
            t = PyTuple_New(col_cnt);
            PyList_SET_ITEM(data_list, i, t);

            for (j = 0; j < col_cnt; j++) {
                dv = *(datai++);
                if (isnan(dv)) {
                    PyTuple_SET_ITEM(t, j, Py_None);
                    Py_INCREF(Py_None);
                } else {
                    PyTuple_SET_ITEM(t, j, PyFloat_FromDouble((double) dv));
                }
            }
        }

        for (i = 0; i < col_cnt; i++) {
            rrd_freemem(legend_v[i]);
        }
        rrd_freemem(legend_v);
        rrd_freemem(data);
    }
    destroy_args();
    return r;
}

static char _rrdtool_fetch__doc__[] = "Fetch data from an RRD.\n\n\
  Usage: fetch(args..)\n\
  Arguments:\n\n\
    filename\n\
    CF\n\
    [--resolution|-r resolution]\n\
    [--start|-s start]\n\
    [--end|-e end]\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdfetch.en.html";

static PyObject *
_rrdtool_fetch(PyObject *self, PyObject *args)
{
    PyObject *ret, *range_tup, *dsnam_tup, *data_list, *t;
    rrd_value_t *data, *datai, dv;
    unsigned long step, ds_cnt, i, j, row;
    time_t start, end;
    char **ds_namv;

    if (convert_args("fetch", args) == -1)
        return NULL;

    if (rrd_fetch(rrdtool_argc, rrdtool_argv, &start, &end, &step, &ds_cnt,
                  &ds_namv, &data) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        row = (end - start) / step;
        ret = PyTuple_New(3);
        range_tup = PyTuple_New(3);
        dsnam_tup = PyTuple_New(ds_cnt);
        data_list = PyList_New(row);

        PyTuple_SET_ITEM(ret, 0, range_tup);
        PyTuple_SET_ITEM(ret, 1, dsnam_tup);
        PyTuple_SET_ITEM(ret, 2, data_list);

        datai = data;

        PyTuple_SET_ITEM(range_tup, 0, PyLong_FromLong((long)start));
        PyTuple_SET_ITEM(range_tup, 1, PyLong_FromLong((long)end));
        PyTuple_SET_ITEM(range_tup, 2, PyLong_FromLong((long)step));

        for (i = 0; i < ds_cnt; i++)
            PyTuple_SET_ITEM(dsnam_tup, i, PyUnicode_FromString(ds_namv[i]));

        for (i = 0; i < row; i++) {
            t = PyTuple_New(ds_cnt);
            PyList_SET_ITEM(data_list, i, t);

            for (j = 0; j < ds_cnt; j++) {
                dv = *(datai++);
                if (isnan(dv)) {
                    PyTuple_SET_ITEM(t, j, Py_None);
                    Py_INCREF(Py_None);
                } else
                    PyTuple_SET_ITEM(t, j, PyFloat_FromDouble((double)dv));
            }
        }

        for (i = 0; i < ds_cnt; i++)
            rrd_freemem(ds_namv[i]);

        rrd_freemem(ds_namv);
        rrd_freemem(data);
    }

    destroy_args();
    return ret;
}

static char _rrdtool_flushcached__doc__[] = "Flush RRD files from memory.\n\n\
  Usage: flushcached(args..)\n\
  Arguments:\n\n\
    [--daemon address]\n\
    filename\n\
    [filename ...]\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdflushcached.en.html";

static PyObject *
_rrdtool_flushcached(PyObject *self, PyObject *args)
{
    PyObject *ret;

    if (convert_args("flushcached", args) == -1)
        return NULL;

    if (rrd_flushcached(rrdtool_argc, rrdtool_argv) != 0) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        Py_INCREF(Py_None);
        ret = Py_None;
    }

	destroy_args();
    return ret;
}

static char _rrdtool_graph__doc__[] = "Create a graph based on one or more " \
  "RRDs.\n\n\
  Usage: graph(args..)\n\
  Arguments:\n\n\
    filename | -\n\
    [-s|--start start]\n\
    [-e|--end end]\n\
    [-S|--step step]\n\
    [-t|--title string]\n\
    [-v|--vertical-label string]\n\
    [-w|--width pixels]\n\
    [-h|--height pixels]\n\
    [-j|--only-graph]\n\
    [-D|--full-size-mode]\n\
    [-u|--upper-limit value]\n\
    [-l|--lower-limit value]\n\
    [-r|--rigid]\n\
    [-A|--alt-autoscale]\n\
    [-J|--alt-autoscale-min]\n\
    [-M|--alt-autoscale-max]\n\
    [-N|--no-gridfit]\n\
    [-x|--x-grid (GTM:GST:MTM:MST:LTM:LST:LPR:LFM|none)]\n\
    [-y|--y-grid (grid step:label factor|none)]\n\
    [-Y|--alt-y-grid]\n\
    [-o|--logarithmic]\n\
    [-X|--units-exponent value]\n\
    [-L|--units-length value]\n\
    [--units=si]\n\
    [--right-axis scale:shift]\n\
    [--right-axis-label label]\n\
    [--right-axis-format format-string]\n\
    [-g|--no-legend]\n\
    [-F|--force-rules-legend]\n\
    [--legend-position=(north|south|west|east)]\n\
    [--legend-direction=(topdown|bottomup)]\n\
    [-z|--lazy]\n\
    [--daemon address]\n\
    [-f|--imginfo printfstr]\n\
    [-c|--color COLORTAG#rrggbb[aa]]\n\
    [--grid-dash on:off]\n\
    [--border width]\n\
    [--dynamic-labels]\n\
    [-m|--zoom factor]\n\
    [-n|--font FONTTAG:size:[font]]\n\
    [-R|--font-render-mode {normal,light,mono}]\n\
    [-B|--font-smoothing-threshold size]\n\
    [-P|--pango-markup]\n\
    [-G|--graph-render-mode {normal,mono}]\n\
    [-E|--slope-mode]\n\
    [-a|--imgformat {PNG,SVG,EPS,PDF}]\n\
    [-T|--tabwidth value]\n\
    [-b|--base value]\n\
    [-W|--watermark string]\n\
    DEF:vname=rrdfile:ds-name:CF[:step=step][:start=time][:end=time]\n\
    CDEF:vname=RPN expression\n\
    VDEF=vname:RPN expression\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html";

static PyObject *
_rrdtool_graph(PyObject *self, PyObject *args, PyObject *kwargs)
{
    PyObject *ret;
    int xsize, ysize, i;
    int keep_in_mem = 0;
    double ymin, ymax;
    char **calcpr, *bp;
#ifdef _POSIX_C_SOURCE
    FILE *orig_stdout = stdout;
    size_t bsize;
#endif

    if (convert_args("graph", args) == -1)
        return NULL;

    if (rrdtool_argc >= 2 && strcmp(rrdtool_argv[1], "-") == 0) {
#ifdef _POSIX_C_SOURCE
        keep_in_mem = 1;
#else
        PyErr_SetString(rrdtool_ProgrammingError,
          "Output filename cannot be '-', because this platform does not "\
          "support output buffering");
        destroy_args();
        return NULL;
#endif
    }

#ifdef _POSIX_C_SOURCE
    if (keep_in_mem)
        stdout = open_memstream(&bp, &bsize);
#endif

    if (rrd_graph(rrdtool_argc, rrdtool_argv, &calcpr, &xsize, &ysize, NULL,
                  &ymin, &ymax) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        ret = PyTuple_New(keep_in_mem ? 4 : 3);

        PyTuple_SET_ITEM(ret, 0, PyLong_FromLong((long)xsize));
        PyTuple_SET_ITEM(ret, 1, PyLong_FromLong((long)ysize));

        if (calcpr) {
            PyObject *e, *t;

            e = PyList_New(0);
            PyTuple_SET_ITEM(ret, 2, e);

            for (i = 0; calcpr[i]; i++) {
                t = PyUnicode_FromString(calcpr[i]);
                PyList_Append(e, t);
                Py_DECREF(t);
                rrd_freemem(calcpr[i]);
            }
        } else {
            Py_INCREF(Py_None);
            PyTuple_SET_ITEM(ret, 2, Py_None);
        }

        /* feed buffered contents into a PyBytes object */
        if (keep_in_mem) {
            PyObject *pb;

            fflush(stdout);
            pb = PyBytes_FromStringAndSize(bp, bsize);

            PyTuple_SET_ITEM(ret, 3, pb);
        }
    }

    if (keep_in_mem) {
        fclose(stdout);
        stdout = orig_stdout;
    }

    destroy_args();
    return ret;
}

static char _rrdtool_graphv__doc__[] = "Create a graph based on one or more "\
  "RRDs and return header information.\n\n\
  This function works in the same manner as 'graph', but will return a info\n\
  dictionary instead of None.";

static PyObject *
_rrdtool_graphv(PyObject *self, PyObject *args)
{
    PyObject *ret;
    rrd_info_t *data;

    if (convert_args("graphv", args) == -1)
        return NULL;

    if ((data = rrd_graph_v(rrdtool_argc, rrdtool_argv)) == NULL) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        ret = _rrdtool_util_info2dict(data);
        rrd_info_free(data);
    }

    destroy_args();
    return ret;
}

static char _rrdtool_tune__doc__[] = "Modify some basic properties of a " \
  "Round Robin Database.\n\n\
  Usage: tune(args..)\n\
  Arguments:\n\n\
    filename\n\
    [-h|--heartbeat ds-name:heartbeat]\n\
    [-i|--minimum ds-name:min]\n\
    [-a|--maximum ds-name:max]\n\
    [-d|--data-source-type ds-name:DST]\n\
    [-r|--data-source-rename old-name:new-name]\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdtune.en.html";

static PyObject *
_rrdtool_tune(PyObject *self, PyObject *args)
{
    PyObject *ret;

    if (convert_args("tune", args) == -1)
        return NULL;

    if (rrd_tune(rrdtool_argc, rrdtool_argv) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        Py_INCREF(Py_None);
        ret = Py_None;
    }

    destroy_args();
    return ret;
}

static char _rrdtool_first__doc__[] = "Get the first UNIX timestamp of the "\
  "first data sample in an Round Robin Database.\n\n\
  Usage: first(args..)\n\
  Arguments:\n\n\
    filename\n\
    [--rraindex number]\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdfirst.en.html";

static PyObject *
_rrdtool_first(PyObject *self, PyObject *args)
{
    PyObject *ret;
    int ts;

    if (convert_args("first", args) == -1)
        return NULL;

    if ((ts = rrd_first(rrdtool_argc, rrdtool_argv)) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else
        ret = PyLong_FromLong((long)ts);

    destroy_args();
    return ret;
}

static char _rrdtool_last__doc__[] = "Get the UNIX timestamp of the most "\
  "recent data sample in an Round Robin Database.\n\n\
  Usage: last(args..)\n\
  Arguments:\n\n\
    filename\n\
    [--daemon address]\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdlast.en.html";

static PyObject *
_rrdtool_last(PyObject *self, PyObject *args)
{
    PyObject *ret;
    int ts;

    if (convert_args("last", args) == -1)
        return NULL;

    if ((ts = rrd_last(rrdtool_argc, rrdtool_argv)) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else
        ret = PyLong_FromLong((long)ts);

    destroy_args();
    return ret;
}

static char _rrdtool_resize__doc__[] = "Modify the number of rows in a "\
 "Round Robin Database.\n\n\
  Usage: resize(args..)\n\
  Arguments:\n\n\
    filename\n\
    rra-num\n\
    GROW|SHRINK\n\
    rows\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdlast.en.html";

static PyObject *
_rrdtool_resize(PyObject *self, PyObject *args)
{
    PyObject *ret;
    int ts;

    if (convert_args("resize", args) == -1)
        return NULL;

    if ((ts = rrd_resize(rrdtool_argc, rrdtool_argv)) == -1) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        Py_INCREF(Py_None);
        ret = Py_None;
    }

    destroy_args();
    return ret;
}

static char _rrdtool_info__doc__[] = "Extract header information from an "\
 "Round Robin Database.\n\n\
  Usage: info(filename)\n\
  Arguments:\n\n\
    filename\n\n\
    Full documentation can be found at:\n\
    http://oss.oetiker.ch/rrdtool/doc/rrdinfo.en.html";

static PyObject *
_rrdtool_info(PyObject *self, PyObject *args)
{
    PyObject *ret;
    rrd_info_t *data;

    if (convert_args("info", args) == -1)
        return NULL;

    if ((data = rrd_info(rrdtool_argc, rrdtool_argv)) == NULL) {
        PyErr_SetString(rrdtool_OperationalError, rrd_get_error());
        rrd_clear_error();
        ret = NULL;
    } else {
        ret = _rrdtool_util_info2dict(data);
        rrd_info_free(data);
    }

    destroy_args();
    return ret;
}

static char _rrdtool_lib_version__doc__[] = "Get the version this binding "\
  "was compiled against.";

static PyObject *
_rrdtool_lib_version(PyObject *self, PyObject *args)
{
    return PyUnicode_FromString(rrd_strversion());
}

static PyMethodDef rrdtool_methods[] = {
	{"create", (PyCFunction)_rrdtool_create,
     METH_VARARGS, _rrdtool_create__doc__},
    {"update", (PyCFunction)_rrdtool_update,
     METH_VARARGS, _rrdtool_update__doc__},
    {"updatev", (PyCFunction)_rrdtool_updatev,
     METH_VARARGS, _rrdtool_updatev__doc__},
    {"fetch", (PyCFunction)_rrdtool_fetch,
     METH_VARARGS, _rrdtool_fetch__doc__},
    {"xport", (PyCFunction)_rrdtool_xport,
     METH_VARARGS, _rrdtool_xport__doc__},
    {"flushcached", (PyCFunction)_rrdtool_flushcached,
     METH_VARARGS, _rrdtool_flushcached__doc__},
    {"graph", (PyCFunction)_rrdtool_graph,
     METH_VARARGS, _rrdtool_graph__doc__},
    {"graphv", (PyCFunction)_rrdtool_graphv,
     METH_VARARGS, _rrdtool_graphv__doc__},
    {"tune", (PyCFunction)_rrdtool_tune,
     METH_VARARGS, _rrdtool_tune__doc__},
    {"first", (PyCFunction)_rrdtool_first,
     METH_VARARGS, _rrdtool_first__doc__},
    {"last", (PyCFunction)_rrdtool_last,
     METH_VARARGS, _rrdtool_last__doc__},
    {"resize", (PyCFunction)_rrdtool_resize,
     METH_VARARGS, _rrdtool_resize__doc__},
    {"info", (PyCFunction)_rrdtool_info,
     METH_VARARGS, _rrdtool_info__doc__},
    {"lib_version", (PyCFunction)_rrdtool_lib_version,
     METH_VARARGS, _rrdtool_lib_version__doc__},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef rrdtoolmodule = {
	PyModuleDef_HEAD_INIT,
	"rrdtool",
	"rrdtool bindings for Python 3",
	-1,
	rrdtool_methods
};

PyMODINIT_FUNC
PyInit_rrdtool(void)
{
	PyObject *m;

	m = PyModule_Create(&rrdtoolmodule);
	if (m == NULL)
		return NULL;

	rrdtool_ProgrammingError = PyErr_NewException("rrdtool.ProgrammingError",
	                                              NULL, NULL);
	Py_INCREF(rrdtool_ProgrammingError);
	PyModule_AddObject(m, "ProgrammingError", rrdtool_ProgrammingError);

	rrdtool_OperationalError = PyErr_NewException("rrdtool.OperationalError",
	                                              NULL, NULL);
	Py_INCREF(rrdtool_OperationalError);
	PyModule_AddObject(m, "OperationalError", rrdtool_OperationalError);
    PyModule_AddObject(m, "__version__", PyUnicode_FromString(_version));

	return m;
}
