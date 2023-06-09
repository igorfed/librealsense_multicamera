import pyrealsense2 as rs
import logging
import datetime
import sys
from pprint import pprint

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
        if device_suffix and not d.get_info(rs.camera_info.name).endswith(device_suffix):
            continue
        ret_list.append(d.get_info(rs.camera_info.serial_number))
    return ret_list

class D455CameraSource:
    def __init__(self, serial_number:str):
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
        print("Start pipeline")
        # Configure depth and color streams
        self.__pipeline = rs.pipeline()
        self.__config = rs.config()
        self.__config.enable_device(self.__serial_number)
        self.__config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.__pipeline.start(self.__config)
        #self.__started = True
        #logging.debug('D455 ({}) camera is ready.'.format(self.__serial_number))

    #def get(self) -> rs.pose:
        #frames = self.__pipeline.wait_for_frames()
        #data = frames.get_pose_frame()
        #return data.get_pose_data()

    #def get_xyz(self):
        #data = self.get()
        #return data.translation.x, data.translation.y, data.translation.z,

if __name__ == "__main__":
    number_of_experiments = 2
    serial_numbers = get_devices_serial_numbers()

    print('Serial experiment', '-' * 50)
    print(f'Serial_numbers {serial_numbers}' )
    sources = [D455CameraSource(serial_number) for serial_number in serial_numbers]

    for camera_index, source in enumerate(sources):
        for experiment_index in range(number_of_experiments):
            print(experiment_index, camera_index,  source.get_serial_number(), datetime.datetime.now())

    for experiment_index in range(number_of_experiments):
        for camera_index, source in enumerate(sources):
            print(experiment_index, camera_index, source.get_serial_number(),  datetime.datetime.now())