# -*- coding: utf-8 -*-
"""
Created on Wed Jul 3 09:14:00 2019

@author: cndaqiang
"""
import numpy as np
import os
import sys


# cell[abc,xyz]
# 坐标 xyz[nstep,ntype,nat,xyz]
def readposcar(poscar,dnstep=1):
    f=open(poscar,'r')
    f.readline()
    alat=float(f.readline().split()[0])
    cell=np.zeros([3,3])
    for i in np.arange(3):
        cell[i,0:3] = [ float(x) for x in f.readline().split()[0:3] ]
    if np.abs(cell).sum()-np.abs( [ cell[0,0], cell[1,1], cell[2,2] ] ).sum() > 1E-8:
      cubic=False
    else:
      cubic=True
    cell=cell*alat
    #元素
    ntyp=np.array(f.readline().split())
    nat=np.array(f.readline().split())
    totaltype=min(ntyp.size,nat.size)
    ntyp=ntyp[0:totaltype].copy()
    nat=nat[0:totaltype].copy().astype(int)
    #坐标类型
    xyztype=f.readline().split()[0]
    #
    #nstep
    natmax=int(np.max(nat))
    natoms=int(nat.sum())
    header=8
    # 替代 os.popen('wc -l ' + poscar)
    with open(poscar, 'r') as ftmp:
        rownum = sum(1 for _ in ftmp)  # 逐行遍历并计数
    #rownum=len(f.readlines())#总行数
    if rownum%(natoms+header) == 0:
        nstep=int(rownum/(natoms+header))  #每个xyz单元,2个
    else:
        print(poscar+", rownum can't be split by natoms + header",rownum,natoms+header)
        nstep=int(rownum/(natoms+header))  #每个xyz单元,2个
    #读坐标
    #======
    xyz=np.zeros([nstep,totaltype,natmax,3]) #步数,元素,原子编号,xyz
    ierror=f.seek(0,0)
    istep=-1
    for istep_all in np.arange(nstep):
        if istep_all%dnstep != 0:
            for i in np.arange(int(natoms+header)) : f.readline()
            continue
        istep=istep+1
        for i in np.arange(header): f.readline()
        for itype in np.arange(totaltype):
            for i in np.arange(nat[itype]):
                xyz[istep,itype,i,0:3]=[ float(x) for x in f.readline().split()[0:3] ]
    #计算坐标
    if xyztype[0] == 'D' or xyztype[0] == 'd':
        Dxyz=xyz.copy()
        for d in np.arange(3):
            if cubic:
              xyz[:,:,:,d]=Dxyz[:,:,:,d]*cell[d,d]
            else:
              xyz[:,:,:,d]=(Dxyz*cell[:,d]).sum(axis=3)
        #for d in np.arange(3):
        #    xyz=xyz[:,:,:,0:3]*cell[0:3,d]
    else:
        xyz=xyz*alat
    f.close()
    nstep=istep+1
    xyz=xyz[0:nstep,:,:,:]
    return nstep,ntyp,nat,xyz,cell
    
def readxyz(xyzfile,beforenum=0,header=2,dnstep=1):
    f=open(xyzfile,'r')
    for i in np.arange(beforenum): f.readline()#原子数前有几行
    natoms=int(f.readline())#原子数
    ierror=f.seek(0,0)
    rownum=int(os.popen('wc -l '+xyzfile).read().split()[0])#总行数
    #rownum=len(f.readlines())#总行数
    if rownum%(natoms+header) == 0:
        nstep=int(rownum/(natoms+header))  #每个xyz单元,2个
    else:
        print("rownum can't be split by natoms + header",rownum,natoms+header)
        nstep=int(rownum/(natoms+header))  #每个xyz单元,2个
    print(xyzfile+", rownum/(natoms+header",rownum,(natoms+header))
    #收集元素种类和数量
    ntyp=np.array([]).astype(np.str)
    nat=np.array([])
    ierror=f.seek(0,0)
    for i in np.arange(header): f.readline()
    for i in np.arange(natoms):
        label=f.readline().split()[0]
        if np.where(ntyp==label)[0].size == 0:
           ntyp =   np.append(ntyp,label)
           nat  =   np.append(nat,1)
        else:
            nat[np.where(ntyp==label)[0][0]]=nat[np.where(ntyp==label)[0][0]]+1
    nat=nat.astype(np.int)
    natmax=int(np.max(nat))
    totaltype=ntyp.size
    #======
    xyz=np.zeros([nstep,totaltype,natmax,3]) #步数,元素,原子编号,xyz
    ierror=f.seek(0,0)
    istep=-1
    for istep_all in np.arange(nstep):
        if istep_all%dnstep != 0:
            for i in np.arange(int(natoms+header)) : f.readlines()
            continue
        else:
            istep=istep+1
        index=np.zeros(totaltype)
        for i in np.arange(header): f.readline()
        for iatom in np.arange(natoms):
            line=f.readline()
            label=line.split()[0]
            itype=np.where(ntyp==label)[0][0]
            for idir in np.arange(3):
                xyz[istep,itype,int(index[itype]),idir]=float(line.split()[idir+1])
            index[itype]=index[itype]+1
    f.close()
    nstep=istep+1
    xyz=xyz[0:nstep,:,:,:]
    return nstep,ntyp,nat,xyz
