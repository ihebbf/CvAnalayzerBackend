from Tools.scripts.dutree import display
from elasticsearch import Elasticsearch
import pandas as pd
import  joblib
from fastapi.encoders import jsonable_encoder

es = Elasticsearch()
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from sklearn.preprocessing import MultiLabelBinarizer
from project.Services.CvService import CvService
from project.utils.Keywords import *
from project.utils import currentPath

cvService=CvService()
class PredictorService:

    def __init__(self):
        pass

    def predict(self,skills):

        data = pd.read_csv(os.path.join(keywordpath,"skills.csv")).apply(lambda x: x.astype(str).str.lower())
        # extract values
        skillsKeyword = list(data.columns.str.lower().values)



        CVs=jsonable_encoder([{'skills':skills}])

        df = pd.DataFrame.from_dict(CVs, orient="columns")

        mlb = MultiLabelBinarizer(classes=skillsKeyword)

        Dfskills = pd.DataFrame(mlb.fit_transform(df['skills']), columns=mlb.classes_, index=df.index)

        df = df.drop("skills", axis=1)

        result = pd.concat([Dfskills], axis=1, sort=False)
        knn_from_joblib = joblib.load(os.path.join(currentPath,"filename.pkl"))

        # Use the loaded model to make predictions
        if knn_from_joblib.predict(result)[0]==0:
            return "Reseau "

        elif  knn_from_joblib.predict(result)[0]==1:
            return "Developpement"
        elif knn_from_joblib.predict(result)[0]==2:
            return "Data science"


    def  getDomaineOffre(self,skills):
        dataScience= pd.read_csv(os.path.join(keywordpath, "datascience.csv")).apply(lambda x: x.astype(str).str.lower())
        # extract values
        dataScienceKeyword = list(dataScience.columns.str.lower().values)
        web = pd.read_csv(os.path.join(keywordpath, "web.csv")).apply(lambda x: x.astype(str).str.lower())
        webKeyword = list(web.columns.str.lower().values)
        countdatascience=0
        countweb=0
        countreseau=0
        reseau = pd.read_csv(os.path.join(keywordpath, "reseau.csv")).apply(lambda x: x.astype(str).str.lower())
        # extract values
        reseauKeyword = list(reseau.columns.str.lower().values)

        all=[]
        for skill in skills:

            if skill in dataScienceKeyword :
                countdatascience+=1

            if skill in webKeyword:
                countweb += 1

            if skill in reseauKeyword:
                countreseau += 1


        all.append(countdatascience)
        all.append(countreseau)
        all.append(countweb)
        m = max(all)
        maxIndexes=[i for i, j in enumerate(all) if j == m]
        if len(maxIndexes)==1:
            if all.index(max(all)) == 0:
                return  "Data science"
            elif all.index(max(all)) == 1:
                return "Reseau"
            elif all.index(max(all)) == 2:
                return  "Developpement"





