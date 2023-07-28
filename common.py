import pyrealsense2 as rs
from typing import List
import cv2
import numpy as np
from image_ẁindow import ImgWindow
class D455:
    '''
    Realsense Camera Class
    '''
    def __init__(self, serial_number :str, name: str):
        self.__serial_number  = serial_number
        self.__name = name
        self.__pipeline = None
        self.__started = False

    def get_full_name(self):
        return f'{self.__name} ({self.__serial_number})'
    
class D455Frames2Image:
    '''
    Take all frames in one moment and interpret them as one image. 
    
    - Starts with the interpretation of each frame to separate the image. 
    - Connects all images together.
    '''

    def __init__(self):
        self.__casched_fonts = {}


class ImgWindow:
    '''
    Window from OpenCV for showing the result [in the loop].
    '''
    def __init__(self, name: str = 'ImgWindow', type: int = cv2.WINDOW_NORMAL):
        self._name = name
        cv2.namedWindow(self._name, type)

    def swow(self, img_array: np.ndarray) -> bool:
        if img_array is None:
            return True
        cv2.imshow(self._name, img_array)
        return True

    def is_stopped(self) -> bool:
        key = cv2.waitKey(1)
        if key == ord('q') or key == 27:
            return True
        return cv2.getWindowProperty(self._name, cv2.WND_PROP_VISIBLE) < 1
    
class D455Loop:



    def __init__(self):

        self.__d455_cameras = self.get_all_connected_cameras(device_suffix='D455')
        self.__frames_interpreter = D455Frames2Image()

    def get_devices_serial_numbers(self, device_suffix:str='D455')-> [(str, str)]:
        '''
        Return list of serial numbers conected devices.
        Eventualy only fit given suffix (like T265, D415, ...)`
        (based onhttps://rahulvishwakarma.wordpress.com/2019/08/17/realsense-435i-depth-rgb-multi-camera-setup-and-opencv-python-wrapper-intel-realsense-sdk-2-0-compiled-from-source-on-win10/)
        '''
        ret_list = []
        ctx = rs.context()
        for d in ctx.devices:
            serial_number = d.get_info(rs.camera_info.serial_number)
            name = d.get_info(rs.camera_info.name)

            print(f'Found Device: {name} : {serial_number}')
            if device_suffix and not d.get_info(rs.camera_info.name).endswith(device_suffix):
                continue
        
            ret_list.append((serial_number, name))
        print (ret_list)
        return ret_list
    

    def get_all_connected_cameras(self, device_suffix='D455')->[D455]:
        
        cameras = self.get_devices_serial_numbers(device_suffix='D455')        
        for serial_number, name in cameras:
            return [D455(serial_number=serial_number, name=name)] 
    
    def __get_window_name(self):
        s = ''
        for camera in self.__d455_cameras:
            if s:
                s += ', '
            s =s + camera.get_full_name()

        return s

    def get_frames(self) -> [rs.frame]:
        '''
        Return frames in given order. 
        '''
        ret_frames = []

        for camera in self.__d455_cameras:
            frames = camera.get_frames()
            if frames:
                ret_frames += frames
        return ret_frames
    

    def run_loop(self):
        stop = False
        name=self.__get_window_name()
        print(f'Name of Window {name}')
        
        window = ImgWindow(name=name)
        while not stop:
            frames = self.get_frames()

