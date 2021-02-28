import sys

def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]

current_platform = get_platform()

import tkinter as tk
from TkinterDnD2 import *
from pdf2image import convert_from_path
import PyPDF2, datetime, os, base64
from io import BytesIO
import webbrowser

def convert(file_path):
    imgs2del = []
    try: #check if the user has entered a valid file
        PyPDF2.PdfFileReader(open(file_path, "rb"))
        TBox.insert(tk.END, logging_message_datetime("I",file_path))
    except PyPDF2.utils.PdfReadError:
        TBox.insert(tk.END, logging_message_datetime("E","invalid PDF file"))
    else:
        TBox.insert(tk.END, logging_message_datetime("I","valid PDF file"))
        TBox.insert(tk.END, logging_message_datetime("I","let's turn on the fans with poppler!"))
        folder = os.path.dirname(os.path.abspath(file_path))
        TBox.insert(tk.END, logging_message_datetime("I","the output folder will be the same as the pdf"))
        pages = None
        if current_platform == "Windows":
            pages = convert_from_path(file_path, 500, output_folder=folder,
                                      poppler_path=r'C:\Program Files\poppler-0.68.0\bin', fmt="png")
        else:
            pages = convert_from_path(file_path, 500, output_folder=folder, fmt="png")

        f = open(os.path.join(folder,'out.html'),'w')
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        .responsive {
          max-width: 100%;
          height: auto;
        }
        </style>
        </head>
        <body>

        """)
        
        #convert each image to base64 and add it to the html file
        for p in pages:
            with open(p.filename, "rb") as image_file:
                f.write("<img src=\"data:image/png;base64, "+base64.b64encode(image_file.read()).decode('utf-8')+"\" class=\"responsive\">")
            imgs2del.append(p.filename)
            
        f.write("""

        </body>
        </html>
        """)
        f.close()
        
        #opening html file created in your favorite browser 
        webbrowser.open_new_tab(os.path.join(folder,'out.html'))

    return imgs2del

def drop(event):
    file_path = event.data

    #the path still have / in winzoz lol
    if current_platform == "Windows":
        file_path = file_path.replace("/", "\\")

    #chars to remove for desktop program link {path}
    for c in "{}":
        file_path = file_path.replace(c, "")

    toDelete = convert(file_path)
    if toDelete != []:
        TBox.insert(tk.END, logging_message_datetime("I","cleaning temporary files in progress"))
        for i in toDelete:
            os.remove(i)
        TBox.insert(tk.END, logging_message_datetime("I","temporary files deleted"))
    TBox.insert(tk.END, logging_message_datetime("I","-------------------/////-------------------"))
            
#basic logging format
def logging_message_datetime(state, message):
    return "[" + state + "] " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')\
           + ": " + message + "\n"
    

root = TkinterDnD.Tk()

root.title("pdf2html")
root.geometry('600x400')

#label drop area
lbl = tk.Label(root, text="Drag and drop your file here",\
            font=("Arial Bold", 20), width=25, height=1,\
            borderwidth=3, relief="ridge")
lbl.drop_target_register(DND_FILES)
lbl.dnd_bind("<<Drop>>", drop)
lbl.pack(expand=0, fill=tk.BOTH)

#scrollbar for logs tbox - https://www.geeksforgeeks.org/how-to-make-a-proper-double-scrollbar-frame-in-tkinter/
SVBar = tk.Scrollbar(root) 
SVBar.pack(side=tk.RIGHT, fill="y") 
SHBar = tk.Scrollbar(root, orient=tk.HORIZONTAL) 
SHBar.pack (side=tk.BOTTOM, fill= "x")
TBox = tk.Text(root, height=50, width=200, yscrollcommand=SVBar.set, xscrollcommand=SHBar.set, wrap="none") 
TBox.pack(expand=0, fill=tk.BOTH) 
SHBar.config(command = TBox.xview) 
SVBar.config(command = TBox.yview) 

root.mainloop()
