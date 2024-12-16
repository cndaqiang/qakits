#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2020-09-03 @IOP
@Author  : cndaqiang
@Blog    : cndaqiang.github.io
@File    : 单位换算把ev转为各种
"""

import sys
from qakits.vars.units import *


def main():
    # -----Input File
    if len(sys.argv) > 1:
        pass
    else:
        print("Usage: "+str(sys.argv[0])+" 1.0eV")
        eV = 1.0

    eV2kcal_mol = 23.06  # 1eV=23.06 kcal/mol
    value = str(sys.argv[1])
    #
    if value[-2:] == "eV":
        eV = float(value[:-2])
    if value[-2:] == "Ry":
        eV = float(value[:-2])*Ry2eV
    elif value[-2:] == "cm":
        eV = float(value[:-2])/eV2cm
    elif value[-2:] == "fs":
        eV = 1/(float(value[:-2]))*ifs2eV
    elif value[-3:] == "THz":
        eV = float(value[:-3])*1e12*Hz2eV
    elif value[-2:] == "Hz":
        eV = float(value[:-2])*Hz2eV
    elif value[-2:] == "kcal":
        eV = float(value[:-2])/eV2kcal_mol
    elif value[-2:] == "au":  # 时间
        eV = 1/(float(value[:-2])*0.048378)*ifs2eV
    elif value[-2:] == "nm":
        eV = 1.0/(nm2ieV*float(value[:-2]))
    elif value[-3:] == "ang":
        eV = 1.0/(nm2ieV*float(value[:-3])*0.1)
    elif value[-4:] == "bohr":
        eV = 1.0/(nm2ieV*float(value[:-4])*0.529177249*0.1)
    elif value[-1:] == "K":  # 温度
        eV = (float(value[:-1])*8.617333262145e-5)
    else:
        eV = float(value[:-2])

    eV = eV
    # -----------下面以eV进行所有计算
    Ry = eV/Ry2eV
    nm = 1/(eV)*ieV2nm
    ang = nm*10
    bohr = ang*1.8897259886
    Hz = eV*eV2Hz
    THz = Hz/1e12
    au = 1/Hz*1e15/0.048378
    fs = 1/Hz*1e15
    cm = eV*eV2cm
    kcal_mol = eV*eV2kcal_mol
    T = eV/8.617333262145e-5  # kb*T=eV,
    # print("eV:\t",eV,"\tnm:\t",nm,"\tHz:\t",Hz,"\tTHz:\t",THz,"\tT(fs):\t",fs,"\tT(au):\t",au,"\tcm-1\t",cm,"\tkcal/mol\t",kcal_mol)
    print(eV, "eV\t")
    print(Ry, "Ry\t")
    print(T, "K\t", T/315774.66, "Tem(i-pi)\t")
    print(nm, "nm\t", ang, "Angstrom\t", bohr, "bohr\t")
    print(Hz, "Hz\t", THz, "THz\t", 1/fs, "fs-1\t", fs, "fs\t", au, "au(time)\t", cm, "cm-1\t", kcal_mol, "kcal/mol")


if __name__ == "__main__":
    main()
