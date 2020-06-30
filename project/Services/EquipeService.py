from datetime import datetime

from project.utils.Database import es


class EquipeService:

    def __init__(self):
        pass

    def list(self):
        equipe_data = es.search(index="equipe",
                               body={'size': 10000, 'query': {"match": {"_type": "_doc"}}},
                               filter_path=['hits.hits._id', 'hits.hits._source'])
        equipes = []
        if 'hits' in equipe_data and 'hits' in equipe_data['hits']:

            for data in equipe_data['hits']['hits']:
                json = data["_source"]
                json["id"] = data['_id']
                equipes.append(json)
        return equipes

    def get(cls, id):
        equipe_data = es.search(index="equipe", body={
            'query': {"bool": {"must": [{"match": {"_type": "_doc"}}, {'match': {'_id': id}}]}}})
        if equipe_data['hits']["total"]['value'] > 0:
            json = equipe_data['hits']['hits'][0]["_source"]
            json["id"] = equipe_data['hits']['hits'][0]['_id']
            return json
        else:
            return False

    def create(self, Equipe):
        id = int(datetime.timestamp(datetime.now()))

        res = es.index(index="equipe", doc_type='_doc', id=id, body=Equipe)

        return res



    def delete(self, id):
        equipe = self.get(id)
        if equipe:
            res = es.delete(index="equipe", doc_type='_doc', id=id)
            return res

    def getEquipeByManager(self,idmanager):
        equipe_data = es.search(index="equipe",
                              body={"query": {
                                  "term": {
                                      "idManager": idmanager
                                  }}})
        equipes = []
        print(equipe_data['hits']["total"]['value'])
        if equipe_data['hits']["total"]['value'] > 0:

            for data in equipe_data['hits']['hits']:
                json = data["_source"]
                json["id"] = data['_id']
                equipes.append(json)

            return equipes
        else:
            return []
