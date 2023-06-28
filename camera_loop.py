import pyrealsense2 as rs
from camera import Camera
from camera_frames import RealsenseFramesToImage
from image_ẁindow import ImgWindow
from typing import List
import time
import cv2
class AllCamerasLoop:
    '''
    Take info from all conected cameras in the loop.
    '''

    def __init__(self):

        self.__cameras = self.get_all_conected_cameras()
        self.__frames_interpreter = RealsenseFramesToImage()
        #print(len(self.__cameras))

    def get_all_conected_cameras(self) -> List[Camera]:
        
        def get_conected_cameras_info(device_suffix: str) -> [[str, str, rs.rs400_advanced_mode]]:
            '''
            Return list of (serial number,names) conected devices.
            Eventualy only fit given suffix (like T265, D415, ...)
            (based on https://github.com/IntelRealSense/librealsense/issues/2332)
            '''
            self.save_serials = []
            ret_list = []
            ctx = rs.context()
            i =  0
            self.advnc_mode = []
            devices = ctx.devices
            for d in devices:
                serial_number = d.get_info(rs.camera_info.serial_number)
                name = d.get_info(rs.camera_info.name)
                usb_type = d.get_info(rs.camera_info.usb_type_descriptor)
                print(f'Found Device: {i}  {name} : {serial_number}: on USB {usb_type} ')
                if device_suffix and not d.get_info(rs.camera_info.name).endswith(device_suffix):
                    continue
                ret_list.append([serial_number, name, rs.rs400_advanced_mode(d)])
                print('-----------------', type(rs.rs400_advanced_mode(d)))
                self.advnc_mode.append(rs.rs400_advanced_mode(d))
                i = i +1
            return ret_list

        cameras = get_conected_cameras_info(device_suffix='D455')
        __camera = []
        for serial_number, name, advnc_mode in cameras:
            
            __camera.append(Camera(serial_number=serial_number, name=name, adv=advnc_mode))
            self.save_serials.append(serial_number)
        self.save_all_serials()
        return __camera    
    
    def save_all_serials(self):
        with open(f'serials.txt', 'w') as fp:
            for item in self.save_serials:
            # write each item on a new line
                fp.write("%s\n" % item)
        fp.close()                
        print('Done')
        

    def __get_window_name(self):
        s = ''
        for camera in self.__cameras:
            if s:
                s += ', '
            s += camera.get_full_name()
        return s
    
    def get_frames(self) -> List[rs.frame]:
        '''
        Return frames in given order. 
        '''
        ret_frames = []

        for camera in self.__cameras:
            frames = camera.get_frames()
            if frames:
                ret_frames += frames

        return ret_frames


    def set_videos(self):
        colorwriter = []
        depthwriter = []
        for camera in self.__cameras:
            colorwriter.append(camera.colorwriter)
            depthwriter.append(camera.depthwriter)
        return colorwriter, depthwriter



    def f_close(self):
        for camera in self.__cameras:
            camera.f.close()
        
    #def f_time(self, i, date_start):
    #    for camera in self.__cameras:
    #        camera.f.write(str(time.time()*1000)+'\n')



    def run_loop(self, camera_mode, N = 10):
        stop = False
        date_start = time.time()
        if camera_mode == 0:
            # Here I plot RGB and Depth frames
            window = ImgWindow(name=self.__get_window_name())
            while not stop:
                frames = self.get_frames()
                ret_img = self.__frames_interpreter.get_image_from_frames(frames=frames, add_tile=False)
                window.show(ret_img)
                stop = window.is_stopped()   
            self.f_close()
        else:
            # here i save RGB and Depth frames in AVI
            colorwriter, depthwriter = self.set_videos()
            for i in range (N):
                # wait for pipeline
                frames = self.get_frames()
                img_frame_tuples = self.__frames_interpreter.save_image_from_frames(frames, self.save_serials)
                total_elapsed = time.time()-date_start
                
                #self.f_time(self, i, date_start)
                m, n = 0,0

                for i in range(len(img_frame_tuples)):
                    if i%2:
                        colorwriter[n].write(img_frame_tuples[i][0])
                        n = n+1
                    else:
                        depthwriter[m].write(img_frame_tuples[i][0])
                        m = m +1                                                
                
                #print('Frame num: %d, fps: %d' %(i, N/total_elapsed))
                #cv2.imwrite('1.png',img_frame_tuples[0][0])
            for i in range(4):
                colorwriter[i].release()
                depthwriter[i].release()                                        

            self.f_close()
            
            exit
            #frame_save = window.is_single_frame_save()
            
            #if save == True:
            #    self.__frames_interpreter.save_image_from_frames(frames)
            #else:                
            #ret_img = self.__frames_interpreter.get_image_from_frames(frames=frames, add_tile=False)
            
            #if frame_save == False:
            
            #window.show(ret_img)
            #stop = window.is_stopped()   
                
                
        #    frames = self.get_frames()
        #    window.swow(self.__frames_interpreter.get_image_from_frames(frames))
        #    stop = window.is_stopped()
