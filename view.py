from tkinter import *
import time
import cv2, os
from model import *
import urllib.request
from dao import *
from threading import Thread

class GUI(Tk):
    def __init__(self, esp8266_url=None, video_url_in=0, video_url_out=1):
        Tk.__init__(self)
        self.frm_camera = Frame(self)
        self.frm_function = Frame(self, borderwidth=2, relief='solid')
        self.font = ("Arial", 15)
        # self.curr_frame_time = 0
        # self.prev_frame_time = 0
        self.video_url_in = video_url_in
        self.video_url_out = video_url_out
        self.esp8266_url = esp8266_url
        self.cap_in = cv2.VideoCapture(self.video_url_in)
        self.cap_out = cv2.VideoCapture(self.video_url_out)
        self.dao = DAO()
        self.list_license_plate = self.dao.find_all_license_plates()
        self.is_vehicle = False
        self.auto = False
        self.request_in = False # nếu đang gửi yêu cầu
        self.request_out = False
        self.curr_license_plate = str()
        self.model = Model()
        self.init_frame_function()
        self.config_frame()
        self.align_components()
        self.change_to_auto()

    def init_frame_function(self):
        self.frm_entrance = Frame(self.frm_function, borderwidth=1, relief='solid')
        self.frm_exit = Frame(self.frm_function, borderwidth=1, relief='solid')
        self.canvas_in = Canvas(self.frm_camera, width=320, height=240)
        self.canvas_out = Canvas(self.frm_camera, width=320, height=240)
        self.lbl_license_plate_img = Label(self.frm_function, text='Check')
        self.lbl_license_plate = Label(self.frm_function, text='Biển số xe', font=self.font)
        self.lbl_license_plate_text = Label(self.frm_function, text='')
        self.lbl_mode = Label(self.frm_function, text='Chế độ: Auto', font=self.font, anchor='e')
        self.lbl_entrance = Label(self.frm_function, text='Cửa vào', font=self.font)
        self.lbl_exit = Label(self.frm_function, text='Cửa ra', font=self.font)
        self.btn_change_mode = Button(self.frm_function, text='Đổi', command=self.change_mode)
        self.btn_entrance_open = Button(self.frm_entrance, text='MỞ', width=10, command=self.open_entrance_barrier)
        self.btn_entrance_close = Button(self.frm_entrance, text='ĐÓNG', width=10, command=self.close_entrance_barrier)
        self.btn_exit_open = Button(self.frm_exit, text='MỞ', width=10, command=self.open_exit_barrier)
        self.btn_exit_close = Button(self.frm_exit, text='ĐÓNG', width=10, command=self.close_exit_barrier)
        self.btn_end_program = Button(self.frm_function, text='END', width=20, bg='red')

    def config_frame(self):
        self.frm_function.grid_propagate(False)
        self.frm_entrance.grid_propagate(False)
        self.frm_exit.grid_propagate(False)
        self.frm_function.config(width=308, height=480)
        self.frm_entrance.config(width=150, height=180)
        self.frm_exit.config(width=150, height=180)

    def align_components(self):
        self.frm_camera.pack(side='left')
        self.frm_function.pack(pady=10)

        self.canvas_in.grid(row=0, column=0, columnspan=6, rowspan=8)
        self.canvas_out.grid(row=8, column=0, columnspan=6, rowspan=8)
        self.lbl_license_plate_img.grid(row=0, column=6, columnspan=2, rowspan=2)
        self.lbl_license_plate.grid(row=2, column=6, columnspan=2)
        self.lbl_license_plate_text.grid(row=3, column=6, columnspan=2)
        self.lbl_mode.grid(row=4, column=6, pady=20)
        self.lbl_entrance.grid(row=5, column=6, pady=10)
        self.lbl_exit.grid(row=5, column=7)
        self.frm_entrance.grid(row=6, column=6)
        self.frm_exit.grid(row=6, column=7)
        self.btn_change_mode.grid(row=4, column=7, padx=50)
        self.btn_entrance_open.grid(row=0, column=0, padx=40, pady=30, columnspan=2)
        self.btn_entrance_close.grid(row=1, column=0, padx=40, pady=50, columnspan=2)
        self.btn_exit_open.grid(row=0, column=0, padx=40, pady=30, columnspan=2)
        self.btn_exit_close.grid(row=1, column=0, padx=40, pady=50, columnspan=2)
        self.btn_end_program.grid(row=7, column=7, sticky='e')

    @staticmethod
    def convert_image(img):
        h, w = img.shape[:2]
        data = f'P6 {w} {h} 255 '.encode() + img[..., ::-1].tobytes()
        return PhotoImage(width=w, height=h, data=data, format='PPM')
    
    def update_camera_out(self):
        ret, frame =self.cap_out.read()
        if ret:
            list_detected_license_plates = set()
            if self.is_vehicle:
                frame, list_detected_license_plates = self.model.detect(ret, frame)
                if len(list_detected_license_plates):
                    detected_license_plate = list_detected_license_plates[0]
                    is_valid_car = dao.find_license_plate_by_name_and_status(detected_license_plate, 0)
                    if is_valid_car:
                        if not self.request_out:
                            self.request_out = True
                            thread = Thread(target=self.open_exit_barrier)
                            thread.start()
                else:
                    if self.request_out: # nếu đang yêu cầu mà xe đã đi qua thì mới gửi request đóng cửa
                        thread = Thread(target=self.close_exit_barrier)
                        thread.start()
            
            photo = GUI.convert_image(cv2.resize(frame, (320, 240)))

            self.canvas_out.create_image(0, 0, image=photo, anchor=NW)
            self.canvas_out.image = photo

            image_video_url = 'crop.jpg'
            if os.path.exists(image_video_url):
                crop_image = cv2.imread(image_video_url)
            else:
                crop_image = cv2.imread('nf.png')
            crop_image = cv2.resize(crop_image, (300, 100))
            crop_image_photo = GUI.convert_image(crop_image)
            self.lbl_license_plate_img.config(image=crop_image_photo)  # Cập nhật hình ảnh trên Label
            self.lbl_license_plate_img.image = crop_image_photo
            self.lbl_license_plate_text.config(text= ', '.join(list_detected_license_plates))

            # self.canvas_in.create_text(50, 50, text=str(fps), font=self.font, fill="green")
            self.after(15, self.update_camera_out)  

    def update_frame_camera(self, gate='in'):
        ret, frame = self.cap_in.read() if gate == 'in' else self.cap_out.read()
        if ret:
            list_detected_license_plates = set()
            if self.is_vehicle:
                frame, list_detected_license_plates = self.model.detect(ret, frame)
                if len(list_detected_license_plates) and list_detected_license_plates[0] in self.list_license_plate:
                    if not self.request_in:
                        self.request_in = True
                        self.curr_license_plate = list_detected_license_plates[0]
                        thread = Thread(target=self.open_entrance_barrier)
                        thread.start()
                else:
                    if self.request_in: # nếu đang yêu cầu mà xe đã đi qua thì mới gửi request đóng cửa
                        self.curr_license_plate = str()
                        thread = Thread(target=self.close_entrance_barrier)
                        thread.start()
            
            photo = GUI.convert_image(cv2.resize(frame, (320, 240)))

            self.canvas_in.create_image(0, 0, image=photo, anchor=NW)
            self.canvas_in.image = photo

            image_video_url = 'crop.jpg'
            if os.path.exists(image_video_url):
                crop_image = cv2.imread(image_video_url)
            else:
                crop_image = cv2.imread('nf.png')
            crop_image = cv2.resize(crop_image, (300, 100))
            crop_image_photo = GUI.convert_image(crop_image)
            self.lbl_license_plate_img.config(image=crop_image_photo)  # Cập nhật hình ảnh trên Label
            self.lbl_license_plate_img.image = crop_image_photo
            self.lbl_license_plate_text.config(text= ', '.join(list_detected_license_plates))

            # self.canvas_in.create_text(50, 50, text=str(fps), font=self.font, fill="green")
            self.after(15, self.update_frame_camera)  

    def run(self):
        thread1 = Thread(target=self.update_camera_out, args=())
        thread2 = Thread(target=self.update_frame_camera, args=('in', ))
        thread1.daemon = True
        thread2.daemon = True
        thread1.start()
        thread2.start()
        # self.update_camera_out()
        # self.update_frame_camera(gate='in')
        self.mainloop()


    # -----------------------------function----------------------------
    '''Control servo through HTTP request'''
    def send_request(self, url):
        n = urllib.request.urlopen(url) # send request to ESP

    def open_entrance_barrier(self):
        self.send_request(self.esp8266_url + "/openentrancebarrier")
        print("barrier is opening")

    
    def close_entrance_barrier(self):
        self.request_in = False
        if self.auto:
            time.sleep(3)
        if not self.request_in: # sau 2 giây mà biển số vẫn detect ra không trong csdl thì đóng cửa
            self.send_request(self.esp8266_url + "/closeentrancebarrier")
            print("barrier is closed")
    def open_exit_barrier(self):
        self.send_request(self.esp8266_url + "/openexitbarrier")
    def close_exit_barrier(self):
        self.send_request(self.esp8266_url + "/closeexitbarrier")
    def control_barrier(self):
        self.open_entrance_barrier()


    '''change mode control'''
    def change_to_auto(self):
        self.is_vehicle = True
        self.lbl_mode.config(text='Chế độ: Auto')
        for child in self.frm_entrance.winfo_children():
            child.configure(state='disable')
        for child in self.frm_exit.winfo_children():
            child.configure(state='disable')

    def change_to_human(self):
        self.is_vehicle = False
        self.lbl_mode.config(text='Chế độ: Human')
        for child in self.frm_entrance.winfo_children():
            child.configure(state='normal')
        for child in self.frm_exit.winfo_children():
            child.configure(state='normal')

    def change_mode(self):
        self.auto = not self.auto
        if self.auto:
            self.change_to_auto()
        else:
            self.change_to_human()
    


    

if __name__ == '__main__':
    a = GUI(esp8266_url="http://192.168.0.105", video_url_out="http://192.168.0.101:4747/video")
    a.run()