def writexyz(xyzfile,nstep,ntyp,nat,xyz,cell):
    f=open(xyzfile,'w')
    natoms=nat.sum()
    for istep in np.arange(nstep):
        f.write(str(int(natoms))+'\n')
        f.write("# "+str(istep)+"#"+np.str(cell).replace('\n', ' ').replace(']', ' ').replace('[', ' ') +'\n')
        for ityp in np.arange(ntyp.size):
            label=ntyp[ityp]
            for iatom in np.arange(nat[ityp]):
                f.write(label+" "+np.str(xyz[istep,ityp,iatom,:]).replace('\n', ' ').replace(']', ' ').replace('[', ' ') +'\n')
    f.close()
def writeposcar(xyzfile,nstep,ntyp,nat,xyz,cell):
    f=open(xyzfile,'w')
    natoms=nat.sum()
    for istep in np.arange(nstep):
        f.write("Step "+str(istep)+'\n')
        f.write(str(1.0)+'\n')
        for icell in np.arange(3):
            f.write(np.str(cell[icell,:]).replace('\n', ' ').replace(']', ' ').replace('[', ' ') +'\n')
        f.write(np.str(ntyp).replace('\n', ' ').replace(']', ' ').replace('[', ' ').replace('\'', ' ')+'\n')
        f.write(np.str(nat).replace('\n', ' ').replace(']', ' ').replace('[', ' ') +'\n')
        f.write("Car \n")
        for ityp in np.arange(ntyp.size):
            label=ntyp[ityp]
            for iatom in np.arange(nat[ityp]):
                f.write(" "+np.str(xyz[istep,ityp,iatom,:]).replace('\n', ' ').replace(']', ' ').replace('[', ' ')+" "+label +'\n')
    f.close()
#移动原子到原胞中
def move2cell(nat,xyz,cell,cubic=False):
    nstep=xyz.shape[0]
    if cubic:
        #平移到原胞内,仅支持cubic原胞的算法
        for i in np.arange(nat.size):
            for x in np.arange(3):
                xyz[:,i,0:nat[i],x]=xyz[:,i,0:nat[i],x]-np.floor(xyz[:,i,0:nat[i],x]/cell[x,x])*cell[x,x]
    else:
       ##下面这套算法适合任意晶格,但是不严格
        for istep in np.arange(nstep):
            for i in np.arange(nat.size):
                for j in np.arange(nat[i]):
                    while xyz[istep,i,j,0] > cell[0,0]:
                        #print("i,j",i,j,"addcell 0")
                        xyz[istep,i,j,:]=xyz[istep,i,j,:]-cell[0,:]
                    while xyz[istep,i,j,0] < 0:
                        #print("i,j",i,j,"delcell 0")
                        xyz[istep,i,j,:]=xyz[istep,i,j,:]+cell[0,:]
                    while xyz[istep,i,j,1] > cell[1,1]:
                        #print("i,j",i,j,"addcell 1")
                        xyz[istep,i,j,:]=xyz[istep,i,j,:]-cell[1,:]
                    while xyz[istep,i,j,1] < 0:
                        #print("i,j",i,j,"delcell 1")
                        xyz[istep,i,j,:]=xyz[istep,i,j,:]+cell[1,:]
                    while xyz[istep,i,j,2] > cell[2,2]:
                        #print("i,j",i,j,"addcell 2")
                        xyz[istep,i,j,:]=xyz[istep,i,j,:]-cell[2,:]
                    while xyz[istep,i,j,2] < 0:
                        #print("i,j",i,j,"delcell 2")
                        xyz[istep,i,j,:]=xyz[istep,i,j,:]+cell[2,:]
#xyz[nstep,ntype,natmax,3] -> xyz[nstep,nats,3]
def gatherxyz(nat,xyz):
    xyz1=np.zeros([xyz.shape[0],nat.sum(),3])
    i=0
    for itype in np.arange(nat.size):
        xyz1[:,i:i+nat[itype],:]=xyz[:,itype,0:nat[itype],:]
        i=i+nat[itype]
    return xyz1
