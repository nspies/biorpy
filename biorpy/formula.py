import numpy
import pandas
from biorpy import r
from biorpy import conversion
from rpy2.robjects import Formula as RPy2Formula

# def getSimpleFormula(x, y):
#     formula = Formula("y ~ x")
#     formula.environment["x"] = x
#     formula.environment["y"] = y
    
#     return formula

class Formula(object):
    def __init__(self, formula, table):
        self.f = RPy2Formula(formula)
        for name in table:
            self.f.environment[name] = conversion.convertToR(table[name])
        self.table = conversion.convertToR(table)

class Model(object):
    def __init__(self, formula, table):
        self.f = Formula(formula, table)
        self.lm = r.lm(self.f.f, data=conversion.convertToR(table))
        self._summary = None
        self._coeff = None
        self._residuals = None

    def summary(self):
        if self._summary is None:
            self._summary = r.summary(self.lm)
        return self._summary

    def coeff(self):
        if self._coeff is None:
            x = self.summary().rx("coefficients")[0]
            self._coeff = pandas.DataFrame(numpy.array(x), columns=r.colnames(x), index=r.rownames(x))
        return self._coeff

    def residuals(self):
        if self._residuals is None:
            self._residuals = numpy.array(self.lm.rx("residuals")[0])
        return self._residuals


class GAM(object):
    def __init__(self, formula, table, **gamExtras):
        self.f = Formula(formula, table)
        self.lm = r.gam(self.f.f, data=conversion.convertToR(table), **gamExtras)
        self._summary = None
        self._coeff = None
        self._residuals = None