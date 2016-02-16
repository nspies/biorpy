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
from biorpy import r, conversion
#import rpy2.robjects.numpy2ri
from rpy2 import robjects as robj
from rpy2.rlike.container import TaggedList
# rpy2.robjects.numpy2ri.activate()

from biorpy.dotplots import DotPlots, asdict

def _setdefaults(toupdate, defaults):
    """ calls dict.setdefault() multiple times """
    for key, val in defaults.iteritems():
        toupdate.setdefault(key, val)

def plotMulti(xs, ys, names, colors=None, legendWhere="bottomright", xlab="", ylab="", plotArgs=None, lineArgs=None, **kwdargs):
    """ Plot multiple lines on the same axes; convenience function for calling 
    r.plot() and then r.lines() (possibly multiple times) and adding an r.legend()

    Args:
        xs: a list of vectors of x values, one vector for each dataset to be plotted
        ys: a list of vectors of y values, as above, in the same order
        names: the names of each dataset, used for putting together the legend 
        colors: an optional list of colors (html hex style)
        legendWhere: the location parameter used to specify positioning of the legend (a combination 
            of bottom/top and right/left)
        plotArgs: an optional dictionary of arguments to ``r.plot()``, for example ``xlim=[0,3]``
        lineArgs: an option dictionary of arguments to ``r.lines()``
        kwdArgs: optional R plotting arguments can be passed in as keyword arguments [eg, plotMulti(xs, ys, names, lty=3)]
            to specify parameters for both the ``r.plot()`` and ``r.lines()`` commands
    """

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
        
    r.plot(x, y, main="{} rs = {:.3g}".format(main, cor), **kwdargs)

def plotWithFit(x, y, main="", show=["r", "p"], fitkwdargs=None, **plotkwdargs):
    """ Plots data and adds a linear best fit line to the scatterplot

    Args
        fitkwdargs: a dictionary with ``r.line()`` drawing parameters for the fit line
            additional keyword arguments arg passed directly to ``r.plot()``
    """

    import scipy.stats
    if fitkwdargs is None:
        fitkwdargs = {}

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)

    main = main
    for name in show:
        if name == "slope":
            main += " m={:.2g}".format(slope)
        elif name == "intercept":
            main += " b={:.2g}".format(intercept)
        elif name == "r":
            main += " r={:.2g}".format(r_value)
        elif name == "p":
            main += " p={:.2g}".format(p_value)
        elif name == "r2":
            main += " r2={:.2g}".format(r_value*r_value)

    r.plot(x, y, main=main, **plotkwdargs)
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
            
    

def ecdf(vectors, labels=None, colors=["red", "blue", "orange", "violet", "green", "brown"],
         xlab="", ylab="cumulative fraction", main="", legendWhere="topleft", 
         lty=1, lwd=1, legendArgs=None, labelsIncludeN=True, **ecdfKwdArgs):
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

    # ecdfKwdArgs.update({"verticals":True, "do.points":False, "col.hor":colors[0], "col.vert":colors[0], "lty":lty[0], "lwd":lwd[0]})

    if not "xlim" in ecdfKwdArgs or ecdfKwdArgs["xlim"] is None:
        xlim = [min(min(vector) for vector in vectors if len(vector) > 0),
                max(max(vector) for vector in vectors if len(vector) > 0)]
        ecdfKwdArgs["xlim"] = xlim


    started = False
    for i, vector in enumerate(vectors):
        if len(vector) > 0:
            ecdfKwdArgs.update({"verticals":True, "do.points":False, 
                                "col.hor":colors[(i)%len(colors)],
                                "col.vert":colors[(i)%len(colors)],
                                "lty":lty[(i)%len(lty)],
                                "lwd":lwd[(i)%len(lwd)]})
            if not started:
                r.plot(r.ecdf(vector), main=main, xlab=xlab, ylab=ylab, **ecdfKwdArgs)
                started = True
            else:
                r.plot(r.ecdf(vector), add=True, **ecdfKwdArgs)

        # r.plot(r.ecdf(vector), add=True,
        #             **{"verticals":True, "do.points":False, "col.hor":colors[(i+1)%len(colors)], "col.vert":colors[(i+1)%len(colors)],
        #                "lty":lty[(i+1)%len(lty)], "lwd":lwd[(i+1)%len(lwd)]})

    if labels is not None:
        if labelsIncludeN:
            labelsWithN = []
            for i, label in enumerate(labels):
                labelsWithN.append(label+" (n=%d)"%len(vectors[i]))
        else:
            labelsWithN = labels
        legendArgs = asdict(legendArgs, {"cex":0.7})
        r.legend(legendWhere, legend=labelsWithN, lty=lty, lwd=[lwdi*2 for lwdi in lwd], col=colors, bg="white", **legendArgs)



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

def barPlot2(dataframe, legend=False, legendWhere="topright", **kwdArgs):
    rdf = conversion.pandasDataFrameToRPy2DataFrame(dataframe)
    if legend:
        kwdArgs["legend.text"] = list(dataframe.index)
        kwdArgs["args.legend"] = robj.ListVector({"x":legendWhere})
    kwdArgs.setdefault("names.arg", list(dataframe.columns))
    coords = r.barplot(r("as.matrix")(rdf), **kwdArgs)
    return coords


