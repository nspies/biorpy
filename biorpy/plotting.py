##
## biorpy plotting wrappers
##
## nspies in ze house
##
import collections

import numpy
import pandas
import rpy2

#from rpy2.robjects import r
from biorpy.betteR import BetteR
import rpy2.robjects.numpy2ri
from rpy2 import robjects as robj
from rpy2.rlike.container import TaggedList
# rpy2.robjects.numpy2ri.activate()

r = BetteR()

def _setdefaults(toupdate, defaults):
    """ calls dict.setdefault() multiple times """
    for key, val in defaults.iteritems():
        toupdate.setdefault(key, val)

def plotMulti(xs, ys, names, colors=None, legendWhere="bottomright", xlab="", ylab="", plotArgs=None, lineArgs=None, **kwdargs):
    """ Plot multiple lines on the same axes; convenience function for calling 
    r.plot() and then r.lines() (possibly multiple times) and adding an r.legend()

    :param xs: a list of vectors of x values, one vector for each dataset to be plotted
    :param ys: a list of vectors of y values, as above, in the same order
    :param names: the names of each dataset, used for putting together the legend 
    :param colors: an optional list of colors (html hex style)
    :param legendWhere: the location parameter used to specify positioning of the legend (a combination 
        of bottom/top and right/left)
    :param plotArgs: an optional dictionary of arguments to r.plot(), for example xlim=[0,3]
    :param lineArgs: an option dictionary of arguments to r.lines()

    optional R plotting arguments can be passed in as keyword arguments [ie, plotMulti(xs, ys, names, lty=3)]
        to specify parameters for both the r.plot() and r.lines() commands """

    assert len(ys) == len(names)
    if len(xs) != len(ys):
        xs = [xs for i in range(len(names))]
    assert len(xs) == len(ys)

    if colors is None:
        colors = ["red", "blue", "green", "orange", "brown", "purple", "black"]

    ylim = [min(min(y) for y in ys), max(max(y) for y in ys)]
    xlim = [min(min(x) for x in xs), max(max(x) for x in xs)]

    if plotArgs is None: plotArgs = {}
    if lineArgs is None: lineArgs = {}

    plotArgsDefaults = {"xlab":xlab, "ylab":ylab, "xlim":xlim, "ylim":ylim, "type":"l"}
    _setdefaults(plotArgs, plotArgsDefaults)
    plotArgs.update(kwdargs)

    lineArgsDefaults = {"type":"l"}
    _setdefaults(lineArgs, lineArgsDefaults)
    lineArgs.update(kwdargs)

    for i in range(len(xs)):
        if i == 0:
            r.plot(xs[0], ys[0], col=colors[0], **plotArgs)
        else:
            r.lines(xs[i], ys[i], col=colors[i%len(colors)], **lineArgs)

    r.legend(legendWhere, legend=names, lty=1, lwd=2, col=colors, bg="white")


def plotWithCor(x, y, method="spearman", main="", **kwdargs):
    """ Adds the correlation coefficient to the title of a scatterplot """
    cor = r.cor(x, y, method=method)[0]
        
    r.plot(x, y, main="{} rs = {}".format(main, cor), **kwdargs)

def plotWithFit(x, y, main="", fitkwdargs=None, **plotkwdargs):
    """ Plots data and adds a linear best fit line to the scatterplot

    Args
        fitkwdargs: a dictionary with r.line() drawing parameters for the fit line
            additional keyword arguments arg passed directly to r.plot()
    """

    import scipy.stats
    if fitkwdargs is None:
        fitkwdargs = {}

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)

    r.plot(x, y, main="{} r={:.2g} p={:.2g}".format(main, r_value, p_value), **plotkwdargs)
    r.abline(a=intercept, b=slope, **fitkwdargs)

def errbars(x=None, y=None, x_lower=None, x_upper=None, y_lower=None, y_upper=None, length=0.08, *args, **kwdargs):
    """ Draws error bars on top of an existing plot

    specify EITHER: (y, x_lower and x_upper) OR (x, y_lower, y_upper)
    y: the y coordinate of each data point
    x_lower: the left coordinate of the error bar
    x_upper: the right coordinate of the error bar

    similarly for `x`, `y_lower` and `y_upper`
    uses the r.arrows() command, and passes any additional keyword args to r.arrows()
    """
    if y is not None and  x_lower is not None  and x_upper is not None:
        r.arrows(x_lower, y, x_upper, y, angle = 90, code = 3, length = length, *args, **kwdargs)
    elif x is not None and y_lower is not None and y_upper is not None:
        r.arrows(x, y_lower, x, y_upper, angle = 90, code = 3, length = length, *args, **kwdargs)
    else:
        raise Exception("must define either (y, x_lower, x_upper) or (x, y_lower, y_upper)")
            
    

