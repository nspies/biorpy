Quick start
***********

biorpy provides an easy interface to R from python, wrapping the lower-level functionality provided by the rpy2 python package. To start, you'll need to ensure that R, rpy2, biorpy, numpy and pandas are all installed. The examples.py script included in the biorpy distribution is a good example of the one- or few-line commands that can be issued to produce full-featured R plots.

To start:

.. ipython::

    In [1]: from biorpy import r
    
    In [2]: r.plot([1,3,5], [2.5, 3.5, 1.5])


.. figure::  ../images/plot1.png
   :align:   center


The plot appear in an interactive window (an X11 device on the Mac). We can use any of the standard R arguments to the ``plot`` function, for example to add color to the points and labels to the axes and the plot:

.. ipython::

    In [12]: r.plot([1,3,5], [2.5, 3.5, 1.5], cex=3, col=["red", "blue", "green"], 
       ....:        xlab="length", ylab="width", main="Length vs Width")


.. figure::  ../images/plot2.png
   :align:   center


Some R functions expect a ``data.frame`` as input. biorpy transparently converts pandas ``DataFrame`` to R ``data.frame``:

.. ipython::

    In [12]: import pandas

    In [13]: dataFrame = pandas.DataFrame({"x":range(5), "y":[12, 21, 35, 40, 52]})

    In [15]: print dataFrame

    In [16]: result = r.boxplot(dataFrame)


.. figure::  ../images/boxplot1.png
   :align:   center


Here you also see another little trick used in rpy2 and biorpy: because names can contain periods (".") in R, but not in python, you can access functions containing a period using the dictionary-like access, ``r["wilcox.test"]``.

.. ipython::

    In [22]: wilcoxResult = r["wilcox.test"](range(10), range(100, 120))


The output from R functions is by default returned exactly as if from rpy2. (The exception to this is if the object is an R ``data.frame``, which gets converted directly to a pandas DataFrame.) Because everything in R is a type of vector, and vectors are not standard data types in python, these returned objects can look pretty odd. biorpy adds a convenience variable, ``.py``, to each result from R, which behaves like a dictionary or an object (depending on your preference):

.. ipython::

    In [23]: wilcoxResult.py.keys()

    In [23]: wilcoxResult.py.method

    In [23]: wilcoxResult.py["p.value"]

The ``wilcoxResult.py`` attribute will perform some amount of conversion between dotted and non-dotted attribute names, so it will understand both ``wilcoxResult.py.pvalue`` or ``wilcoxResult.py["p.value"]``.

Items in ``.py`` are converted into pandas DataFrames or numpy arrays where possible.