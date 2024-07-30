###############################################################################
# Will query PACS
#
# [DICOM settings]
# AET: MY_SCP
# PORT: 104
# 
# [STORAGE LOCATION]
# Folder: dicom_storage
#
# Alban Killingback July 2024
################################################################################

import configparser
from pydicom.dataset import Dataset
from pynetdicom import AE, debug_logger
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

#debug_logger()

# load the COM port number from the config file
config = configparser.ConfigParser()
config.read(r'DICOM Query SCU WORKING.ini')
my_ae_title = config['MY AET']['AET']
patient_id = config['SEARCH']['PATIENTID']
PACSAET = config['PACS DICOM settings']['AET']
PACSPORT = int(config['PACS DICOM settings']['PORT'])
PACSIP = config['PACS DICOM settings']['IPADDRESS']

# Create our Application Entity (AE)
ae = AE(ae_title=my_ae_title)
ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)

# Create our Identifier (query) dataset
ds = Dataset()
ds.PatientID = patient_id  # Replace with the actual PatientID you want to search for
ds.QueryRetrieveLevel = 'PATIENT'

# Associate with the peer AE at IP 10.165.131.130 and port 1133, with AE title 'MEDCON_SERVER'
assoc = ae.associate(PACSIP, PACSPORT, ae_title=PACSAET)
if assoc.is_established:
    # Send the C-FIND request
    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
    for (status, identifier) in responses:
        if status:
            print('C-FIND query status: 0x{0:04X}'.format(status.Status))
            if identifier:
                print(identifier)
        else:
            print('Connection timed out, was aborted or received invalid response')

    # Release the association
    assoc.release()
else:
    print('Association rejected, aborted or never connected')
