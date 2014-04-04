import pydoc
from rpy2 import robjects
import operator

from biorpy.conversion import convertToR, addResultWrapper

def isIPy():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

def isInteractive():
    import __main__ as main
    return not hasattr(main, '__file__')


## DEFAULT ARGS, OUTPUT HANDLING

def rx(name):
    """ extracts a value by name from an R object """
    def f(x):
        return x.rx(name)
    return f

def item(i):
    """ Short name for operator.itemgetter() """
    return operator.itemgetter(i)



def getDefaultHandlers(converter):
    handlers = []
    handlers.append(Handler("wilcox.test", 
        # outputs={"p.value":[rx("p.value"), item(0), item(0)]},
        converter=converter)
    )

    handlers.append(Handler("plot", 
        defaults={"xlab":"", "ylab":"", "main":""},
        converter=converter)
    )

    handlers.append(Handler("hist", 
        defaults={"xlab":"", "main":""},
        converter=converter)
    )

    return handlers

def getDefaultAliases():
    return {"devoff":"dev.off"}


class Handler(object):
    """ Wrapper for R objects to implement:
    
    1. default arguments
    2. argument conversion
    3. output conversion

    """

    def __init__(self, rname, pyname=None, defaults=None, converter=convertToR):
        """
        Args
            name: name of the R function
            defaults: a dictionary of default arguments to the function
            outputs: a dictionary whose values are lists of functions used to extract values from 
                the return R value. For example: {"p.value":[rx("p.value"), item(0), item(0)]}
            converter: a conversion function used to convert python objects into R objects
        """
        self.rname = rname
        if pyname is None:
            self.pyname = rname
        else:
            self.pyname = pyname

        self.defaults = defaults if defaults else {}
        # self.outputs = outputs if outputs else {}
        self.converter = converter

        # may want some extra error checking here
        self._robject = robjects.r[self.rname]

    def __call__(self, *args, **kwdargs):
        # python -> R conversion
        args = [self.converter(arg) for arg in args]
        for kwd in kwdargs:
            kwdargs[kwd] = self.converter(kwdargs[kwd])

        # default arguments
        defaults = self.defaults.copy()
        defaults.update(kwdargs)

        # call R
        rval = robjects.r[self.rname](*args, **defaults)
        #rval = super(Handler, self).__call__(*args, **defaults)

        # output conversion
        addResultWrapper(rval)

        # if self.outputs:
        #     result = {}

        #     for output in self.outputs:
        #         result[output] = reduce(lambda x, f: f(x), self.outputs[output], rval)

        #     rval.py = result
        return rval

    def help(self):
        """ Displays the R help for the current object """

        pydoc.pager(robjects.help.pages(self.rname)[0].to_docstring())

    # @property
    # def __doc__(self):
    #     return str(robjects.r.help(self.rname))


class BetteR(object):
    """ Wrapper for rpy2.robjects.R """

    def __init__(self, converter=convertToR):
        """ Initialize the RPy2 wrapper instance """
        self.aliases = getDefaultAliases()

        self._handlers = {}

        for handler in getDefaultHandlers(converter):
            self.addHandler_(handler)

        if isInteractive():
            self.initInteractive()

    def initInteractive(self):
        """ Checks to see if we're running interactively (eg ipython), and if so, 
        starts the event manager in RPy2. (This allows resizing of interactive 
        plot windows.) """
        # This allows graphics windows to be resized
        from rpy2.interactive import process_revents
        try:
            process_revents.start()
        except RuntimeError:
            # this can occur when we've already called process_revents.start()
            # in any case, it's not a big deal if the above didn't work
            # so let's ignore the error
            pass


    def addHandler_(self, handler):
        """ Add a :class:`biorpy.betteR.Handler`."""
        self._handlers[handler.pyname] = handler


    def __getattribute__(self, attr):
        try:
            return super(BetteR, self).__getattribute__(attr)
        except AttributeError as ae:
            orig_ae = ae

        try:
            return self.__getitem__(attr)
        except LookupError:
            raise orig_ae


    def __getitem__(self, attr):
        if attr in self.aliases:
            attr = self.aliases[attr]

        if attr.startswith("gg"):
            print "do something for ggplot..."

        if not attr in self._handlers:
            self._handlers[attr] = Handler(attr)
        return self._handlers[attr]


    def __call__(self, string):
        rval = robjects.r(string)
        addResultWrapper(rval)

        return rval



if __name__ == '__main__':
    r = BetteR()

    result = r["wilcox.test"](robjects.FloatVector(range(5)), robjects.FloatVector([1,2,55,3,6]))
    print result.py["p.value"]

    #r.plot(robjects.FloatVector(range(5)), robjects.FloatVector([1,2,55,3,6]))

    r.plot([1,2,3,4,5], [1,3,4,4.5,5], col=["red" for i in range(5)])
    for i in range(100000):
        for j in range(1000):
            pass