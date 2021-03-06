#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import argparse
import re
import gzip

import numpy as np
import scipy.stats


def main(args):
    import matplotlib as mpl
    if args.format != "X11" and mpl.get_backend() != "agg":
        mpl.use("Agg")
    import matplotlib.pyplot as plt
    if args.format != "X11":
        plt.ioff()

    # Read the file.
    observed = []

    # Read three bytes of the file to see if zipped.
    gzipped = False
    f = open(args.filename, "rb")
    if f.read(3) == "\x1f\x8b\x08":
        # File is not zipped.
        gzipped = True
    f.seek(0)

    if gzipped:
        f.close()
        f = gzip.open(args.filename, "rb")

    header = f.readline()
    header = [re.sub(r"\r|\n", "", elem) for elem in header.split("\t")]
    if args.col not in header:
        raise Exception("Column '{0}' was not found.".format(args.col))
    col_id = header.index(args.col)
    for line in f:
        o = line.rstrip("\r\n").split("\t")[col_id]
        if o.upper() == "NA" or o.upper() == "NAN":
            continue
        observed.append(float(o))

    observed = np.array(observed, dtype=float)
    observed = np.sort(observed)
    # Compute -log_10(p_value)
    observed = -1 * np.log10(observed)

    n = len(observed) + 1
    expected = np.arange(1, n, dtype=float)
    qbeta = scipy.stats.beta.ppf
    c975 = -1 * np.log10(qbeta(0.975, expected, n - expected + 1))
    c025 = -1 * np.log10(qbeta(0.025, expected, n - expected + 1))

    expected = -1 * np.log10(expected / len(observed))

    # Some assertions
    assert np.min(expected) >= 0
    assert np.min(observed) >= 0

    fig, axe = plt.subplots(1, 1)
    axe.plot(expected, observed, "o", ms=1, mec=args.color, mfc=args.color)
    axe.set_xlabel(args.xlabel)
    axe.set_ylabel(args.ylabel)
    axe.set_title(args.title)

    axe.fill_between(expected, c025, c975, facecolor="#cccccc",
                     edgecolor="#cccccc")

    # Making sure the axis are not negative
    axe.set_xlim(0, axe.get_xlim()[1])
    axe.set_ylim(0, axe.get_ylim()[1])

    if args.format == "X11":
        plt.show()
    else:
        if not re.search(r".+[.](pdf|ps|png)$", args.out):
            args.out = "{}.{}".format(args.out, args.format)
        plt.savefig(args.out, dpi=args.dpi, format=args.format)

    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create uniform QQ plot for p-values."
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
        "--color",
        type=str,
        help="The color of the points",
        dest="color",
        default="#000000"
    )

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print "Interrupted by user"
        exit(0)