#xyz[nstep,nats,3] -> xyz[nstep,ntype,natmax,3]
def splitxyz(nat,xyz1):
    natmax=int(np.max(nat))
    xyz=np.zeros([xyz1.shape[0],nat.size,natmax,3])
    i=0
    for itype in np.arange(nat.size):
        xyz[:,itype,0:nat[itype],:]=xyz1[:,i:i+nat[itype],:]
        i=i+nat[itype]
    return xyz
#这种最近邻的方法，虽然能找到最近邻，但是容易把一个分子分成两份，还是要选择一个分子中心
#不完美
def jinlin(nat,xyz,cell):
    xyz1=gatherxyz(nat,xyz)
    edir=0
    for istep in np.arange(xyz1.shape[0]):
        edir_move = 1
        while edir_move > 0:
            edir_move = 0
            for edir in np.arange(3):
                print("-------edir",edir)
                move = 1
                while  move > 0 :
                    move = 0
                    for i in np.arange(xyz1.shape[1]):
                        L=np.square(xyz1[istep,i,:]-np.delete(xyz1[istep,:,:],i,axis=0)).sum(axis=1).min()
                        R=np.square(xyz1[istep,i,:]-np.delete(xyz1[istep,:,:],i,axis=0)+cell[edir]).sum(axis=1).min()
                        if L > R :
                            print("move atom",i,str(L)[0:5],str(R)[0:5],xyz1[istep,i,:])
                            xyz1[istep,i,:]+=cell[edir]
                            move=move+1
                    edir_move=max(edir_move,move)
    return splitxyz(nat,xyz1)
#以centeratom为中心,平移其他原子到最近邻的centeratom
def molecule_center(nat,xyz,cell,centeratom=-1,dr=-1):
    #适合没有电离发生的情况
    if centeratom < 0: centeratom=nat.argmin()
    if dr < 0: dr = 1.4  #!Ang,分子内间距～1Ang，因此先将所有原子平移到原胞内,在统计距离边界小于dr=1.5Ang的原子,判断是否需要平移
    #先把所有原子移动到原胞内,便于计算到原胞的边界距离,就只处理距离边界dr的原子
    #这样也是为了固定中心原子一定在原胞内，便于后面的移动其他原子
    move2cell(nat,xyz,cell,cubic=True) 
    for istep in np.arange(xyz.shape[0]):
        for itype in np.arange(nat.size):
            if itype == centeratom: continue
            for iat in np.arange(nat[itype]):
                #计算到边界的距离小于dr才后续处理
                for x in np.arange(3):
                    d2cell=np.abs(xyz[istep,itype,iat,x]-np.rint(xyz[istep,itype,iat,x]/cell[x,x])*cell[x,x])
                    if d2cell <= dr : break
                if d2cell > dr: continue    #距离边界太远,不进行处理
                dis=np.zeros([3,3,3])
                for addx in np.arange(3):
                    for addy in np.arange(3):
                        for addz in np.arange(3):
                            dis[addx,addy,addz]=np.square(
                                            xyz[istep,itype,iat,:]  
                                        -   xyz[istep,centeratom,0:nat[centeratom],:]
                                        +   (addx-1)*cell[0]
                                        +   (addy-1)*cell[1]
                                        +   (addz-1)*cell[2]
                                        ).sum(axis=1).min()

                if abs(dis.min()-dis[1,1,1]) < 1e-8: continue
                if dis[dis==dis.min()].size > 1:
                    print("There are many minmum value, choose the first one")
                    addx=np.where(dis==dis.min())[0][0]
                    addy=np.where(dis==dis.min())[0][1]
                    addz=np.where(dis==dis.min())[0][2]
                else:
                    addx=np.where(dis==dis.min())[0]
                    addy=np.where(dis==dis.min())[1]
                    addz=np.where(dis==dis.min())[2]
                #print("Move ",ntyp[itype],iat,"to",addx,addy,addz )
                #print(xyz[istep,itype,iat,:])
                xyz[istep,itype,iat,:] +=  \
                                        +   (addx-1)*cell[0]    \
                                        +   (addy-1)*cell[1]    \
                                        +   (addz-1)*cell[2]
                #print(xyz[istep,itype,iat,:])
    return centeratom
