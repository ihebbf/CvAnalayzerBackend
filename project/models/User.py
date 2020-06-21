
from datetime import date, datetime, time, timedelta
from typing import List, Optional


from pydantic import BaseModel


class UserSchema(BaseModel):
    nom :str
    prenom : str
    dateNaissance : date
    password : str
    email : str
    role : str

class AuthSchema(BaseModel):

    password : str
    Email : str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    Email: str = None

