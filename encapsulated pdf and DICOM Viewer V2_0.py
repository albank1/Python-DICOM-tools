# *****************************************************************************
# The program enable a check of DICOM files to see if they contain encapsulated
# pdf and to display the text contained.
# It will also determine if the file is a DICOM ultrasound image or other image
# and try to display the image
# Alban Killingback 27/5/2024
# Lincence: you can use for personal or commercial applications but must
# acknowledge the author
# *****************************************************************************

import pydicom
import PyPDF2
import io
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Determine if the file is a DICOM one
def is_dicom_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            header = f.read(132)
            if len(header) < 132:
                return False
            return header[128:132] == b'DICM'
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return False

# Extract the pdf from the DICOM file 
def extract_pdf_from_dicom(dicom_path):
    dicom = pydicom.dcmread(dicom_path)
    if "EncapsulatedDocument" not in dicom:
        raise ValueError("The DICOM file does not contain an encapsulated PDF.")
    return dicom.EncapsulatedDocument

# Function to extract text from the encapsulate pdf   
def extract_text_from_pdf(pdf_bytes):
    pdf_file = io.BytesIO(pdf_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Determines what type of DICOM file it is
def dicom_file_type(dicom_path):
    try:
        dicom = pydicom.dcmread(dicom_path)
        if "EncapsulatedDocument" in dicom:
            filetype = "pdf"
            return filetype
        if "NumberOfFrames" in dicom:
            filetype = "cineloop"
            display_image(dicom_path)
            return filetype
        elif dicom.Modality == "US":
            filetype = "USimage"
            display_image(dicom_path)
            return filetype
        elif dicom.Modality == "ECG":
            filetype = "ECG"
            return filetype
        else:
            filetype = "Otherimage"
            display_image(dicom_path)
            return filetype       
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return "??"

# Function to open a new window - NOT USED
def open_new_window():
    new_window = tk.Toplevel(root)
    new_window.title("New Window")
    new_window.geometry("300x200")
    label = tk.Label(new_window, text="This is a new window")
    label.pack(pady=20)

def display_image(dicom_path):
    try:
        dicom = pydicom.dcmread(dicom_path)
        if 'NumberOfFrames' in dicom:
            image_data = dicom.pixel_array[0]
            title_text = "First image in DICOM cine loop"
        else:
            image_data = dicom.pixel_array
            title_text = "DICOM image"
        image = Image.fromarray(image_data)
        image = image.convert("L")  # Convert to grayscale if necessary

        # Resize the image to fit the GUI window, keeping aspect ratio
        base_width = 1000
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
            
        new_window = tk.Toplevel(root)
        new_window.title(title_text)
        #new_window.geometry("300x200")
        label = tk.Label(new_window, text=title_text)
        label.pack(pady=20)
        label.configure(image=photo, text="")
        label.image = photo
    except Exception as e:
        label = tk.Label(new_window, text=title_text)
        label.pack(pady=20)
        label.configure(image="", text="Cannot load image")
        label.image = None

def open_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        path, filename = os.path.split(file_path)
        filename = "\"" + filename + "\""
        try:
            if is_dicom_file(file_path):
                filetype = dicom_file_type(file_path)                
                if filetype == "pdf":
                    pdf_bytes = extract_pdf_from_dicom(file_path)
                    extracted_text = extract_text_from_pdf(pdf_bytes)
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(tk.END, extracted_text)
                    select_label.config(text=f"{filename} is a DICOM encapsulated PDF with text")
                elif filetype == "cineloop":
                    text_widget.delete(1.0, tk.END)
                    select_label.config(text=f"{filename} is a DICOM cine loop")
                elif filetype == "USimage":
                    text_widget.delete(1.0, tk.END)
                    select_label.config(text=f"{filename} is an Ultrasound DICOM image")
                elif filetype == "ECG":
                    text_widget.delete(1.0, tk.END)
                    select_label.config(text=f"{filename} is a DICOM ECG")
                else:
                    text_widget.delete(1.0, tk.END)
                    select_label.config(text=f"{filename} is a DICOM image")
            else:
                select_label.config(text=f"{filename} is not a DICOM file")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def exit_app():
    root.destroy()

root = tk.Tk()
root.title("Indentify if DICOM encapsulated PDF ")
frame = ttk.Frame(root, padding="20")
frame.pack(padx=20, pady=20)

# Load the St George's MPCE image
img = Image.open("MPCElogo.png")
#img = img.resize((100, 100), PIL.Image.Resampling.LANCZOS)  # Resize the image if necessary
photo = ImageTk.PhotoImage(img)

# Create a label to display the image
image_label = tk.Label(frame, image=photo)
image_label.grid(row=0, column=0, columnspan=2, pady=30)

select_label = ttk.Label(frame, text="Select a File to determine if it contains DICOM information", font=("", 14))
select_label.grid(row=1, column=0, columnspan=2, pady=10)

#sub_label = ttk.Label(frame, text="")
#sub_label.grid(row=2, column=0, columnspan=2, pady=10)

text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=20)
text_widget.grid(row=3, column=0, columnspan=2, pady=10)

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12), padding=10)
style.map('TButton', foreground=[('!active', 'black'), ('active', 'gray')],
          background=[('!active', 'lightgray'), ('active', 'gray')],
          relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

open_button = ttk.Button(frame, text="Open DICOM File", command=open_file, style="TButton", cursor="hand2")
open_button.grid(row=4, column=0, pady=10, padx=10)

exit_button = ttk.Button(frame, text="Exit", command=exit_app, style="TButton", cursor="hand2")
exit_button.grid(row=4, column=1, pady=10, padx=10)

root.mainloop()
