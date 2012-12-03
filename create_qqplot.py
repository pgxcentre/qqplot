#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import re
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats as stats

def main(args):
    # Read the file.
    observed = []
    # TODO: Handle les fichiers zippes
    with open(args.filename, 'rb') as f:
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
    # c975 = []
    # c025 = []

    # for i in xrange(1, len(observed) + 1):
    #     if i % 1000 == 0:
    #         print "Long {}".format(i)
    #     #FIXME
    #     c975.append(stats.beta.ppf(0.975, i, len(observed) - i + 1))
    #     c025.append(stats.beta.ppf(0.025, i, len(observed) - i + 1))
    # axe.fill_between(expected, c025, c975)
    plt.ioff()
    plt.show()


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
                            default="Expected $-log_{10}(p)$"
                       )

    parser.add_argument(
                            "--ylabel",
                            type=str,
                            help="Title for y axis",
                            dest="ylabel",
                            metavar="LABEL",
                            default="Observed $-log_{10}(p)$"
                       )
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print "Interrupted by user"
        exit(0)
