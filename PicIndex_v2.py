import Tkinter as tk
import tkMessageBox
import Tkconstants as tkc
import tkFileDialog
from PIL import Image, ImageTk
import os
import threading
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

rT = 'sunken'
bW = 2

class pdf_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.filename = ""
        self.pics = []
        
    def run(self):
        c = canvas.Canvas(self.filename, pagesize=letter)
        #c.drawString(inch, inch*0.5, self.filename)
        py = 10.5-self.size
        px = 0.5
        x = 0
        count = 0
        for pic in self.pics:
            name = os.path.join(self.path, pic)
            count += 1
            c.drawImage(image=name, x=inch*px, y=inch*py, width=inch*self.size,
                    height=inch*self.size, preserveAspectRatio=0)
            c.drawString(inch*px, inch*(py-0.125), pic)
            px += self.size+0.25
            x += 1
            if x >= self.cols:
                py -= self.size+0.25
                px = 0.5
                x = 0
                if py < 0.125:
                    c.showPage()
                    py = 10.5-self.size
        c.showPage()
        c.save()
        
    def is_running(self):
        return self.running
        
    def set_variables(self, name, path, pics, cols):
        self.filename = path+"/"+name
        self.name = name
        self.path = path
        self.pics = pics
        self.cols = cols
        self.size = (8.5 - (((cols-1)*0.25)+1.0))/cols
        
class pic_widget(tk.Label):
    def __init__(self, parent, path, name, size, event):
        self.selected = False
        self.path = path
        self.name = name
        self.size = size
        self.event = event
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
        #if (event.state & 0x0001):
        #    self.master.master.master.shift_select(self.name)
        if self.selected:
            self.unselect()
        else:
            self.select()
    
    def unselect(self):
        self.configure(background='light grey')
        self.selected=False
        self.event(-1)
        
    def select(self):
        self.configure(background='yellow')
        self.selected=True
        self.event(1)
    
    def is_selected(self):
        return self.selected
        
    def resize(self, size):
        self.size = size
        self.set_thumbnail()
        
    def get_image(self):
        return self.name

