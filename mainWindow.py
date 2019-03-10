import pandas as pd
import windowHelper as w
import sys
import tkinter
def RegInForm():
    values.configure(state='normal')
    w.doRegression()
    values.configure(state='disabled')
def ChkDir():
    values.configure(state='normal')
    w.readImportDir('spc')
    w.readImportDir('yvalues')
    values.configure(state='disabled')
def clearText():
    values.configure(state='normal')
    values.delete('1.0', tkinter.END)
    values.configure(state='disabled')
#Alte Werte aus CSV einlesen
df = w.readCSV()

window = tkinter.Tk()
frame = tkinter.Frame(window)
frame.pack()

bottom_frame = tkinter.Frame(window)
bottom_frame.pack( side = tkinter.BOTTOM )

btn1 = tkinter.Button(frame, text = "Regression durchführen", fg = "Black", command = RegInForm)
btn1.pack(side = tkinter.LEFT)
btn2 = tkinter.Button(frame, text = "Import Starten", fg = "Black", command = w.importCSVfromForm)
btn2.pack(side = tkinter.LEFT)
btn3 = tkinter.Button(frame, text = "X-Werte Exportieren", fg = "Black", command = w.exportX)
btn3.pack(side = tkinter.LEFT)
btn4 = tkinter.Button(frame, text = "Y-Werte Exportieren", fg = "Black", command = w.exportY)
btn4.pack(side = tkinter.LEFT)
btn5 = tkinter.Button(frame, text = "Ausgabe leeren", fg = "Black", command = clearText)
btn5.pack(side = tkinter.LEFT)

#Textbereich für die Vergangenen Messwerte
values = tkinter.Text(bottom_frame)
#values.pack()
values.pack(side = tkinter.BOTTOM)
class PrintToT1(object): 
 def write(self, s):
     values.configure(state='normal')
     values.insert(tkinter.END, s)
     values.configure(state='disabled')
sys.stdout = PrintToT1()
print ('Übersicht der Letzten fünf Regressionsdurchläufe:')
print (df)
ChkDir()
window.mainloop()
