import time

import odrive
from odrive.enums import * 
from odrive.utils import *

from config import config
from utils import exceptions

from logger.logger import logger

#logger = logger.getChild(__name__)

def calibrate(axis):
    """
    Calibrate and start control of a given axis.

    It secuencially request and waits the following states,
    1-encoder offset calibration,
    2-Axis state homming
    3-closed loop control

    Parameters
    -----------
    axis: an odrive axis, ej: odrv0.axis0

    Returns
    ----------
    None.


    """
    # only the encoder must be calibrated, the motor parameters are saved in 
    # the odrive
    # this should check if the axis changed correctly
    axis.requested_state = AXIS_STATE_ENCODER_OFFSET_CALIBRATION  
    # exception if unable to enter requested state
    exceptions.raise_except(axis,AXIS_STATE_ENCODER_OFFSET_CALIBRATION) 
    # exception if time out and still in the same state
    exceptions.timeout_except(axis,AXIS_STATE_ENCODER_OFFSET_CALIBRATION) 
    logger.info('succesfully entered AXIS_STATE_ENCODER_OFFSET_CALIBRATION')  
    
    #execute homing
    axis.requested_state = AXIS_STATE_HOMING 
    # exception if unable to enter requested state
    exceptions.raise_except(axis,AXIS_STATE_HOMING) 
    # exception if time out and still in the same state
    exceptions.timeout_except(axis,AXIS_STATE_HOMING)  
    logger.info('Current axis successfully homed')
    
    #execute control loop
    axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    # exception if unable to enter requested state
    exceptions.raise_except(axis, AXIS_STATE_CLOSED_LOOP_CONTROL) 
    logger.info('Current axis successfully enters control mod3')


# straight
# z
# if should_comeback:
#     offset_z_stg = -3.25 # 6.25
#     odrvc.axis0.controller.move_incremental(offset_z_stg, False)
#     time.sleep(5)
#     # codo
#     offset_c_stg = -2.6
#     odrvc.axis1.controller.move_incremental(offset_c_stg, False)
#     time.sleep(5)
#     # hombro
#     offset_h_stg = -1.75 
#     odrvh.axis0.controller.move_incremental(offset_h_stg, False)
#     time.sleep(5)

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Nelen homing",
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-j", "--joint", type=str, required=True,
            help="Joint to calibrate: hombro, codo, z or all")
    args = parser.parse_args()
    joint_to_calibrate = args.joint
  
    # odrv radio cubito, axis 0->Z, 1->codo
    odrv_d = {}
    if joint_to_calibrate == 'all':
        odrv_d['codo-muneca'] = odrive.find_any(
                serial_number=config.rc_serial) # codo and z
        odrv_d['hombro'] = odrive.find_any(
                serial_number=config.hombro_serial) # hombro
    elif joint_to_calibrate in ['codo', 'z']:
        odrv_d['codo-muneca'] = odrive.find_any(
                serial_number=config.rc_serial) # codo and z
    elif joint_to_calibrate == 'hombro':
        odrv_d['hombro'] = odrive.find_any(
                serial_number=config.hombro_serial) # hombro
    else:
        raise KeyError(f'there is no {joint_to_calibrate} joint')
    
    for odrv_name in odrv_d:
        # dump errors
        logger.info('Dumping errors for %s odrive: %s',odrv_name,
                dump_errors(odrv_s[odrv_name]))
        dump_errors(odrv_d[odrv_name], True)
        
        # calibrate
        if odrv == 'codo-muneca':
            #Z
            logger.info('Working on z')
            calibrate(odrv_d[odrv_name].axis0)
            logger.infoprint('z calibrated')

            #codo
            logger.info('Working on codo')
            calibrate(odrv_d[odrv_name].axis1)
            logger.info('hombro calibrated')
        elif odrv == 'hombro':
            ## Hombro
            logger.info('Working on Hombro')
            calibrate(odrv_d[odrv_name].axis0)
            logger.info('hombro calibrated')
    logger.info("End calibration")