class selection(tk.Frame):
    def __init__(self, parent, event, status, **args):
        tk.Frame.__init__(self, parent, args)
        self.parent = parent
        self.working_dir = '/'
        self.last_sel = ""
        self.pics = {}
        self.packing_width = 1
        self.pic_size = 150
        self.event = event
        self.status = status
        
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
        self.sel_all.pack(fill='x')
        self.sel_non.pack(fill='x')
        self.clear.pack(fill='x')
        self.big.pack(fill='x')
        self.sml.pack(fill='x')
        self.scrollbar.pack(side=tkc.RIGHT, fill=tkc.Y)
        self.canvas.pack(side=tkc.LEFT, fill=tkc.BOTH)
        self.scrollbar.config(command=self.canvas.yview)
        self.pictures.bind("<Configure>", self.pictures_resized)
        
    def new_dir_selection(self):
        self.working_dir = tkFileDialog.askdirectory(initialdir="/home/charles/Desktop/picidxer", title="Select Directory")
        self.status("loading")
        for file in os.listdir(self.working_dir):
            if file.endswith(".JPG") and file not in self.pics:
                lb = pic_widget(self.canvas, self.working_dir, file, self.pic_size, self.event)
                self.pics[file] = lb
        self.update()
        self.status("waiting")
        
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
        if c == 0:
            height = (r)*self.pic_size
        else:
            height = (r+1)*self.pic_size
        self.canvas.config(scrollregion=(0,0,0,height))
                
    def enlarge(self):
        if self.pic_size < 300:
            self.pic_size += 50
            self.resized(1)
        
    def shrink(self):
        if self.pic_size > 50:
            self.pic_size -= 50
            self.resized(-1)

    def pictures_resized(self, e):
        if (self.packing_width != (e.width // self.pic_size) and (e.width // self.pic_size) != 0):
            self.packing_width = (e.width // self.pic_size)
            self.canvas.config(width=e.width, height=e.height)
            self.update()
            
    def resized(self, change):
        self.packing_width = (self.pictures.winfo_width() // self.pic_size)
        keys = sorted(self.pics)
        for key in keys:
            self.pics[key].resize(self.pic_size)
            self.canvas.itemconfigure(key, width=self.pic_size, height=self.pic_size)
            ##self.canvas.move(key, change*c*50, change*r*50)
        self.update()
    
    def select_all(self):
        for key in self.pics:
            if not self.pics[key].is_selected():
                self.pics[key].select()
            
    def select_none(self):
        for key in self.pics:
            if self.pics[key].is_selected():
                self.pics[key].unselect()
    
    def shift_select(self, curr_sel):
        print self.last_sel
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
        
    def get_pics(self):
        p = []
        keys = sorted(self.pics)
        for key in keys:
            p.append(self.pics[key].get_image())
        return p

class main_app(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.bind("<Escape>", self.exit)
        self.parent.title("Picture Indexer")
        self.sel_count = 0
        self.threads = []
        
        # Setup main Frames
        self.format = tk.Frame(self, relief=rT, borderwidth=bW)
        self.select = selection(self, self.event, self.update_status)
        
        # Setup widgets
        self.title = tk.Entry(self.format)
        self.tlabel = tk.Label(self.format, text="Title")
        self.column = tk.Spinbox(self.format, from_=1, to=8, width=2, command=self.refig)
        self.clabel = tk.Label(self.format, text="Columns")
        self.ilabel = tk.Label(self.format, text="")
        self.prev = tk.Button(self.format, text="Generate", command=self.preview, width=10)
        #self.nlabel = tk.Label(self.format, text=str(self.sel_count)+" selected")
        #self.rlabel = tk.Label(self.format, text="0 pages required")
        self.status = tk.Label(self.format, text="status:")
        self.slabel = tk.Label(self.format, text="waiting")
        
        # Pack all widgets
        self.format.pack(side=tkc.TOP, fill=tkc.X)
        self.select.pack(side=tkc.BOTTOM, fill=tkc.BOTH, expand=True)
        self.tlabel.grid(column=0, row=0, sticky=tkc.W)
        self.clabel.grid(column=0, row=1, sticky=tkc.W)
        self.title.grid(column=1, row=0, sticky=tkc.W, columnspan=2)
        self.column.grid(column=1, row=1, sticky=tkc.W)
        self.ilabel.grid(column=2, row=1, sticky=tkc.W)
        #self.nlabel.grid(column=3, row=0, sticky=tkc.E)
        #self.rlabel.grid(column=3, row=1, sticky=tkc.E)
        self.format.columnconfigure(3, weight=1)
        self.status.grid(column=4, row=0, sticky=tkc.W)
        self.slabel.grid(column=4, row=1, sticky=tkc.W)
        self.format.columnconfigure(5, weight=1)
        self.prev.grid(column=6, row=0, sticky=tkc.E, rowspan=2)
    
    def update_status(self, status):
        self.slabel.configure(text=status)
        self.update_idletasks()
    
    def event(self, by):
        self.sel_count += by
        #self.nlabel.configure(text=str(self.sel_count)+" selected")
        self.refig()
        
    def refig(self):
        total = self.sel_count // (int(self.column.get())**2)
        #self.rlabel.configure(text="about "+str(total)+" pages required")
        
    def preview(self):
        if self.title.get() == "":
            tkMessageBox.showinfo("Warning!", "Document needs a title!")
            return
        if self.select.count_selected() == 0:
            tkMessageBox.showinfo("Warning!", "No pictures selected!")
            return
        thread = pdf_thread()
        self.threads.append(thread)
        thread.set_variables(self.title.get()+".pdf",
                self.select.working_dir, self.select.get_pics(), 
                int(self.column.get()))
        thread.start()
        
    def exit(self, e):
        self.parent.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    main_app(root).pack(fill=tkc.BOTH, expand=True)
    root.mainloop()
