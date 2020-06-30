from datetime import date

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from starlette import status
import os

from starlette.requests import Request

from project import app
from project.Controllers.UserController import  pd
from project.Services.CvService import CvService
from project.Services.OffreService import OffreService
from project.Services.PredictorService import PredictorService
from project.models.Offre import OffreSchema
from project.utils.Keywords import keywordpath

offreService = OffreService()
predicService = PredictorService()
cvService=CvService()

@app.get("/offre/getAll", status_code=201)
async def get_all_offres():
    return offreService.list()


@app.get("/offre/getAllActif", status_code=201)
async def get_all_offres():
    return offreService.getAllActif()
@app.post("/offre/add", status_code=201)
async def register(offre:OffreSchema):

    offre.etat="actif"
    offre.dateAjout= date.today()

    if not offre.titre  or not offre.description  or not offre.dateAjout  or not offre.etat  or not offre.manager  or not offre.equipe  or offre.skills == [] or offre.skills == None  or not offre.anneeExperience  :
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    offre.domaine=predicService.getDomaineOffre(offre.skills)

    return  offreService.create(jsonable_encoder(offre))


@app.put("/offre/update/{id}", status_code=201)
async def update(offre:OffreSchema,id):
    if offre.titre == ''  or offre.description == "" or offre.etat == ""  or offre.titre == None  or offre.description == None or offre.etat == None :
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return offreService.edit(id,jsonable_encoder(offre))


@app.get("/offre/get/{id}", status_code=201)
async def get(id):

    return offreService.get(id)



@app.get("/offre/getAllSkills/", status_code=201)
async def getSkills():
    data = pd.read_csv(os.path.join(keywordpath, 'skills.csv'))

    # extract values
    skills = list(data.columns.values)

    return skills

@app.delete("/offre/delete/{id}", status_code=201)
async def delete(id):
    return offreService.delete(id)


@app.delete("/offre/deleteAll", status_code=201)
async def deleteAll():
    return offreService.deleteAll()


@app.post("/offre/search", status_code=201)
async def search(request:Request):
    data=await request.json()

    if offreService.searchOffre(data['titre'],data["manager"],data['equipe'])==False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return offreService.searchOffre(data['titre'],data["manager"],data['equipe'])

@app.get("/offre/matching/{id}", status_code=201)
async def matching(id):
    offre=offreService.get(id)
    if cvService.matchCVs(offre['domaine']) == False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Aucun CV",

            headers={"WWW-Authenticate": "Bearer"},
        )
    return  cvService.matchCVs(offre["domaine"])



