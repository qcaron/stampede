# What you can achieve with Stampede
Stampede can stamp your PDF evidences in order to file them. Choose a PDF file as input and three outputs will be generated:
    1. A series of image files: one stamped TIFF image for each and every page of the PDF
    2. The stamped PDF (named after the first page' stamp)
    3. A raw text file containing the PDF text (named after the first page' stamp)
  
# How you can use, redistribute and modify Stampede:
License is GPL License v3: it is intended to remain a free open-source software to help both defense and prosecution teams in filing evidences during trial. Moreover, texts extracted from PDF files uses pdftotext from xPDF. xPDF cannot only be redistributed with GPL License.

# Stampede' story:
This project is based on inputs from a defense team member working at the ICC - CPI based in The Hague, Netherlands.

Stampede name is inspired from Vash The Stampede — Trigun. Wherever he goes, Vash only leaves ruins behind him and so has a price put on his head. Even if Vash seems to be guilty, he should have the right for a fair trial. And so is anyone who is subject to trial.

# Roadmap
* Make the TIFF IMAGE_DENSITY a parameter that can be modified by the user 
* Use MVC paradigm for the GUI (using Tkinter)
* Provide a "help" content and "about" content as sub windows
* Make it work on Unix and Windows (currently manually tested on Mac OS X)
* Implement unit tests
* Use py2exe or similar tool to build a software to be downloaded
* Let user customize stamp to support various patterns
* Support different input files maybe: video, images, transcripts?
