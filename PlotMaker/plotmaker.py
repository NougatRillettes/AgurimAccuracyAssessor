#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import argparse
from os.path import basename

flows = set()
counts = {}
index = {}


argparser = argparse.ArgumentParser(description="Generates a graphical representation of a comparision between two outputs and saves it on disk")
argparser.add_argument("measfile",action='store',metavar="comparision.meas",help="The comparision file")
argparser.add_argument("subtitle",action='store',help="A subtitle for the plot",nargs='?',default='')
argparser.add_argument("-s","--show",action='store_true',help="Also displays the plot")
args = argparser.parse_args()



def tuparse(s):
    return tuple(int(x) for x in s[1:-1].split(','))

measfile = open(args.measfile)
for l in list(measfile)[2:]:
    words = l.split(' ')
    ti = tuparse(words[0])
    to = tuparse(words[1])
    flows.add(ti)
    flows.add(to)
    counts[(ti,to)] = counts.get((ti,to),0) + int(words[2])

flows = list(flows)
flows.sort(key=sum)

for (k,v) in enumerate(flows):
    index[v] = k


x= []
y = []
s = []

for (k,c) in counts.items():
    y.append(index[k[0]])
    x.append(index[k[1]])
    s.append(c)

ttal = sum(s) 
size = 0.3 * len(flows)
mpl.rc('figure',figsize=(size,size))
plt.scatter(x=x,y=y,s=[1200*x/ttal for x in s],label='Number of bytes (area)',marker='o',color='blue')

plt.xticks(range(len(flows)),flows,rotation='vertical')
plt.yticks(range(len(flows)),flows)
plt.grid()

costx = []
costy = []
costs = []
for (y,fi) in enumerate(flows):
    for (x,fo) in enumerate(flows):
        if y > x:
            costs.append(150*(max(sum(fi)-sum(fo),0)**2/64**2))
            costx.append(x)
            costy.append(y)

plt.scatter(x=costx,y=costy,s=costs,marker='+',color='red',alpha=0.5,label='Cost (height)')

plt.ylabel("Ground truth prefixes")
plt.xlabel("Outputed prefixes")

tag = "\n" + args.subtitle
    
plt.plot([-1,len(flows)],[-1,len(flows)],color='black',linestyle='-',linewidth=0.25)
plt.title("Approximation of ground truth for each byte" + tag)
#plt.legend(('circle','cross'),("Number of bytes (area)","Cost (height)"))
plt.legend(loc='lower right',scatterpoints=1)
plt.savefig('.'.join(basename(args.measfile).split('.')[:-1]) +".png",dpi=80)
if args.show:
    plt.show()