def nearest_atom(atom,atoms,cell,mdis=0.01):
    find=0;mx=0;my=0;mz=0;mmin=cell.max()**2
    dierct=np.array([1,0,2])
    for iatom in np.arange(atoms.shape[0]):
        for addz in dierct:
            for addy in dierct:
                for addx in dierct:
                    dis=np.square(
                                - atom
                                + atoms[iatom]
                                +   (addx-1)*cell[0]
                                +   (addy-1)*cell[1]
                                +   (addz-1)*cell[2]
                                ).sum()
                    if dis <= mmin :
                        find=iatom;mx=addx;my=addy;mz=addz;mmin=dis
                    #通过mdis加速计算
                    if dis <= mdis:
                        #水分子内原子和WF的最近距离>0.3Ang,
                        #相对运动最小可以达到0.01Ang(300K)*5nstep,所以不同原子间距仍>0.2Ang
                        #设最近邻距离可以达到是0.1Ang,平方后是0.01,不同原子间距必然大于0.01
                        #取得太小一定没有问题,取得太大会识别错误
                        #如果nstep很大那就另说了
                        return find,mx,my,mz,atoms[find] + (mx-1)*cell[0] + (my-1)*cell[1] + (mz-1)*cell[2]
    return find,mx,my,mz,atoms[find] + (mx-1)*cell[0] + (my-1)*cell[1] + (mz-1)*cell[2]

#一初始结构为准,调整之后的原子位置
def track_atom(nat,xyz,cell,wannier=True,dr=-1):
    newxyz=xyz.copy()
    #wannier,最后一个是否是Wannier中心，Wannier中心的位置可能是随机的,需要track
    #否表示,全是正常原子,不用追踪
    if dr < 0: dr = 1.4  #!Ang,分子内间距～1Ang，因此先将所有原子平移到原胞内,在统计距离边界小于dr=1.5Ang的原子,判断是否需要平移
    mincell= np.square(cell[cell!=0]).min()
    for istep in np.arange(1,xyz.shape[0]):
        tracknat=np.arange(nat.size)
        for iat in tracknat:
            if wannier: 
                notmove = (iat < nat.size-1)
            else:
                notmove = True
            #遍历上一时刻,寻找当前时刻的最临近原子
            if not notmove : now=xyz[istep,iat,0:nat[iat],:].copy()
            for atom in np.arange(nat[iat]):
                last=newxyz[istep-1,iat,atom,:].copy()
                if notmove:
                    now=xyz[istep,iat,atom:(atom+1),:].copy()
                    #对于编号固定的原子,如果相邻间距平方小于0.5则可视为没跨原胞,不用修改
                    if np.square(last-now).max() < min(mincell/4.0,0.5):
                        continue
                #
                find,mx,my,mz,tempxyz=nearest_atom(last,now,cell)
                #找到后保存
                now=np.delete(now,find,axis=0)
                newxyz[istep,iat,atom,:]=tempxyz      
    return newxyz
#--------- 
#一初始结构为准,调整之后的原子位置
def split_track_atom(nat,xyz,cell,m_snstep,m_enstep,wannier=True):
    newxyz=xyz.copy()
    #wannier,最后一个是否是Wannier中心，Wannier中心的位置可能是随机的,需要track
    #否表示,全是正常原子,不用追踪
    mincell= np.square(cell[cell!=0]).min()
    for split in np.arange(1,m_snstep.shape[0]):
        start=m_snstep[split]
        end=m_enstep[split]
        #
        tracknat=np.arange(nat.size)
        for iat in tracknat:#原子种类
            #
            if wannier: 
                notmove = (iat < nat.size-1)
            else:
                notmove = True
            #遍历上一时刻,寻找当前时刻的最临近原子
            now=newxyz[start:end,iat,0:nat[iat],:].copy() #当前及以后时刻待分辨的原子
            for atom in np.arange(nat[iat]):
                last=newxyz[m_enstep[split-1]-1,iat,atom,:].copy()#注意这里要-1
                if notmove:
                    now=xyz[start:end,iat,atom:(atom+1),:].copy()
                    if np.square(last-now[0]).max() < min(mincell/4.0,0.5):
                        continue
                #
                find,mx,my,mz,tempxyz=nearest_atom(last,now[0],cell)#仅根据now[0]进行判断
                tempxyz=now[:,find] + (mx-1)*cell[0] + (my-1)*cell[1] + (mz-1)*cell[2]#对所有时刻进行同一处理
                #找到后保存start,end的数据
                newxyz[start:end,iat,atom]=tempxyz
                now=np.delete(now,find,axis=1)
    return newxyz
        
#一初始结构为准,调整之后的原子位置



#计算原胞体积 
def calV(cell):
    V=0
    V=V+(cell[0,1]*cell[1,2]-cell[0,2]*cell[1,1])*cell[2,0] 
    V=V+(cell[0,2]*cell[1,0]-cell[0,0]*cell[1,2])*cell[2,1]
    V=V+(cell[0,0]*cell[1,1]-cell[0,1]*cell[1,0])*cell[2,2]
    return V
