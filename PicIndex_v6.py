# Author - Charles Herrmann
# Date - 6/9/17

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
import win32api
import win32print
import tempfile

rT = 'ridge'
bW = 2

GHOSTSCRIPT_PATH = "G:\\Picture Perfect\\GHOSTSCRIPT\\bin\\gswin32.exe"
GSPRINT_PATH = "G:\\Picture Perfect\\Ghostgum\\gsview\\gsprint.exe"


class rename_widget(tk.Tk):
    def __init__(self, rename, width=250, height=125):
        tk.Tk.__init__(self)
        self.rename = rename
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.title("Rename")
        self.label = tk.Label(self, text="Enter a new name and then press return.", wraplength=width)
        self.entry = tk.Entry(self)
        self.label.pack(expand=1, fill=tk.X)
        self.entry.pack(expand=1, fill=tk.X)
        self.update_idletasks()
        self.bind("<Return>", self.kill)
        self.bind("<Escape>", self.kill)

    def kill(self, e=None):
        if self.entry.get() != "":
            self.rename(self.entry.get())
        self.destroy()


class status(tk.Tk):
    def __init__(self, width=250, height=125):
        tk.Tk.__init__(self)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.title("Status")
        self.label = tk.Label(self, text="", wraplength=width)
        self.label.pack(expand=1, fill=tk.BOTH)
        self.update_idletasks()
        self.bind("<Return>", self.kill)
        self.bind("<Escape>", self.kill)

    def update(self, udt):
        self.label.config(text=udt)
        self.update_idletasks()

    def finish(self, udt, cor):
        self.label.config(text=udt + ", ".join(cor))
        b = tk.Button(self, text="ok", command=self.kill)
        b.pack(side=tk.BOTTOM)
        self.update_idletasks()

    def kill(self, e=None):
        self.destroy()


