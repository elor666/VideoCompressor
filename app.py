import customtkinter as ctk
import ffmpeg
import threading
import os
from functools import partial
import itertools


WIDTH = 900
HEIGHT = 600

def find_output(output_f, f_name, ext):
  actualname = "%s%s" % (output_f+"\\"+f_name+"-COMPRESS", ext)
  c = itertools.count()
  while os.path.exists(actualname):
      actualname = "%s(%d)%s" % (output_f+"\\"+f_name+"-COMPRESS", next(c), ext)
  return actualname


class App(ctk.CTk):
    def __init__(self):
        #ctk.set_appearance_mode("dark")
        #ctk.set_default_color_theme("dark-blue")
        ctk.CTk.__init__(self,fg_color="#130208")
        self.title("Video Compressor")
        self.geometry(f"{WIDTH}x{HEIGHT}")
        #self.resizable(False,False)
        self.minsize(WIDTH,HEIGHT)
        #self.iconbitmap("icon.ico")
        self._frame = None
        self.switch_frame(MainFrame)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame


class MainFrame(ctk.CTkFrame):
    def __init__(self, master):
        ctk.CTkFrame.__init__(self, master,fg_color="#1f0510")
        self.place(anchor='center', relx=0.5, rely=0.5, relheight=0.95, relwidth=0.95)
        
        self.filepaths = []
        self.outputpath = ""
        
        ctk.CTkLabel(self,text="VideoCompressor",font=("Impact",25)).pack()
        
        self.file_button = ctk.CTkButton(self,
                                         text="Choose File", 
                                         command=lambda:self.choose_file(),
                                         fg_color="#460e2b",
                                         hover_color="#7c183c",font=("Impact",20))
        self.file_button.place(anchor="e", rely=0.75, relx=0.25)
        
        self.output_button = ctk.CTkButton(self,
                                           text="Choose Output", 
                                           command=lambda:self.choose_output(),
                                           fg_color="#460e2b",
                                           hover_color="#7c183c",font=("Impact",20))
        self.output_button.place(anchor="w", rely=0.75, relx=0.75)
        
        self.output_button._command
        
        self.output_label = ctk.CTkLabel(self,text="Output Folder:\n",font=("Impact",20))
        self.output_label.place(anchor='center',rely=0.85,relx=0.5)
        
        self.compress_button = ctk.CTkButton(self,
                                             text="Compress",
                                             font=("Impact",20),
                                             command=lambda:self.start_compress(),
                                             fg_color="#460e2b",
                                             hover_color="#7c183c")
        self.compress_button.place(anchor="center",rely=0.75, relx=0.5)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self,fg_color="#1f0510",label_text="Video Files",label_font=("Impact",20))
        self.scrollable_frame.place(anchor="n",rely=0.05, relx=0.5,relwidth=0.75,relheight=0.5)
        
        self.remove_buttons = []
        self.file_names = []
        
        
        
    def choose_output(self):
        self.outputpath = ctk.filedialog.askdirectory(initialdir = "/",title="Select a Save Location")
        self.output_label.configure(text="Output Folder:\n"+self.outputpath)
        
    
    def choose_file(self):
      files = ctk.filedialog.askopenfilenames(initialdir = "/", title = "Select a File", filetypes=[("Video files", ".mp4")])
      
      for i,name in enumerate(list(files)):
        self.remove_buttons.append(ctk.CTkRadioButton(self.scrollable_frame,text="",border_color="red",width=11,radiobutton_height=11,radiobutton_width=11,text_color="#1f0510",command=partial(self.remove_file, i)))
        tname = "".join([item for i,item in enumerate(name) if i<=65]+["..."]) if len(name)>65 else name
        self.file_names.append(ctk.CTkLabel(self.scrollable_frame,text=tname))
        
      self.filepaths += list(files)
      self.show_files()
    
    
    def show_files(self):
      [item.grid_forget() for item in self.remove_buttons]
      [item.grid_forget() for item in self.file_names]
      for j in range(len(self.remove_buttons)):
        self.remove_buttons[j].configure(command=partial(self.remove_file, j))
        self.remove_buttons[j].grid(row=j,column=0)
        self.file_names[j].grid(row=j,column=1,sticky="W")
  
    
    def remove_file(self,index):
      self.filepaths.remove(self.filepaths[index])
      
      self.remove_buttons[index].destroy()
      self.remove_buttons.remove(self.remove_buttons[index])
      
      self.file_names[index].destroy()
      self.file_names.remove(self.file_names[index])
      
      self.show_files()
    
    
    def start_compress(self):
      if self.filepaths != [] and self.outputpath != "":
        self.disable_buttons()
        print("started compress")
        
        thread = threading.Thread(target=self.compress_queue)
        thread.start()
        self.after(2000,self.thread_closer, thread)
    
    
    def compress_queue(self):
      for i,path in enumerate(self.filepaths):
        if str(self.remove_buttons[i]._border_color) == "green":
          continue
        else:
          file_name, ext = os.path.splitext(os.path.basename(path))
          self.remove_buttons[i].configure(border_color="orange")
          self.compress(path,find_output(self.outputpath,file_name,ext))
          self.remove_buttons[i].configure(border_color="green")
    
    
    def thread_closer(self,thread):
      thread.join(timeout=0.5)
      
      if thread.is_alive():
        self.after(2000,self.thread_closer, thread)
      else:
        print("thread ended")
        self.enable_buttons()
    
    def compress(self,file_path : str, output_path : str):
      fle = ffmpeg.input(file_path)
      ffmpeg.output(fle,output_path,**{'vcodec': 'libx265', 'crf': 28}).overwrite_output().run()
      
    
    
    def disable_buttons(self):
      self.compress_button.configure(state=ctk.DISABLED)
      self.file_button.configure(state=ctk.DISABLED)
      self.output_button.configure(state=ctk.DISABLED)
      [item.configure(state=ctk.DISABLED,border_color="grey" if item._border_color!="green" else item._border_color) for item in self.remove_buttons]
    
    def enable_buttons(self):
      self.compress_button.configure(state=ctk.NORMAL)
      self.file_button.configure(state=ctk.NORMAL)
      self.output_button.configure(state=ctk.NORMAL)
      [item.configure(state=ctk.NORMAL, border_color="red" if item._border_color!="green" else item._border_color) for item in self.remove_buttons]
    
if __name__ == "__main__":    
  app = App()
  app.mainloop()
