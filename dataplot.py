#!/usr/bin/env python3

import optparse
import matplotlib.pylab as pylab
import matplotlib.pyplot as pyplot
import numpy
import math
import sys
import locale
import re

options = None

def main():
    """Main entry point.
    """
    global options
    usage = "Usage: %prog [options] FILES..."
    version = "0.1.4"
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option("-o", "--outfile", default="out.png", type="string", help="Output image. Default is 'out.png'. PNG, JPG, PDF and others are supported.", metavar="FILE")
    parser.add_option("-x", "--xcol", default=-1, type="int", help="X column. Use -1 for 'index' (if no X column is present in file).", metavar="N")
    parser.add_option("-y", "--ycol", default=1, type="int", help="Y column. Use -v to first to figure out column indices of data.", metavar="N")
    parser.add_option("-c", "--colors", default="rbyg", help="Set colors. One character per graph. Try rbyg.", metavar="COLSTR")
    parser.add_option("-s", "--shapes", default="o", help="Set Dot shapes (try oO.,+x).", metavar="SHAPESTR")
    parser.add_option("-a", "--addstyle", default="", help="Add additional style to all graphs (use -a - to add lines).", metavar="STYLE")
    parser.add_option("-f", "--filter", default="", help="Only use lines which match regex RE.", metavar="RE")
    parser.add_option(      "--xlog", default=False, action="store_true", help="Use logscale for X.")
    parser.add_option(      "--xdiv", default=1.0, type="float", help="Divide X values by N (float).", metavar="N")
    parser.add_option(      "--ymax", default=0, type="float", help="Set Y range to MAX (float).", metavar="MAX")
    parser.add_option(      "--ymin", default=0, type="float", help="Set Y range to MIN (float).", metavar="MIN")
    parser.add_option(      "--ylog", default=False, action="store_true", help="Use logscale for Y.")
    parser.add_option(      "--sort", default=False, action="store_true", help="Sort Y values. Only makes sense without --xcol.")
    parser.add_option(      "--legend", default="upper left", help="Set legend position (default \"upper left\").", metavar="POS")
    parser.add_option(      "--fig-width", default=15, type="float", help="Width of output image in inch at 100 dpi.", metavar="W")
    parser.add_option(      "--fig-height", default=5, type="float", help="Height of output image in inch at 100 dpi.", metavar="H")
    parser.add_option(      "--print-high", default=0, type="float", help="Print lines with Y values higher than N.", metavar="N")
    parser.add_option(      "--print-stats", default=False, action="store_true", help="Print statistics of all Y values.")
    parser.add_option("-v", "--verbose", default=0, action="count", help="Be more verbose.")
    (options, args) = parser.parse_args()

    # Check args.
    if len(args) < 1:
        parser.error("Please specify at least one file!");
    infile = args[0]

    pyplot.figure(figsize = (options.fig_width, options.fig_height))

    # Plot files
    fileindex = 0
    index = 0
    total_y = 0
    for infile in args:
        with open(infile) as file:
            lines = file.readlines()
        if options.filter:
            lines = [l for l in lines if re.search(options.filter, l) != None]
        xx = []
        yy = []
        for line in lines:
            data = re.findall("[+-]?[0-9.]+", line);
            if options.verbose:
                print(["[{}]={}".format(i, data[i]) for i in range(len(data))])
            if options.xcol >= len(data) or options.ycol > len(data):
                print("Ignoring short line: '{}'".format(line.strip()))
                continue
            x = index
            if options.xcol >= 0:
                x = float(data[options.xcol])
            x = x / options.xdiv
            y = float(data[options.ycol])
            if options.print_high and (y >= options.print_high):
                sys.stdout.write(line)
            #y = x + y
            xx.append(x)
            yy.append(y)
            index += 1
            total_y += y

        if options.sort:
            yy = sorted(yy)

        color = options.colors[fileindex % len(options.colors)]
        shape = options.shapes[fileindex % len(options.shapes)]
        pyplot.plot(xx, yy, color + shape + options.addstyle, label = infile)
        fileindex += 1

    if options.xlog:
        pyplot.xscale("log")
    if options.ylog:
        pyplot.yscale("log")
    if options.ymax != 0.0 or options.ymin != 0.0:
        pyplot.ylim([options.ymin, options.ymax])
    pyplot.legend(loc = "upper left")

    if options.print_stats:
        print("Sum={:.1f}, average={:.1f}".format(total_y, total_y / index))

    # Save image
    if options.verbose:
        print("Saving image to '{}'".format(options.outfile))
    pyplot.savefig(options.outfile, bbox_inches='tight', dpi=128)


# call main()
if __name__ == "__main__":
    main()

