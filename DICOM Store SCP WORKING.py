###############################################################################
# Hosts a DICOM Storage SCP where the IP Address is the address of the PC
# and the AE Title and Port and storage location are defined in the ini file as
# [DICOM settings]
# AET: MY_SCP
# PORT: 104
# 
# [STORAGE LOCATION]
# Folder: dicom_storage
# Alban Killingback July 2024
################################################################################

import os
import configparser
import logging
from pydicom.dataset import Dataset
from pynetdicom import AE, evt, debug_logger
from pynetdicom.sop_class import Verification
from pynetdicom.sop_class import (
    CTImageStorage,
    MRImageStorage,
    PositronEmissionTomographyImageStorage,
    RTImageStorage,
    RTDoseStorage,
    RTStructureSetStorage,
    RTPlanStorage,
    SecondaryCaptureImageStorage,
    DigitalXRayImageStorageForPresentation,
    DigitalXRayImageStorageForProcessing,
    DigitalMammographyXRayImageStorageForPresentation,
    DigitalMammographyXRayImageStorageForProcessing,
    DigitalIntraOralXRayImageStorageForPresentation,
    DigitalIntraOralXRayImageStorageForProcessing,
    EnhancedSRStorage,
    ComprehensiveSRStorage,
    BasicTextSRStorage,
    XRayAngiographicImageStorage,
    XRayRadiofluoroscopicImageStorage,
    NuclearMedicineImageStorage,
    UltrasoundImageStorage,
    VLPhotographicImageStorage,
    VLEndoscopicImageStorage,
    VLMicroscopicImageStorage,
    VLSlideCoordinatesMicroscopicImageStorage,
    VLPhotographicImageStorage,
    EnhancedPETImageStorage,
    EnhancedCTImageStorage,
    EnhancedMRImageStorage,
    SegmentationStorage,
    SurfaceSegmentationStorage,
    ParametricMapStorage,
    EncapsulatedPDFStorage,
    EncapsulatedCDAStorage
)

# Enable logging for debugging purposes
# debug_logger()

# load the COM port number from the config file
config = configparser.ConfigParser()
config.read(r'DICOM Store SCP WORKING.ini')
ae_title = config['DICOM settings']['AET']
server_address = '127.0.0.1'  # Listen on all available network interfaces
server_port = int(config['DICOM settings']['PORT'])
storage_location = config['STORAGE LOCATION']['Folder']

# Define the storage directory
storage_dir = storage_location
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)

# Define a handler for the C-STORE request
def handle_store(event):
    """Handle a C-STORE request event."""
    ds = event.dataset
    ds.file_meta = event.file_meta

    # Create a filename based on the SOP Instance UID
    filename = os.path.join(storage_dir, f'{ds.SOPInstanceUID}.dcm')

    # Save the DICOM file
    ds.save_as(filename, write_like_original=False)
    return 0x0000  # Success status

# Define a handler for the C-ECHO request
def handle_echo(event):
    """Handle a C-ECHO request event."""
    return 0x0000  # Success status

# Initialize the Application Entity (AE)
ae = AE()

# Add supported presentation contexts for storage SOP classes
storage_sop_classes = [
    CTImageStorage,
    MRImageStorage,
    PositronEmissionTomographyImageStorage,
    RTImageStorage,
    RTDoseStorage,
    RTStructureSetStorage,
    RTPlanStorage,
    SecondaryCaptureImageStorage,
    DigitalXRayImageStorageForPresentation,
    DigitalXRayImageStorageForProcessing,
    DigitalMammographyXRayImageStorageForPresentation,
    DigitalMammographyXRayImageStorageForProcessing,
    DigitalIntraOralXRayImageStorageForPresentation,
    DigitalIntraOralXRayImageStorageForProcessing,
    EnhancedSRStorage,
    ComprehensiveSRStorage,
    BasicTextSRStorage,
    XRayAngiographicImageStorage,
    XRayRadiofluoroscopicImageStorage,
    NuclearMedicineImageStorage,
    UltrasoundImageStorage,
    VLPhotographicImageStorage,
    VLEndoscopicImageStorage,
    VLMicroscopicImageStorage,
    VLSlideCoordinatesMicroscopicImageStorage,
    VLPhotographicImageStorage,
    EnhancedPETImageStorage,
    EnhancedCTImageStorage,
    EnhancedMRImageStorage,
    SegmentationStorage,
    SurfaceSegmentationStorage,
    ParametricMapStorage,
    EncapsulatedPDFStorage,
    EncapsulatedCDAStorage,
]

for sop_class in storage_sop_classes:
    ae.add_supported_context(sop_class)

# Add supported presentation context for Verification SOP Class
ae.add_supported_context(Verification)

# Define the handlers for the supported services
handlers = [
    (evt.EVT_C_STORE, handle_store),
    (evt.EVT_C_ECHO, handle_echo),
]

# AET, Port are loaded from ini file and IP is the host IP

# Start the SCP
print(f'Starting DICOM Storage SCP on {server_address}:{server_port} with AE title {ae_title}')
ae.start_server((server_address, server_port), ae_title=ae_title, evt_handlers=handlers)
