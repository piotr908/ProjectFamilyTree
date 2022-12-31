from neo4j import GraphDatabase


class Database:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()         # Don't forget to close the driver connection when you are finished with it

    def read_query(self, query):
        def cypher(tx, cypher):
            outcome = tx.run(cypher)
            values = []
            for records in outcome:
                values.append(records.values())
            return values
        with self.driver.session(database="neo4j") as session:
            return session.read_transaction(cypher, query)

    def write_query(self, query):
        def cypher(tx, cypher):
            outcome = tx.run(cypher)
            values = []
            for records in outcome:
                values.append(records.values())
            return values
        with self.driver.session(database="neo4j") as session:
            return session.write_transaction(cypher, query)

uri = "neo4j+s://068d36af.databases.neo4j.io"
user = "neo4j"
password = "vZC1Ql9DS_83iGnumKpl4KJzximfhJ3yBiTO3F16dZk"
app = Database(uri, user, password)

def execute_read_query(query):
    return app.read_query(query)

def execute_write_query(query):
    return app.write_query(query)