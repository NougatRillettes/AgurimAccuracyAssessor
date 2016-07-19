import re

from ipaddress import IPv4Network,IPv6Network

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

def parse(fName,allParsed,currentParsed):
    with open(fName) as f:
        i = -1
        for l in f:
            m = regexp.match(l)
            if m:
                g = m.groupdict()
                entry = FlowEntry(
                            address_convert_uncut(g['src']),
                            address_convert_uncut(g['dst']),
                            int(g['bytes']),
                            len(allParsed)
                            )
                currentParsed[i].append(entry)
                allParsed.append(entry)
            elif sep_reg.match(l):
                i+=1
                currentParsed.append([])






