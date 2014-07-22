import numpy
import pandas
from biorpy import r

def asdict(x):
    if x is None:
        return {}
    return x


class DotPlots(object):
    def __init__(self, betweenMembers=0.5, betweenGroups=0.5, jitter=0.1, drawMemberLabels=True, memberColors="black", mar=None,
            drawMeans=True, drawStd=False, drawConfInt=True, errBarColors="black",
            pointsArgs=None, errBarArgs=None, xaxisArgs=None, yaxisArgs=None):
        self.betweenMembers = betweenMembers
        self.betweenGroups = betweenGroups
        self.defaultMemberColors = memberColors
        self.defaultErrBarColors = errBarColors
        self.drawMemberLabels = drawMemberLabels
        self.jitter = jitter

        self.drawMeans = drawMeans
        self.drawStd = drawStd
        self.drawConfInt = drawConfInt

        self.pointsArgs = asdict(pointsArgs)
        self.errBarArgs = asdict(errBarArgs)

        self.xaxisArgs = asdict(xaxisArgs)
        self.yaxisArgs = asdict(yaxisArgs)

        if mar is None:
            mar = numpy.array([6,4.5,4,2])+0.1
        self.mar = mar

    def draw(self, data, groups=None, groupLabels=None, groupColors=None, xlim=None, ylim=None, memberColors=None, 
            memberBackgroundColors=None, errBarColors=None):
        oldpar = r.par(las=2, mar=self.mar)

        self.data = data
        if groups is None:
            groups = [[x] for x in data]
        self.groups = groups

        self.groupLabels = groupLabels

        self._getPositions()
        self._getAxisSizes(xlim, ylim)
        self._getMemberColors(memberColors, groupColors)
        self._getErrBarColors(errBarColors)
        self._getBackgroundColors(memberBackgroundColors)

        self.plot()

        r.par(oldpar)

    def plot(self):
        # open plotting with an empty plot, custom axes
        r.plot(1, xlim=self.xlim, ylim=self.ylim, xaxt="n", yaxt="n", type="n")
        r.axis(2)

        # draw the background colors
        if self.memberBackgroundColors is not None:
            assert len(self.memberBackgroundColors) == len(self.members)
            for member, bgColor in zip(self.members, self.memberBackgroundColors):
                # y1 = r.par("usr")[2]
                # y2 = r.par("usr")[3]
                y1 = self.ylim[0]
                y2 = self.ylim[1]
                r.rect(self.positions[member]-self.betweenMembers/2.0, y1, self.positions[member]+self.betweenMembers/2.0, y2, 
                    col=bgColor, border=False)

        # draw the different sets of points
        for i, member in enumerate(self.members):
            curColor = self.memberColors[i]
            x = r.jitter([self.positions[member]]*len(self.data[member]), amount=self.jitter)
            r.points(x, self.data[member], col=curColor)

        # draw the error bars
        if self.drawConfInt:
            import scipy.stats

        for member, curColor in zip(self.members, self.errBarColors):
            x = self.positions[member]
            y = numpy.mean(self.data[member])
                    
            if self.drawMeans:
                r.segments(x-0.2, y, x+0.2, y, lwd=2, col=curColor)

            curValues = numpy.asarray(self.data[member])
            curValues = curValues[~numpy.isnan(curValues)]
            if self.drawConfInt:
                ci = scipy.stats.sem(curValues) * 1.96
                r.arrows(x, y-ci, x, y+ci, lwd=2, col=curColor, angle=90, code=3, length=0.1)
            if self.drawStd:
                ci = numpy.std(curValues)
                r.arrows(x, y-ci, x, y+ci, lwd=2, col=curColor, angle=90, code=3, length=0.1)

        # add in the labels
        if self.drawMemberLabels:
            r.mtext([str(x) for x in self.members], side=1, line=1, at=[self.positions[x] for x in self.members])
        if self.groupLabels is not None:
            r.mtext(self.groupLabels, side=1, line=2, las=1, at=self.groupPositions, cex=1.6)

    def _getErrBarColors(self, errBarColors):
        if errBarColors is None:
            self.errBarColors = [self.defaultErrBarColors] * len(self.members)
        else:
            self.errBarColors = errBarColors

    def _getMemberColors(self, memberColors, groupColors):
        if memberColors is not None and groupColors is not None:
            raise Exception("may only define one of groupColors, memberColors")
        elif groupColors is not None:
            memberColors = []
            for i, group in enumerate(self.groups):
                memberColors.extend([groupColors[i]]*len(group))
        elif memberColors is not None:
            if isinstance(memberColors, list):
                assert len(memberColors) == len(self.members)
            elif isinstance(memberColors, basestring):
                memberColors = [memberColors] * len(self.members)
        else:
            memberColors = [self.defaultMemberColors] * len(self.members)

        self.memberColors = memberColors

    def _getBackgroundColors(self, memberBackgroundColors):
        ## XXX SHOULD EXTEND TO ALLOW SETTING GROUP BACKGROUND COLORS OR ALTERNATING BACKGROUND COLORS PER SAMPLE/GROUP
        self.memberBackgroundColors = memberBackgroundColors


    def _getAxisSizes(self, xlim, ylim):
        xlim = [min(self.positions.values()) - self.betweenMembers/2.0, max(self.positions.values()) + self.betweenMembers/2.0]
        if ylim is not None:
            pass
        elif isinstance(self.data, pandas.DataFrame):
            ylim = [self.data.min().min(), self.data.max().max()]
        else:
            low = min(min(self.data[x]) for x in self.data)
            high = max(max(self.data[x]) for x in self.data)
            ylim = [low, high]

        self.xlim = xlim
        self.ylim = ylim

    def _getPositions(self):
        members = []
        positions = {}
        curPosition = 0
        groupPositions = []

        for group in self.groups:
            curGroupPositions = []
            for member in group:
                members.append(member)
                positions[member] = curPosition
                curGroupPositions.append(curPosition)
                curPosition += self.betweenMembers
            groupPositions.append((max(curGroupPositions)+min(curGroupPositions))/2.0)
            curPosition += self.betweenGroups

        self.members = members
        self.positions = positions
        self.groupPositions = groupPositions



def main():
    datasets = {"a":[1,2,3], "b":[1.2, 1.5, 2.5, 3.5], "c":[0.5, 0.7, 0.9], "d":[2,4,7]}
    groups = [["a", "b"], ["c", "d"]]
    groupnames = ["1", "2"]

    r.pdf("temp.pdf")
    dp = DotPlots(betweenGroups=0)
    dp.draw(datasets, groups, groupLabels=groupnames, memberBackgroundColors=["lightblue", "yellow"]*2)
    r.devoff()


if __name__ == '__main__':
    main()