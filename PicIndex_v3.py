import Tkinter as tk
import tkMessageBox
import Tkconstants as tkc
import tkFileDialog
from ttk import Progressbar
from PIL import Image, ImageTk
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import date
import math

rT = 'ridge'
bW = 2

class pdf_maker(object):
    def __init__(self, status):
        self.running = False
        self.filename = ""
        self.pics = []
        self.status = status
        
    def run(self):
        c = canvas.Canvas(self.filename, pagesize=letter)
        py = 10.0-self.size
        px = 0.5
        x = 0
        y = 0
        page = 1
        count = 1
        new_page = True
        for pic in self.pics:
            self.status("status: loading ["+str(count)+"/"+str(len(self.pics))+"]")
            if new_page:
                c.drawCentredString(inch*4.25, inch*0.3, str(page))
                c.drawString(inch*0.5, inch*1.5, "Filename: "+self.filename)
                c.drawString(inch*0.5, inch*1.3, "Date: "+date.today().strftime("%B %d, %Y"))
                if (count + (self.cols**2) <= len(self.pics)):
                    lastidx = count + (self.cols**2) - 1
                else:
                    lastidx = len(self.pics)
                c.drawString(inch*0.5, inch*1.1, "Pictures: "+str(count)+" - "+str(lastidx))
                new_page = False
            name = os.path.join(self.path, pic)
            c.drawImage(image=name, x=inch*px, y=inch*py, width=inch*self.size,
                    height=inch*self.size, preserveAspectRatio=1)
            c.rect(x=inch*px, y=inch*py, width=inch*self.size,
                    height=inch*self.size)
            c.drawString(inch*px, inch*(py-0.18), str(count))
            count += 1
            px += self.size+0.25
            x += 1
            if x >= self.cols:
                py -= self.size+0.25
                px = 0.5
                x = 0
                y += 1
                if y >= self.cols:
                    y = 0
                    new_page = True
                    c.showPage()
                    py = 10.0-self.size
                    page += 1
        c.save()
        self.status("status: ready")
        
    def set_variables(self, name, path, pics, cols):
        if tkMessageBox.askyesno("Path to save PDF?", "Would you like to save PDF\nin picture directory?"):
            self.filename = path+"/"+name
        else:
            temp = tkFileDialog.askdirectory(initialdir=path, title="Select Directory")
            if temp:
                self.filename = temp+"/"+name
            else:
                return 0
        self.name = name
        self.path = path
        self.pics = pics
        self.cols = cols
        self.size = (8.5 - (((cols-1)*0.25)+1.0))/cols
        return 1

class pic_widget(tk.Frame):
    def __init__(self, parent, path, name, size, chng):
        tk.Frame.__init__(self, parent, relief=rT, borderwidth=bW)
        self.selected = False
        self.path = path
        self.name = name
        self.size = size
        self.chng = chng
        self.image = Image.open(os.path.join(path, name))
        self.image.thumbnail((self.size-10, self.size-10))
        self.photo = ImageTk.PhotoImage(self.image)
        self.img = tk.Label(self, image=self.photo)
        self.img.place(x=self.size/2, y=self.size/2, anchor=tk.CENTER)
        self.label = tk.Label(self, text=self.name)
        self.label.pack(side=tkc.BOTTOM, fill=tkc.X)
        self.bind("<Button-1>", self.single_click)
        self.bind("<Button-3>", self.double_click)
        self.img.bind("<Button-1>", self.single_click)
        self.img.bind("<Button-3>", self.double_click)
        self.label.bind("<Button-1>", self.single_click)
        self.label.bind("<Button-3>", self.double_click)
        
    def single_click(self, event):
        self.clicked()
            
    def double_click(self, event):
        top = tk.Toplevel()
        top.title(self.name)
        tmp = Image.open(os.path.join(self.path, self.name))
        tmp.thumbnail((600, 600))
        photo = ImageTk.PhotoImage(tmp)
        l = tk.Label(top, image=photo)
        l.pack()
        self.tmp = photo
        
    def clicked(self):
        if self.selected:
            self.unselect()
        else:
            self.select()
    
    def unselect(self):
        self.configure(background='light grey')
        self.selected=False
        self.chng(-1)
        
    def select(self):
        self.configure(background='yellow')
        self.selected=True
        self.chng(1)
    
    def is_selected(self):
        return self.selected
        
    def get_image(self):
        return self.name

