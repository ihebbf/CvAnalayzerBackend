
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from project.Services.extractor import *
from fastapi import  HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

from project import app
from project.Services.UserService import UserService
from project.models.User import UserSchema, Token
from fastapi.security import HTTPBasic, HTTPBasicCredentials
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



from fastapi import Response, Depends

userService=UserService()
# A route to return all phone numbers
@app.get("/user/getAll", status_code=201)
async def read_all_users():
    return userService.list()



@app.post("/user/add", status_code=201)
async def register(user:UserSchema):

    if user.email.count("@")>1 :
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid Email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    searchUser=userService.getUserByEmail(user.email)

    if  searchUser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.password=pwd_context.hash(user.password)
    if user.email=='' or user.password=="" or user.nom=="" or user.prenom=="" or user.dateNaissance=="" or user.role=="":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field manquant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return  userService.create(jsonable_encoder(user))


@app.put("/user/update/{id}", status_code=201)
async def update(user:UserSchema,req:Request,id):
    data=await req.json()
    searchUser=userService.getUserByEmail(user.email)


    if not userService.verify_password(data["currentPassword"],searchUser["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )


    user.password=pwd_context.hash(user.password)
    return  userService.edit_user(id,jsonable_encoder(user))






@app.post("/user/login", response_model=Token)
async def login_for_access_token(request:Request):
    data=await request.json()
    user  =userService.authenticate_user(data['email'],data['password'])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = userService.create_access_token(
        data={"sub": user['email']}

    )
    return jsonable_encoder({"access_token": access_token, "token_type": "bearer"})



@app.delete("/user/delete/{id}", status_code=201)
async def delete(id):
    return userService.delete(id)


@app.get("/user/userEmail/{email}", status_code=201)
async def getByEmail(email):
    return userService.getUserByEmail(email)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@app.get("/user/secret")
async def read_items(current_user: UserSchema = Depends(userService.get_current_user)):
    return  current_user

