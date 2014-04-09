from IPython.core.displaypub import publish_display_data
import tempfile
from glob import glob
from shutil import rmtree

from biorpy import r

class InlineImage(object):
    def __init__(self):
        self.running = False
        self.directory = None
    def start(self):
        if self.running:
            return
        self.running = True
        self.directory = tempfile.mkdtemp()
        r.png("{}/Rplots%03d.png".format(self.directory))
    def finish(self):
        if not self.running:
            return
        self.running = False
        r.devoff()
        
        imageFiles = glob("{}/Rplots*png".format(self.directory))
        images = [open(imgfile, 'rb').read() for imgfile in imageFiles]

        for image in images:
            publish_display_data("biorpy", {'image/png': image})

        rmtree(self.directory)

iimage = InlineImage()