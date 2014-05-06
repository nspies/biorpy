from IPython.core.displaypub import publish_display_data
from IPython.lib.display import IFrame
from IPython.display import HTML
import tempfile
import os
from glob import glob
from shutil import rmtree, copyfile

from biorpy import r

class InlineImage(object):
    def __init__(self):
        self.running = False
        self.directory = None

    def start(self, format="svg", **kwdargs):
        if self.running:
            return
        self.running = True
        self.directory = tempfile.mkdtemp()
        self.format = format

        if self.format == "svg":
            r.svg("{}/Rplots%03d.svg".format(self.directory), **kwdargs)
        elif self.format == "png":
            r.png("{}/Rplots%03d.png".format(self.directory), **kwdargs)
        else:
            raise Exception("Unknown image format:{}".format(format))

    def finish(self):
        if not self.running:
            return
        self.running = False
        r.devoff()
        
        if self.format == "svg":
            imageFiles = glob("{}/Rplots*svg".format(self.directory))
            image_type = 'image/svg+xml'
        elif self.format == "png":
            imageFiles = glob("{}/Rplots*png".format(self.directory))
            image_type = "image/png"
        images = [open(imgfile, 'rb').read() for imgfile in imageFiles]

        for image in images:
            publish_display_data("biorpy", {image_type: image})
            # publish_display_data("biorpy", {'image/png': image})

        rmtree(self.directory)

iimage = InlineImage()


# Switching to use IPython.lib.display.IFrame
    IFRAMEHTML = """<a href="{path}">{path}</a><br /><iframe name="myiframe" id="myiframe" src="{path}" height={height}px width=100%></iframe>"""

class InlinePDF(object):
    def __init__(self):
        self.running = False

    def __call__(self, path=None, **kwdargs):
        print self.running, path
        if not self.running:
            if path is None:
                raise Exception("Need to start InlinePDF first by passing the file path of the PDF to create.")
            self.start(path, **kwdargs)
        elif path is not None:
            raise Exception("Need to finish InlinePDF by calling without a file path.")
        else:
            return self.finish()

    def start(self, path, **kwdargs):
        if self.running:
            print "tried to restart"
            return
        print "starting..."
        self.running = True
        self.path = path
        self.kwdargs = kwdargs

        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        r.pdf(path, **kwdargs)


    def finish(self):
        if not self.running:
            print "tried to end but not running"
            return
        print "finishing"
        self.running = False
        r.devoff()

        # this factor probably depends on browser
        height = self.kwdargs.get("height", 7) * 100

        # imagesHtml = IFRAMEHTML.format(path=self.path, height=height)

        # h = imagesHtml

        # print h
        # # return HTML(h)
    
        return IFrame(self.path, height=height, width="100%")    

