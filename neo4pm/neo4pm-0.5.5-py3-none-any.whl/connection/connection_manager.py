from py2neo import Graph

class connection_manager:

    def __init__(self, uri, userName, password):
        self.uri = uri
        self.user = userName
        self.password = password
        
        self.connection = Graph(uri, auth=(userName, password))
        self.version, self.edition = self.get_version_edition()
        
        
    def get_connection(self):
        return self.connection
    
    def run_command(self, cypher):
        try:
            res = self.connection.run(cypher)
        except:
            try:
                res = self.connection.run(cypher)
            except:
                raise
        return res
    
    def get_query_result(self, cypher):
        return self.run_command(cypher).data()


    def get_version_edition(self):
        cypher_query = """call dbms.components() yield name, versions, edition unwind versions as version return name, version, edition""".replace('\r', ' ').replace('\n', ' ')
        result = self.get_query_result(cypher_query)
        
        version = result[0]['version']
        edition = result[0]['edition']
        
        return (version, edition)    