class selection(tk.Frame):
    def __init__(self, parent, status, **args):
        tk.Frame.__init__(self, parent, args)
        self.parent = parent
        self.working_dir = ""
        self.last_sel = ""
        self.pics = {}
        self.packing_width = 1
        self.pic_size = 150
        self.status = status
        self.num_pics = 0
        self.num_sel = 0
        self.var1 = tk.StringVar()
        self.var1.set("Selected: 0")
        self.var2 = tk.StringVar()
        self.var2.set("Pages: 0")
        
        # Setup widgets
        self.buttons = tk.Frame(self, relief=rT, borderwidth=bW)
        self.pictures = tk.Frame(self, relief=rT, borderwidth=bW)
        self.sel_dir = tk.Button(self.buttons, text='Select Directory', command=self.new_dir_selection)
        self.sel_all = tk.Button(self.buttons, text='Select All', command=self.select_all)
        self.sel_non = tk.Button(self.buttons, text='Select None', command=self.select_none)
        self.selected = tk.Label(self.buttons, textvariable=self.var1, pady=5)
        self.required = tk.Label(self.buttons, textvariable=self.var2, pady=5)
        self.scrollbar = tk.Scrollbar(self.pictures, width=10)
        self.canvas = tk.Canvas(self.pictures, yscrollcommand=self.scrollbar.set)
        
        # Pack all widgets
        self.buttons.pack(side=tkc.LEFT, fill=tkc.Y)
        self.pictures.pack(side=tkc.LEFT, fill=tkc.BOTH, expand=1)
        self.sel_dir.pack(fill='x')
        self.sel_all.pack(fill='x')
        self.sel_non.pack(fill='x')
        self.selected.pack(fill='x')
        self.required.pack(fill='x')
        self.scrollbar.pack(side=tkc.RIGHT, fill=tkc.Y)
        self.canvas.pack(side=tkc.LEFT, fill=tkc.BOTH)
        self.scrollbar.config(command=self.canvas.yview)
        
        # Bindings
        self.pictures.bind("<Configure>", self.pictures_resized)
        
    def new_dir_selection(self):
        self.working_dir = ""
        temp = tkFileDialog.askdirectory(initialdir="/home/charles/Desktop/picidxer", title="Select Directory")
        if temp:
            self.working_dir = temp
        if self.working_dir != "":
            print(self.working_dir)
            jpgs = [f for f in os.listdir(self.working_dir) if (f.endswith(".JPG") or f.endswith(".jpg"))]
            self.num_pics = len(jpgs)
            if self.num_pics != 0:
                count = 0
                corrupt = 0
                self.status("status: loading ["+str(count)+"/"+str(self.num_pics)+"]")
                for file in jpgs:
                    try:
                        lb = pic_widget(self.canvas, self.working_dir, file, self.pic_size, self.change_in_sel)
                        self.pics[file] = lb
                        count += 1
                    except IOError:
                        corrupt += 1
                    self.status("status: loading ["+str(count)+"/"+str(self.num_pics)+"]")
                if corrupt != 0:
                    self.status("status: "+str(corrupt)+" file(s) not loaded")
                else:
                    self.status("status: ready")
            else:
                self.status("status: no pics found")
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
            c += 1
            if c >= self.packing_width:
                c = 0
                r += 1
        if c == 0:
            height = (r)*self.pic_size
        else:
            height = (r+1)*self.pic_size
        self.canvas.config(scrollregion=(0,0,0,height))

    def pictures_resized(self, e):
        if (self.packing_width != (e.width // self.pic_size) and (e.width // self.pic_size) != 0):
            self.packing_width = (e.width // self.pic_size)
            self.canvas.config(width=e.width, height=e.height)
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
        
    def change_in_sel(self, by):
        self.num_sel += by
        self.update_var()
        
    def update_var(self):
        self.var1.set("Selected: "+str(self.num_sel))
        if self.num_sel == 0:
            self.var2.set("Pages: 0")
            return
        col = float(self.parent.get_cols())
        req = math.ceil(float(self.num_sel)/(col**2.0))
        self.var2.set("Pages: "+str(int(req)))

    def has_pics(self):
        if len(self.pics) > 0:
            return True
        else:
            return False
        
    def get_pics(self):
        p = []
        keys = sorted(self.pics)
        for key in keys:
            if self.pics[key].is_selected():
                p.append(self.pics[key].get_image())
        return p

class main_app(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.bind("<Escape>", self.exit)
        self.parent.bind("<F11>", self.toggle_fullscreen)
        self.parent.title("Picture Indexer")
        self.sel_count = 0
        self.maker = pdf_maker(self.update_status)
        self.state = False
        self.loading = False;
        
        # Setup main Frames
        self.format = tk.Frame(self, relief=rT, borderwidth=bW)
        self.select = selection(self, self.update_status)
        
        # Setup widgets
        self.title = tk.Entry(self.format)
        self.tlabel = tk.Label(self.format, text="Title")
        self.column = tk.Spinbox(self.format, from_=1, to=8, width=2, command=self.select.update_var)
        self.clabel = tk.Label(self.format, text="Columns")
        self.ilabel = tk.Label(self.format, text="")
        self.prev = tk.Button(self.format, text="Preview", command=self.preview, width=10)
        self.status = tk.Label(self.format, text="status: ready")
        
        # Pack all widgets
        self.format.pack(side=tkc.TOP, fill=tkc.X)
        self.select.pack(side=tkc.BOTTOM, fill=tkc.BOTH, expand=True)
        self.tlabel.grid(column=0, row=0, sticky=tkc.W)
        self.clabel.grid(column=0, row=1, sticky=tkc.W)
        self.title.grid(column=1, row=0, sticky=tkc.W, columnspan=2)
        self.column.grid(column=1, row=1, sticky=tkc.W)
        self.ilabel.grid(column=2, row=1, sticky=tkc.W)
        self.format.columnconfigure(3, weight=1)
        self.status.grid(column=4, row=0, sticky=tkc.W)
        self.format.columnconfigure(5, weight=1)
        self.prev.grid(column=6, row=0, sticky=tkc.E, rowspan=2)
    
    def update_status(self, status):
        self.status.configure(text=status)
        self.update_idletasks()

    def preview(self):
        if self.title.get() == "":
            tkMessageBox.showinfo("Warning!", "Document needs a title!")
            return
        if int(self.column.get()) > 8 or int(self.column.get()) < 1:
            tkMessageBox.showinfo("Warning!", "Column selection must\nbe between 1 and 8")
            return
        if self.select.count_selected() == 0:
            if self.select.has_pics():
                if tkMessageBox.askyesno("Warning!", "No pictures selected!\nSelect all pictures?"):
                    self.select.select_all()
                else:
                    return
            else:
                tkMessageBox.showinfo("Warning!", "No pictures loaded!\nSelect a directory.")
                return
        if self.maker.set_variables(self.title.get()+".pdf",
                self.select.working_dir, self.select.get_pics(), 
                int(self.column.get())) == 1:
            self.maker.run()
        
    def get_cols(self):
        return int(self.column.get())
        
    def exit(self, e):
        self.parent.destroy()
        
    def toggle_fullscreen(self, event=None):
        self.state = not self.state
        self.parent.attributes("-fullscreen", self.state)
        return "break"

if __name__ == "__main__":
    root = tk.Tk()
    main_app(root).pack(fill=tkc.BOTH, expand=True)
    root.mainloop()
