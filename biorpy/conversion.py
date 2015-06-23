from collections import OrderedDict
import pandas
import numpy
from rpy2.robjects import numpy2ri
from rpy2 import robjects, rinterface

## CONVERSION

def asstr(x):
    return robjects.StrVector(x)
    
def asint(x):
    return robjects.IntVector(x)

def asfloat(x):
    return robjects.FloatVector(x)

# this might be best put in a separate module
def convertToR(obj):
    """
    Convert Pandas/Numpy objects to R objects.

    If the inumpyut object is a Pandas DataFrame, convert it to
    an R DataFrame.  If it's a Series, treat it like a vector/numpy
    array. 
    """
    if isinstance(obj, pandas.core.frame.DataFrame):
        return pandasDataFrameToRPy2DataFrame(obj)
    elif isinstance(obj, pandas.Series) or isinstance(obj, pandas.core.index.NumericIndex):
        return convertToR(list(obj))
    elif isinstance(obj, numpy.ndarray):
        return numpy2ri.numpy2ri(obj)
    elif isinstance(obj, list) or isinstance(obj, tuple):
        if len(obj) == 0:
            return robjects.FloatVector([])
        else:
            try:
                return robjects.FloatVector(obj)
            except ValueError:
                pass
            try:
                return robjects.StrVector(obj)
            except ValueError:
                pass
    elif isinstance(obj, dict):
        lengths = set()
        asrpy2 = OrderedDict()

        for key in obj:
            asrpy2[key] = convertToR(obj[key])
            try:
                lengths.add(len(asrpy2[key]))
            except:
                lengths.add(1)

        if len(lengths) == 1:
            return robjects.DataFrame(asrpy2)
        else:
            return robjects.ListVector(asrpy2)

    return obj

class ResultWrapper(object):
    """ Represents output from R as a dictionary-like object, with conversion of each value
    to a pandas DataFrame or a numpy.array if possible 

    Attributes that contain a period in R can usually be accessed directly from python by omitting the period 
    (eg, 'p.value' can be accessed from 'pvalue') """
    def __init__(self, result):
        self._result = result

    def __repr__(self):
        return str(dict(self.iteritems()))
    def __str__(self):
        return str(self._result)

    def keys(self):
        return list(self._result.names)
        
    def iteritems(self):
        for key in self._result.names:
            yield (key, self[key])

    def __getitem__(self, attr):
        return self.__getattribute__(attr)

    def __getattribute__(self, attr):
        try:
            return super(ResultWrapper, self).__getattribute__(attr)
        except AttributeError as ae:
            orig_ae = ae

        if attr in self._result.names:
            toconvert = self._result.rx2(attr)
            return convertFromR(toconvert)
        else:
            try:
                # see if we can find the attribute if we remove periods
                undotted_names = dict((name.replace(".", ""), name) for name in self._result.names)
                undotted_name = undotted_names[attr]
                return convertFromR(self._result.rx2(undotted_name))
            except AttributeError:
                pass
        raise orig_ae

def addResultWrapper(result):
    if isinstance(result, rinterface.RNULLType):
        # could convert this to numpy.nan
        return
    if isinstance(result, numpy.ndarray):
        return

    try:
        if isinstance(result, robjects.vectors.DataFrame):
            result.py = rpy2DataFrameToPandasDataFrame(result)
        else:
            result.py = ResultWrapper(result)
    except:
        result.py = None
        
def convertFromR(obj):
    if isinstance(obj, robjects.vectors.DataFrame):
        return rpy2DataFrameToPandasDataFrame(obj)
    elif isinstance(obj, robjects.vectors.Vector):
        return numpy.array(obj)
    else:
        return obj


VECTOR_TYPES = {numpy.float64: robjects.FloatVector,
                numpy.float32: robjects.FloatVector,
                numpy.float: robjects.FloatVector,
                numpy.int: robjects.IntVector,
                numpy.int32: robjects.IntVector,
                numpy.int64: robjects.IntVector,
                numpy.object_: robjects.StrVector,
                numpy.str: robjects.StrVector,
                numpy.bool: robjects.BoolVector}

NA_TYPES = {numpy.float64: robjects.NA_Real,
            numpy.float32: robjects.NA_Real,
            numpy.float: robjects.NA_Real,
            numpy.int: robjects.NA_Integer,
            numpy.int32: robjects.NA_Integer,
            numpy.int64: robjects.NA_Integer,
            numpy.object_: robjects.NA_Character,
            numpy.str: robjects.NA_Character,
            numpy.bool: robjects.NA_Logical}

import rpy2.rlike.container as rlc

def rpy2DataFrameToPandasDataFrame(rdf):
    recarray = numpy.transpose(numpy.asarray(rdf))
    df = pandas.DataFrame.from_records(recarray, index=list(rdf.rownames), columns=list(rdf.colnames))
    return df

def pandasDataFrameToRPy2DataFrame(df, strings_as_factors=False):
    """
    Convert a pandas DataFrame to a R data.frame.


    Args:        
        df: The DataFrame being converted
        strings_as_factors: Whether to turn strings into R factors (default: False)

    Returns:
        An R data.frame

    """

    columns = rlc.OrdDict()

    # FIXME: This doesn't handle MultiIndex

    for column in df:
        value = df[column]
        value_type = value.dtype.type

        if value_type == numpy.datetime64:
            value = convert_to_r_posixct(value)
        else:
            value = [item if pandas.notnull(item) else NA_TYPES[value_type]
                     for item in value]

            value = VECTOR_TYPES[value_type](value)

            if not strings_as_factors:
                I = robjects.baseenv.get("I")
                value = I(value)

        columns[column] = value

    r_dataframe = robjects.DataFrame(columns)
    r_dataframe.rownames = robjects.StrVector(df.index)

    return r_dataframe