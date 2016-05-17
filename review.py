# Copied from zetcode.com/gui/tkinter/layout/

import time
from Tkinter import Tk, BOTH, X, LEFT
from ttk import Frame, Label, Entry, Button
import tkMessageBox as mbox

class Example(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.date = (time.strftime("%m_%d_%Y"))
        self.initUI()


    def initUI(self):
        self.parent.title("Experiment")
        self.pack(fill=BOTH, expand=True)

        self.frame1 = Frame(self)
        self.frame1.pack(fill=X)

        self.lbl1 = Label(self.frame1, text="Participant", width=10)
        self.lbl1.pack(side=LEFT, padx=5, pady=5)

        self.entry1 = Entry(self.frame1)
        self.entry1.pack(fill=X, padx=5, expand=True)

        self.frame2 = Frame(self)
        self.frame2.pack(fill=X)

        self.lbl2 = Label(self.frame2, text="Date", width=10)
        self.lbl2.pack(side=LEFT, padx=5, pady=5)

        self.entry2 = Entry(self.frame2)
        self.entry2.insert(0, self.date)
        self.entry2.state()
        self.entry2.pack(fill=X, padx=5, expand=True)

        self.frame3 = Frame(self)
        self.frame3.pack(fill=X)

        self.accept = Button(self.frame3, text="Ok", command=self.makeVariables)
        self.accept.pack(fill=X, padx=5)


    def makeVariables(self):
        self.participant = self.entry1.get()
        print self.participant
        print self.date
        self.verify()
        Frame.quit(self)


    def verify(self):
        mbox.showwarning('Check', 'Have you set the markers on Emotiv Toolbox?')


    def getName(self):
        return self.participant


    def getDate(self):
        return self.date

class Escape(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.UIinit()
        self.do_exit = False

    def UIinit(self):
        self.parent.title('Warning')
        self.pack(fill=BOTH, expand=1)

        frame1 = Frame(self)
        frame1.pack(fill=X)
        lbl1 = Label(frame1, text="Are you sure you want to exit the \nexperiment?")
        lbl1.pack(side=LEFT, padx=5, pady=5)

        frame2 = Frame(self)
        frame2.pack(fill=X)

        button1 = Button(frame2, text="Yes", command=self.yes)
        button1.pack(side=LEFT, padx=5, pady=5)
        button2 = Button(frame2, text="No", command=self.stay)
        button2.pack(padx=5,pady=5)

    def yes(self):
        self.do_exit = True
        Frame.quit(self)

    def stay(self):
        Frame.quit(self)

    def getStatus(self):
        return self.do_exit

def getParticipant():
    root = Tk()
    root.geometry("300x100+300+300")
    app = Example(root)
    root.mainloop()
    participant = app.getName()
    date = app.getDate()
    return app

def checkExit():
    root = Tk()
    root.geometry("200x90+300+300")
    app = Escape(root)
    root.mainloop()
    result = app.getStatus()
    return result


