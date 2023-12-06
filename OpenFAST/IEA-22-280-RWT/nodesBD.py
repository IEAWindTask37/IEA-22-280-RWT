from pyFAST.input_output.postpro import BD_BldStations
import numpy as np
import os

run_dir = os.path.dirname( os.path.realpath(__file__) )


BD    = os.path.join(run_dir, 'IEA-22-280-RWT_BeamDyn.dat')
BDBld = os.path.join(run_dir, 'IEA-22-280-RWT_BeamDyn_Blade.dat')
r = BD_BldStations(BD, BDBld)
print(r)

data = np.loadtxt(os.path.join(run_dir, 'IEA-22-280-RWT_AeroDyn15_blade.dat'), skiprows = 6)

data_interp = np.zeros((len(r), len(data[0,:])))
data_interp[:,0] = r
for i in range(1,len(data[0,:])):
    # if i == len(data[0,:]):
    data_interp[:,i] = np.interp(r, data[:,0], data[:,i])

for i in range(len(r)):
    data_interp[i,-1] = round(data_interp[i,-1])

filename = os.path.join(run_dir, 'IEA-22-280-RWT_AeroDyn15_blade2.dat')
f = open(filename, 'w')

f.write('------- AERODYN v15.00.* BLADE DEFINITION INPUT FILE -------------------------------------\n')
f.write('Generated with AeroElasticSE FAST driver\n')
f.write('======  Blade Properties =================================================================\n')
f.write('{:<11d} {:<11} {:}'.format(len(r), 'NumBlNds', '- Number of blade nodes used in the analysis (-)\n'))
f.write('    BlSpn        BlCrvAC        BlSwpAC        BlCrvAng       BlTwist        BlChord          BlAFID\n')
f.write('     (m)           (m)            (m)            (deg)         (deg)           (m)              (-)\n')
for i in range(len(r)):
    f.write('{: 2.15e} {: 2.15e} {: 2.15e} {: 2.15e} {: 2.15e} {: 2.15e} {: 8d}\n'.format(data_interp[i,0], 
        data_interp[i,1], data_interp[i,2], data_interp[i,3], data_interp[i,4], data_interp[i,5], int(data_interp[i,6])))

f.close()
pass
