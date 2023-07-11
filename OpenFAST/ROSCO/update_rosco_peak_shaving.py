'''
Update the DISCON.IN examples in the IEA-22MW repository using tuning .yamls in rosco conda environment

'''
import os
from ROSCO_toolbox.ofTools.fast_io.update_discons import update_discons
import numpy as np
from ROSCO_toolbox.tune import yaml_to_objs
import matplotlib.pyplot as plt
from ROSCO_toolbox.ofTools.util.FileTools import save_yaml
from ROSCO_toolbox.inputs.validation import load_rosco_yaml



# Add DTU min pitch values
dtu_min_pitch_table = np.array([[3.0 ,-3.735157000000000060e-02],
  [4.0 ,-2.473450899999999897e-01],
  [5.0 ,-5.161431699999999845e-01],
  [6.0 ,-8.509175900000000015e-01],
  [7.0 ,-1.177307050000000022e+00],
  [7.5 ,-1.340484919999999969e+00],
  [8.0 ,-1.384459139999999921e+00],
  [8.5 ,-1.384752090000000102e+00],
  [9.0 ,-1.376258610000000049e+00],
  [9.5 ,-1.325457069999999904e+00],
  [10.0, -5.787865500000000107e-01]])


if __name__=="__main__":

    # directory references
    this_dir = os.path.dirname(os.path.abspath(__file__))
    of_dir = os.path.realpath(os.path.join(this_dir,'..'))


    # For each yaml, incorporate the DTU min pitch with the desired level of peak shaving
    # paths relative to this OpenFAST directory
    # List of yamls
    iea22_yamls = [
        'IEA-22-280-RWT-Monopile/IEA-22-280-RWT-Monopile.yaml',
        'IEA-22-280-RWT-Semi/IEA-22-280-RWT-Semi.yaml',
    ]

    for yaml in iea22_yamls:
        yaml_file = os.path.join(of_dir,yaml)
        controller, turbine, _ = yaml_to_objs(yaml_file)
        inps = load_rosco_yaml(yaml_file)

         # Plot minimum pitch schedule
        fig, ax = plt.subplots(1,1)
        # ax.plot(controller.v, controller.pitch_op,label='Steady State Operation')
        ax.plot(controller.v, controller.ps_min_bld_pitch, label='Original Pitch Schedule')


        vv = controller.v
        first_ps_ind = np.where(controller.ps_min_bld_pitch > 0)[0][0]
        last_dtu_ind = np.where(vv>dtu_min_pitch_table[-1][0])[0][0]
        dtu_min_pitch = np.radians(np.interp(vv,dtu_min_pitch_table[:,0],dtu_min_pitch_table[:,1])[:last_dtu_ind+1])
        # min_pitch = np.radians(dtu_min_pitch)
        ps_min_pitch = controller.ps_min_bld_pitch[first_ps_ind:]
        dtu_v = vv[:last_dtu_ind+1]
        ps_v = vv[first_ps_ind:]

        controller.ps_min_bld_pitch = np.r_[dtu_min_pitch,ps_min_pitch]
        controller.v = np.r_[dtu_v,ps_v]    # don't actually want to overwrite this, just for vis

       
        ax.plot(controller.v, controller.ps_min_bld_pitch, label='Updated Pitch Schedule',linestyle='--')
        ax.legend()
        ax.set_xlabel('Wind speed (m/s)')
        ax.set_ylabel('Blade pitch (rad)')
        plt.savefig(os.path.join(this_dir,os.path.split(yaml)[0]+'.peakshave.png'))


        # Update yaml
        inps['controller_params']['DISCON']['PS_WindSpeeds'] = controller.v
        inps['controller_params']['DISCON']['PS_BldPitchMin'] = controller.ps_min_bld_pitch
        inps['controller_params']['DISCON']['PS_BldPitchMin_N'] = len(controller.v)
        save_yaml(os.path.dirname(yaml_file), os.path.split(yaml_file)[-1]+'.new', inps)

        print('here')


