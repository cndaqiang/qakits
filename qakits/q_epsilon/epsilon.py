import os
import numpy as np
class epsilon:
    def __init__(self,file_end="pwscf.dat",file_prefix=""):
        self.epsr=self.readfile(file_prefix+"epsr_"+file_end)
        self.epsi=self.readfile(file_prefix+"epsi_"+file_end)
        self.ieps=self.readfile(file_prefix+"ieps_"+file_end)
    #
    def readfile(self,filename=""):
       if not os.path.isfile(filename):
          print("Can't find "+filename)
          exit()
       f=open(filename)
       dat=f.readlines()
       f.close()
       i=0
       for i in np.arange(len(dat)):
          info=dat[i].strip()
          if len(info) == 0: continue
          if '#' == info[0]: continue
          break
       dat=dat[i:]
       colnums=len(dat[0].split())
       npda=np.zeros([len(dat),colnums])
       for i in np.arange(len(dat)):
          try:
            npda[i]=np.array([ float(x) for x in dat[i].split()[:colnums] ])
          except:
             print("Error in read "+filename+" at "+dat[i])
             exit()
       return npda
    def returnepsilon(self,eps=None):
       return eps if eps else [self.epsr, self.epsi]
    #
    def sqrt_epsilon(self,eps=None):
       """
       \sqrt(\epsilon)
       n=\sqrt(\frac{\sqrt(e_1^2+e_2^2)+e_1}{2})
       k=\sqrt(\frac{\sqrt(e_1^2+e_2^2)-e_1}{2})
       """
       eps=self.returnepsilon(eps)
       epsr=eps[0]
       epsi=eps[1]
       sqrt=np.sqrt(np.square(epsr)+np.square(epsi))
       n=np.sqrt(0.5*(sqrt+epsr))
       k=np.sqrt(0.5*(sqrt-epsr))
       return n,k
    # reflectivity 
    def eps2reflect(self,eps1=1,eps=None):
       """
       R=\frac{N1-N2}{N1+N2}^2
       n1 for vacuum (or air), which is close to 1
       """
       eps=self.returnepsilon(eps)
       n,k=self.sqrt_epsilon(eps)
       if eps1 == 1:
          n1=1
          k1=0
       else:
          n1,k1=self.sqrt_epsilon(eps1)
       N=n+k*1j
       N1=n1+k1*1j
       Ru=N1-N
       Rd=N1+N
       R=np.square(np.abs(Ru)/np.abs(Rd))
       return R