#--------------
#计算rdf
def calrdf(A_in,B_in,minr=0.0,maxr=10.0,dr=0.02,ngrid=501):
    A=A_in.copy()
    B=B_in.copy()
    rdf=np.zeros(ngrid)
    for i in np.arange(A.shape[0]):
        dis=np.sqrt(np.square(B-A[i]).sum(axis=1))
        choose=np.floor(  ( dis[(dis >= max(minr, 1e-5) )&(dis < maxr+10*dr )] - minr )/dr  ).astype(int)
        #忽略本身原子1e-5, #向下取整,处以体积4/3pi(r^3 -(r-dr)^3)
        choose=choose[choose<ngrid]
        for uniq in np.unique(choose):
            rdf[uniq]=rdf[uniq]+choose[(choose==uniq)].size
    return rdf*1.0/A.shape[0] #算一个A原子就够了,算多个A原子进行平均
def rdf(nstep,ntyp,nat,xyz,cell,minr=0.0,maxr=10.0,dr=0.02):
    #数据网格
    ngrid=int(np.ceil(maxr-minr)/dr)+2
    grid=np.arange(ngrid)*dr+minr
    #
    rdftype=int(np.arange(ntyp.size+1).sum())#几种rdf
    timerdf=np.zeros([nstep,rdftype,ngrid])#含时rdf
    rdflable=np.zeros(rdftype).astype(np.str)#rdftype种键长
    supercell=np.zeros(3)
    for i in np.arange(3):  supercell[i]=max(np.around(maxr/cell[i,i]),1) #超胞数量，至少3x3x3
    supercell.astype(np.int)
    #print("Super cell",supercell)
    for istep in np.arange(nstep):
        irdftype=0
        for left in np.arange(ntyp.size):
            lindex=left#A元素编号
            A=xyz[istep,lindex,0:nat[lindex]].copy()#原胞中的A
            for right in np.arange(ntyp.size-left):
                rindex=lindex+right#B元素编号
                rdflable[irdftype]=ntyp[lindex]+"-"+ntyp[rindex]
                #下面计算AB两种原子的rdf
                for x in np.arange(-supercell[0],1+supercell[0]):
                    for y in np.arange(-supercell[1],1+supercell[1]):
                        for z in np.arange(-supercell[2],1+supercell[2]):
                            B=xyz[istep,rindex,0:nat[rindex],:]+x*cell[0]+y*cell[1]+z*cell[2]#超胞中的B
                            timerdf[istep,irdftype,0:ngrid] = timerdf[istep,irdftype,0:ngrid] + calrdf(A,B,minr,maxr,dr,ngrid)
                rho=1.0*nat[rindex]/calV(cell)
                #算完了元素A与元素B的，进行归一化，和下一种类型
                timerdf[istep,irdftype,0:ngrid]=timerdf[istep,irdftype,0:ngrid]/(rho*4.0/3.0*np.pi*dr*(3*grid[:]**2+3*grid[:]*dr+dr**2)) #dN/(4*pi*rho_N,r^2*dr)
                #这里使用体积4/3*pi[ (r+dr)^3-r^3 ]=4/3*pi[ dr^3 +3r^2dr+3r*dr^2]
                irdftype=irdftype+1
    return rdftype,rdflable,ngrid,grid,timerdf #种类数,标签,数据timerdf[istep,irdftype,igrid]

def DeltaBond(nstep,ntyp,nat,xyz,cell,minr=0.0,maxr=3,dr=0.001):
    #数据网格
    ngrid=int(np.ceil(maxr-minr)/dr)+2
    grid=np.arange(ngrid)*dr+minr
    #
    rdftype=int(np.arange(ntyp.size+1).sum())#几种rdf
    timerdf=np.zeros([nstep,rdftype,ngrid])#含时rdf
    rdflable=np.zeros(rdftype).astype(np.str)#rdftype种键长
    supercell=np.zeros(3)
    for i in np.arange(3):  supercell[i]=1 #因为统计键的差异,仅相邻原胞就可以了
    supercell=supercell.astype(np.int)
    for istep in np.arange(nstep):
        irdftype=0
        for left in np.arange(ntyp.size):
            lindex=left#A元素编号
            A=xyz[istep,lindex,0:nat[lindex]].copy()#原胞中的A
            for right in np.arange(ntyp.size-left):
                rindex=lindex+right#B元素编号
                rdflable[irdftype]=ntyp[lindex]+"-"+ntyp[rindex]
                #统计dis和rdf的计算不同,可能会面临相邻原胞的键做差
                B=np.zeros([nat[rindex]*(2*supercell[0]+1)*(2*supercell[1]+1)*(2*supercell[2]+1),3])
                isupercell=0 #0-27
                #构建超胞
                for x in np.arange(-supercell[0],1+supercell[0]):
                    for y in np.arange(-supercell[1],1+supercell[1]):
                        for z in np.arange(-supercell[2],1+supercell[2]):
                            B[isupercell*nat[rindex]:(isupercell+1)*nat[rindex],:]=xyz[istep,rindex,0:nat[rindex],:]+x*cell[0]+y*cell[1]+z*cell[2]#超胞中的B
                            isupercell=isupercell+1
        
                Adis=np.zeros(A.shape[0])+1E5    #默认无穷大,如果设置为0,会影响0处的分布
                for i in np.arange(A.shape[0]):
                    dis=np.sqrt(np.square(B-A[i]).sum(axis=1))
                    dis.sort()
                    if Adis[0] < 1E-5: # 同种原子的情况,位置相同的舍去, 不同原子不会靠的这么近
                        Adis[i] = dis[2] - dis[1]
                    else: #因为B包含原胞的成份, 应该不会发生统计的键长很长的情况
                        Adis[i] = dis[1] - dis[0]
                choose=np.floor(  ( Adis[(Adis >= max(minr,0) ) &(Adis < maxr+10*dr )] - minr )/dr  ).astype(int)
                choose=choose[choose<ngrid]
                for uniq in np.unique(choose):
                    timerdf[istep,irdftype,uniq]=choose[(choose==uniq)].size/A.shape[0]
                irdftype=irdftype+1                       
    return rdftype,rdflable,ngrid,grid,timerdf #种类数,标签,数据timerdf[istep,irdftype,igrid]

