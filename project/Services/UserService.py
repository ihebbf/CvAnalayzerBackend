import json
import os
from datetime import datetime, timedelta

import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext

from project.Controllers.UserController import SECRET_KEY, ALGORITHM
from project.models.User import TokenData
from project.utils.Database import es

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
class UserService:

    def __init__(self):
        pass

    def list(self):
        user_data = es.search(index="users",
                                 body={'size': 10000, 'query': {"match": {"_type": "_doc"}}},
                                 filter_path=['hits.hits._id', 'hits.hits._source'])
        users = []
        if 'hits' in user_data and 'hits' in user_data['hits']:


            for data in user_data['hits']['hits'] :
                json = data["_source"]
                json["id"] = data['_id']
                users.append(json)


        return users

    def get(cls, id):
       user_data = es.search(index="users",body={'query': {"bool": {"must": [{"match": {"_type": "_doc"}},{'match': {'_id': id}}]}}})
       if user_data['hits']["total"]['value']>0:
           json = user_data['hits']['hits'][0]["_source"]
           json["id"] = user_data['hits']['hits'][0]['_id']
           return json
       else:
            return False

    def create(self, User):
        id = int(datetime.timestamp(datetime.now()))

        res = es.index(index="users", doc_type='_doc', id=id, body=User)

        return res

    def edit_user(self,id, User):
        res = es.index(index="users", doc_type='_doc', id=id, body=User)
        if "result" in res and res["result"] == "updated":
            return True
        return False

    def getUserByEmail(cls, email):
        user_data = es.search(index="users",
                                 body={  "query": {
        "term" : {
            "email.keyword": email
        }}})
        if user_data['hits']["total"]['value'] > 0:

            json=user_data['hits']['hits'][0]["_source"]
            json["id"]= user_data['hits']['hits'][0]['_id']
            return json
        else:
            return False

    def delete(self,id):
        country_rec = self.get(id)
        if country_rec:
            res = es.delete(index="users", doc_type='_doc', id=id)
            return res

    def verify_password(self,plain_password, hashed_password):

        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self,email,password):
        user = self.getUserByEmail(email)
        print(user)
        if not user:
            return False
        if not self.verify_password(password, user['password']):

            return False
        else:
            return user

    def create_access_token(self, data: dict):
        to_encode = data.copy()

        to_encode.update()
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user(self,token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            token_data = TokenData(Email=email)
        except PyJWTError:
            raise credentials_exception
        user = self.getUserByEmail(token_data.Email)
        if user is None:
            raise credentials_exception
        return user

