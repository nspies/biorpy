import collections
import numpy
import pandas
from biorpy import r, plotting

DEMO = []

def demo(fn):
    global DEMO
    DEMO.append(fn)
    return fn

def demodata():
    return numpy.arange(10), numpy.random.normal(size=10)

@demo
def scatterplot():
    # converts numpy arrays transparently
    x, y = demodata()
    r.plot(x, y)

@demo
def multiPlot():
    # also converts python lists transparently
    x1 = range(10)
    y1 = numpy.random.normal(size=10)

    x2 = x1
    y2 = x2

    x3 = range(10, 20)
    y3 = numpy.random.normal(size=10)

    plotting.plotMulti([x1, x2, x3], [y1, y2, y3], ["1", "2", "3"], lty=2)

@demo
def plotErrBars():
    x = numpy.arange(10)
    y = x + numpy.random.normal(size=10)

    y_upper = y + abs(numpy.random.normal(size=10))
    y_lower = y - abs(numpy.random.normal(size=10))
    ylim = [y_lower.min(), y_upper.max()]

    r.plot(x, y, pch=20, xlab="x axis label", ylab="y!!", ylim=ylim)
    plotting.errbars(x=x, y_lower=y_lower, y_upper=y_upper, col="red")

@demo
def ecdf():
    dataset = []
    for i in range(5):
        # each "sample" has mean=i
        dataset.append(numpy.random.normal(loc=i, size=30))

    plotting.ecdf(dataset, ["a", "b", "c", "d", "e"], xlab="xxx", main="comparing 5 normals")

@demo
def boxPlot():
    # could also be a normal dictionary

    dataset = collections.OrderedDict()
    for i, sample in enumerate("ABCDE"):
        dataset[sample] = numpy.random.normal(loc=i, size=30)

    plotting.boxPlot(dataset)


@demo
def barPlot():
    # could also be a normal dictionary

    dataset = collections.OrderedDict()
    for i, sample in enumerate("ABCDE"):
        dataset[sample] = numpy.random.normal(loc=i)

    plotting.barPlot(dataset)

@demo
def barPlotWithErrBars():
    # could also be a normal dictionary

    dataset = collections.OrderedDict()
    for i, sample in enumerate("ABCDE"):
        dataset[sample] = numpy.random.normal(loc=i)

    y_lower = numpy.array(dataset.values()) - 1
    y_upper = numpy.array(dataset.values()) + 1

    x = plotting.barPlot(dataset, printCounts=False, ylim=[y_lower.min(), y_upper.max()])
    plotting.errbars(x=x, y_lower=y_lower, y_upper=y_upper)

@demo
def scatterplotMatrix():
    x = numpy.arange(250)
    y = x + numpy.random.normal(scale=25, size=250)
    z = x + numpy.random.normal(scale=75, size=250)

    df = pandas.DataFrame({"x":x, "y":y, "z":z})

    plotting.scatterplotMatrix(df, main="Comparing multiple datasets")

def demoMessage(message):
    print "\n", "*"*10, message, "*"*10

@demo
def convertResultsFromR():
    # automatic conversion to pandas DataFrame

    rDataFrame = r("data.frame(A=1:5, B=5:9, row.names=c('a', 'b', 'c', 'd', 'e'))")

    demoMessage("An R data.frame, returned for use in python:")
    print rDataFrame

    # rDataFrame.py gets automatically converted, in this case from an R data.frame to a pandas DataFrame
    demoMessage("Automatic conversion of output to pandas DataFrame")
    print rDataFrame.py

    # More complicated output:
    result = r["wilcox.test"](range(5), range(5, 10))

    demoMessage("Output directly from rpy2:")
    print result

    demoMessage("Auto conversion with biorpy:")
    print type(result.py)
    print repr(result.py)




def main(topdf=False):
    if topdf:
        r.pdf("examples.pdf")

    for fn in DEMO:
        fn()

        if not topdf and raw_input("continue? (hit enter or 'y' to continue, any other key to exit)") not in ["", "Y", "y"]:
            break

    if topdf:
        r.devoff()

if __name__ == '__main__':
    main(topdf=True)