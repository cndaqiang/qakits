import os
import numpy as np
class epsilon:
    def __init__(self,file_end="pwscf.dat",file_prefix="",xlim=None):
        self.epsr=self.readfile(file_prefix+"epsr_"+file_end)
        self.energy=self.epsr[:,0]
        self.epsr=self.epsr[:,1:]
        self.epsi=self.readfile(file_prefix+"epsi_"+file_end)[:,1:]
        self.ieps=self.readfile(file_prefix+"ieps_"+file_end)[:,1:]
        self.eels=self.readfile(file_prefix+"eels_"+file_end)[:,1:]
        if xlim:
            _x,self.epsr=self.cuteps(xlim=xlim,y=self.epsr)
            _x,self.epsi=self.cuteps(xlim=xlim,y=self.epsi)
            _x,self.ieps=self.cuteps(xlim=xlim,y=self.ieps)
            _x,self.eels=self.cuteps(xlim=xlim,y=self.eels)
            self.energy=_x
        # eV 2 mnm
        self.energy_nm=1239.8/(1e-15+self.energy)
        self.refl=self.eps2reflect()
        
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
       return eps if eps is not None else [self.epsr, self.epsi]
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
    # 截断能量范围
    def cuteps(self,xlim=[0.5,3],x=None,y=None):
        x = x if x is not None else self.energy
        y = y if y is not None else self.epsr
        
        # 检查 x 是否为一维数组，y 是否为二维数组
        if x.ndim != 1 or y.ndim != 2:
            raise ValueError("x should be a 1-dimensional array and y should be a 2-dimensional array")
        
        # 检查 x 和 y 的第一维度长度是否相同
        if x.shape[0] != y.shape[0]:
            raise ValueError("The first dimension of x and y should match")
        
        # 使用布尔索引选择 x 在 xlim 范围内的元素
        mask = (x >= xlim[0]) & (x <= xlim[1])
        
        # 使用 mask 来选择 y 中对应的行
        selected_x = x[mask]
        selected_y = y[mask, :]
        
        # 返回选择后的 x 和 y
        return selected_x, selected_y        





