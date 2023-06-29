
import pyrealsense2 as rs
import numpy as np
from typing import List
import sys
import time
import cv2
import os
from queue import Queue


import threading as th


class Camera(th.Thread):
    '''
    Realsense Camera Class
    '''
    __colorizer = rs.colorizer()
    
    def __init__(self, serial_number :str, name: str, adv : rs.rs400_advanced_mode):
        self.__serial_number  = serial_number
        self.__name = name
        self.__colorizer = rs.colorizer()
        self.__pipeline = None
        self.__started = False
        self.advnc_mode = adv
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        dir_name = 'save'
        
        check_if_dir_existed(dir_name, create=True)
        check_if_dir_existed('frames', create=True)
        self.color_path = f'{dir_name}/{self.__serial_number}_rgb.avi'
        self.depth_path = f'{dir_name}/{self.__serial_number}_depth.avi'
        self.colorwriter = cv2.VideoWriter(self.color_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (1280,720), 1)
        self.depthwriter = cv2.VideoWriter(self.depth_path, cv2.VideoWriter_fourcc(*'XVID'), 30, (1280,720), 1)
        self.txt = f'{dir_name}/{self.__serial_number}.txt'
        self.f = open(self.txt, 'w')
        self.stop_flag = th.Event()
        self.stop_flag.set()
        self.queue = Queue()
        print("Advanced mode is", "enabled" if adv.is_enabled() else "disabled")
        self.__advanced_mode()
        self.__start_pipeline()
        self.__get_intrinsic()

    def __advanced_mode(self):
        # Get each control's current value
        print(f'{self.__name} : {self.__serial_number}')

        #print("Depth Control: \n", self.advnc_mode.get_depth_control())
        #print("RSM: \n", self.advnc_mode.get_rsm())
        #print("RAU Support Vector Control: \n", self.advnc_mode.get_rau_support_vector_control())
        #print("Color Control: \n", self.advnc_mode.get_color_control())
        #print("RAU Thresholds Control: \n", self.advnc_mode.get_rau_thresholds_control())
        #print("SLO Color Thresholds Control: \n", self.advnc_mode.get_slo_color_thresholds_control())
        #print("SLO Penalty Control: \n", self.advnc_mode.get_slo_penalty_control())
        #print("HDAD: \n", self.advnc_mode.get_hdad())
        #print("Color Correction: \n", self.advnc_mode.get_color_correction())
        #print("Depth Table: \n", self.advnc_mode.get_depth_table())
        #print("Auto Exposure Control: \n", self.advnc_mode.get_ae_control())
        #print("Census: \n", self.advnc_mode.get_census())


    def __start_pipeline(self):
        
        # Configure depth and color streams
        
        #ctx = rs.context()
        #devices = ctx.query_devices()
        #for dev in devices:
        #    dev.hardware_reset()
        #print("reset done")

       
        self.__pipeline = rs.pipeline()
        config = rs.config()
        config.enable_device(self.__serial_number)
        config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

        #Inter Cam Sync Mode
        #Description   : Inter-camera synchronization mode: 0:Default, 1:Master, 2:Slave, 3:Full Salve, 4-258:Genlock with burst count of 1-255 frames for each trigger, 259 and 260 for two frames per trigger with laser ON-OFF and OFF-ON.
        #Current Value : 1
        if (self.__serial_number == "039222250073"):
            MASTER = 1
        else:
            MASTER = 2

        self.prof = self.__pipeline.start(config)
        # Pipeline started
        self.__started = True
        print(f'{self.get_full_name()} camera is ready. Pipeline started') 
        
        

        sensors = self.prof.get_device().query_sensors()

        
        for sensor in sensors:              
            if sensor.supports(rs.option.auto_exposure_priority):
                aep = sensor.set_option(rs.option.auto_exposure_priority, 0)
                aep = sensor.get_option(rs.option.auto_exposure_priority)
                #print(f'{sensor} Auto Exposure {aep}')
            
            
        #exit            
                 
        
        #depth_sensor = prof.get_device().first_depth_sensor()   
        ##depth_scale = depth_sensor.get_depth_scale()
        #align_to = rs.stream.color
        #align = rs.align(align_to)


    def __get_intrinsic(self):
         
          # get camera intrinsics
        intr = self.prof.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        print('Camera Intrinsic')
        print(intr.width, intr.height, intr.fx, intr.fy, intr.ppx, intr.ppy)

    def get_full_name(self):
        return f'{self.__name} ({self.__serial_number})'
    

    def get_frames(self) -> List[rs.frame]:
        '''
        Return a frame do not care about type
        '''
        frameset = self.__pipeline.wait_for_frames()
        
        
        #print(f"frameset {frameset}")
        #frameset <pyrealsense2.frameset Z16 RGB8 MOTION_XYZ32F MOTION_XYZ32F #42 @1686821341094.023926>
        #frameset <pyrealsense2.frameset Z16 RGB8 MOTION_XYZ32F MOTION_XYZ32F #31 @1686821341101.560791>
        #frameset <pyrealsense2.frameset Z16 RGB8 MOTION_XYZ32F MOTION_XYZ32F #9 @1686821341263.020508>
        #frameset <pyrealsense2.frameset Z16 RGB8 MOTION_XYZ32F MOTION_XYZ32F #9 @1686821341788.717285>
        if frameset:
            return [f for f in frameset]
        else:
            return []
    
    @classmethod
    def get_images_from_video_frames(clc, frames):
        max_width = -1
        max_height = -1

        img_frame_tuples = []
        unused_frames = []
        #print(f'Len frameset {len(frames)}')
        i = 0

        #color_frame = frames.get_color_frame()
        #depth_frame = frames.get_depth_frame()

        for frame in frames:
            # We can only save video frames as pngs, so we skip the rest
            if frame.is_video_frame():
                if frame.is_depth_frame():
                    # extract depth Image
                    # convert images to numpy arrays
                    # To better visualize the depth data, we apply the colorizer on any incoming depth frames:
                    img = np.asanyarray(Camera.__colorizer.process(frame).get_data()).copy()
                else:
                    # extract color image
                    # convert images to numpy arrays
                    img = np.asanyarray(frame.get_data()).copy()

                max_height = max(max_height, img.shape[0])
                max_width  = max(max_width, img.shape[1])
                # image chunk
                img_frame_tuples.append((img,frame))
            
        #img = np.asanyarray(frames.get_infrared_data(1))
        #img_frame_tuples.append((img,frame))
        #print(max_width, max_height)
        return img_frame_tuples, max_width, max_height 

    @classmethod
    #def recording(clc, frames):
    #    for frame in frames:
    #        if frame.is_video_frame():
    #            if frame.is_depth_frame():
    #                img = np.asanyarray(Camera.__colorizer.process(frame).get_data()).copy()
    #                self.colo




    @classmethod
    def get_title(cls, frame: rs.frame, whole: bool) -> str:
        # <pyrealsense2.video_stream_profile: Fisheye(2) 848x800 @ 30fps Y8>
        profile_str = str(frame.profile)
        first_space_pos = profile_str.find(' ')
        whole_title = profile_str[first_space_pos + 1: -1]
        if whole:
            return whole_title
        return whole_title.split(' ')[0]
    
   
def check_if_dir_existed(dir_name, create=False):
	if not os.path.exists(dir_name):
		print(f'folder \t\t: {dir_name} is not available')
		if create:
			os.mkdir(dir_name)
			print(f'folder \t\t: {dir_name} created')	
	else:
		print(f'folder \t\t: {dir_name} is available')   