import pydicom
from os import listdir,walk,rename,makedirs
from os.path import isfile, isdir, join

def person_names_callback(dataset, data_element):
    if data_element.VR == "PN":
        data_element.value = "anonymous"
def deID(filepath,ds=None,hash_id=True,items={'InstitutionName':'None','InstitutionalDepartmentName':'None','InstitutionAddress':'None','ReferringPhysicianName':'None','StationName':'AREA51','RETIRED_OtherPatientIDs':'0000000','AdmissionID':'0000000','ProtocolName':'SAMPLE'}):
    if ds is None:
        ds=pydicom.dcmread(filepath)
    
    for item in items:
        val=items[item]
        if hasattr(ds,item):
            setattr(ds,item,val)
    ds.walk(person_names_callback)
    ds.walk(curves_callback)
    if hash_id:
      ds.PatientID=md5(ds.PatientID+'deID')
    #ds.save_as(filepath)
    return ds

def curves_callback(dataset, data_element):
    if data_element.tag.group & 0xFF00 == 0x5000:
        del dataset[data_element.tag]

def reNameDS(dirpath,serier_folder=True):
    seriesMap={}
    for root, dns, fns in walk(dirpath):
        for fn in fns:
            if 'dcm' in fn:
              fp= join(root, fn )
              new_fp=None
              try:
                
                ds=pydicom.dcmread(fp)
                
                serNumMark='S'+("0000"+str(ds.SeriesNumber))[-3:]
                
                serSymble=ds.SeriesDescription
                if serier_folder:
                    makedirs(join(root, serSymble ), exist_ok=True)
                    new_fn=serSymble+"/"+str(ds.Modality)+"."+serNumMark+"."+("0000"+str(ds.InstanceNumber))[-3:]+'.dcm'

                else:
                    new_fn=str(ds.Modality)+"."+serNumMark+"."+("0000"+str(ds.InstanceNumber))[-3:]+'.dcm'
                    
                new_fp=join(root, new_fn )
                rename(fp,new_fp)
                print(fp)
              except:
                print("error",fp,new_fp)

import hashlib
def md5(x,salt=None):
    if salt is not None:
        x=x+salt
    return hashlib.md5(x.encode('utf-8')).hexdigest()
def DIRdeID(dirpath):
    dss=[]
    for root, dns, fns in walk(dirpath):
        for fn in fns:
            fp= join(root, fn )
            ds=deID(fp)
            
            ds.save_as(fp)
            dss.append(ds)
    return dss
DIRdeID("./dicom")
reNameDS("./dicom")