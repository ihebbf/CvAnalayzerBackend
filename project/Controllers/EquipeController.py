from fastapi.encoders import jsonable_encoder
from project import app
from project.Services.EquipeService import EquipeService
from project.models.Equipe import EquipeSchema


equipeService = EquipeService()


@app.get("/equipe/getAll", status_code=201)
async def get_all_offres():
    return equipeService.list()


@app.post("/equipe/add", status_code=201)
async def register(equipe: EquipeSchema):
    return equipeService.create(jsonable_encoder(equipe))


@app.get("/equipe/getByManager/{id}", status_code=201)
async def getByManager(id):
    return equipeService.getEquipeByManager(id)


@app.delete("/equipe/delete/{id}", status_code=201)
async def delete(id):
    return equipeService.delete(id)
