
from datetime import datetime

from project.utils.Database import es


class OffreService:

    def __init__(self):
        pass

    def list(self):
        offre_data = es.search(index="offre",
                                 body={'size': 10000, 'query': {"match": {"_type": "_doc"}}},
                                 filter_path=['hits.hits._id', 'hits.hits._source'])
        offres = []
        if 'hits' in offre_data and 'hits' in offre_data['hits']:


            for data in offre_data['hits']['hits'] :
                json = data["_source"]
                json["id"] = data['_id']
                offres.append(json)
        return offres

    def get(cls, id):
       offre_data = es.search(index="offre",body={'query': {"bool": {"must": [{"match": {"_type": "_doc"}},{'match': {'_id': id}}]}}})
       if offre_data['hits']["total"]['value']>0:
           json = offre_data['hits']['hits'][0]["_source"]
           json["id"] = offre_data['hits']['hits'][0]['_id']
           return json
       else:
            return False

    def create(self, Offre):
        id = int(datetime.timestamp(datetime.now()))

        res = es.index(index="offre", doc_type='_doc', id=id, body=Offre)

        return res

    def edit(self,id, Offre):
        res = es.index(index="offre", doc_type='_doc', id=id, body=Offre)
        if "result" in res and res["result"] == "updated":
            return True
        return False


    def delete(self,id):
        offre = self.get(id)
        if offre:
            res = es.delete(index="offre", doc_type='_doc', id=id)
            return res


    def deleteAll(self):
      es.delete_by_query(index="offre", body={"query": {"match_all": {}}})

    def searchOffre(self,titre,manager,equipe):
        user_data = es.search(index="offre", body={
            'query': {"bool": {"must": [{"match": {"_type": "_doc"}},{"term": {"titre.keyword": titre}},{"term": {"manager.keyword": manager}},{"term": {"equipe.keyword": equipe}},{"term": {"etat.keyword": "actif"}}]}}})

        users=[]
        if user_data['hits']["total"]['value'] > 0:

            for data in user_data['hits']['hits']:
                json = data["_source"]
                json["id"] = data['_id']
                users.append(json)

            return users
        else:
            return False

    def getAllActif(self):
        user_data = es.search(index="offre", body={
            'query': {"bool": {"must": [{"match": {"_type": "_doc"}}, {"term": {"etat.keyword": "actif"}},
                                      ]}}})

        users = []
        if user_data['hits']["total"]['value'] > 0:

            for data in user_data['hits']['hits']:
                json = data["_source"]
                json["id"] = data['_id']
                users.append(json)

            return users
        else:
            return False



