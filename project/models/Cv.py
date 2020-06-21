
from datetime import date, datetime, time, timedelta
from typing import List, Optional


from pydantic import BaseModel


class CvSchema(BaseModel):


    nomPrenom :str=None
    email : str=None
    dateAjout : date=None
    skills : List[str]=None
    langues : List[str]=None
    domaine: str=None
    numTel:str=None
    age: str=None
    etat:str=None
    anneeExperience: int=None


