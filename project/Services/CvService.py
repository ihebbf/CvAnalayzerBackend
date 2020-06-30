
from datetime import datetime

from project.utils.Database import es


class CvService:

    def __init__(self):
        pass

    def list(self):
        cv_data = es.search(index="cvsweb",
                                 body={'size': 10000, 'query': {"match": {"_type": "_doc"}}},
                                 filter_path=['hits.hits._id', 'hits.hits._source'])
        cvs = []
        if 'hits' in cv_data and 'hits' in cv_data['hits']:


            for data in cv_data['hits']['hits'] :
                json = data["_source"]
                json["id"] = data['_id']
                cvs.append(json)
        return cvs

    def get(cls, id):
       cv_data = es.search(index="cvsweb",body={'query': {"bool": {"must": [{"match": {"_type": "_doc"}},{'match': {'_id': id}}]}}})
       if cv_data['hits']["total"]['value']>0:
           json = cv_data['hits']['hits'][0]["_source"]
           json["id"] = cv_data['hits']['hits'][0]['_id']
           return json
       else:
            return False

    def create(self, Cv):
        id = int(datetime.timestamp(datetime.now()))

        res = es.index(index="cvsweb", doc_type='_doc', id=id, body=Cv)

        return res

    def edit_cv(self,id, Cv):
        res = es.index(index="cvsweb", doc_type='_doc', id=id, body=Cv)
        if "result" in res and res["result"] == "updated":
            return True
        return False


    def delete(self,id):
        cv = self.get(id)
        if cv:
            res = es.delete(index="cvsweb", doc_type='_doc', id=id)
            return res

    def matchCVs(self, domaine):
        cv_data = es.search(index="cvsweb", body={
            'query': {"bool": {"must": [{"match": {"_type": "_doc"}}, {"term": {"domaine.keyword": domaine}},
                                       ]}}})

        cvs = []
        if cv_data['hits']["total"]['value'] > 0:

            for data in cv_data['hits']['hits']:
                json = data["_source"]
                json["id"] = data['_id']
                cvs.append(json)

            return cvs
        else:
            return False