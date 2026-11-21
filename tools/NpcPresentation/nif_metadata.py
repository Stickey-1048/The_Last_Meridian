import struct
def nif(b):
 p=b.index(b'\n')+1;ver,endian,user,nb,bs=struct.unpack_from('<IBIII',b,p);p+=17;assert(ver,endian,user,bs)==(0x14020007,1,12,130)
 for _ in range(4):n=b[p];p+=1+n
 nt=struct.unpack_from('<H',b,p)[0];p+=2;types=[]
 for _ in range(nt):n=struct.unpack_from('<I',b,p)[0];p+=4;types.append(b[p:p+n].decode());p+=n
 ids=struct.unpack_from('<'+'H'*nb,b,p);p+=nb*2;sizes=struct.unpack_from('<'+'I'*nb,b,p);p+=nb*4;ns,maxs=struct.unpack_from('<II',b,p);p+=8;strings=[]
 for _ in range(ns):n=struct.unpack_from('<I',b,p)[0];p+=4;strings.append(b[p:p+n].decode());p+=n
 ng=struct.unpack_from('<I',b,p)[0];p+=4+ng*4;blocks=[]
 for t,size in zip(ids,sizes):blocks.append((types[t],b[p:p+size]));p+=size
 return blocks,strings
