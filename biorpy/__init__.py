from biorpy import betteR
r = betteR.BetteR()

from biorpy import pandas_additions


try:
    from biorpy.interactive import iimage, png
except ImportError:
    pass

from biorpy.conversion import asstr, asfloat, asint

from biorpy.formula import Model, GAM
