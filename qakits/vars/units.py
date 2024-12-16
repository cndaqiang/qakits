
#phy cons
#pi=3.14159265358979
from numpy import pi #3.141592653589793
h_planck_eV =  4.135667516e-15   #  h  =  4.135667516e-15 eV·s | eV/Hz
h_planck_J =   6.62606957e-34    #  h  =  6.62606957e-34 J·s   | eV/Hz

#unit to unit
Hz2eV = h_planck_eV              #  1 (s^-1) = 1 * ifs2eV (eV)
eV2Hz = 1.0/h_planck_eV
ifs2eV = Hz2eV * 1e15            #  1 (fs^-1) = 1 * ifs2eV (eV) ～= 4.1356 ; 1 eV = 1/T fs ^1- & T=4.1356 fs
#https://www2.chemistry.msu.edu/faculty/reusch/VirtTxtJml/cnvcalc.htm
ieV2nm   =   1.2398e+3   # a (eV) = 1/a * ieV2nm (nm)
nm2ieV   =   1/ieV2nm    #  a (nm) = 1/( a * nm2ieV) (eV)
Ry2eV  = 13.6056980659                #  1 Ry      = 13.60581eV
eV2cm   = 8.0656e+3 #1eV= eV2cm (cm^-1)
Ha2eV   =   2*Ry2eV
#a.u.
#http://www.unitconversion.org/length/angstroms-to-bohr-radius-conversion.html
Ang2Bohr =  1.889725989          #  1  Ang   =  1.889725989 Bohr
Bohr2Ang =  0.529177249          #  1  Bohr   =  1.889725989 Ang
Ry_au2fs =  0.048378             #  1  a.u.   =  Ry_au2fs  fs
Ry_au2s  =  Ry_au2fs*1e-15       #  1  a.u.   =  Ry_au2s  s