def angle(nstep,ntyp,nat,xyz,cell,minr=0.0,maxr=180.0,dANG=1,abctype=np.array([0,1,0]),abcatom=np.array([0,0,1])):
    #数据网格
    ANGngrid=int(np.ceil(maxr-minr)/dANG)+2
    ANGgrid=np.arange(ANGngrid)*dANG+minr
    #
    timeANG=np.zeros([nstep,1,ANGngrid]) #目前仅支持一种角
    ANGtype=1
    ANGlable=np.zeros(ANGtype).astype(np.str)#ANGtype种键长
    ANGlable[0]=ntyp[abctype[0]]+"-"+ntyp[abctype[1]]+"-"+ntyp[abctype[2]]
    #     O
    #  a / \ b
    #   /   \
    #  1----2
    #    c
    A=xyz[:,abctype[1],abcatom[1]]-xyz[:,abctype[0],abcatom[0]]
    B=xyz[:,abctype[1],abcatom[1]]-xyz[:,abctype[2],abcatom[2]]
    C=xyz[:,abctype[2],abcatom[2]]-xyz[:,abctype[0],abcatom[0]]
    a=np.sqrt(np.square(A).sum(axis=1))
    b=np.sqrt(np.square(B).sum(axis=1))
    c=np.sqrt(np.square(C).sum(axis=1))
    cos=-(c*c-b*b-a*a)/(2*a*b)
    theta=np.arccos(cos)*180/np.pi
    #
    #theta[ ( theta >= max(minr,0) ) &( theta < maxr+10*dr ) ] - minr )/dr  ).astype(int)
    #choose=choose[choose<ANGngrid]

    for istep in np.arange(nstep):
        iANGtype=0
        choose=np.floor(  ( theta[istep:istep+1] - minr )/dANG ).astype(int)
        choose=choose[choose<ANGngrid]
        for uniq in np.unique(choose):
            timeANG[istep,iANGtype,uniq] = timeANG[istep,iANGtype,uniq] + choose[(choose==uniq)].size
        iANGtype=iANGtype+1
    return ANGtype,ANGlable,ANGngrid,ANGgrid,timeANG
            
#----------------------------------------------------------------------------------
def absvector(a):
    return np.sqrt((a*a).sum())
#----------------------------------------------------------------------------------
def normvector(a):
    return a/absvector(a)
#----------------------------------------------------------------------------------
def axb3(A,B):
   C=np.zeros(3)
   for x in np.arange(3):
      for y in np.arange(3):
         for z in np.arange(3):
            if x == y or x == z or y==z: continue
            num=(z+1)+10*(y+1)+100*(x+1)
            sign = -1
            if num in [ 123, 231, 312]: sign = 1
            C[x]=C[x]+sign*A[y]*B[z]
   return C

def AXB3(A,B):
   if len(A.shape) == 1: return axb3(A,B)
   if A.shape[1] != 3 :
      print("A's shape is not Nx3")
      exit()
   if A.shape != B.shape:
      print("A.shape != B.shape")
      exit()
   C=np.zeros(A.shape)*0j
   for x in np.arange(3):
      for y in np.arange(3):
         for z in np.arange(3):
            if x == y or x == z or y==z: continue
            num=(z+1)+10*(y+1)+100*(x+1)
            sign = -1
            if num in [ 123, 231, 312]: sign = 1
            C[:,x]=C[:,x]+sign*A[:,y]*B[:,z]
   return C
