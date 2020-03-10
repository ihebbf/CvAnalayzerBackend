from fastapi.encoders import jsonable_encoder
from project.utils.Database import es
from project.controllers.extractor import *
from project import app


# A route to return all phone numbers
@app.get('/api/v1/getPhoneNumber')
def extract_Phone_Number():
    lista = []
    print("o")
    for e in loopAllCv():
        lista.append(extract_mobile_number(e))
    return jsonable_encoder({"Phone number": lista})


# A route to return all emails
@app.get('/api/v1/getEmail')
def extractEmail():
    lista = []
    for e in loopAllCv():
        lista.append(extract_email(e))
    return jsonable_encoder({"Email": lista})


# A route to return all ages
@app.get('/api/v1/getAge')
def extractAge():
    lista = []
    for e in loopAllCv():
        lista.append(extract_age(e))
    return jsonable_encoder({"Age": lista})


# A route to return all year of experience
@app.get('/api/v1/getYearsOfExp')
def extractExp():
    lista = []
    for e in loopAllCv():
        lista.append(extract_Year_of_experience(e))
    return jsonable_encoder({"Experience": lista})


# A route to return all names
@app.get('/api/v1/getName')
def extractName():
    lista = []
    for e in loopAllCv():
        lista.append(extract_name(e))

    return jsonable_encoder({"Name": lista})
    # return jsonify({"Name": extract_NAmes_NLTK(text)})


# A route to return all skills
@app.get('/api/v1/getSkills')
def extractSkills():
    lista = []
    for e in loopAllCv():
        lista.append(extract_skills(e))

    return jsonable_encoder({"Skills": lista})


# A route to return all phone langues
@app.get('/api/v1/getLanguages')
def extractLangues():
    lista = []
    for e in loopAllCv():
        lista.append(extract_langues(e))

    return jsonable_encoder({"Langues": lista})


# A route to return all CVs in format json and index all CVs in elasticSearch
@app.get('/api/v1/getCvJson')
async def FinalCvJson():
    lista = []
    for i, val in enumerate(loopAllCv()):
        lista.append(
            {"Name": extract_name(val), "Email": extract_email(val), "Phone Number": extract_mobile_number(val),
             "Skills": extract_skills(val), "Langues": extract_langues(val), "age": extract_age(val),
             "Year of experience": extract_Year_of_experience(val)})
        cv = {"Name": extract_name(val), "Email": extract_email(val), "Phone Number": extract_mobile_number(val),
              "Skills": extract_skills(val), "Langues": extract_langues(val), "age": extract_age(val),
              "Year of experience": extract_Year_of_experience(val)}
        es.index(index='cvs', doc_type='title', id="cv" + str(i + 1), body=cv)
    return jsonable_encoder({"CVs": lista})
