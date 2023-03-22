#!/usr/bin/env python3
#
# dataplot.py - Plot numerical data extracted from logfiles.
#
# Copyright (c) 2010-2023 Johannes Overmann
#
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE or copy at https://www.boost.org/LICENSE_1_0.txt)
#
# This works with Python 2.7 and 3.x.

import argparse
import matplotlib.pyplot as pyplot
import numpy
import math
import sys
import locale
import re

version = "0.2.2"

options = None

def calcHistogram(yy, binsize):
    """Calculate histogram of yy values.
    Return (xx, yy) where xx is the start of each bin and yy the number of items in the bin.
    """
    hist = {}
    for y in yy:
        bin = y // binsize
        if bin in hist:
            hist[bin] += 1
        else:
            hist[bin] = 1
    xxout = []
    yyout = []
    for key, value in sorted(hist.items()):
        xxout.append(key * binsize)
        yyout.append(value)
    return (xxout, yyout)


def main():
    """Main entry point.
    """
    global options
    usage = """%(prog)s [options] FILES...

This program extracts numerical data from arbitrary text files, typically
logfiles. It plots the data in a graph which is written to a file in
PNG/JPG/PDF format.
Input lines are first optionally filtered with --filter. Each line forms a
data row. Numeric values in each line are extracted using a regex
(--num-regex). The X and Y values of each record are extracted from fixed
columns specified by --xcol and --ycol, respectively. When --xcol is not
specified the row index (the line number in the file after filtering) is used
as X value.

Example: Plotting roundtrip times of ping:
    sudo ping example.com -c 1000 -i 0.001 > log.txt
    dataplot.py -f time= -x 2 -y 4 -s . log.txt -o log.png
    Try adding --sort.
"""
    parser = argparse.ArgumentParser(usage = usage, epilog ="%(prog)s version {} *** Copyright (c) 2010-2023 Johannes Overmann *** https://github.com/jovermann/dataplot".format(version))
    parser.add_argument(      "--version", action="version", version=version)
    parser.add_argument("FILES", nargs="*", help="Files to process.")
    parser.add_argument("-o", "--outfile", default="out.png", help="Output image. Default is 'out.png'. PNG, JPG, PDF and others are supported.", metavar="F")
    parser.add_argument("-x", "--xcol", default=-1, type=int, help="X column. Use -1 for 'index' (if no X column is present in file).", metavar="N")
    parser.add_argument("-y", "--ycol", default=[], action="append", help="Y column. Use -vv to figure out column indices of data.", metavar="N")
    parser.add_argument("-c", "--colors", default="rbyg", help="Set colors. One character per graph. Try rbyg.", metavar="C")
    parser.add_argument("-s", "--shapes", default="o", help="Set dot shapes (try oO.,+x).", metavar="S")
    parser.add_argument("-a", "--addstyle", default="", help="Add additional style to all graphs (use -a - to add lines).", metavar="S")
    parser.add_argument("-f", "--filter", default="", help="Only use lines which match regex RE.", metavar="RE")
    parser.add_argument(      "--num-regex", default="[+-]?[0-9.]+", help="Regex used to extrat numeric values in line.", metavar="RE")
    parser.add_argument(      "--xlog", default=False, action="store_true", help="Use logscale for X.")
    parser.add_argument(      "--xdiv", default=1.0, type=float, help="Divide X values by N (float).", metavar="N")
    parser.add_argument(      "--ymax", default=0, type=float, help="Set Y range to MAX (float).", metavar="MAX")
    parser.add_argument(      "--ymin", default=0, type=float, help="Set Y range to MIN (float).", metavar="MIN")
    parser.add_argument(      "--ylog", default=False, action="store_true", help="Use logscale for Y.")
    parser.add_argument(      "--sort", default=False, action="store_true", help="Sort Y values. Only makes sense without --xcol.")
    parser.add_argument(      "--hist", default=0, type=float, help="Build histogram over data with the specified binsize B. Try --bar and --alpha 0.5.", metavar="B")
    parser.add_argument(      "--legend", default="upper left", help="Set legend position (default \"upper left\").", metavar="POS")
    parser.add_argument(      "--bar", action="store_true", help="Draw filled bars.")
    parser.add_argument(      "--alpha", default=1.0, type=float, help="Set transparency. Useful for --bar with multiple plots.")
    parser.add_argument(      "--fig-width", default=15, type=float, help="Width of output image in inch at 100 dpi.", metavar="W")
    parser.add_argument(      "--fig-height", default=5, type=float, help="Height of output image in inch at 100 dpi.", metavar="H")
    parser.add_argument(      "--print-high", default=0, type=float, help="Print lines with Y values higher than N.", metavar="N")
    parser.add_argument(      "--print-stats", default=False, action="store_true", help="Print statistics of all Y values.")
    parser.add_argument("-v", "--verbose", default=0, action="count", help="Be more verbose.")
    options = parser.parse_args()

    if len(options.FILES) == 0:
        parser.error("Please specify at least one file!")

    # Parse ycols.
    ycols = []
    ycolnames = []
    if len(options.ycol) == 0:
        options.ycol = ["0"]
    for i in range(len(options.ycol)):
        fields = options.ycol[i].split("=", 1)
        if len(fields) == 1:
            ycolnames.append("{}".format(options.ycol[i]))
            ycols.append(int(fields[0]))
        else:
            ycolnames.append(fields[0])
            ycols.append(int(fields[1]))
    options.ycol = ycols

    pyplot.figure(figsize = (options.fig_width, options.fig_height))

    # Plot files
    graphindex = 0
    index = 0
    total_y = 0
    for infile in options.FILES:
        if options.verbose:
            print("Reading file '{}'.".format(infile))
        with open(infile) as file:
            lines = file.readlines()
        if options.filter:
            lines = [l for l in lines if re.search(options.filter, l) != None]
        xx = []
        yy = []
        for i in options.ycol:
            yy.append([])
        for line in lines:
            data = re.findall(options.num_regex, line);
            if options.verbose >= 2:
                print(", ".join(["{}={}".format(i, data[i]) for i in range(len(data))]))
            if options.xcol >= len(data) or max(options.ycol) > len(data):
                print("Ignoring short line: '{}'.".format(line.strip()))
                continue
            x = index
            if options.xcol >= 0:
                x = float(data[options.xcol])
            x = x / options.xdiv
            xx.append(x)
            for i in range(len(yy)):
                y = float(data[options.ycol[i]])
                if options.print_high and (y >= options.print_high):
                    sys.stdout.write(line)
                yy[i].append(y)
                total_y += y
            index += 1

        for i in range(len(yy)):
            xxplot = xx
            yyplot = yy[i]
            if options.sort:
                yyplot = sorted(yyplot)
            if options.hist > 0:
                (xxplot, yyplot) = calcHistogram(yyplot, options.hist)

            color = options.colors[graphindex % len(options.colors)]
            shape = options.shapes[graphindex % len(options.shapes)]
            label = infile
            if len(yy) > 1 or (ycolnames[i] != "{}".format(options.ycol[i])):
                label += "/" + ycolnames[i]
            if options.bar:
                pyplot.bar(xxplot, yyplot, alpha=options.alpha, color=color, edgecolor=color, width=0.8*options.hist, label = label)
            else:
                pyplot.plot(xxplot, yyplot, color + shape + options.addstyle, alpha=options.alpha, label = label)
            graphindex += 1

    if options.xlog:
        pyplot.xscale("log")
    if options.ylog:
        pyplot.yscale("log")
    if options.ymax != 0.0 or options.ymin != 0.0:
        pyplot.ylim([options.ymin, options.ymax])
    pyplot.grid(color="lightgray", linestyle=":")
    pyplot.legend(loc = "upper left")

    if options.print_stats:
        print("Sum={:.1f}, average={:.1f}.".format(total_y, total_y / index))

    # Save image
    if options.verbose:
        print("Saving image to '{}'.".format(options.outfile))
    pyplot.savefig(options.outfile, bbox_inches='tight', dpi=128)


# call main()
if __name__ == "__main__":
    main()

