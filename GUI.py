from tkinter import *
import time
import cv2, os
from webcam import *

class GUI(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.frm_camera = Frame(self)
        self.frm_function = Frame(self, borderwidth=2, relief='solid')
        self.font = ("Arial", 15)
        self.curr_frame_time = 0
        self.prev_frame_time = 0
        self.path = 0
        self.cap = cv2.VideoCapture(self.path)
        self.auto = True
        self.model = Model()
        self.init_frame_function()
        self.config_frame()
        self.align_components()
        self.change_to_auto()

    def init_frame_function(self):
        self.frm_entrance = Frame(self.frm_function, borderwidth=1, relief='solid')
        self.frm_exit = Frame(self.frm_function, borderwidth=1, relief='solid')
        self.canvas = Canvas(self.frm_camera, width=640, height=480)
        self.lbl_license_img = Label(self.frm_function, text='Check')
        self.lbl_license_info = Label(self.frm_function, text='Biển số xe', font=self.font)
        self.lbl_mode = Label(self.frm_function, text='Chế độ: Auto', font=self.font)
        self.lbl_entrance = Label(self.frm_function, text='Cửa vào', font=self.font)
        self.lbl_exit = Label(self.frm_function, text='Cửa ra', font=self.font)
        self.btn_change_mode = Button(self.frm_function, text='Đổi')
        self.btn_entrance_open = Button(self.frm_entrance, text='MỞ', width=10)
        self.btn_entrance_close = Button(self.frm_entrance, text='ĐÓNG', width=10)
        self.btn_exit_open = Button(self.frm_exit, text='MỞ', width=10)
        self.btn_exit_close = Button(self.frm_exit, text='ĐÓNG', width=10)
        self.btn_end_program = Button(self.frm_function, text='END', width=20, bg='red')

    def config_frame(self):
        self.frm_function.grid_propagate(False)
        self.frm_entrance.grid_propagate(False)
        self.frm_exit.grid_propagate(False)
        self.frm_function.config(width=308, height=480)
        self.frm_entrance.config(width=150, height=200)
        self.frm_exit.config(width=150, height=200)

    def change_to_auto(self):
        for child in self.frm_entrance.winfo_children():
            child.configure(state='disable')
        for child in self.frm_exit.winfo_children():
            child.configure(state='disable')

    def change_to_human(self):
        for child in self.frm_entrance.winfo_children():
            child.configure(state='normal')
        for child in self.frm_exit.winfo_children():
            child.configure(state='normal')

    def align_components(self):
        self.frm_camera.pack(side='left')
        self.frm_function.pack(pady=10)

        self.canvas.grid(row=0, column=0, columnspan=6, rowspan=8)
        self.lbl_license_img.grid(row=0, column=6, columnspan=2, rowspan=2)
        self.lbl_license_info.grid(row=2, column=6, columnspan=2, sticky='nsew')
        self.lbl_mode.grid(row=3, column=6, columnspan=2, pady=20)
        self.lbl_entrance.grid(row=4, column=6, pady=10)
        self.lbl_exit.grid(row=4, column=7)
        self.frm_entrance.grid(row=5, column=6)
        self.frm_exit.grid(row=5, column=7)
        self.btn_change_mode.grid(row=3, column=7, padx=5)
        self.btn_entrance_open.grid(row=0, column=0, padx=40, pady=30, columnspan=2)
        self.btn_entrance_close.grid(row=1, column=0, padx=40, pady=50, columnspan=2)
        self.btn_exit_open.grid(row=0, column=0, padx=40, pady=30, columnspan=2)
        self.btn_exit_close.grid(row=1, column=0, padx=40, pady=50, columnspan=2)
        self.btn_end_program.grid(row=6, column=7, sticky='e')

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
            frame = self.model.detect(ret, frame)
            photo = GUI.convert_image(frame)

            self.canvas.create_image(0, 0, image=photo, anchor=NW)
            self.canvas.image = photo

            image_path = 'crop.jpg'
            if os.path.exists(image_path):
                crop_image = cv2.imread(image_path)
            else:
                crop_image = cv2.imread('nf.png')
            crop_image = cv2.resize(crop_image, (300, 100))
            crop_image_photo = GUI.convert_image(crop_image)
            self.lbl_license_img.config(image=crop_image_photo)  # Cập nhật hình ảnh trên Label
            self.lbl_license_img.image = crop_image_photo

            self.canvas.create_text(50, 50, text=str(fps), font=("Arial", 20), fill="red")
            self.after(15, self.update_frame_camera)  

    def run(self):
        self.update_frame_camera()
        self.mainloop()
if __name__ == '__main__':
    a = GUI()
    a.run()
