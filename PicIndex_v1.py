import Tkinter as tk
import tkMessageBox
import Tkconstants as tkc
import tkFileDialog
from PIL import Image, ImageTk
import os
import threading
from reportlab.pdfgen.canvas import Canvas
import reportlab.lib as rll

rT = 'sunken'
bW = 2

class pic_load_thread(threading.Thread):
    def __init__(self, threadID, parent):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.parent = parent
        
    def run(self):
        self.parent.load()

class pic_widget(tk.Label):
    def __init__(self, parent, path, name, size):
        self.selected = False
        self.path = path
        self.name = name
        self.size = size
        tk.Label.__init__(self, parent, text=self.name, compound=tkc.TOP, borderwidth=1, relief=rT)
        self.image = Image.open(os.path.join(path, name))
        self.set_thumbnail()
        self.bind("<Button-1>", self.clicked)
        
    def set_thumbnail(self):
        im = self.image.copy()
        im.thumbnail((self.size-5, self.size-5))
        self.photo = ImageTk.PhotoImage(im)
        self.configure(image=self.photo)
        
    def clicked(self, event):
        if (event.state & 0x0001):
            self.master.master.master.shift_select(self.name)
        elif self.selected:
            self.unselect()
        else:
            self.select()
        self.master.master.master.last_sel = self.name
        #print("You clicked on picture", self.name)
    
    def unselect(self):
        self.configure(background='light grey')
        self.selected=False
        
    def select(self):
        self.configure(background='yellow')
        self.selected=True
    
    def is_selected(self):
        return self.selected
        
    def resize(self, size):
        self.size = size
        self.set_thumbnail()

