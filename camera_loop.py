import pyrealsense2 as rs
from camera import Camera
from camera_frames import RealsenseFramesToImage
from image_ẁindow import ImgWindow
from typing import List
import time
import cv2
import time


class AllCamerasLoop:
 
    def __init__(self):

        self.__cameras = self.get_all_conected_cameras()
        self.__frames_interpreter = RealsenseFramesToImage()
 
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
                
                # setup Sync Mode
                # Inter-camera synchronization mode: 0:Default, 1:Master, 2:Slave, 3:Full Salve, 4-258:Genlock with burst count of 1-255 frames for each trigger, 259 and 260 for two frames per trigger with laser ON-OFF and OFF-ON.

                if serial_number == "039222250073":
                    MASTER = 1
                else:
                    MASTER = 2
                ctx.query_devices()[0].first_depth_sensor().set_option(rs.option.inter_cam_sync_mode, MASTER)
                
                print(f'Found Device: {i}  {name} : {serial_number}: on USB {usb_type} ')
                print(f'\t Camera {serial_number} is : {ctx.query_devices()[0].first_depth_sensor().get_option(rs.option.inter_cam_sync_mode)} ')                     
                #   
                if device_suffix and not d.get_info(rs.camera_info.name).endswith(device_suffix):
                    continue
                ret_list.append([serial_number, name, rs.rs400_advanced_mode(d)])
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

    def frames2plot(self):
        # Here I plot RGB and Depth frames
        window = ImgWindow(name=self.__get_window_name())
        self.save = False
        j = 0
        timestr = time.strftime("%Y%m%d-%H%M%S")
        while not self.stop:
            frames = self.get_frames()
            ret_img = self.__frames_interpreter.get_image_from_frames(frames=frames, add_tile=False)
            window.show(ret_img)
            key = cv2.waitKey(1)
            self.stop = window.is_stopped(key)   
            self.save = window.is_save(key)

            if (self.save==True):
                m, n = 0, 0
                for i in range(len(ret_img)):
                    if i%2:
                        fname = f"frames/RGB_{self.save_serials[n]}_{timestr}_{j}.png"
                        n = n+1
                    else:
                        fname = f"frames/D_{self.save_serials[m]}_{timestr}_{j}.png"                        
                        m = m +1                                                
                    #cv2.imwrite(fname,ret_img[i][0])
                j = j + 1

            self.save = False
        self.f_close()



    def frames2avi(self, N):
        colorwriter, depthwriter = self.set_videos()
        j = 0 
        while not self.stop:
            # wait for pipeline
            frames = self.get_frames()
            img_frame_tuples = self.__frames_interpreter.save_image_from_frames(frames, self.save_serials)
            #total_elapsed = time.time()-date_start
            #self.f_time(self, i, date_start)
            m, n = 0, 0
            for i in range(len(img_frame_tuples)):
                if i%2:
                    colorwriter[n].write(img_frame_tuples[i][0])
                    n = n+1
                else:
                    depthwriter[m].write(img_frame_tuples[i][0])
                    m = m +1                                                
                
                #print('Frame num: %d, fps: %d' %(i, N/total_elapsed))
                #cv2.imwrite('1.png',img_frame_tuples[0][0])
                                       
            j = j +1
            if j == N:
                self.f_close()
                for i in range(4):
                    colorwriter[i].release()
                    depthwriter[i].release() 
                self.stop = True
            
    def frames2png(self, N):
        j = 0
        while not self.stop:
            frames = self.get_frames()
            img_frame_tuples = self.__frames_interpreter.save_image_from_frames(frames, self.save_serials)
            m, n = 0,0
            for i in range(len(img_frame_tuples)):
                if i%2:
                    fname = f"frames/RGB_{self.save_serials[n]}_{j}.png"
                    n = n+1
                else:
                    fname = f"frames/D_{self.save_serials[m]}_{j}.png"                        
                    m = m +1                                                
                cv2.imwrite(fname,img_frame_tuples[i][0])
            j = j + 1
            if j == N:
                self.f_close()
                self.stop = True
    def frames2pointCloud():
        pass

    def run_loop(self, camera_mode, N = 10):
        self.stop = False
        
        # Capture 10 frames to give autoexposure, etc. a chance to settle
        
        for i in range(10):
            _ = self.get_frames()
        
        print('Camera running')
        date_start = time.time()
        
        if camera_mode == 0:
            self.frames2plot()

        elif camera_mode ==1:
            # here i save RGB and Depth frames in AVI
            
            self.frames2avi(N)
        elif camera_mode ==2:
            
            self.frames2png(N)
        else:

            self.frames2pointCloud()
           
