import numpy
import pandas
from biorpy import r, asstr

def asdict(x, defaults=None):
    if defaults is None:
        defaults = {}
    if x is None:
        return defaults
    defaults.update(x)
    return defaults

def aslist(value, length):
    if isinstance(value, list):
        assert len(value) == length
    elif isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
        value = [value] * length
    return value

class DotPlots(object):
    def __init__(self, betweenMembers=0.5, betweenGroups=0.5, jitter=0.1, drawMemberLabels=True, memberColors="black", mar=None,
            drawMeans=True, drawMedians=False, drawStd=False, drawConfInt=True, errBarColors="black",
            pointsArgs=None, errBarArgs=None, memberLabelArgs=None, groupLabelArgs=None, plotArgs=None, yaxisArgs=None,
            deterministicJitter=True, ordered=False, labelAngle=90):
        self.betweenMembers = betweenMembers
        self.betweenGroups = betweenGroups
        self.defaultMemberColors = memberColors
        self.defaultErrBarColors = errBarColors
        self.defaultErrBarLwd = 2
        self.drawMemberLabels = drawMemberLabels
        self.jitter = jitter
        self.ordered = ordered

        self.drawMeans = drawMeans
        self.drawMedians = drawMedians
        self.drawStd = drawStd
        self.drawConfInt = drawConfInt

        self.pointsArgs = asdict(pointsArgs, {"cex":1.5, "lwd":2})
        self.plotArgs = asdict(plotArgs)
        self.errBarArgs = asdict(errBarArgs)
        self.yaxisArgs = asdict(yaxisArgs)

        self.memberLabelArgs = asdict(memberLabelArgs)
        self.groupLabelArgs = asdict(groupLabelArgs, {"cex":1.6, "las":1})
        self.labelAngle = labelAngle


        if mar is None:
            mar = numpy.array([6,4.5,4,2])+0.1
        self.mar = mar

        if deterministicJitter:
            r("set.seed")(2521)


    def draw(self, data, groups=None, groupLabels=None, groupColors=None, nestedColors=None, xlim=None, ylim=None, memberColors=None, 
            memberBackgroundColors=None, errBarColors=None, errBarLwds=None, xlab="", ylab="", main=""):
        oldpar = r.par(las=2, mar=self.mar)

        self.data = data
        if groups is None:
            groups = [[x] for x in data]
        self.groups = groups

        self.groupLabels = groupLabels

        self._getPositions()
        self._getAxisSizes(xlim, ylim)
        self._getMemberColors(memberColors, groupColors, nestedColors)
        self._getErrBarColors(errBarColors)
        self._getErrBarLwds(errBarLwds)
        self._getBackgroundColors(memberBackgroundColors)

        memberCoords, groupCoords = self.plot(main=main, xlab=xlab, ylab=ylab)

        r.par(oldpar)

        return memberCoords, groupCoords

    def plot(self, xlab="", ylab="", main=""):
        print("*"*200)
        # open plotting with an empty plot, custom axes
        r.plot(1, xlim=self.xlim, ylim=self.ylim, xlab=xlab, ylab=ylab, xaxt="n", yaxt="n", type="n", main=main, **self.plotArgs)
        r.axis(2, **self.yaxisArgs)

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
            if self.ordered:
                x = numpy.linspace(self.positions[member]-self.jitter, self.positions[member]+self.jitter, len(self.data[member]))
                y = sorted(self.data[member])
            else:
                x = r.jitter([self.positions[member]]*len(self.data[member]), amount=self.jitter)
                y = self.data[member]
            r.points(x, y, col=curColor, **self.pointsArgs)

        # draw the error bars
        if self.drawConfInt:
            import scipy.stats

        print(self.errBarLwds)
        for member, curColor, curLwd in zip(self.members, self.errBarColors, self.errBarLwds):
            x = self.positions[member]
                    
            if self.drawMeans:
                y = numpy.mean(self.data[member])
                r.segments(x-0.2, y, x+0.2, y, lwd=curLwd, col=curColor)
            elif self.drawMedians:
                y = numpy.median(self.data[member])
                r.segments(x-0.2, y, x+0.2, y, lwd=curLwd, col=curColor)

            curValues = numpy.asarray(self.data[member])
            curValues = curValues[~numpy.isnan(curValues)]
            if self.drawConfInt:
                ci = scipy.stats.sem(curValues) * 1.96
                y = numpy.mean(self.data[member])
                r.arrows(x, y-ci, x, y+ci, lwd=2, col=curColor, angle=90, code=3, length=0.1)
            if self.drawStd:
                ci = numpy.std(curValues)
                y = numpy.mean(self.data[member])
                r.arrows(x, y-ci, x, y+ci, lwd=2, col=curColor, angle=90, code=3, length=0.1)

        # add in the labels
        if self.drawMemberLabels:
            # r.mtext(asstr(self.members), side=1, line=1, at=[self.positions[x] for x in self.members], **self.memberLabelArgs)
            r.text([self.positions[x] for x in self.members], r('par("usr")[3] - 0.25'), labels=asstr(self.members), 
                xpd=True, srt=self.labelAngle, adj=1, **self.memberLabelArgs)

            # r.mtext([str(x) for x in self.members], side=1, line=1, at=[self.positions[x] for x in self.members], **self.memberLabelArgs)
        if self.groupLabels is not None:
            r.mtext(asstr(self.groupLabels), side=1, line=2, at=self.groupPositions, **self.groupLabelArgs)

        return [self.positions[member] for member in self.members], self.groupPositions

    def _getErrBarColors(self, errBarColors):
        if errBarColors is None:
            self.errBarColors = [self.defaultErrBarColors] * len(self.members)
        else:
            self.errBarColors = aslist(errBarColors, len(self.members))
    def _getErrBarLwds(self, errBarLwds):
        if errBarLwds is None:
            self.errBarLwds = [self.defaultErrBarLwd] * len(self.members)
        else:
            self.errBarLwds = aslist(errBarLwds, len(self.members))

    def _getMemberColors(self, memberColors, groupColors, nestedColors):
        if sum(map(bool, [memberColors, groupColors, nestedColors])) > 1:
            raise Exception("may only define one of groupColors, memberColors")
        elif groupColors is not None:
            memberColors = []
            for i, group in enumerate(self.groups):
                memberColors.extend([groupColors[i]]*len(group))
        elif memberColors is not None:
            if isinstance(memberColors, list):
                assert len(memberColors) == len(self.members)
            elif isinstance(memberColors, str):
                memberColors = [memberColors] * len(self.members)
        elif nestedColors is not None:
            memberColors = nestedColors
        else:
            memberColors = [self.defaultMemberColors] * len(self.members)

        self.memberColors = memberColors

    def _getBackgroundColors(self, memberBackgroundColors):
        ## XXX SHOULD EXTEND TO ALLOW SETTING GROUP BACKGROUND COLORS OR ALTERNATING BACKGROUND COLORS PER SAMPLE/GROUP
        self.memberBackgroundColors = None
        if memberBackgroundColors is not None:
            self.memberBackgroundColors = aslist(memberBackgroundColors, len(self.members))


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