class selection(tk.Frame):
    def __init__(self, parent, **args):
        tk.Frame.__init__(self, parent, args)
        self.parent = parent
        self.working_dir = '/'
        self.last_sel = ""
        self.pics = {}
        self.packing_width = 1
        self.pic_size = 150
        
        # Setup widgets
        self.buttons = tk.Frame(self, relief=rT, borderwidth=bW)
        self.pictures = tk.Frame(self, relief=rT, borderwidth=bW)
        self.sel_dir = tk.Button(self.buttons, text='Select Directory', command=self.new_dir_selection)
        self.sel_all = tk.Button(self.buttons, text='Select All', command=self.select_all)
        self.sel_non = tk.Button(self.buttons, text='Select None', command=self.select_none)
        self.big = tk.Button(self.buttons, text='Enlarge', command=self.enlarge)
        self.sml = tk.Button(self.buttons, text='Shrink', command=self.shrink)
        self.clear = tk.Button(self.buttons, text='Remove Unselected', command=self.clear)
        self.scrollbar = tk.Scrollbar(self.pictures)
        self.canvas = tk.Canvas(self.pictures, yscrollcommand=self.scrollbar.set)
        
        # Pack all widgets
        self.buttons.pack(side=tkc.LEFT, fill=tkc.Y)
        self.pictures.pack(side=tkc.RIGHT, fill=tkc.BOTH, expand=1)
        self.sel_dir.pack(fill='x')
        self.clear.pack(fill='x')
        self.sel_all.pack(fill='x')
        self.sel_non.pack(fill='x')
        self.big.pack(fill='x')
        self.sml.pack(fill='x')
        self.scrollbar.pack(side=tkc.RIGHT, fill=tkc.Y)
        self.canvas.pack(side=tkc.LEFT, fill=tkc.BOTH)
        self.scrollbar.config(command=self.canvas.yview)
        self.pictures.bind("<Configure>", self.pictures_resized)
        
    def new_dir_selection(self):
        self.working_dir = tkFileDialog.askdirectory(initialdir="/home/charles/Desktop/picidxer", title="Select Directory")
        id = self.canvas.create_text(self.canvas.winfo_width()/2, self.canvas.winfo_height()/2, text="loading")
        self.canvas.update_idletasks()
        self.load()
        self.canvas.delete(id)
        
    def load(self):
        for file in os.listdir(self.working_dir):
            if file.endswith(".JPG") and file not in self.pics:
                lb = pic_widget(self.canvas, self.working_dir, file, self.pic_size)
                self.pics[file] = lb
        self.update()
        
    def clear(self):
        to_remove = []
        for key in self.pics:
            if not self.pics[key].is_selected():
                to_remove.append(key)
        for key in to_remove:
            self.pics[key].grid_forget()
            self.pics[key].destroy()
            self.canvas.delete(key)
            del self.pics[key]
        self.update()

    def update(self):
        c = r = 0
        keys = sorted(self.pics)
        for key in keys:
            self.canvas.create_window((c*self.pic_size, r*self.pic_size), window=self.pics[key], anchor=tkc.NW, width=self.pic_size, height=self.pic_size, tags=key)
            #self.pics[key].grid(row = r, column = c)
            c += 1
            if c >= self.packing_width:
                c = 0
                r += 1
        self.canvas.config(scrollregion=(0,0,0,(r+1)*self.pic_size))
                
    def enlarge(self):
        self.pic_size += 50
        self.resized(1)
        
    def shrink(self):
        self.pic_size -= 50
        self.resized(-1)

    def pictures_resized(self, e):
        if (self.packing_width != (e.width // self.pic_size) and (e.width // self.pic_size) != 0):
            self.packing_width = (e.width // self.pic_size)
            self.canvas.config(width=e.width, height=e.height)
            self.update()
            
    def resized(self, change):
        r = c = 0
        keys = sorted(self.pics)
        for key in keys:
            self.pics[key].resize(self.pic_size)
            self.canvas.itemconfigure(key, width=self.pic_size, height=self.pic_size)
            self.canvas.move(key, change*c*50, change*r*50)
            c += 1
            if c >= self.packing_width:
                c = 0
                r += 1
    
    def select_all(self):
        for key in self.pics:
            if not self.pics[key].is_selected():
                self.pics[key].select()
            
    def select_none(self):
        for key in self.pics:
            if self.pics[key].is_selected():
                self.pics[key].unselect()
    
    def shift_select(self, curr_sel):
        if self.last_sel != "":
            in_range = False
            if curr_sel > self.last_sel:
                temp = curr_sel
                curr_sel = self.last_sel
                self.last_sel = temp
            keys = sorted(self.pics)
            #print(curr_sel, self.last_sel)
            for key in keys:
                if (key == curr_sel):
                    in_range = True
                    #print(key, "true", curr_sel)
                if in_range:
                    self.pics[key].select()
                    #print(key)
                if (key == self.last_sel):
                    in_range = False
                    #print(key, "false", self.last_sel)
                    
    def count_selected(self):
        count = 0
        for key in self.pics:
            if self.pics[key].is_selected():
                count += 1
        return count

class main_app(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.bind("<Escape>", self.exit)
        self.parent.title("Picture Indexer")
        
        # Setup main Frames
        self.format = tk.Frame(self, relief=rT, borderwidth=bW)
        self.select = selection(self)
        
        # Setup widgets
        self.title = tk.Entry(self.format)
        self.tlabel = tk.Label(self.format, text="Title", justify=tkc.LEFT)
        self.column = tk.Spinbox(self.format, from_=1, to=8, width=2)
        self.clabel = tk.Label(self.format, text="Columns")
        self.ilabel = tk.Label(self.format, text="")
        self.prev = tk.Button(self.format, text="Preview", command=self.preview, width=10)
        
        # Pack all widgets
        self.format.pack(side=tkc.TOP, fill=tkc.X)
        self.select.pack(side=tkc.BOTTOM, fill=tkc.BOTH, expand=True)
        self.tlabel.grid(column=0, row=0, sticky=tkc.W)
        self.clabel.grid(column=0, row=1, sticky=tkc.W)
        self.title.grid(column=1, row=0, sticky=tkc.W, columnspan=2)
        self.column.grid(column=1, row=1, sticky=tkc.W)
        self.ilabel.grid(column=2, row=1, sticky=tkc.W)
        self.format.columnconfigure(3, weight=1)
        self.prev.grid(column=4, row=0, sticky=tkc.E, rowspan=2)
        
    def preview(self):
        if self.title.get() == "":
            tkMessageBox.showinfo("Warning!", "Document needs a title!")
            return
        if self.select.count_selected() == 0:
            tkMessageBox.showinfo("Warning!", "No pictures selected!")
            return
        savename = self.select.working_dir+"/"+self.title.get()+".pdf"
        print savename
        c = Canvas(savename,
                pagesize=rll.pagesizes.letter)
        c.drawString(100,100,"Hello World")
        c.showPage()
        c.save()
        
    def exit(self, e):
        self.parent.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    main_app(root).pack(fill=tkc.BOTH, expand=True)
    root.mainloop()