#----------------------------------------------------------------------------------
#返回向量a,b夹角的\theta[0,\pi]的sin,cos值
def thetaAB(a,b):
    axb=AXB3(a,b)
    sin=absvector(axb)/(absvector(a)*absvector(a))
    cos=(a*b).sum()/(absvector(a)*absvector(a))
    return sin,cos
def tetrahedron(C_in,H1_in,H2_in,scale1=1.0,scale2=1.0,scale3=1.0,scale4=1.0):
    C=C_in.copy()
    H1=H1_in.copy()
    H2=H2_in.copy()
    center=C.copy()
    b1=C-H1_in#平面内H1->C
    b2=C-H2_in#平面内H2->C
    #平面内, b1,b2的中线
    midline=normvector(b1+b2)
    #垂直平面, b1,b2的垂线
    perpendicular=normvector(AXB3(b1,b2))
    #中线和H1/2->C的夹角
    H3=np.zeros(H1.shape)
    H4=np.zeros(H2.shape)
    sin1,cos1=thetaAB(midline,b1)
    H3=center   \
        +   (absvector(b1)*scale1*cos1)*midline + \
        +   (absvector(b1)*scale1*sin1)*perpendicular
    sin2,cos2=thetaAB(midline,b2)
    H4=center   \
        +   (absvector(b2)*scale2*cos2)*midline + \
        -   (absvector(b2)*scale2*sin2)*perpendicular
    H1=center-b1*scale1
    H2=center-b2*scale2
    return C,H1,H2,H3,H4
#
#
def example_simianti():
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    """
    @author: cndaqiang 2020-
    计算水分子的四面体的另外两个顶角
    """
    import numpy as np
    import sys
    from pyramids.process.structure import tetrahedron

    C =np.array([6.05348,  5.67034,   5.99999])
    H1=np.array([6.75908,  6.32965,   5.99999])
    H2=np.array([5.24091,  6.19133,   5.99999])
    C,H1,H2,H3,H4=tetrahedron(C,H1,H2,0.45,0.45,0.3,0.3)

    print(C [0:3])
    print(H1[0:3])
    print(H2[0:3])
    print(H3[0:3])
    print(H4[0:3])

    #c=6.371      ,5.9670295  ,5.99999   :s
    #c=5.6878235  ,5.9047855  ,5.99999   :s
    #c=6.07673676 ,5.41372648 ,6.33122529:s
    #c=6.07669756 ,5.41415897 ,5.66890756:s

#
#----------------------------------------------------------------------------------
#下面为旧脚本备份
#----------------------------------------------------------------------------------
def calculateRMSD(traj, selectedStep=None, atomsOrigin=None, init=0, selectedAtoms=None):
  """ 
  return the radius mean square displacements of the selected steps 
  compared with the init step
  """
  #from ase.io.trajectory import Trajectory
  if atomsOrigin is None:
    atomsOrigin = traj[init]
    #print 'no'
  if selectedStep == None:
    selectedStep = range(len(traj))

  distance = np.array([np.mean(calculateDisplacement(traj[step],atomsOrigin,selectedAtoms)**2)**0.5
              for step in selectedStep])
  return distance

#-------------------------------------------------------------------
def calculateDisplacement(atoms,atomsOrigin,selectedAtoms=None):
  """ 
  return the displacements as a dimension of Natoms
  """
  if selectedAtoms == None:
    selectedAtoms = range(atomsOrigin.get_number_of_atoms())
    
  return np.array([
          np.min([np.linalg.norm(atoms.get_positions()[index] - 
                  atomsOrigin.get_positions()[index] + np.dot([i,j,k],atoms.get_cell())) 
                  for i in range(-1,2) 
                  for j in range(-1,2) 
                  for k in range(-1,2)
                  ])
          for index in selectedAtoms])
#-------------------------------------------------------------------
def readXV(xvfile="siesta.XV"):
    f=open(xvfile,'r')
    cell=np.zeros([3,3])
    for i in np.arange(3):
        cell[i,0:3] = [ float(x) for x in f.readline().split()[0:3] ]
    if np.abs(cell).sum()-np.abs( [ cell[0,0], cell[1,1], cell[2,2] ] ).sum() > 1E-8:
      cubic=False
    else:
      cubic=True
    bohr=0.52917721
    #暂时不写坐标的部分
    xyz=np.zeros([])
    #
    cell=cell*bohr #输出的单是A
    xyz=xyz*bohr
    #
    return cell,xyz
