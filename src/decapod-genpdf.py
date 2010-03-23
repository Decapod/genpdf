#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import getopt


msg = '\nusage: python runPipeLine.py input file in pdf form \n\nworks iff "." only appears prior ext\nntake an input file and run ocropus clustering genPdf'

def main(sysargv):
    clustercommand = []
    pdfgencommand = []
    bookFileName = ""
    # parse command line options
    if len(sysargv) == 1:
        usage(sysargv[0])
        sys.exit(0)        
    try:
        optlist, args = getopt.getopt(sysargv[1:], 'hb:t:d:p:W:H:e:s:RCSv:r:', ['help','book=','type=','dir=','pdf=','width=','height=',"eps=","reps","remerge","enforceCSEG","seg2bbox",'verbose=','resolution='])
        #print(optlist, args)
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    # process options
    for o, a in optlist:
        if o in ("-h", "--help"):
            usage(sysargv[0])
            sys.exit(0)
        if o in ("-t", "--type"):
            pdfOutputType = int(a)
            pdfgencommand.append(" -t %d " % (pdfOutputType))
        if o in ("-W", "--width"):
            pageWidth = float(a)
            pdfgencommand.append(" -W %f " % (pageWidth))
        if o in ("-H", "--height"):
            pageHeight = float(a)
            pdfgencommand.append(" -H %f " % (pageHeight))
        if o in ("-d", "--dir"):
            bookDir = a
            # FIXME: check if this works as expected
            if (len(a)>0 and a[len(a)-1]!='/'):
                a = a+'/'
            pdfgencommand.append(" -d %s " % (bookDir))
            clustercommand.append(" -b %s " % (bookDir))
        if o in ("-p", "--pdf"):
            pdfFileName = a
            pdfgencommand.append(" -p %s " % (pdfFileName))
        if o in ("-v", "--verbose"):
            verbose = int(a)
            clustercommand.append(" -v %d " % (verbose))
            pdfgencommand.append(" -v %d " % (verbose))
        if o in ("-r", "--resolution"):
            dpi = int(a)
            pdfgencommand.append(" -r %d " (dpi))
        if o in ("-b", "--book"):
            bookFileName = a
        if o in ("-e","--eps"):
            eps = int(a)
            clustercommand.append(" -e %d " % (eps) )
        if o in ("-s","--reps"):
            reps = float(a)
            clustercommand.append( " -r %f " % (reps))
        if o in ("-R","--remerge"):
            clustercommand.append(" -R ")
        if o in ("-C","--enforceCSEG"):
            clustercommand.append(" -C ")
        if o in ("-S","--seg2bbox"):
            clustercommand.append(" -S ")  

    print "cluster command","".join(clustercommand)
    print "pdf command","".join(pdfgencommand)

    outputLog = str(bookFileName)+"-log"
    #directory = inputFile.split(".")[0]+"-book"
    #pdfOUT = inputFile.split(".")[0]+"-OUT.pdf"


    out = open(outputLog, 'w')

#First, we binarize and deskew the input images. This also copies them from their original form into a book-structured directory.
#$ ocropus-binarize -o book AIM-916/*.png
## loading AIM-916/img-000.png
#[info] got 1500 bboxes
## writing book/0001
## loading AIM-916/img-001.png
#[info] got 2023 bboxes
## writing book/0002
#...

#Next, we perform page layout analysis and textline extraction. Since the document is single column, we're using a single column layout analysis component. The "-D" flag means that we get a progress window that shows the result of segmentation, but it doesn't stop after each page.
#$ ocropus-pseg -S SegmentPageByRAST1 -D book/????.png
# loading book/0001.png
## loading book/0001.bin.png
## segmenting
## writing 26 lines
#...
#If you want to check line recognizers interactively, you can run ocropus-showlrecs. You can select different classifiers and language models, look at lines, and inspect the recognition process for individual lines.

#$ ocropus-showlrecs book/????/??????.png
#For actually running the recognition process, you use ocropus-linerec.
#$ ocropus-linerec -D book/????/??????.png
#Finally, you need to put together the outputs into an HTML file. The command for that will be ocropus-xhtml (it's not available yet).
#$ ocropus-xhtml book/???? > output.html

    #prep ocropus statements
    book2pages = "ocropus book2pages %s %s" % (bookDir,bookFileName)
    pages2lines = "ocropus pages2lines %s" % (bookDir) 
    lines2fsts = "ocropus lines2fsts %s" % (bookDir)
    fsts2text = "ocropus fsts2text %s" % (bookDir)

    #prep clustering statement
    clustercommand = "binned-inter %s" % ("".join(clustercommand))

    #prep pdf gen statement
    pdfcommand = "ocro2pdf.py %s" % ("".join(pdfgencommand))

    start = time.time()

    #run ocropus pipeline
    print "running ocropus pipeline"
    os.system(book2pages)
    os.system(pages2lines)
    os.system(lines2fsts)
    os.system(fsts2text)

    endOCROPUS = time.time()
    print >> out, "Time elapsed OCROPUS= ", endOCROPUS - start, "seconds"

    #run clustering
    # FIXME:check if this works
    if(type==3):
        print "running clustering"
        os.system(clustercommand)

    endClustering = time.time()
    print >> out, "Time elapsed clustering= ",endClustering - endOCROPUS, "seconds"

    #run pdf gen
    print "generating pdf"
    os.system(pdfcommand)
    endGenPDF = time.time()
    print >> out, "Time elapsed pdfGen= ",endGenPDF - endClustering, "seconds"
    print >> out, "total time elapsed =",endGenPDF - start,"seconds"


def usage(progName):
    print "\n%s [OPTIONS]\n\n"\
	  "   -b  --book	 name of multipage tiff file\n"\
          "   -d, --dir          Ocropus Directory to be converted\n"\
          "   -p, --pdf          PDF File that will be generated\n"\
          " Options:\n"\
          "   -h, --help:        print this help\n"\
          "   -v, --verbose:     verbose level [0,1,2,3]\n"\
          "   -t, --type:        type of the PDF to be generates:\n"\
          "                          1: image only [default]\n"\
          "                          2: recognized text overlaid with image\n"\
          "                          3: tokenized\n"\
          "   -W, --width:       width of the PDF page [in cm] [default = 21.0]:\n"\
          "   -H, --height:      height of the PDF page [in cm] [default = 29.7]:\n"\
          "   -r, --resolution:  resolution of the images in the PDF [default = 200dpi]\n"\
	  "   -R --remerge 	 remerge token clusters [default = false] \n"\
	  "   -S, --seg2bbox      suppresses generating files necessary to generate PDF \n"\
	  "   -C, --enforceCSEG   characters can only match if there CSEG labels are equal \n"\
          "   -e, --eps           matching threshold [default=7] \n"\
	  "   -s, --reps          matching threshold [default=.07] \n"\


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)


 