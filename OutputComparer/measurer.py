#!/usr/bin/python
import sys
#from ipaddress import IPv4Network,IPv6Network
import itertools
import io
from subprocess import PIPE,run
import tempfile
import argparse

from costfunc import *
from parsing import FlowEntry,parse


argprser = argparse.ArgumentParser(description="Analyze two agurim's outputs and match the packets between the two")
argprser.add_argument("truth",action='store',metavar="truth.agr",help="The ground truth aggregation file")
argprser.add_argument("tested",action='store',metavar="tested.agr",help="The aggregation file being tested against the G.T.")
argprser.add_argument("-c","--costfunc",action='store',choices=['cst','exp','squ','lin'],help="The cost function to use (default: linear).")
args = argprser.parse_args()

entries = []
truth_allintervals = []
tested_allintervals = []

parse(args.truth,entries,truth_allintervals)
parse(args.tested,entries,tested_allintervals)

costfunc = None
if args.costfunc == "cst":
    costfunc = cstcost
elif args.costfunc == "exp":
    costfunc = expcost
elif args.costfunc == "squ":
    costfunc = squarecost
else:
    costfunc = linecost




infinity = 0xFFFFFFFF

def onedcost(inpt,outpt):
    if inpt.overlaps(outpt):
        return costfunc(max(inpt.prefixlen - outpt.prefixlen, 0))
    else:
        return infinity


def twodcost(inpt,outpt):
    x = onedcost(inpt.src,outpt.src)
    y = onedcost(inpt.dst,outpt.dst)
    return x + y




infile = tempfile.TemporaryFile(mode='w+')

inputs = truth_allintervals[0]
outputs = tested_allintervals[0]
in_nbr = 0
out_nbr = 0
print(len(inputs),len(outputs),file=infile)

for p in inputs:
    in_nbr += p.bytes;
for p in outputs:
    out_nbr += p.bytes
delta = out_nbr - in_nbr
if delta != 0:
    print("Delta was: {}".format(delta))
    sys.exit(1)

for p in inputs:
    print(p.tag,p.bytes,sep=':',end=" ",file=infile)
print(file=infile)
for p in outputs:
    print(p.tag,p.bytes,sep=':',end=" ",file = infile)
print(file=infile)
for i in inputs:
    for o in outputs:
        c= twodcost(i,o)
        print(c,end=" ",file=infile)
        #print("{}->{} becomes {}->{} with cost {}".format(i.src,i.dst,o.src,o.dst,c))
print(file=infile)

infile.seek(0)

res = run("./tps",stdout=PIPE,stdin=infile,universal_newlines=True)
min_cost = int(res.stdout.split('\n')[0].split(":")[1])
print("Cost was {} err/Byte".format((min_cost)/max(in_nbr,out_nbr)))
for l in res.stdout.split('\n')[1:]:
    if (l == ""):
        break
    words = l.split(' ')
    inpt = entries[int(words[0])]
    outpt = entries[int(words[1])]
    quota = int(words[2])
    print("({ins},{ind}) ({ous},{oud}) {q}".format(ins=inpt.src.prefixlen - 96, ind=inpt.dst.prefixlen - 96, ous=outpt.src.prefixlen - 96, oud=outpt.dst.prefixlen - 96, q=quota))

