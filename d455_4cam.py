import pyrealsense2 as rs
import numpy as np
from camera import Camera
from image_ẁindow import ImgWindow
from camera_loop import AllCamerasLoop
import argparse

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-cm",   "--camera_mode",  
                        type=int, 
                        required=False, 
                        default=0,
                        help="default 0 - image show, 1- save n frame into avi, 2 - save n frames in png")
    
    parser.add_argument("-n",   "--n",  
                        type=int,
                        default=10, 
                        required=False, help="save N frames")
    return vars(parser.parse_args())

if __name__ == "__main__":
    print('--------------------------------')
    args = arg_parser()
    print(args)
    print('--------------------------------')
    camera_mode = args['camera_mode']
    n = args['n']
    __d455 = AllCamerasLoop()
    __d455.run_loop(camera_mode=camera_mode, N=n)
    #__d455.run_loop(camera_mode=2, N=100)
    print('done')