#-------------------------------------------------------------------
def readCrystalKP(filename='pwscf.crystal.KP'):
  """
  read siesta.crystal.KP or pwscf.crystal.KP
  kcrystal[n,3],kweight[n]
  """
  f=open(filename,'r')
  nkpts = int(f.readline().split()[0])
  #
  #确定数据结构
  line=f.readline()
  data1=[float(value) for value in line.split()]
  haveindex=True #历史原因,输出的前面可能不带k点编号
  if len(data1) == 4: haveindex=False
  #存储第一组数据
  kweight = [ data1[-1] ]
  kx, ky, kz = data1[-4:-1]
  kcrystal=[(kx, ky, kz)]
  #
  for i in range(nkpts-1):
    if haveindex:
        index, kx, ky, kz, wk = [float(value) for value in f.readline().split()]
    else:
               kx, ky, kz, wk = [float(value) for value in f.readline().split()]
    kcrystal.append((kx,ky,kz))
    kweight.append(wk)
  return np.array(kcrystal), np.array(kweight)
#-------------------------------------------------------------------
def readKP(filename='pwscf.KP'):
  """
  read siesta.KP or pwscf.KP
  """
  #siesta.KP/pwscf.KP单位是Bohr^-1,只有要化成Ang^-1进行画图
  #b[Ang^-1]=b[Bohr^-1]/0.529177
  bohr=0.52917721
  kcoor,kweight=readCrystalKP(filename)
  #crystal.KP和KP的结构是一样的,可以读入,但是读入的单位是Bohr^-1
  #注意, 1 Ang^-1 = 0.529177*1Bohr^-1,但是倒格式涉及物理， b[Ang^-1]=b[Bohr^-1]/0.529177
  return kcoor/bohr,kweight
#-------------------------------------------------------------------
#读入pwcf.crystal.KP, pwscf.XV, 保存到pwscf.KP
def crystalKP2KP(prefix="pwscf"):
  kcrystal,kweight=readCrystalKP(prefix+".crystal.KP")
  for i in np.arange(kweight.size):
      for j in np.arange(3):
          if kcrystal[i,j] > 0.5: kcrystal[i,j]=kcrystal[i,j]-1
          if kcrystal[i,j] < -0.5: kcrystal[i,j]=kcrystal[i,j]+1
  cell,xyz=readXV(prefix+'.XV')
  bcell=invcell(cell)
  kcoor=Frac2Car(kcrystal,bcell) #kcrystal(n,b123)
  bohr=0.52917721
  kcoor=kcoor*bohr
  #转成Bohr坐标再保存
  saveKP(kcoor,kweight,prefix+".KP")
#-------------------------------------------------------------------
def saveKP(kcoor,kweight,file="pwscf.KP"):
  f=open(file,'w')
  nkpnt=kweight.size
  f.write("%i\n"%(nkpnt))
  for i in np.arange(nkpnt):
      f.write("%i\t%15.12f\t%15.12f\t%15.12f\t%15.12f\n"%
              (i+1,kcoor[i,0],kcoor[i,1],kcoor[i,2],kweight[i])
              )
  f.close()
#-------------------------------------------------------------------
#计算倒格矢
def invcell(a=np.ones([3,3])):
#  cell=a[abc,xyz]
#  return 倒格矢b[b123,xyz]
  b=np.zeros([3,3])
  V=np.dot(a[0],np.cross(a[1],a[2]))
  b[0]=np.cross(a[1],a[2])
  b[1]=np.cross(a[2],a[0])
  b[2]=np.cross(a[0],a[1])
  b=b/V*np.pi*2
  return b

def Car2Frac(car,cell):
    #笛卡尔坐标转分数坐标 car(n,xyz),cell[abc,123]
    bcell=invcell(cell)
    car=car.reshape([int(car.size/3),3])
    frac=np.zeros(car.shape)
    for i in np.arange(frac.shape[0]):
        frac[i]=np.dot(bcell,car[i])/(2*np.pi)
    return frac
def Frac2Car(frac,cell):
    #分数坐标转笛卡尔坐标 car(n,xyz),cell[abc,123]
    car=np.zeros(frac.shape)
    for i in np.arange(frac.shape[0]):
        car[i]=np.dot(cell.T,frac[i])
    return car

def frac2cell(frac,maxstep=0):
  step=0
  if maxstep == 0: maxstep = frac.size**3
  while frac.max() > 1 or frac.min() < 0:
    for i in np.arange(frac.shape[0]):
      for j in np.arange(frac.shape[1]):
        if frac[i,j] > 1:
          #CNQ: 一定一定要对所有坐标执行相同的平行操作,不然就很难保证相邻坐标构成的向量的方向了
          frac[:,j] = frac[:,j] - 1
        if frac[i,j] < 0:
          frac[:,j] = frac[:,j] + 1
    step+=1
    if step % 10 == 0:
        sys.stdout.write("\rMove frac coor to cell %i"%(step))
        sys.stdout.flush()
    if step > maxstep:
      print("Error没能移动到元胞内")
      exit()
  sys.stdout.write("\n")
  return frac