def scatterplotMatrix(dataFrame, main="", **kwdargs):
    """ Plots a scatterplot matrix, with scatterplots in the upper left and correlation
    values in the lower right. Input is a pandas DataFrame.
    """
    r.library("lattice")

    if isinstance(dataFrame, pandas.core.frame.DataFrame):
        df = dataFrame
    else:
        taggedList = TaggedList(map(robj.FloatVector, [dataFrame[col] for col in dataFrame.columns]), dataFrame.columns)
        df = robj.DataFrame(taggedList)

    #print taggedList
    #df = robj.r['data.frame'](**datapointsDict)
    #df = robj.r['data.frame'](taggedList)
    #print df
    #robj.r.splom(df)
    #robj.r.pairs(df)

    r("""panel.cor <- function(x, y, digits=2, prefix="", cex.cor)
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
    r("""panel.hist <- function(x, ...)
    {
        usr <- par("usr"); on.exit(par(usr))
        par(usr = c(usr[1:2], 0, 1.5) )
        h <- hist(x, plot = FALSE)
        breaks <- h$breaks; nB <- length(breaks)
        y <- h$counts; y <- y/max(y)
        rect(breaks[-nB], 0, breaks[-1], y, col="lightgrey", ...)
    }""")
                                        

    additionalParams = {"upper.panel": r["panel.smooth"]._robject, 
                        "lower.panel": r["panel.cor"]._robject, 
                        "diag.panel": r["panel.hist"]._robject}
    additionalParams.update(kwdargs)
    r.pairs(df, main=main, **additionalParams)


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


def plotMatrixAsImage(mat, x1=None, y1=None, x2=None, y2=None, maxval=None, main=""):
    """ adds the image to the current plot if x1, x2, y1 and y2 are defined;
    otherwise, create a new image with the dimensions of the matrix """
    if x1 is None:
        x1 = y1 = 0
        x2 = mat.shape[1]
        y2 = mat.shape[0]
        print x1, x2, y1, y2
        r.plot([0], xlim=[0,x2], ylim=[0,y2], type="n", main=main)

    if maxval is None:
        maxval = mat.max()
    r.rasterImage(r["as.raster"](mat, max=maxval), x1, y1, x2, y2)


def dotplots(data, groups=None, **kwdargs):
    constructorArgs = ["betweenMembers", "betweenGroups", "jitter", "drawMemberLabels", 
                       "mar", "drawMeans", "drawStd", "drawConfInt", "errBarColors", "pointsArgs", "plotArgs",
                       "yaxisArgs", "errBarArgs", "groupLabelArgs", "memberLabelArgs", "labelAngle", "ordered",
                       "drawMedians"]

    drawArgs = ["groupLabels", "groupColors", "xlim", "ylim", "memberColors", "nestedColors",
                "memberBackgroundColors", "errBarColors", "errBarLwds", "main", "xlab", "ylab"]

    for kwd in kwdargs:
        if kwd not in constructorArgs and kwd not in drawArgs:
            raise Exception("not yet (re-)implemented: {}".format(kwd))

    constructorInput = dict((key, kwdargs[key]) for key in kwdargs if key in constructorArgs)
    plotter = DotPlots(**constructorInput)

    drawInput = dict((key, kwdargs[key]) for key in kwdargs if key in drawArgs)
    
    return plotter.draw(data, groups, **drawInput)



# DIDWARN = False
# def dotplots(data, groups=None, drawMeans=True, drawConfInt=False, drawStd=False, memberColors=None, 
#           betweenMembers=0.5, betweenGroups=0.5, groupLabels=None, drawMemberLabels=True, memberBackgroundColors=None,
#           groupBackgroundColors=None, errBarArgs=None, plotArgs=None,
#           groupColors=None, errBarColors=None, main="", ylab="", ylim=None, jitter=0.1, mar=None, **kwdargs):
#     """ This plots a nice dot/strip plot, where all the data points for each sample are plotted in jittered
#     form

#     Args:
#         data: a dictionary of lists or a pandas dataframe, where each key/column corresponds to a sample or set of 
#             samples and the values are the data points
#         groups: an optional list of lists defining a visual grouping of the sample names
#         drawMeans: option to draw a hash mark at the mean point of each sample
#         drawConfInt: option to draw error bars indicating the 95% confidence interval (calculated as +/-1.96*SEM)
#         drawStd: draw confidence intervals based on std dev
#         memberColors: list of colors for each sample; need to define the order of samples using groups
#         groupColors: list of colors, one for each group in groups; mutually exclusive with memberColors
#         betweenMembers: spacing between samples
#         betweenGroups: spacing between groups
#         groupLabels: optional list of labels for the groups; probably won't look good if drawMemberLabels is True
#         drawMemberLabels: whether or not to draw the labels for each sample (probably use in conjunction with groupLabels)
#         errBarColors: colors for the error bars; either a string, or a list of strings with length equal to the total number of samples
#         main: plot title
#         ylab: y-axis label
#         ylim: y-axis limits
#         jitter: the amount of jitter to use to distribute points for each sample
#         mar: the margins used for the plot; defaults to numpy.array([6,4.5,4,2])+0.1
#     """

#     import scipy.stats

#     global DIDWARN
#     if not DIDWARN:
#         print "The dotplots() function is deprecated"
#         DIDWARN = True

    
#     if groups is None:
#         assert memberColors is None
#         groups = [[x] for x in data]
    
#     members = []
#     positions = {}
#     curPosition = 0
#     groupPositions = []

#     for group in groups:
#         curGroupPositions = []
#         for member in group:
#             members.append(member)
#             positions[member] = curPosition
#             curGroupPositions.append(curPosition)
#             curPosition += betweenMembers
#         groupPositions.append((max(curGroupPositions)+min(curGroupPositions))/2.0)
#         curPosition += betweenGroups
    
#     if memberColors is not None and groupColors is not None:
#         raise Exception("may only define one of groupColors, memberColors")
#     elif groupColors is not None:
#         memberColors = []
#         for i, group in enumerate(groups):
#             memberColors.extend([groupColors[i]]*len(group))
#     elif memberColors is not None:
#         if isinstance(memberColors, list):
#             assert len(memberColors) == len(members)
#         elif isinstance(memberColors, basestring):
#             memberColors = [memberColors] * len(members)
#     else:
#         memberColors = ["black"] * len(members)
        
#     if isinstance(errBarColors, basestring):
#         errBarColors = [errBarColors] * len(members)
    
#     xlim = [min(positions.values()) - betweenMembers/2.0, max(positions.values()) + betweenMembers/2.0]
#     if ylim is not None:
#         pass
#     elif isinstance(data, pandas.DataFrame):
#         ylim = [data.min().min(), data.max().max()]
#     else:
#         low = min(min(data[x]) for x in data)
#         high = max(max(data[x]) for x in data)
#         ylim = [low, high]
    
#     if mar is None:
#         mar = numpy.array([6,4.5,4,2])+0.1
#     oldpar = r.par(las=2, mar=mar)

#     plotArgDefaults = {"cex":1.5, "lwd":2}
#     if plotArgs is None: plotArgs = {}
#     _setdefaults(plotArgs, plotArgDefaults)

#     r.plot(1, cex=plotArgs["cex"], xlim=xlim, ylim=ylim, xaxt="n", yaxt="n", main=main, ylab=ylab, type="n")
#                    # **{"cex.lab":1.25})
#     r.axis(2, kwdargs.get("cex.axis", 1.0))

#     if memberBackgroundColors is not None:
#         if groupBackgroundColors is not None:
#             raise Exception("should only define either member or group background colors!")
#         assert len(memberBackgroundColors) == len(members)
#         for member, bgColor in zip(members, memberBackgroundColors):
#             # y1 = r.par("usr")[2]
#             # y2 = r.par("usr")[3]
#             y1 = ylim[0]
#             y2 = ylim[1]
#             r.rect(positions[member]-betweenMembers/2.0, y1, positions[member]+betweenMembers/2.0, y2, 
#                 col=bgColor, border=False)


#     for i, member in enumerate(members):
#         curColor = memberColors[i]
#         x = r.jitter([positions[member]]*len(data[member]), amount=jitter)
#         # if i == 0:
#         #     r.plot(x, data[member], cex=1.5, lwd=2, col=curColor, xlim=xlim, ylim=ylim, xaxt="n", main=main, ylab=ylab,
#         #            **{"cex.lab":1.25})
#         # else:
#         r.points(x, data[member], cex=plotArgs["cex"], lwd=plotArgs["lwd"], col=curColor)
    
#     errBarDefaults = {"lwd":2, "length":0.1}
#     if errBarArgs is None: errBarArgs = {}
#     _setdefaults(errBarArgs, errBarDefaults)

#     for i, member in enumerate(members):
#         x = positions[member]
#         y = numpy.mean(data[member])
#         if errBarColors is None:
#             curColor = memberColors[i]
#         else:
#             curColor = errBarColors[i]
                
#         if drawMeans:
#             r.segments(x-0.2, y, x+0.2, y, lwd=errBarArgs["lwd"], col=curColor)

#         curValues = numpy.asarray(data[member])
#         curValues = curValues[~numpy.isnan(curValues)]
#         if drawConfInt:
#             ci = scipy.stats.sem(curValues) * 1.96
#             r.arrows(x, y-ci, x, y+ci, lwd=errBarArgs["lwd"], col=curColor, angle=90, code=3, length=errBarArgs["length"])
#         if drawStd:
#             ci = numpy.std(curValues)
#             r.arrows(x, y-ci, x, y+ci, lwd=errBarArgs["lwd"], col=curColor, angle=90, code=3, length=errBarArgs["length"])

#     if drawMemberLabels:
#         r.mtext([str(x) for x in members], side=1, line=1, at=[positions[x] for x in members])#, col=memberColors)
#     if groupLabels is not None:
#         r.mtext(groupLabels, side=1, line=2, las=1, at=groupPositions, cex=1.6)
#     r.par(oldpar)