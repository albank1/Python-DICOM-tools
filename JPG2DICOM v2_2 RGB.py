################################################################################
# Converts a jpg to a DICOM file. If run as a command line with -i jpgname.jpg
# it will convert to grayscale DICOM jpgname.dcm
# It also works with -i jpgname.jpg -o dicomname.dcm
# If no arguments are entered a GUI is loaded and this can be used to load and
# save a DICOM RGB image
# Needs a jpg2dicom.ini file with the following
# [Patient Demographics]
# Name: Smith^John
# MRN: H000000
# DOB: 20000101
# Gender: M
# AccessionNo: 1234567
# Modality: US
# Alban Killingback Jul 2024
################################################################################

import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
import PIL
from PIL import Image, ImageTk
import numpy as np
import configparser
import datetime
import argparse
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os

# Load the patient demographics from the config file
config = configparser.ConfigParser()
config.read('JPG2DICOM.ini')
NAME = config['Patient Demographics']['Name']
MRN = config['Patient Demographics']['MRN']
DOB = config['Patient Demographics']['DOB']
GENDER = config['Patient Demographics']['Gender']
ACCESSIONNO = config['Patient Demographics']['AccessionNo']
MODALITY = config['Patient Demographics']['Modality']
JPG_FILE = ""

VERSION = "V2_2"

def create_dicom_from_jpg(jpg_path, dicom_path):
    print(f"Creating DICOM from {jpg_path}")
    
    # Read the JPEG image
    img = Image.open(jpg_path)
    
    # Convert image to numpy array
    pixel_data = np.array(img)
    
    # Create the FileDataset instance
    meta = Dataset()
    meta.MediaStorageSOPClassUID = pydicom.uid.SecondaryCaptureImageStorage
    meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian  # Explicitly setting TransferSyntaxUID
    meta.MediaStorageSOPInstanceUID = generate_uid()
    meta.ImplementationClassUID = generate_uid()

    ds = FileDataset(dicom_path, {}, file_meta=meta, preamble=b"\0" * 128)
    
    # Set patient information
    ds.PatientName = NAME
    ds.PatientID = MRN
    ds.PatientBirthDate = DOB  # Valid format: YYYYMMDD
    ds.Modality = MODALITY  # Set an appropriate modality
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.7"  # Secondary Capture Image Storage
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.SeriesNumber = 1
    ds.InstanceNumber = 1
    ds.ImageComments = "Converted from JPEG"

    ds.Rows, ds.Columns, RGB = pixel_data.shape
    if RGB > 1:
        # Set the image data attributes for RGB
        ds.SamplesPerPixel = 3
        ds.PhotometricInterpretation = "RGB"
        ds.Rows, ds.Columns, _ = pixel_data.shape
    else:
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.Rows, ds.Columns = pixel_data.shape
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PlanarConfiguration = 0  # RGB by pixel

    # Convert pixel data to bytes and set it
    ds.PixelData = pixel_data.tobytes()
    
    # Set the creation date and time
    dt = datetime.datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    ds.ContentTime = dt.strftime('%H%M%S')
    
    # Save the DICOM file
    ds.save_as(dicom_path)


################################################################################
# GUI
################################################################################

