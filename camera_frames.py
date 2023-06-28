import pyrealsense2 as rs
from typing import List
import numpy as np
from camera import Camera
from PIL import ImageFont, ImageDraw, Image
import tableprint
import io
import os 
from fonts import TTFontSource
import cv2
class RealsenseFramesToImage:
    '''
    Take all frames in one moment and interpret them as one image. 
    
    - Starts with the interpretation of each frame to separate the image. 
    - Connects all images together.
    '''
    def __init__(self):
        self.__casched_fonts = {}

    def get_image_from_frames(self, frames, add_tile: bool = True) -> np.array:
        # frameset <pyrealsense2.frameset Z16 RGB8 MOTION_XYZ32F MOTION_XYZ32F #42 @1686821341094.023926>
        # add_title True or Not
        img_frame_tuples, max_width, max_height  = Camera.get_images_from_video_frames( frames)

        if add_tile:
            images, max_height = self.__add_titles(img_frm_tuples=img_frame_tuples, 
                                                   max_height=max_height)
        else:
            images = [img_frame[0] for img_frame in img_frame_tuples]

        # 'data' or 'tex' kind of frames
        #images_from_text_frames = self.__images_from_text_frames(unused_frames, max_width, max_height)
        # together
        #images += images_from_text_frames
        #print('len(images)', len(images))
        if len(images) > 0:
            # concat all to one image
            ret_img = self.__concat_images(images, max_width, max_height)
        else:
            # placeholder for no frames (no images)
            ret_img = np.zeros(shape=(800, 600, 3))
        #print(ret_img[:640, :480])
        return ret_img
        
    def save_image_from_frames(self, frames, serials):
        
        img_frame_tuples, _, _  = Camera.get_images_from_video_frames( frames)

        #print(len(img_frame_tuples))

        return img_frame_tuples
    
    def __add_titles(self, img_frm_tuples: [(np.ndarray, rs.frame)],
                            max_height:int,
                            default_height: int = 40,
                            default_font_size: int = 28,
                            bacground_color = (255, 255, 255),
                            color = (0, 0, 0),
                            dx: int = 10,
                            dy: int = 10) -> ([np.ndarray], int):
        ret_images = []
        font = TTFontSource.get_font(size=default_font_size)
        for img, frame in img_frm_tuples:
            title = Camera.get_title(frame, whole=True)
            if len(img.shape) > 2:
                rgb = True
                height, width, _ = img.shape
                title_img = Image.new('RGB', (width, default_height), color=bacground_color)
            else:
                rgb = False
                height, width = img.shape
                r, g, b = bacground_color
                intcolor = (b << 16) | (g << 8) | r
                title_img = Image.new('RGB', (width, default_height), color=intcolor)

            draw = ImageDraw.Draw(title_img)
            draw.text((dx, dy), title, font=font, fill=color)
            #draw.text((dx, dy), title,  fill=color)
            title_img = np.array(title_img)
            if not rgb:
                title_img = title_img[:,:,0]
            #key = cv2.waitKey(1)
                
            ret_images.append(np.vstack((title_img, img)))
            #ret_images.append(img)
            print('-------',ret_images[-1].shape)
        return ret_images, max_height + default_height

    def __concat_images(
        self,
        images: [np.array],
        max_width: int,
        max_height: int,
        max_columns: int = 4,
        bacground_color=(255,255,255)
    ) -> np.array:
        # diferent images in the set, transform all to RGB
        images = [cv2.cvtColor(img,cv2.COLOR_GRAY2RGB) if len(img.shape) < 3 else img for img in images]
        # divide images to rows and columns
        images = [images[i:i + max_columns] for i in range(0, len(images), max_columns)]
        for row_index, rows_images in enumerate(images):
            # concat images in one rows
            for col_index, img in enumerate(rows_images):
                if col_index == 0:
                    # first one
                    col_img = img
                else:
                    col_img = np.hstack((col_img, img))
            # add placeholder to shor column
            for i in range(max_columns - len(rows_images)):
                placeholder_img = np.zeros((max_height, max_width, 3), np.uint8)
                placeholder_img[:, :] = bacground_color
                col_img = np.hstack((col_img, placeholder_img))
            # concat rows to one image
            if row_index == 0:
                # first one
                ret_img = col_img
            else:
                ret_img = np.vstack((ret_img, col_img))
        return ret_img




   
def check_if_dir_existed(dir_name, create=False):
	if not os.path.exists(dir_name):
		print(f'folder \t\t: {dir_name} is not available')
		if create:
			os.mkdir(dir_name)
			print(f'folder \t\t: {dir_name} created')	
	else:
		print(f'folder \t\t: {dir_name} is available')   