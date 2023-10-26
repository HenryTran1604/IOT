from tkinter import *
import time
import cv2, os
from model import *
import urllib.request
from dao import *
from threading import Thread

class GUI(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.frm_camera = Frame(self)
        self.frm_function = Frame(self, borderwidth=2, relief='solid')
        self.font = ("Arial", 15)
        self.curr_frame_time = 0
        self.prev_frame_time = 0
        self.video_url = 0
        self.esp8266_url = "http://192.168.0.100"
        self.cap = cv2.VideoCapture(self.video_url)
        self.list_license_plate = get_all_license_plates()
        self.is_vehicle = True
        self.auto = True
        self.requesting = False # nếu đang gửi yêu cầu
        self.curr_license_plate = str()
        self.model = Model()
        self.init_frame_function()
        self.config_frame()
        self.align_components()
        self.change_to_auto()

    def init_frame_function(self):
        self.frm_entrance = Frame(self.frm_function, borderwidth=1, relief='solid')
        self.frm_exit = Frame(self.frm_function, borderwidth=1, relief='solid')
        self.canvas = Canvas(self.frm_camera, width=640, height=480)
        self.lbl_license_plate_img = Label(self.frm_function, text='Check')
        self.lbl_license_plate = Label(self.frm_function, text='Biển số xe', font=self.font)
        self.lbl_license_plate_text = Label(self.frm_function, text='')
        self.lbl_mode = Label(self.frm_function, text='Chế độ: Auto', font=self.font, anchor='e')
        self.lbl_entrance = Label(self.frm_function, text='Cửa vào', font=self.font)
        self.lbl_exit = Label(self.frm_function, text='Cửa ra', font=self.font)
        self.btn_change_mode = Button(self.frm_function, text='Đổi', command=self.change_mode)
        self.btn_entrance_open = Button(self.frm_entrance, text='MỞ', width=10, command=self.open_entrance_barrier)
        self.btn_entrance_close = Button(self.frm_entrance, text='ĐÓNG', width=10, command=self.close_entrance_barrier)
        self.btn_exit_open = Button(self.frm_exit, text='MỞ', width=10)
        self.btn_exit_close = Button(self.frm_exit, text='ĐÓNG', width=10)
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

        self.canvas.grid(row=0, column=0, columnspan=6, rowspan=8)
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

    def update_frame_camera(self):
        ret, frame = self.cap.read()
        if ret:
            self.curr_frame_time = time.time()
            fps = 1 / (self.curr_frame_time - self.prev_frame_time)
            fps = int(fps)
            self.prev_frame_time = self.curr_frame_time
            list_detected_license_plates = set()
            if self.is_vehicle:
                frame, list_detected_license_plates = self.model.detect(ret, frame)
                if len(list_detected_license_plates) and list_detected_license_plates[0] in self.list_license_plate:
                    if not self.requesting:
                        self.requesting = True
                        self.curr_license_plate = list_detected_license_plates[0]
                        thread = Thread(target=self.open_entrance_barrier)
                        thread.start()
                else:
                    if self.requesting: # nếu đang yêu cầu mà xe đã đi qua thì mới gửi request đóng cửa
                        self.curr_license_plate = str()
                        thread = Thread(target=self.close_entrance_barrier)
                        thread.start()
            
            photo = GUI.convert_image(frame)

            self.canvas.create_image(0, 0, image=photo, anchor=NW)
            self.canvas.image = photo

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

            self.canvas.create_text(50, 50, text=str(fps), font=self.font, fill="green")
            self.after(15, self.update_frame_camera)  

    def run(self):
        self.update_frame_camera()
        self.mainloop()


    # -----------------------------function----------------------------
    '''Control servo through HTTP request'''
    def send_request(self, url):
        n = urllib.request.urlopen(url) # send request to ESP

    def open_entrance_barrier(self):
        self.send_request(self.esp8266_url + "/openentrancebarrier")
        print("barrier is opening")

    
    def close_entrance_barrier(self):
        self.requesting = False
        time.sleep(3)
        if not self.requesting: # sau 2 giây mà biển số vẫn detect ra không trong csdl thì đóng cửa
            self.send_request(self.esp8266_url + "/closeentrancebarrier")
            print("barrier is closed")

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
    a = GUI()
    a.run()
