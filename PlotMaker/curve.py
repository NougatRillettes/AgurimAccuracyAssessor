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
args = argparser.parse_args()



def tuparse(s):
    return tuple(int(x) for x in s[1:-1].split(','))

for measfile_name in args.measfiles:
    measfile = open(measfile_name)
    counts = {}
    for l in list(measfile)[2:]:
        words = l.split(' ')
        ti = tuparse(words[0])
        to = tuparse(words[1])
        key = max(sum(ti)-sum(to),0)
        counts[key] = counts.get(key,0) + int(words[2])
    
    total = sum(counts.values()) 
    
    countsorted = sorted(counts.items(),reverse=True)
    x = [65]
    y = [1]
    acc = total
    for (diff,count) in countsorted:
        x.append(diff+1)
        y.append(acc/total)
        acc -= count
        x.append(diff+1)
        y.append(acc/total)
    plt.plot(x,y,label=measfile_name)


#mpl.rc('figure',figsize=(size,size))

plt.xticks(range(0,65,4))
plt.grid()
plt.legend(loc='lower right')
#plt.yscale('logit')

#plt.ylabel("Ground truth prefixes")
#plt.xlabel("Outputed prefixes")

#tag = "\n" + args.subtitle
    
#plt.title("" + tag)
#plt.savefig('.'.join(basename(args.measfile).split('.')[:-1]) +"_curve.png",dpi=80)
if args.show:
    plt.show()
