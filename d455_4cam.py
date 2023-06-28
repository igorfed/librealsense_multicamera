import pyrealsense2 as rs
import numpy as np
from camera import Camera
from image_ẁindow import ImgWindow
from camera_loop import AllCamerasLoop



if __name__ == "__main__":
    
    __d455 = AllCamerasLoop()
    #__d455.run_loop(camera_mode=0, N = 10)
    __d455.run_loop(camera_mode=2)
    print('done')
