# Small modification to pyminifakeDNS by Francisco Santos.
# There was a patch on dropbox that was used in REMnux. Patch is no longer there.
# Details: https://www.aldeid.com/wiki/PyminifakeDNS
# 
# Usage:
# Accepts the IP address to be used as a command line argument
# e.g. ~$ sudo python pyfakedns.py 10.1.1.1
# Original code: http://code.activestate.com/recipes/491264-mini-fake-dns-server/

import socket
import sys

if len(sys.argv) != 2:
	print "[+] Usage: sudo python pyfakedns.py 10.1.1.1"
	exit()

class DNSQuery:
  def __init__(self, data):
    self.data=data
    self.domain=''

    type = (ord(data[2]) >> 3) & 15   # Opcode bits
    if type == 0:                     # Standard query
      ini=12
      lon=ord(data[ini])
      while lon != 0:
        self.domain+=data[ini+1:ini+lon+1]+'.'
        ini+=lon+1
        lon=ord(data[ini])

  def answer(self, ip):
    packet=''
    if self.domain:
      packet+=self.data[:2] + "\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+='\xc0\x0c'                                             # Pointer to domain name
      packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
    return packet

if __name__ == '__main__':
  ip= sys.argv[1]

  try: 
    socket.inet_aton(ip)

  except socket.error:
    print '[!] Invalid IPv4 address supplied'
    print "[+] Usage: sudo python pyfakedns.py 10.1.1.1"
    exit()
  else:
  	print '[+] pyfakeDNS:: dom.query. 60 IN A %s' % ip
  
  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udps.bind(('',53))
  
  try:
    while 1:
      data, addr = udps.recvfrom(1024)
      p=DNSQuery(data)
      udps.sendto(p.answer(ip), addr)
      print 'answer: %s -> %s' % (p.domain, ip)
  except KeyboardInterrupt:
    print 'Exiting'
    udps.close()
