################################################################################
# Loads a DICOM image and allows the editing of the patient demographics
# Alban Killingback Jul 2024
################################################################################

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pydicom
from PIL import Image, ImageTk
import os
import numpy as np

VERSION = "V2_0"

def select_dicom_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            global dicom_file
            dicom_file = pydicom.dcmread(file_path)
            update_fields(dicom_file)
            display_image(dicom_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read DICOM file: {e}")
    else:
        messagebox.showwarning("No file selected", "Please select a DICOM file.")

def ybr_to_rgb(ybr_image):
    ybr_image = ybr_image.astype(np.float32)
    y, cb, cr = ybr_image[:,:,0], ybr_image[:,:,1], ybr_image[:,:,2]

    r = y + 1.402 * (cr - 128.0)
    g = y - 0.344136 * (cb - 128.0) - 0.714136 * (cr - 128.0)
    b = y + 1.772 * (cb - 128.0)

    rgb_image = np.stack([r, g, b], axis=-1)
    rgb_image = np.clip(rgb_image, 0, 255).astype(np.uint8)
    return rgb_image

def update_fields(dicom):
    entry_patient_name.delete(0, tk.END)
    entry_patient_name.insert(0, str(dicom.get('PatientName', '')))

    entry_patient_id.delete(0, tk.END)
    entry_patient_id.insert(0, str(dicom.get('PatientID', '')))

    entry_patient_birthdate.delete(0, tk.END)
    entry_patient_birthdate.insert(0, str(dicom.get('PatientBirthDate', '')))

    entry_patient_sex.delete(0, tk.END)
    entry_patient_sex.insert(0, str(dicom.get('PatientSex', '')))

    entry_modality.delete(0, tk.END)
    entry_modality.insert(0, str(dicom.get('Modality', '')))

    entry_accession_number.delete(0, tk.END)
    entry_accession_number.insert(0, str(dicom.get('AccessionNumber', '')))

def display_image(dicom):
    try:
        if "NumberOfFrames" in dicom:
            image_data = dicom.pixel_array[0]
        else:
            image_data = dicom.pixel_array

        # Check the Photometric Interpretation
        if dicom.PhotometricInterpretation == "YBR_FULL":
            image = ybr_to_rgb(image_data)
        elif dicom.PhotometricInterpretation in ["RGB", "MONOCHROME2", "MONOCHROME1"]:
            image = Image.fromarray(image_data)
        else:
            raise ValueError(f"Unsupported Photometric Interpretation: {dicom.PhotometricInterpretation}")

        # Resize the image to fit the GUI window, keeping aspect ratio
        base_width = 500
        w_percent = (base_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        image = image.resize((base_width, h_size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        lbl_image.configure(image=photo)
        lbl_image.image = photo
    except Exception as e:
        lbl_image.configure(text="Cannot load image")
        messagebox.showerror("Error", f"Failed to display image: {e}")

def save_dicom_file():
    if dicom_file:
        try:
            dicom_file.PatientName = entry_patient_name.get()
            dicom_file.PatientID = entry_patient_id.get()
            dicom_file.PatientBirthDate = entry_patient_birthdate.get()
            dicom_file.PatientSex = entry_patient_sex.get()
            dicom_file.Modality = entry_modality.get()
            dicom_file.AccessionNumber = entry_accession_number.get()

            save_path = filedialog.asksaveasfilename(defaultextension=".dcm")
            if save_path:
                dicom_file.save_as(save_path)
                messagebox.showinfo("File Saved", f"File saved successfully as {save_path}")
            else:
                messagebox.showwarning("Save cancelled", "Save operation cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save DICOM file: {e}")
    else:
        messagebox.showwarning("No file loaded", "Please load a DICOM file first.")

def exit_application():
    app.destroy()

app = tk.Tk()
app.title("DICOM Editor " + VERSION)

frame_image = ttk.Frame(app, padding="10")
frame_image.grid(row=0, column=0, rowspan=7, padx=10, pady=5, sticky="nsew")

lbl_image = ttk.Label(frame_image, text="No Image Loaded")
lbl_image.pack(expand=True)

frame_info = ttk.Frame(app, padding="10")
frame_info.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="nsew")

ttk.Label(frame_info, text="Patient Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
entry_patient_name = ttk.Entry(frame_info)
entry_patient_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_info, text="Patient ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
entry_patient_id = ttk.Entry(frame_info)
entry_patient_id.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_info, text="Patient Birth Date (YYYYMMDD):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
entry_patient_birthdate = ttk.Entry(frame_info)
entry_patient_birthdate.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_info, text="Patient Sex (M/F):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
entry_patient_sex = ttk.Entry(frame_info)
entry_patient_sex.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_info, text="Modality:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
entry_modality = ttk.Entry(frame_info)
entry_modality.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

ttk.Label(frame_info, text="Accession Number:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
entry_accession_number = ttk.Entry(frame_info)
entry_accession_number.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

frame_buttons = ttk.Frame(app, padding="10")
frame_buttons.grid(row=6, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12), padding=10)
style.map('TButton', foreground=[('!active', 'black'), ('active', 'gray')],
        background=[('!active', 'lightgray'), ('active', 'gray')],
        relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

btn_select = ttk.Button(frame_buttons, text="Select DICOM File", command=select_dicom_file)
btn_select.pack(side=tk.LEFT, padx=10, pady=20)

btn_save = ttk.Button(frame_buttons, text="Save DICOM File", command=save_dicom_file)
btn_save.pack(side=tk.LEFT, padx=10, pady=20)

btn_exit = ttk.Button(frame_buttons, text="Exit", command=exit_application)
btn_exit.pack(side=tk.LEFT, padx=10, pady=20)

dicom_file = None

app.columnconfigure(1, weight=1)
frame_info.columnconfigure(1, weight=1)

app.mainloop()
