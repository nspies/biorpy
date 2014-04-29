from IPython.core.displaypub import publish_display_data
import tempfile
from glob import glob
from shutil import rmtree

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