class pdf_maker(object):
    def __init__(self):
        self.running = False
        self.filename = ""
        self.pics = []

    def mySplit(self, c, name, font, fontSize, size):
        lines = []
        fst = 0
        snd = -1
        done = False
        while not done:
            ntmp = name[fst:snd]
            while canvas.Canvas.stringWidth(c, ntmp, font, fontSize) > size:
                snd -= 1
                ntmp = name[fst:snd]
            if snd == -1:
                done = True
                lines.append(name[fst:])
            else:
                lines.append(ntmp)
                fst = snd
                snd = -1
        return lines

    def run(self):
        try:
            temp = tempfile.NamedTemporaryFile(delete=False)
            currentprinter = win32print.GetDefaultPrinter()
            command = '-ghostscript "'+GHOSTSCRIPT_PATH+'" -colour -printer "'+currentprinter+'" "'+temp.name+'"'
            c = canvas.Canvas(os.path.join(self.path, "test.pdf"), pagesize=letter)
            py = 10.0 - self.size
            px = 0.5
            x = 0
            y = 0
            page = 1
            count = 1
            maxy = 0
            new_page = True
            stat = status()
            stat.update("status: loading ["+str(count-1)+"/"+str(self.num_pics)+"]")
            for pic in self.pics:
                if new_page:
                    c.setFont("Helvetica", 10)
                    if self.head[0]:
                        if self.head[3]:
                            c.drawCentredString(inch*4.25, inch*10.7, str(page))
                        if self.head[1]:
                            c.drawString(inch*0.5, inch*10.5, "Filename: "+self.filename)
                        if self.head[2]:
                            try:
                                c.drawString(inch*0.5, inch*10.3, "Date: "+date.today().strftime("%B %d, %Y"))
                            except KeyError:
                                print "Exif section corrupted..."
                    if self.foot[0]:
                        if self.foot[3]:
                            c.drawCentredString(inch*4.25, inch*0.3, str(page))
                        if self.foot[1]:
                            c.drawString(inch*0.5, inch*0.7, "Filename: "+self.filename)
                        if self.foot[2]:
                            try:
                                c.drawString(inch*0.5, inch*0.5, "Date: "+date.today().strftime("%B %d, %Y"))
                            except KeyError:
                                print "Exif section corrupted..."
                    new_page = False
                name = os.path.join(pic[0], pic[1])
                c.drawImage(image=name, x=inch*px, y=inch*py, width=inch*self.size,
                            height=inch*self.size, preserveAspectRatio=1)
                if self.printBoard:
                    c.rect(x=inch*px, y=inch*py, width=inch*self.size,
                           height=inch*self.size)
                tmpy = 0
                if self.printName:
                    if canvas.Canvas.stringWidth(c, pic[1], "Helvetica", 10) > (self.size*inch):
                        font = 9
                        while canvas.Canvas.stringWidth(c, pic[1], "Helvetica", font) > (self.size*inch) and font > 6:
                            font -= 1
                        c.setFont("Helvetica", font)
                        if canvas.Canvas.stringWidth(c, pic[1], "Helvetica", font) > (self.size*inch):
                            lines = self.mySplit(c, pic[1], "Helvetica", font, (self.size*inch))
                            for line in lines:
                                tmpy += 0.11
                                c.drawString(inch*px, inch*(py-tmpy), line)
                        else:
                            tmpy += 0.11
                            c.drawString(inch*px, inch*(py-tmpy), pic[1])
                    else:
                        tmpy += 0.11
                        c.drawString(inch*px, inch*(py-tmpy), pic[1])
                if self.printDate:
                    try:
                        picDate = Image.open(name)._getexif()[36867]
                        tmpy += 0.11
                        c.drawString(inch*px, inch*(py-tmpy), picDate.split()[0])
                    except TypeError:
                        pass
                    except KeyError:
                        pass
                c.setFont("Helvetica", 10)
                count += 1
                px += self.size+0.25
                x += 1
                if tmpy > maxy:
                    maxy = tmpy
                if x >= self.cols:
                    if maxy > 0.25:
                        py -= self.size+maxy+0.02
                    else:
                        py -= self.size+0.25
                    maxy = 0
                    px = 0.5
                    x = 0
                    y += 1
                    if y >= self.cols:
                        y = 0
                        new_page = True
                        c.showPage()
                        py = 10.0-self.size
                        page += 1
                stat.update("status: loading ["+str(count-1)+"/"+str(self.num_pics)+"]")
            stat.kill()
            c.save()
            win32api.ShellExecute(0, 'open', GSPRINT_PATH, command, '.', 0)
        finally:
            os.remove(temp.name)

    def set_variables(self, path, pics, cols, b, fn, d, h, f):
        self.path = path
        self.pics = pics
        self.cols = cols
        self.printBoard = b
        self.printName = fn
        self.printDate = d
        self.num_pics = len(pics)
        self.head = h
        self.foot = f
        self.size = (8.5 - (((cols-1)*0.25)+1.0))/cols
        return 1


class pic_widget(tk.Frame):
    def __init__(self, parent, path, name, size, chng, update_key):
        tk.Frame.__init__(self, parent, relief=rT, borderwidth=bW)
        self.selected = False
        self.path = path
        self.name = name
        self.size = size
        self.rotate = 0
        self.chng = chng
        self.top = None
        self.update_key = update_key
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
        top.title("Edit the Picture")
        self.tmpi = Image.open(os.path.join(self.path, self.name))
        self.tmpi.thumbnail((600, 600))
        self.tmpp = ImageTk.PhotoImage(self.tmpi)
        self.tmpl = tk.Label(top, image=self.tmpp)
        self.tmpl.pack()
        hldr = tk.Frame(top)
        left = tk.Button(hldr, text="Rotate Left", command=lambda: self.do_rotate(90))
        right = tk.Button(hldr, text="Rotate Right", command=lambda: self.do_rotate(-90))
        newname = tk.Button(hldr, text="Rename", command=self.get_name)
        left.pack(side=tkc.LEFT, fill='x', expand=1)
        newname.pack(side=tkc.LEFT, fill='x', expand=1)
        right.pack(side=tkc.LEFT, fill='x', expand=1)
        hldr.pack(side=tkc.BOTTOM, fill='x')

    def clicked(self):
        if self.selected:
            self.unselect()
        else:
            self.select()

    def unselect(self):
        self.configure(background='light grey')
        self.label.configure(background='light grey')
        self.selected = False
        self.chng(-1)

    def select(self):
        self.configure(background='yellow')
        self.label.configure(background='yellow')
        self.selected = True
        self.chng(1)

    def is_selected(self):
        return self.selected

    def get_image(self):
        return (self.path, self.name, self.rotate)

    def do_rotate(self, way):
        tmp = Image.open(os.path.join(self.path, self.name))
        exif = tmp.info['exif']
        tmp = tmp.rotate(way, expand=True)
        tmp.save(os.path.join(self.path, self.name), exif=exif)
        self.image = Image.open(os.path.join(self.path, self.name))
        self.image.thumbnail((self.size-10, self.size-10))
        self.photo = ImageTk.PhotoImage(self.image)
        self.img.config(image=self.photo)
        self.tmpi = Image.open(os.path.join(self.path, self.name))
        self.tmpi.thumbnail((600, 600))
        self.tmpp = ImageTk.PhotoImage(self.tmpi)
        self.tmpl.config(image=self.tmpp)

    def get_name(self, e=None):
        self.prompt = rename_widget(self.rename)

    def rename(self, name):
        name = name + ".JPG"
        if self.update_key(name, self.name):
            os.rename(os.path.join(self.path, self.name), os.path.join(self.path, name))
            self.name = name
            self.label.config(text=self.name)
        else:
            tkMessageBox.showinfo("Warning!", "File already exists")


