import tkinter as tk
from PIL import ImageTk,Image,ImageGrab
import numpy as np
import win32clipboard as clip
from io import BytesIO
import win32con

dragging=False
Img = None
SelectedRegion = None
L,T=0,0

def correct(x1,y1,x2,y2):
    return (min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2))

def w_quit(e):
    win.quit()

def start_drag(e):
    global L,T,dragging,rect,SelectedRegion
    dragging=True
    L,T=e.x,e.y
    rect = can.create_rectangle(L,T,L,T, outline='blue', width=3)
    SelectedRegion = can.create_image(L,T,anchor='nw')

def draw(e):
    global _part
    if dragging:
        can.coords(rect,L,T,e.x,e.y)
        Img = scr.crop(correct(L,T,e.x,e.y))
        _part=ImageTk.PhotoImage(Img)
        can.coords(SelectedRegion,(min(L,e.x),min(T,e.y)))
        can.itemconfig(SelectedRegion,image=_part)


def grab(e):
    global Img
    Img = ImageGrab.grab((L,T,e.x,e.y))
    win.quit()

def GrabImg():
    global win,can,scr
    ImageGrab.grab()
    scr = ImageGrab.grab()
    background = np.array(scr)
    bg = np.power(background,0.9)
    bg = Image.fromarray(bg.astype('uint8'))
    win = tk.Tk()
    background = ImageTk.PhotoImage(bg)
    win.geometry("{0}x{1}+0+0".format(win.winfo_screenwidth(), win.winfo_screenheight()))
    win.overrideredirect(True)
    win.configure(bg="black")
    can = tk.Canvas(win)
    can.place(x=0,y=0)
    can.configure(width=win.winfo_screenwidth(),height=win.winfo_screenheight(),highlightthickness=0)
    can.create_image(0,0,anchor='nw',image=background)
    

    win.bind('<Escape>',w_quit)
    win.bind('<Button-1>',start_drag)
    win.bind('<B1-Motion>',draw)
    win.bind('<ButtonRelease-1>',grab)
    win.mainloop()
    global dragging
    dragging = False
    return Img

def PhotoMoveStart(e):
    global dragging,L,T
    dragging = True
    L,T=e.x,e.y

def PhotoMoving(e):
    if dragging:
        global L,T
        win.geometry(f'+{e.x_root-L}+{e.y_root-T}')

def PhotoMoveStop(e):
    global dragging
    dragging = False

def toBMP(img:Image):
    buff = BytesIO()
    img.convert('RGB').save(buff, 'BMP')
    data = buff.getvalue()[14:]
    buff.close()
    return data

def ClipImage(img:Image):
    clip.OpenClipboard()
    clip.EmptyClipboard()
    clip.SetClipboardData(win32con.CF_DIB, toBMP(img))
    clip.CloseClipboard()

def Show(img:Image):
    if not img:
        exit()
    ClipImage(img)
    win.attributes('-topmost','true')
    photo = ImageTk.PhotoImage(img)
    w,h=img.size
    l,t = can.coords(SelectedRegion)
    l=int(l)
    t=int(t)
    win.geometry(f'{w}x{h}+{l}+{t}')
    can.place(x=0,y=0)
    can.configure(width=w,height=h)
    can.itemconfig(SelectedRegion,image=photo)
    can.coords(SelectedRegion,(0,0))
    win.bind('<Button-1>',PhotoMoveStart)
    win.bind('<B1-Motion>',PhotoMoving)
    win.bind('<ButtonRelease-1>',PhotoMoveStop)
    win.bind('<Double-Button-1>',w_quit)
    
    win.mainloop()

if __name__=='__main__':
    Show(GrabImg())