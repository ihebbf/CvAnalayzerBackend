from datetime import date

from fastapi.encoders import jsonable_encoder

from project import app
import shutil
from typing import List

from project.Services.CvService import CvService
from project.Services.extractor import *
from fastapi import  UploadFile, File

from project.utils.CvArchive import *
from project.models.Cv import CvSchema
cvService=CvService()

@app.post("/cv/uploadfiles/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    lista = []
    cv = CvSchema()

    for file in files :
        file_object = file.file
        # create empty file to copy the file_object to
        upload_folder = open(os.path.join(upload, file.filename), 'wb+')
        shutil.copyfileobj(file_object, upload_folder)
        upload_folder.close()

    resume_list=loopOneOrAllCV(files)
    for fname in os.listdir(upload):
        if fname.lower().endswith('.pdf'):
                shutil.move(os.path.join(upload, fname), archiveCv)

    for i, val in enumerate(resume_list):
        Date=date.today()
        cv.nomPrenom=extract_name(val).lower()
        cv.email=extract_email(val)
        cv.numTel=extract_mobile_number(val)
        cv.age=extract_age(val)
        cv.dateAjout=Date
        cv.skills=extract_skills(val)
        cv.langues=extract_langues(val)
        cv.etat="En cours"
        lista.append(cv)
        res=cvService.create(jsonable_encoder(cv))
        cv=CvSchema()


    return jsonable_encoder(res)

@app.get("/cv/getAll", status_code=201)
async def read_all_cvs():
    return cvService.list()

@app.delete("/cv/delete/{id}", status_code=201)
async def delete(id):
    return cvService.delete(id)


@app.get("/cv/get/{id}", status_code=201)
async def get(id):
    return cvService.get(id)

@app.put("/cv/update/{id}", status_code=201)
async def update(cv:CvSchema,id):


    return  cvService.edit_cv(id,jsonable_encoder(cv))