class selection(tk.Frame):
    def __init__(self, parent, **args):
        tk.Frame.__init__(self, parent, args)
        self.parent = parent
        self.working_dir = ""
        self.last_sel = ""
        self.pics = {}
        self.packing_width = 1
        self.pic_size = 150
        self.num_sel = 0

        # Setup widgets
        self.buttons = tk.Frame(self, relief=rT, borderwidth=bW, bg='light goldenrod')
        self.pictures = tk.Frame(self, relief=rT, borderwidth=bW)
        self.sel_dir = tk.Button(self.buttons, text='Select Directory', command=self.new_dir_selection)
        self.sel_all = tk.Button(self.buttons, text='Select All', command=self.select_all)
        self.sel_non = tk.Button(self.buttons, text='Select None', command=self.select_none)
        self.ren_all = tk.Button(self.buttons, text='Rename All', command=self.rename_all)
        self.format = tk.Button(self.buttons, text='Format', command=self.parent.step2)

        self.scrollbar = tk.Scrollbar(self.pictures, width=10)
        self.canvas = tk.Canvas(self.pictures, width=450,
                                yscrollcommand=self.scrollbar.set, bg='plum1')

        # Pack all widgets
        self.buttons.pack(side=tkc.LEFT, fill=tkc.Y)
        self.pictures.pack(side=tkc.LEFT, fill=tkc.BOTH, expand=1)
        self.sel_dir.pack(fill='x')
        self.sel_all.pack(fill='x')
        self.sel_non.pack(fill='x')
        self.ren_all.pack(fill='x')
        self.format.pack(fill='x', pady=10)
        self.scrollbar.pack(side=tkc.RIGHT, fill=tkc.Y)
        self.canvas.pack(side=tkc.LEFT, fill=tkc.BOTH)
        self.scrollbar.config(command=self.canvas.yview)

        # Bindings
        self.pictures.bind("<Configure>", self.pictures_resized)
        self.parent.master.bind('<Control-a>', self.select_all)

    def new_dir_selection(self):
        if len(self.pics) != 0:
            if not tkMessageBox.askyesno("Warning!", "Would you like to keep the pictures already loaded?"):
                self.clear()
        self.working_dir = ""
        temp = tkFileDialog.askdirectory(initialdir="/home/charles/Desktop/picidxer", title="Select Directory")
        if temp:
            self.working_dir = temp
        if self.working_dir != "":
            jpgs = [f for f in os.listdir(self.working_dir) if (f.endswith(".JPG") or f.endswith(".jpg"))]
            num_pics = len(jpgs)
            if num_pics != 0:
                count = 0
                corrupt = []
                stat = status()
                stat.update("status: loading ["+str(count)+"/"+str(num_pics)+"]")
                for file in jpgs:
                    try:
                        lb = pic_widget(self.canvas, self.working_dir, file, self.pic_size, self.change_in_sel, self.update_key)
                        self.pics[file] = lb
                        count += 1
                    except IOError:
                        corrupt.append(file)
                    stat.update("status: loading ["+str(count)+"/"+str(num_pics)+"]")
                if len(corrupt) != 0:
                    stat.finish("status: the following files could not be loaded. " +
                                "Possibly corrupted.\n\n", corrupt)
                else:
                    stat.kill()
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
        self.canvas.config(scrollregion=(0, 0, 0, height))

    def pictures_resized(self, e):
        if (self.packing_width != (e.width // self.pic_size) and (e.width // self.pic_size) != 0):
            self.packing_width = (e.width // self.pic_size)
            self.canvas.config(width=e.width, height=e.height)
            self.update()

    def select_all(self, e=None):
        for key in self.pics:
            if not self.pics[key].is_selected():
                self.pics[key].select()

    def select_none(self):
        for key in self.pics:
            if self.pics[key].is_selected():
                self.pics[key].unselect()

    def rename_all(self, e=None):
        if len(self.pics) <= 0:
            return
        rename = rename_widget(self.rename)

    def rename(self, name):
        i = 1
        keys = sorted(self.pics)
        for key in keys:
            tmp = name+' {:03d}'.format(i)
            print tmp
            self.pics[key].rename(tmp)
            i += 1

    def update_key(self, new, old):
        if new not in self.pics:
            self.pics[new] = self.pics.pop(old)
            return True
        else:
            return False

    def count_selected(self):
        count = 0
        for key in self.pics:
            if self.pics[key].is_selected():
                count += 1
        return count

    def change_in_sel(self, by):
        self.num_sel += by

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


class formation(tk.Frame):
    def __init__(self, parent, **args):
        tk.Frame.__init__(self, parent, args)
        self.parent = parent
        self.var1 = tk.StringVar()
        self.var1.set("Selected: 0")
        self.var2 = tk.StringVar()
        self.var2.set("Pages: 0")
        self.var3 = tk.IntVar()
        self.var4 = tk.IntVar()
        self.var5 = tk.IntVar()
        self.var6 = tk.IntVar()
        self.var7 = tk.IntVar()
        self.num_sel = 0
        self.head = [tk.IntVar(), tk.IntVar(), tk.IntVar()]
        self.foot = [tk.IntVar(), tk.IntVar(), tk.IntVar()]
        self.set = False

        # Setup widgets
        self.frame1 = tk.Frame(self, relief=rT, borderwidth=bW)
        self.frame2 = tk.Frame(self, relief=rT, borderwidth=bW)
        self.frame3 = tk.Frame(self, relief=rT, borderwidth=bW)
        self.frame4 = tk.Frame(self, relief=rT, borderwidth=bW)
        self.frame5 = tk.Frame(self, relief=rT, borderwidth=bW)
        self.label2 = tk.Label(self.frame1, text="Columns")
        self.column = tk.Spinbox(self.frame1, from_=1, to=8, width=2, command=self.update_var)
        self.label3 = tk.Label(self.frame2, textvariable=self.var1)
        self.label4 = tk.Label(self.frame2, textvariable=self.var2)
        self.check1 = tk.Checkbutton(self.frame3, text="Print Boarders", variable=self.var3)
        self.check2 = tk.Checkbutton(self.frame3, text="Print Filename", variable=self.var4)
        self.check3 = tk.Checkbutton(self.frame3, text="Print Date", variable=self.var5)
        self.check4 = tk.Checkbutton(self.frame4, text="Print Header", variable=self.var6)
        self.button1 = tk.Button(self.frame4, text="Settings", command=lambda: self.options(1))
        self.check5 = tk.Checkbutton(self.frame4, text="Print Footer", variable=self.var7)
        self.button2 = tk.Button(self.frame4, text="Settings", command=lambda: self.options(2))
        self.button4 = tk.Button(self.frame5, text="Print >", command=self.parent.master.step3)

        # Pack all widgets
        self.frame1.pack(side=tk.TOP, fill='x')
        self.frame2.pack(side=tk.TOP, fill='x')
        self.frame3.pack(side=tk.TOP, fill='x')
        self.frame4.pack(side=tk.TOP, fill='x')
        self.frame5.pack(side=tk.TOP, fill='x')
        self.label2.grid(row=0, column=0)
        self.column.grid(row=0, column=1, sticky=tk.W)
        self.label3.pack(fill='x', anchor=tk.CENTER)
        self.label4.pack(fill='x', anchor=tk.CENTER)
        self.check1.pack(side=tk.TOP, anchor='w', expand=1)
        self.check2.pack(side=tk.TOP, anchor='w', expand=1)
        self.check3.pack(side=tk.TOP, anchor='w', expand=1)
        self.check4.grid(row=0, column=0, sticky=tk.W)
        self.button1.grid(row=0, column=1)
        self.check5.grid(row=1, column=0, sticky=tk.W)
        self.button2.grid(row=1, column=1)
        self.button4.pack(side=tk.LEFT, fill='x', expand=1)

    def update_var(self, num=None):
        if num:
            self.num_sel = num
        self.var1.set("Selected: "+str(self.num_sel))
        col = float(self.column.get())
        req = math.ceil(float(self.num_sel)/(col**2.0))
        self.var2.set("Pages: "+str(int(req)))

    def options(self, t, e=None):
        if not self.set:
            self.set = not self.set
            self.top = tk.Toplevel()
            if t == 1:
                self.top.title("Header Settings")
                check1 = tk.Checkbutton(self.top, text="Print Folder", variable=self.head[0])
                check2 = tk.Checkbutton(self.top, text="Print Date", variable=self.head[1])
                check3 = tk.Checkbutton(self.top, text="Print Page Number", variable=self.head[2])
            else:
                self.top.title("Footer Settings")
                check1 = tk.Checkbutton(self.top, text="Print Folder", variable=self.foot[0])
                check2 = tk.Checkbutton(self.top, text="Print Date", variable=self.foot[1])
                check3 = tk.Checkbutton(self.top, text="Print Page Number", variable=self.foot[2])

            check1.pack(side=tk.TOP, anchor='w', expand=1, fill='x')
            check2.pack(side=tk.TOP, anchor='w', expand=1, fill='x')
            check3.pack(side=tk.TOP, anchor='w', expand=1, fill='x')
            button = tk.Button(self.top, text="Dismiss", command=self.kill_options)
            button.pack(side=tk.TOP, anchor='w', expand=1, fill='x')
            self.top.protocol('WM_DELETE_WINDOW', self.kill_options)

    def kill_options(self):
        self.top.destroy()
        self.set = not self.set


class main_app(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.bind("<Escape>", self.exit)
        self.parent.bind("<F11>", self.toggle_fullscreen)
        self.parent.title("Picture Indexer")
        self.sel_count = 0
        self.maker = pdf_maker()
        self.state = False
        self.loading = False
        self.fhdr = None

        # Setup main Frames
        self.select = selection(self, relief=rT, borderwidth=bW)

        # Pack all widgets
        self.select.pack(fill=tkc.BOTH, expand=True)

    def step2(self):
        if self.select.count_selected() == 0:
            if self.select.has_pics():
                if tkMessageBox.askyesno("Warning!", "No pictures selected!\nSelect all pictures?"):
                    self.select.select_all()
                else:
                    return
            else:
                tkMessageBox.showinfo("Warning!", "No pictures loaded!\nSelect a directory.")
                return
        if self.fhdr:
            self.fhdr.destroy()
        self.fhdr = tk.Toplevel(self)
        self.format = formation(self.fhdr, relief=rT, borderwidth=bW)
        self.format.pack(fill=tkc.BOTH, expand=True)
        self.format.update_var(self.select.num_sel)
        self.fhdr.resizable(width=False, height=False)

    def step3(self):
        if int(self.format.column.get()) > 8 or int(self.format.column.get()) < 1:
            tkMessageBox.showinfo("Warning!", "Column selection must\nbe between 1 and 8")
            return
        header = (self.format.var6.get(), self.format.head[0].get(), self.format.head[1].get(), self.format.head[2].get())
        footer = (self.format.var7.get(), self.format.foot[0].get(), self.format.foot[1].get(), self.format.foot[2].get())
        if self.maker.set_variables(self.select.working_dir, self.select.get_pics(),
                                    int(self.format.column.get()), self.format.var3.get(),
                                    self.format.var4.get(), self.format.var5.get(),
                                    header, footer) == 1:
            self.fhdr.destroy()
            self.maker.run()

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
