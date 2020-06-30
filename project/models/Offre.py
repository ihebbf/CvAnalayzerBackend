
from datetime import date, datetime, time, timedelta
from typing import List, Optional


from pydantic import BaseModel


class OffreSchema(BaseModel):


    titre :str=None
    description : str=None
    dateAjout : date=None
    skills : List[str]=None
    domaine: str=None
    manager:str=None
    etat: str=None
    equipe:str=None
    anneeExperience: int=None


