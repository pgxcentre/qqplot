#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import os.path
import ctypes
import sys
import argparse
import re
import math
import gzip
import numpy as np

def main(args):
    import matplotlib as mpl
    if args.format != "X11" and mpl.get_backend() != "agg":
        mpl.use("Agg")
    import matplotlib.pyplot as plt
    if args.format != "X11":
        plt.ioff()

    # Read the file.
    observed = []
    
    # Configure the R Math library.
    rlib = ctypes.cdll.LoadLibrary(args.rlib)
    rlib.qbeta.restype = ctypes.c_double
    qbeta = lambda p, a, b: rlib.qbeta(ctypes.c_double(p), 
                                       ctypes.c_double(a),
                                       ctypes.c_double(b),
                                       0,
                                       0)

    # TODO: Handle les fichiers zippes
    # Read three bytes of the file to see if zipped.
    gzipped = False
    f = open(args.filename, 'rb')
    if f.read(3) == '\x1f\x8b\x08':
        # File is not zipped.
        gzipped = True
    f.seek(0)
    
    if gzipped:
        f.close()
        f = gzip.open(args.filename, 'rb') 
    
    header = f.readline()
    header = [re.sub(r"\r|\n", "", elem) for elem in header.split("\t")]
    if not args.col in header:
        raise Exception("Column '{0}' was not found.".format(args.col))
    col_id = header.index(args.col)
    for line in f:
        observed.append(float(line.split("\t")[col_id]))

    observed = np.array(observed, dtype=float)
    observed = np.sort(observed)
    # Compute -log_10(p_value)
    observed = -1 * np.log10(observed)

    expected = np.arange(1, len(observed) + 1, dtype=float)
    expected = -1 * np.log10(expected / len(observed))

    fig, axe = plt.subplots(1, 1)
    axe.plot(expected, observed, "o", ms=1, color='b')
    axe.set_xlabel(args.xlabel)
    axe.set_ylabel(args.ylabel)
    axe.set_title(args.title)
    # scipy.stats.beta.ppf(prb, a, b)
    c975 = np.zeros(len(observed))
    c025 = np.zeros(len(observed))

    for i in xrange(1, len(observed) + 1):
        c975[i - 1] = qbeta(0.975, i, len(observed) - i + 1)
        c025[i - 1] = qbeta(0.025, i, len(observed) - i + 1)
    
    c975 = -1 * np.log10(c975)
    c025 = -1 * np.log10(c025)
    axe.fill_between(expected, c025, c975, facecolor='#cccccc', edgecolor='#cccccc')

    if args.format == "X11":
        plt.show()
    else:
        if not re.search(r".+[.](pdf|ps|png)$", args.out):
            args.out = "{}.{}".format(args.out, args.format)
        plt.savefig(args.out, dpi=args.dpi, format=args.format)

    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                                            description = ("Help creating "
                                                           "beautiful graphs of "
                                                           "linkage results.")
                                    )

    parser.add_argument(
                            "--filename",
                            type=str,
                            help="Data file",
                            dest="filename",
                            metavar="DATA_FILE",
                            required=True
                       )

    parser.add_argument(
                            "--col",
                            type=str,
                            help="Column title to read data from",
                            dest="col",
                            metavar="COL_NAME",
                            default="P"
                       )

    parser.add_argument(
                            "--title",
                            type=str,
                            help="Title for the graph",
                            dest="title",
                            metavar="TITLE",
                            default=""
                       )

    parser.add_argument(
                            "--xlabel",
                            type=str,
                            help="Title for x axis",
                            dest="xlabel",
                            metavar="LABEL",
                            default="$-\\log_{10}(Expected)$"
                       )

    parser.add_argument(
                            "--ylabel",
                            type=str,
                            help="Title for y axis",
                            dest="ylabel",
                            metavar="LABEL",
                            default="$-\\log_{10}(Observed)$"
                       )

    parser.add_argument(
                            "--format",
                            type=str,
                            help="Output file format",
                            dest="format",
                            default="png",
                            choices=["png", "ps", "pdf", "X11"]
                       )

    parser.add_argument(
                            "--out",
                            type=str,
                            help="Output file name",
                            dest="out",
                            default="qqplot"
                       )

    parser.add_argument(
                            "--dpi",
                            type=int,
                            help="DPI of the exported image",
                            dest="dpi",
                            default=150
                       )

    parser.add_argument(
                            "--Rlib",
                            type=str,
                            help=("R math stand-alone C library (.so) "
                                  "to compute qbeta efficiently"),
                            dest="rlib",
                            metavar="RMath",
                            default=os.path.join(
                                os.path.dirname(__file__),
                                "libRmath.so"
                            )
                        )

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print "Interrupted by user"
        exit(0)