def open_gui():
    def save_dicom_file():
        global JPG_FILE
        dicom_path = filedialog.asksaveasfilename(
            title="Save DICOM file as",
            defaultextension=".dcm",
            filetypes=[("DICOM files", "*.dcm"), ("All files", "*.*")]
        )
        
        if not dicom_path:
            return
        
        global NAME, MRN, DOB, GENDER, ACCESSIONNO, MODALITY
        NAME = entry_patient_name.get()
        MRN = entry_patient_id.get()
        DOB = entry_patient_birthdate.get()
        GENDER = entry_patient_sex.get()
        ACCESSIONNO = entry_accession_number.get()
        MODALITY = entry_modality.get()
        
        create_dicom_from_jpg(JPG_FILE, dicom_path)
        print(f"DICOM file saved to {dicom_path}")

    def select_jpg_file():
        global JPG_FILE
        JPG_FILE = filedialog.askopenfilename(
            title="Select JPEG file",
            filetypes=[("JPEG files", "*.jpg;*.jpeg"), ("All files", "*.*")]
        )
        
        if not JPG_FILE:
            lbl_image.config(text="No JPEG file selected")
            return
        
        img = Image.open(JPG_FILE)
        
        # Resize the image to fit the GUI window, keeping aspect ratio
        base_width = 500
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        
        img = img.resize((base_width, h_size), PIL.Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        
        lbl_image.image = photo
        lbl_image.config(image=photo, text="")

    def exit_application():
        app.destroy()

    app = tk.Tk()
    app.title("JPG TO DICOM Converter "+VERSION)

    frame_image = ttk.Frame(app, padding="10")
    frame_image.grid(row=0, column=0, rowspan=7, padx=10, pady=5, sticky="nsew")

    lbl_image = ttk.Label(frame_image, text="No Image Loaded")
    lbl_image.pack(expand=True)

    frame_info = ttk.Frame(app, padding="10")
    frame_info.grid(row=0, column=1, columnspan=2, padx=10, pady=5, sticky="nsew")

    ttk.Label(frame_info, text="Patient Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    entry_patient_name = ttk.Entry(frame_info)
    entry_patient_name.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    entry_patient_name.insert(0, NAME)

    ttk.Label(frame_info, text="Patient ID:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    entry_patient_id = ttk.Entry(frame_info)
    entry_patient_id.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    entry_patient_id.insert(0, MRN)

    ttk.Label(frame_info, text="Patient Birth Date (YYYYMMDD):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    entry_patient_birthdate = ttk.Entry(frame_info)
    entry_patient_birthdate.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    entry_patient_birthdate.insert(0, DOB)

    ttk.Label(frame_info, text="Patient Sex (M/F):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    entry_patient_sex = ttk.Entry(frame_info)
    entry_patient_sex.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    entry_patient_sex.insert(0, GENDER)
  
    ttk.Label(frame_info, text="Modality:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    entry_modality = ttk.Entry(frame_info)
    entry_modality.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
    entry_modality.insert(0, MODALITY)

    ttk.Label(frame_info, text="Accession Number:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
    entry_accession_number = ttk.Entry(frame_info)
    entry_accession_number.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
    entry_accession_number.insert(0, ACCESSIONNO)
    
    frame_buttons = ttk.Frame(app, padding="10")
    frame_buttons.grid(row=6, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.map('TButton', foreground=[('!active', 'black'), ('active', 'gray')],
              background=[('!active', 'lightgray'), ('active', 'gray')],
              relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

    btn_select = ttk.Button(frame_buttons, text="Select JPG", command=select_jpg_file)
    btn_select.pack(side=tk.LEFT, padx=10, pady=20)

    btn_save = ttk.Button(frame_buttons, text="Save DICOM", command=save_dicom_file)
    btn_save.pack(side=tk.LEFT, padx=10, pady=20)

    btn_exit = ttk.Button(frame_buttons, text="Exit", command=exit_application)
    btn_exit.pack(side=tk.LEFT, padx=10, pady=20)

    app.columnconfigure(1, weight=1)
    frame_info.columnconfigure(1, weight=1)
    app.mainloop()

################################################################################
# Main Function - checks command line arguments and if none runs GUI
################################################################################

def main():
    parser = argparse.ArgumentParser(description="Convert a JPEG file to a DICOM file.")
    parser.add_argument("jpg_file", nargs='?', help="Path to the input JPEG file")
    parser.add_argument("dicom_file", nargs='?', help="Path to the output DICOM file")
    args = parser.parse_args()

    if args.jpg_file:
        dicom_path = args.dicom_file if args.dicom_file else os.path.splitext(args.jpg_file)[0] + '.dcm'
        create_dicom_from_jpg(args.jpg_file, dicom_path)
    else:
        open_gui()

if __name__ == "__main__":
    main()
