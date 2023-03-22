dataplot.py
===========
Plot numerical data found in human readable weakly formatted logfiles.

This program extracts numerical data from arbitrary text files, typically
logfiles. It plots the data in a graph which is written to a file in
PNG/JPG/PDF format (really anything supported by matplotlib).

Input lines are first optionally filtered with `--filter`. Each line forms a
data row. Numeric values in each line are extracted using a regex
(`--num-regex`). The X and Y values of each record are extracted from fixed
columns specified by `--xcol` and `--ycol`, respectively. When `--xcol` is not
specified the row index (the line number in the file after filtering) is used
as X value.

Example: Plotting roundtrip times of ping:

```
sudo ping example.com -c 1000 -i 0.001 > log.txt  
dataplot.py -f time= -x 2 -y 4 -s . log.txt -o log.png  
```

Try adding --sort.

Help message
------------
This help message may be outdated. Use `dataplot.py --help` to get an up-to-date help.

```
> dataplot.py --help

positional arguments:
  FILES               Files to process.

optional arguments:
  -h, --help          show this help message and exit
  --version           show program's version number and exit
  -o F, --outfile F   Output image. Default is 'out.png'. PNG, JPG, PDF and
                      others are supported.
  -x N, --xcol N      X column. Use -1 for 'index' (if no X column is present
                      in file).
  -y N, --ycol N      Y column. Use -vv to figure out column indices of data.
  -c C, --colors C    Set colors. One character per graph. Try rbyg.
  -s S, --shapes S    Set dot shapes (try oO.,+x).
  -a S, --addstyle S  Add additional style to all graphs (use -a - to add
                      lines).
  -f RE, --filter RE  Only use lines which match regex RE.
  --num-regex RE      Regex used to extrat numeric values in line.
  --xlog              Use logscale for X.
  --xdiv N            Divide X values by N (float).
  --ymax MAX          Set Y range to MAX (float).
  --ymin MIN          Set Y range to MIN (float).
  --ylog              Use logscale for Y.
  --sort              Sort Y values. Only makes sense without --xcol.
  --hist B            Build histogram over data with the specified binsize B.
                      Try --bar and --alpha 0.5.
  --legend POS        Set legend position (default "upper left").
  --bar               Draw filled bars.
  --alpha ALPHA       Set transparency. Useful for --bar with multiple plots.
  --fig-width W       Width of output image in inch at 100 dpi.
  --fig-height H      Height of output image in inch at 100 dpi.
  --print-high N      Print lines with Y values higher than N.
  --print-stats       Print statistics of all Y values.
  -v, --verbose       Be more verbose.

dataplot.py version 0.2.1 *** Copyright (c) 2010-2023 Johannes Overmann ***
https://github.com/jovermann/dataplot
```

Installation
------------

`dataplot.py` depends on the following:

* Python 3
	* Version 0.2.2 tested with Python 2.7.18, 3.8.2, 3.9.10 and 3.11.1.
* `matplotlib` Python module

Usually you can install `matplotlib` by doing `pip3 install matplotlib`. On my Mac that failed, because it installed `matplotlib` for the system Python 3.8, and not for the Python 3.9 on my path which I installed using Mac ports. To install modules for the Python interpreter on your path use the Python interpreter to execute pip:

`python3 -m pip install matplotlib`

This worked well for me.
