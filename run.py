import pydicom
from os import listdir,walk,rename,makedirs
from os.path import isfile, isdir, join
import traceback
import sys
def person_names_callback(dataset, data_element):
    if data_element.VR == "PN":
        data_element.value = "anonymous"
def deID(filepath,ds=None,hash_id=True,set_id=None,items={'InstitutionName':'None','InstitutionalDepartmentName':'None','InstitutionAddress':'None','ReferringPhysicianName':'None','StationName':'AREA51','RETIRED_OtherPatientIDs':'0000000','AdmissionID':'0000000','ProtocolName':'SAMPLE'}):
    if ds is None:
        ds=pydicom.dcmread(filepath)
    
    for item in items:
        val=items[item]
        if hasattr(ds,item):
            setattr(ds,item,val)
    try:
        ds.walk(person_names_callback)
    except :
        print ('name walk error in',filepath)
    
    try:
        ds.walk(curves_callback)
    except :
        print ('curve walk error in',filepath)
    if set_id is not None:
        ds.PatientID=set_id
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
        print('rename in dir :', root)
        for fn in fns:
            
              fp= join(root, fn )
              new_fp=None
              try:
                
                ds=pydicom.dcmread(fp)
                
                serNumMark='S'+("0000"+str(ds.SeriesNumber))[-3:]
                if 'SeriesDescription' in ds and ds.SeriesDescription!='':
                    serSymble=ds.SeriesDescription
                else:
                    serSymble=serNumMark
                if serier_folder:
                    makedirs(join(root, serSymble ), exist_ok=True)
                    new_fn=serSymble+"/"+str(ds.Modality)+"."+serNumMark+"."+("0000"+str(ds.InstanceNumber))[-3:]+'.dcm'

                else:
                    new_fn=str(ds.Modality)+"."+serNumMark+"."+("0000"+str(ds.InstanceNumber))[-3:]+'.dcm'
                    
                new_fp=join(root, new_fn )
                rename(fp,new_fp)
                print(fp,new_fp)
              except:
                print("error",fp,new_fp)

import hashlib
def md5(x,salt=None):
    if salt is not None:
        x=x+salt
    return hashlib.md5(x.encode('utf-8')).hexdigest()
def DIRdeID(sourceDir,targetDir=None,hash_id=False,set_id=None):
    dss=[]
    if targetDir is None:
        targetDir=sourceDir
    for root, dns, fns in walk(sourceDir):
        targetRoot=targetDir+root[len(sourceDir):]
        print('processing dir :', root,'->',targetRoot)
        for fn in fns:
            fp= join(root, fn )
            targetFp=join(targetRoot, fn )
            try:
                ds=deID(fp,hash_id=hash_id,set_id=set_id)
            
                ds.save_as(targetFp)
                print(targetFp,'processed')
                dss.append(ds)
            except Exception:
                print('error in file',fp)
                print(traceback.format_exc())
                # or
                print(sys.exc_info()[2])

    return dss
DIRdeID("./dicom","./out",set_id='TASTRO')
reNameDS("./out")