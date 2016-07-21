#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import argparse
from os.path import basename

index = {}


argparser = argparse.ArgumentParser(description="Generates a graphical representation of multiple comparision of different outputs to the same ground truth and saves it to the disk.")
argparser.add_argument("measfiles",action='store',metavar="comparision.meas",help="The comparision files",nargs='+')
#argparser.add_argument("subtitle",action='store',help="A subtitle for the plot",nargs='?',default='')
argparser.add_argument("-s","--show",action='store_true',help="Also displays the plot")
argparser.add_argument("-t","--type",choices=['cdf','cost'],action='store',default='cdf',help="Set the curve type (efault: cdf)")
argparser.add_argument("-o",help="Name of file to save to.",default="out.png")
args = argparser.parse_args()



def tuparse(s):
    return tuple(int(x) for x in s[1:-1].split(','))

for measfile_name in args.measfiles:
    measfile = open(measfile_name)
    counts = {65: 0}
    for l in list(measfile)[2:]:
        words = l.split(' ')
        ti = tuparse(words[0])
        to = tuparse(words[1])
        key = max(sum(ti)-sum(to),0)
        counts[key] = counts.get(key,0) + int(words[2])
    
    
    countsorted = sorted(counts.items())
    totalbytes = sum(counts.values())
    
    x = []
    y = []
    acc = 0
    for (diff,count) in countsorted:
        if diff != 0:
            x.append(diff)
            y.append(acc/totalbytes)
        if args.type == 'cdf':
            acc += count
        else:
            acc += count*diff
        x.append(diff)
        y.append(acc/totalbytes)
    plt.plot(x,y,label=measfile_name)


#mpl.rc('figure',figsize=(size,size))

plt.xticks(range(0,65,4))
plt.xlim([0,64])
plt.grid()
if args.type == 'cdf':
    plt.legend(loc='lower right')
else:
    plt.legend(loc='upper left')
#plt.yscale('logit')

if args.type == 'cdf':
    plt.ylabel("Proportion of bytes with an offset least or equal")
else:
    plt.ylabel("Cost caused by bytes with an offset least or equal")
plt.xlabel("Prefix length offset")

#tag = "\n" + args.subtitle
    
if args.type == 'cdf':
    plt.title("Cumulative distribution of prefixes offset")
else:
    plt.title("Cumulative cost by prefixes offset")

file_suffix = 'cdf' if args.type == 'cdf' else 'cost_curve'

plt.savefig(args.o,dpi=80)
if args.show:
    plt.show()
