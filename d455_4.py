import pyrealsense2 as rs
import logging
import datetime
import sys
import cv2
from realsense_device_manager import DeviceManager

import numpy as np

from pprint import pprint
from realsense_device_manager import DeviceManager

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(asctime)s.%(msecs)03d: (%(threadName)-9s) %(message)s',
    datefmt="%H:%M:%S"
)

def get_devices_serial_numbers(device_suffix:str='D455') -> [str]:
    '''
    Return list of serial numbers conected devices.
    Eventualy only fit given suffix (like T265, D415, ...)
    (based on https://github.com/IntelRealSense/librealsense/issues/2332)
    '''
    ret_list = []
    ctx = rs.context()
    for d in ctx.devices:
        print(d)
        print(f'Found Device: {d.get_info(rs.camera_info.name)}, {d.get_info(rs.camera_info.serial_number)}')
        
        if device_suffix and not d.get_info(rs.camera_info.name).endswith(device_suffix):
            continue
        
        ret_list.append(d.get_info(rs.camera_info.serial_number))

    return ret_list


def find_devices_in_advanced_mode():

    ctx = rs.context()
    devices = ctx.query_devices()    
    print("D: ", devices)
    devs = []
    print(rs.camera_info.product_id)
    for dev in devices:
        if dev.supports(rs.camera_info.product_id) and str(dev.get_info(rs.camera_info.product_id)) in "0B5C":
            if dev.supports(rs.camera_info.name):
                print(f"Found device that supports advanced mode: {dev.get_info(rs.camera_info.name)} -> {dev}")
                devs.append(dev)
    return devs 
               

    #3        if dev.supports(rs.camera_info.name):
    #            print("Found device that supports advanced mode:", dev.get_info(rs.camera_info.name), " -> ", dev)
    #            devs.append(dev)
    #raise Exception("No device that supports advanced mode was found")


class D455CameraSource:
    def __init__(self, serial_number:str):
        '''
        Accept Serial Numbers
        '''
        self.__serial_number = serial_number
        self.__pipeline = None
        self.__config = None
        self.__started = False
        self.__start_pipeline()
    
    def __del__(self):
        if self.__started and not self.__pipeline is None:
            self.__pipeline.stop()
            
    def get_serial_number(self):
        return self.__serial_number

    def __start_pipeline(self):
        self.pipelines = []
        
        print(f"Start pipeline {self.__serial_number}")
        # Configure depth and color streams
        self.__pipeline = rs.pipeline()
        self.__config = rs.config()
        self.__config.enable_device(self.__serial_number)
        # enable RGB streaming 
        self.__config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        # enable depth streaming 
        self.__config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        self.__pipeline.start(self.__config)
        self.pipelines.append(self.__pipeline)


        #self.__started = True
        #logging.debug('D455 ({}) camera is ready.'.format(self.__serial_number))

    #def get(self) -> rs.pose:
        #frames = self.__pipeline.wait_for_frames()
        #data = frames.get_pose_frame()
        #return data.get_pose_data()

    #def get_xyz(self):
        #data = self.get()
        #return data.translation.x, data.translation.y, data.translation.z,

def visualise_measurements(frames_devices):
    """
    Calculate the cumulative pointcloud from the multiple devices
    Parameters:
    -----------
    frames_devices : dict
    	The frames from the different devices
    	keys: str
    		Serial number of the device
    	values: [frame]
    		frame: rs.frame()
    			The frameset obtained over the active pipeline from the realsense device
    """
    for (device, frame) in frames_devices.items():
        color_image = np.asarray(frame[rs.stream.color].get_data())
        text_str = device
        print(text_str)
        #cv2.putText(color_image, text_str, (50,50), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0) )
        # Visualise the results
        text_str = f'Color image from RealSense Device Nr: {device}'
        cv2.namedWindow(text_str)
        cv2.imshow(text_str, color_image)
        cv2.waitKey(1)

if __name__ == "__main__":
    # 1 enlist all of the devices

    devs = find_devices_in_advanced_mode()
    width = 1280 
    height = 720 
    frame_rate = 15
    dispose_frame_for_stabilisation = 30

    try:
        rs_config = rs.config()
        rs_config.enable_stream(rs.stream.depth, width, height, rs.format.z16, frame_rate)
        rs_config.enable_stream(rs.stream.infrared, 1, width, height, rs.format.y8, frame_rate)
        rs_config.enable_stream(rs.stream.infrared, 2, width, height, rs.format.y8, frame_rate)
        rs_config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, frame_rate)
        #Use the device manager class to enable the devices and get the frames
        device_manager = DeviceManager(rs.context(), rs_config)
        device_manager.enable_all_devices()
        # Allow some frames for the auto-exposure controller to stablise
         
        while 1:
             for k in range(150):
                frames = device_manager.poll_frames()
            
                visualise_measurements(frames)
                device_manager.enable_emitter(True)
                device_extrinsics = device_manager.get_depth_to_color_extrinsics(frames)
                
    except KeyboardInterrupt:
        print("The program was interupted by the user. Closing the program...")

    finally:
        device_manager.disable_streams()
        cv2.destroyAllWindows()

    # 2 stream images from all devices

    #number_of_experiments = 2

    #serial_numbers = get_devices_serial_numbers()

    #print(f'Serial_numbers {serial_numbers}' )

    #sources = [D455CameraSource(serial_number) for serial_number in serial_numbers]

#    for camera_index, source in enumerate(sources):
#        for experiment_index in range(number_of_experiments):
#            print(experiment_index, camera_index,  source.get_serial_number(), datetime.datetime.now())

#    for experiment_index in range(number_of_experiments):
#        for camera_index, source in enumerate(sources):
#            print(experiment_index, camera_index, source.get_serial_number(),  datetime.datetime.now())