#!/usr/bin/python
import sys
import re
import json
from ipaddress import IPv4Network,IPv6Network
import itertools
import io
from subprocess import PIPE,run
import tempfile

class FlowEntry:
    def __init__(self,src,dst,count,tag):
        self.src=src
        self.dst=dst
        self.bytes=count
        self.tag=tag

    def __str__(self):
        return str(self.src) + " -> " + str(self.dst) + ": " + str(self.bytes)

ip6net_reg = r"(([a-fA-F0-9]?:)+)"
ip4net_reg = r"([0-9]+ (?:\. [0-9]*){3})"
addr_reg = r"((("+ip4net_reg+"|"+ip6net_reg+")(/[0-9]*)?)|(\*(::)?))"
regexp = re.compile(r"""  
    ^ 
    \[ \s* [0-9]* \] \s+ #Line Number
    (?P<src>""" + addr_reg + r""") #src IP
    \s
    (?P<dst>""" + addr_reg + r""") #dst IP
    :\s
    (?P<bytes>[0-9]*)
    [^)]* \) \s
    (?P<pck>[0-9]*)
    """, re.X)

sep_reg = re.compile(r"""%!AGURI-2\.0""")

compiled_ip4net = re.compile(ip4net_reg, re.X)

cut = 32 if len(sys.argv) <= 3 else int(sys.argv[3])
cut += 96

entries = []

def address_convert_uncut(s):
    if s=="*":
        return IPv6Network("::ffff:0:0/96")
    elif s=="*::":
        return IPv6Network("::/0")
    elif compiled_ip4net.match(s):
        n = IPv4Network(s)
        return IPv6Network((bytes(10)+b'\xff\xff'+n.network_address.packed,96+n.prefixlen))
    else:
        return IPv6Network(s)
def address_convert(s):
    net = address_convert_uncut(s)
    if net.prefixlen <= cut:
        return net
    else:
        return net.supernet(new_prefix=cut)


#parses output
int_outputs = []
with open(sys.argv[1]) as f:
    i = -1
    for l in f:
        m = regexp.match(l)
        if m:
            g = m.groupdict()
            entry = FlowEntry(
                        address_convert_uncut(g['src']),
                        address_convert_uncut(g['dst']),
                        int(g['bytes']),
                        len(entries)
                        )
            int_outputs[i].append(entry)
            entries.append(entry)
        elif sep_reg.match(l):
            i+=1
            int_outputs.append([])

int_inputs = []
with open(sys.argv[2]) as f:
    i = -1
    for l in f:
        m = regexp.match(l)
        if m:
            g = m.groupdict()
            entry = FlowEntry(
                        address_convert(g['src']),
                        address_convert(g['dst']),
                        int(g['bytes']),
                        len(entries)
                        )
            int_inputs[i].append(entry)
            entries.append(entry)
        elif sep_reg.match(l):
            i+=1
            int_inputs.append([])

infinity = 0xFFFFFFFF

def linecost(x):
    return x
def cstcost(x):
    if x:
        return 1
    else:
        return 0
def expcost(x):
    if x:
        return 2**x
    else:
        return 0
def squarecost(x):
    if x:
        return x*x
    else:
        return 0
costfunc = linecost

if len(sys.argv) > 4:
    arg = sys.argv[4]
    if arg == "cst":
        costfunc = cstcost
    elif arg == "exp":
        costfunc == expcost
    elif arg == "squ":
        costfunc = squarecost

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

inputs = int_inputs[0]
outputs = int_outputs[0]
in_nbr = 0
out_nbr = 0
print(len(inputs),len(outputs),file=infile)

for p in inputs:
    in_nbr += p.bytes;
for p in outputs:
    out_nbr += p.bytes
delta = out_nbr - in_nbr
print("Delta was: {}".format(delta))
if delta != 0:
    sys.exit(1)

for p in inputs:
    print(p.tag,p.bytes,sep=':',end=" ",file=infile)
#print(max(delta,0),file=infile)
print(file=infile)
for p in outputs:
    print(p.tag,p.bytes,sep=':',end=" ",file = infile)
#print(max(-delta,0),file=infile)
print(file=infile)
for i in inputs:
    for o in outputs:
        c= twodcost(i,o)
        print(c,end=" ",file=infile)
        #print("{}->{} becomes {}->{} with cost {}".format(i.src,i.dst,o.src,o.dst,c))
print(file=infile)

infile.seek(0)

res = run("./tps",stdout=PIPE,stdin=infile,universal_newlines=True)
#print(res.stdout)
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

