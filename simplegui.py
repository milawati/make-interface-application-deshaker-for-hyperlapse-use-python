from Tkinter import *
import tkFileDialog
import os

#PERINTAH UNTUK TOMBOL OPEN
class Video(object):
    def __init__(self, path):
        self.path = path

    def play(self):
        from os import startfile
        startfile(self.path)
       
class Movie_MP4(Video):
    type = "MP4"

class Application(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.parent.title("Software Video Stabilizer")
        self.pack(fill=BOTH, expand=1)
        
        self.label = Label(self, text="VIDEO STABILIX",font=("Cambria",20))
        self.label.pack()
        
        self.insertButt = Button(self, text="Insert Link Video", background='red', width=10, font=("Comic Sans Ms",12),fg="black", command=self.onOpen)
        self.insertButt.pack(side=TOP, anchor=W, fill=X, expand=NO)
        
        self.openButt = Button(self, text="Open Video", background='red', width=10, font=("Comic Sans Ms",12),fg="black", command=self.reveal)
        self.openButt.pack(side=TOP, anchor=W, fill=X, expand=NO)
        
        self.deshakerButt = Button(self, text="Proses Deshaker", background='red', width=10, font=("Comic Sans Ms",12),fg="black", command=self.cmd)
        self.deshakerButt.pack(side=TOP, anchor=W, fill=X, expand=NO)

        self.labelvideo = Label(self, text="LINK VIDEO", bg="red")
        self.labelvideo.pack(ipadx=3000, pady=20)
        
        self.txt = Entry(self, bg='white', width=50)
        self.txt.pack(side=TOP)

    def reveal(self):
        content = self.txt.get()

        if content == "C:/Python27/hyperlapse.mp4":
            content = Movie_MP4(r"C:\Python27\hyperlapse.mp4")
            raw_input
            content.play()
            
#PERINTAH UNTUK TOMBOL INSERT VIDEO
    def onOpen(self):
        ftypes = [('All files', '*')]
        dlg = tkFileDialog.askopenfilename()
        print dlg
        self.txt.insert(END, dlg)
        return

#PERINTAH MEMANGGIL CMD
    def cmd(self):
        os.system('cmd.exe')
        open


#MENAMPILKAN SEMUA
root = Tk()
root.title("Video Stabilizer")
root.geometry("500x500")
app = Application(root)
app = Video(root)
app = Movie_MP4(root)
root.mainloop()