def ecdf(vectors, labels, colors=["red", "blue", "orange", "violet", "green", "brown"],
         xlab="", ylab="cumulative fraction", main="", legendWhere="topleft", 
         lty=1, lwd=1, **ecdfKwdArgs):
    """ Take a list of lists, convert them to vectors, and plots them sequentially on a CDF """

    #print "MEANS:", main
    #for vector, label in zip(convertToVectors, labels):
    #    print label, numpy.mean(vector)
    
    def _expand(item):
        try:
            iter(item)
            return item
        except TypeError:
            return [item] * len(vectors)
            
    
    lty = _expand(lty)
    lwd = _expand(lwd)

    ecdfKwdArgs.update({"verticals":True, "do.points":False, "col.hor":colors[0], "col.vert":colors[0], "lty":lty[0], "lwd":lwd[0]})

    if not "xlim" in ecdfKwdArgs or ecdfKwdArgs["xlim"] is None:
        xlim = [min(min(vector) for vector in vectors),
                max(max(vector) for vector in vectors)]
        ecdfKwdArgs["xlim"] = xlim

    r.plot(r.ecdf(vectors[0]), main=main, xlab=xlab, ylab=ylab, **ecdfKwdArgs)

    for i, vector in enumerate(vectors[1:]):
        r.plot(r.ecdf(vector), add=True,
                    **{"verticals":True, "do.points":False, "col.hor":colors[i+1], "col.vert":colors[i+1],
                       "lty":lty[i+1], "lwd":lwd[i+1]})

    labelsWithN = []
    for i, label in enumerate(labels):
        labelsWithN.append(label+" (n=%d)"%len(vectors[i]))
    r.legend(legendWhere, legend=labelsWithN, lty=lty, lwd=[lwdi*2 for lwdi in lwd], col=colors, cex=0.7, bg="white")



def boxPlot(dict_, keysInOrder=None, **kwdargs):
    """ Plot a boxplot

    dict_: a dictionary of group_name -> vector, where vector is the data points to be plotted for each group;
        use a collections.OrderedDict() to easily convey the order of the groups
    keysInOrder: an optional ordering of the keys in dict_ (alternate option to using collections.OrderedDict)

    additional ``kwdargs`` are passed directly to ``r.boxplot()``
    """

    if not keysInOrder:
        keysInOrder = dict_.keys()
        
    t = TaggedList([])
    for key in keysInOrder:
        t.append(robj.FloatVector(dict_[key]), "X:"+str(key))

    x = r.boxplot(t, names=keysInOrder, **kwdargs)
    return x

def barPlot(dict_, keysInOrder=None, printCounts=True, ylim=None, *args, **kwdargs):
    """ Plot a bar plot

    Args:
        dict_: a dictionary of name -> value, where value is the height of the bar
            use a collections.OrderedDict() to easily convey the order of the groups
        keysInOrder: an optional ordering of the keys in dict_ (alternate option to using collections.OrderedDict)
        printCounts: option to print the counts on top of each bar

    additional kwdargs are passed directly to r.barplot()
    """

    if not keysInOrder:
        keysInOrder = dict_.keys()
    
    heights = [dict_[key] for key in keysInOrder]

    kwdargs["names.arg"] = keysInOrder

    if ylim is None:
        if printCounts:
            ylim = [min(heights), max(heights)*1.1]
        else:
            ylim = [min(heights), max(heights)]

    x = r.barplot(heights, ylim=ylim, *args, **kwdargs)

    if printCounts:
        heightsStrings = ["{:.2g}".format(height) for height in heights]
        r.text(x, heights, heightsStrings, pos=3)
    return x



def scatterplotMatrix(dataFrame, main="", **kwdargs):
    """ Plots a scatterplot matrix, with scatterplots in the upper left and correlation
    values in the lower right. Input is a pandas DataFrame.
    """
    robj.r.library("lattice")

    taggedList = TaggedList(map(robj.FloatVector, [dataFrame[col] for col in dataFrame.columns]), dataFrame.columns)

    #print taggedList
    #df = robj.r['data.frame'](**datapointsDict)
    #df = robj.r['data.frame'](taggedList)
    df = robj.DataFrame(taggedList)
    #print df
    #robj.r.splom(df)
    #robj.r.pairs(df)

    robj.r("""panel.cor <- function(x, y, digits=2, prefix="", cex.cor)
    {
        usr <- par("usr"); on.exit(par(usr))
        par(usr = c(0, 1, 0, 1))
        r <- cor(x, y, method="spearman")
        scale = abs(r)*0.8+0.2
        txt <- format(c(r, 0.123456789), digits=digits)[1]
        txt <- paste(prefix, txt, sep="")
        if(missing(cex.cor)) cex.cor <- 0.8/strwidth(txt)
        text(0.5, 0.5, txt, cex = cex.cor * scale+0.2)
    }
    """)
    robj.r("""panel.hist <- function(x, ...)
    {
        usr <- par("usr"); on.exit(par(usr))
        par(usr = c(usr[1:2], 0, 1.5) )
        h <- hist(x, plot = FALSE)
        breaks <- h$breaks; nB <- length(breaks)
        y <- h$counts; y <- y/max(y)
        rect(breaks[-nB], 0, breaks[-1], y, col="lightgrey", ...)
    }""")
                                        

    additionalParams = {"upper.panel": robj.r["panel.smooth"], "lower.panel": robj.r["panel.cor"], "diag.panel":robj.r["panel.hist"]}
    additionalParams.update(kwdargs)
    robj.r["pairs"](df, main=main, **additionalParams)


def plotWithSolidErrbars(x, y, upper, lower, add=False, errbarcol="lightgray", plotargs={}, polygonargs={}):
    x = numpy.asarray(x)

    errbarx = numpy.concatenate([x, x[::-1]])
    errbary = numpy.concatenate([upper, lower[::-1]])

    if not add:
        r.plot(x, y, type="n", **plotargs)

    polygondefaults = {"border":"NA"}
    polygonargs.update(polygondefaults)

    r.polygon(errbarx, errbary, col=errbarcol, **polygonargs)

    r.lines(x, y, **plotargs)

    return x, y, upper, lower, errbarx, errbary