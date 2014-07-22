# import os
# from IPython.lib.display import IFrame
from IPython.core.displaypub import publish_display_data
from IPython.display import display_html
import tempfile
from glob import glob
from shutil import rmtree
import base64

from biorpy import r

PDFOBJECTHTML = """<object data="data:application/pdf;base64,{pdfdata}" type="application/pdf" width="100%" height="800">
<param name="view" value="FitH" /></object>"""

class InlineImage(object):
    def __init__(self):
        self.running = False
        self.directory = None

    def start(self, format="pdf", **kwdargs):
        if self.running:
            r.devoff()
            
        self.running = True
        self.directory = tempfile.mkdtemp()
        self.format = format

        if self.format == "svg":
            r.svg("{}/Rplots%03d.svg".format(self.directory), **kwdargs)
        elif self.format == "png":
            r.png("{}/Rplots%03d.png".format(self.directory), **kwdargs)
        elif self.format == "pdf":
            r.pdf("{}/Rplots%03d.pdf".format(self.directory), **kwdargs)
        else:
            raise Exception("Unknown image format:{}".format(format))

    def finish(self):
        if not self.running:
            return
        self.running = False
        r.devoff()
        
        if self.format == "pdf":
            pdfFiles = glob("{}/Rplots*pdf".format(self.directory))
            for pdfFile in pdfFiles:
                pdfdata = open(pdfFile, "rb").read()
                pdfdata = base64.b64encode(pdfdata)
                html = PDFOBJECTHTML.format(pdfdata=pdfdata)
                display_html(html, raw=True)
        else:
            if self.format == "svg":
                imageFiles = glob("{}/Rplots*svg".format(self.directory))
                image_type = 'image/svg+xml'
            elif self.format == "png":
                imageFiles = glob("{}/Rplots*png".format(self.directory))
                image_type = "image/png"
            images = [open(imgfile, 'rb').read() for imgfile in imageFiles]

            for image in images:
                # publish_display_data("biorpy", {image_type: image})
                publish_display_data({image_type: image})

        rmtree(self.directory)

iimage = InlineImage()


# # Switching to use IPython.lib.display.IFrame
# IFRAMEHTML = """<a href="{path}">{path}</a><br /><iframe name="myiframe" id="myiframe" src="{path}" height={height}px width=100%></iframe>"""

# # PDFOBJECTHTML = """<object data="data:application/pdf;base64,{pdfdata}" type="application/pdf" width="100%" height="200">
# #   alt : <a href="data/test.pdf">test.pdf</a>
# # <param name="view" value="FitH" />
# # </object>"""

# PDFOBJECTHTML = """<a href="data:application/pdf;base64,{pdfdata}" type="application/pdf" width="100%" height="200">
# {name}</a>"""

# class InlinePDF(object):
#     def __init__(self):
#         self.running = False

#     def __call__(self, path=None, **kwdargs):
#         if not self.running:
#             if path is None:
#                 raise Exception("Need to start InlinePDF first by passing the file path of the PDF to create.")
#             self.start(path, **kwdargs)
#         elif path is not None:
#             raise Exception("Need to finish InlinePDF by calling without a file path.")
#         else:
#             return self.finish()

#     def start(self, path, **kwdargs):
#         if self.running:
#             return
#         self.running = True
#         self.path = path
#         self.kwdargs = kwdargs

#         directory = os.path.dirname(path)
#         if directory and not os.path.exists(directory):
#             os.makedirs(directory)

#         r.pdf(path, **kwdargs)


#     def finish(self):
#         if not self.running:
#             return
#         self.running = False
#         r.devoff()

#         # this factor probably depends on browser
#         height = self.kwdargs.get("height", 7) * 100

#         imagesHtml = IFRAMEHTML.format(path=self.path, height=height)

#         h = imagesHtml

#         return HTML(h)
    
#         # return IFrame(self.path, height=height, width="100%")    

