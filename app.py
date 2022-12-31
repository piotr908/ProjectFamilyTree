from flask import Flask, render_template, request, redirect, url_for
from database import execute_read_query, execute_write_query

app = Flask(__name__)

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/', methods=['GET', 'POST'])
def home():
    nodes = execute_read_query("MATCH (n) RETURN n.id, n.name, n.MOTHER, n.FATHER, n.PARTNER")
    return render_template('home.html', nodes = nodes)

@app.route('/addperson', methods=['GET', 'POST'])
def addPerson():
    females = execute_read_query("MATCH (a:Person WHERE a.sex = 'Female') return a.id, a.name")
    males = execute_read_query("MATCH (a:Person WHERE a.sex = 'Male') return a.id, a.name")
    nodes = execute_read_query("MATCH (n) return n.id, n.name")
    if request.method == 'POST':
        person_name = request.form.get("name")
        person_sex = request.form.get("sex")
        person_father = request.form.get("father")
        person_mother = request.form.get("mother")
        person_partner = request.form.get("partner")

        if(person_name != ""):
            query = "CREATE (p1:Person { name: '%s', id: apoc.create.uuid(), sex: '%s'}) RETURN p1.id" % (person_name, person_sex)
            id = execute_write_query(query)
            if(person_mother != ""):
                mother = execute_read_query("MATCH (mother:Person) WHERE mother.id = '%s' RETURN mother.name" %(person_mother))
                query = "MATCH (mother:Person) WHERE mother.id = '%s' MATCH (person:Person) WHERE person.id = '%s' CREATE (mother)-[:MOTHER]->(person)-[:CHILD]->(mother) SET person.MOTHER = '%s'" %(person_mother, id[0][0], mother[0][0])
                execute_write_query(query)
                        
            if(person_father != ""):
                father = execute_read_query("MATCH (father:Person) WHERE father.id = '%s' RETURN father.name" %(person_father))
                query = "MATCH (father:Person) WHERE father.id = '%s' MATCH (person:Person) WHERE person.id = '%s' CREATE (father)-[:FATHER]->(person)-[:CHILD]->(father) SET person.FATHER = '%s'" %(person_father, id[0][0], father[0][0])
                execute_write_query(query)

            if(person_partner != ""):
                partner = execute_read_query("MATCH (partner:Person) WHERE partner.id = '%s' RETURN partner.name" %(person_partner))
                query = "MATCH (partner:Person) WHERE partner.id = '%s' MATCH (person:Person) WHERE person.id = '%s' CREATE (partner)-[:PARTNER]->(person)-[:PARTNER]->(partner) SET person.PARTNER = '%s' SET partner.PARTNER = '%s'" %(person_partner, id[0][0], partner[0][0], person_name)
                execute_write_query(query)

        return redirect(url_for('home'))
    return render_template('addPerson.html', females = females, males = males, nodes = nodes)

@app.route('/findconnection', methods=['GET', 'POST'])
def findConnection():
    nodes = execute_read_query("MATCH (n) return n.id, n.name")
    if request.method == 'POST':
        person_1_id = request.form.get("person1")
        person_2_id = request.form.get("person2")
        resu =[]
        if(person_1_id != "" and person_2_id != ""):
            query = "MATCH (startNode:Person{id:'%s'}), (endNode:Person{id:'%s'}), p=shortestPath((startNode)-[*..15]-(endNode)) RETURN [x in nodes(p) | x.id]" %(person_1_id, person_2_id)
            outcome_ids = execute_read_query(query)
            for id in outcome_ids[0][0]:
                resu.append(execute_read_query("MATCH (person:Person) WHERE person.id = '%s' RETURN person.id, person.name, person.MOTHER, person.FATHER, person.PARTNER" %id))
        return render_template('findconnection.html',nodes = nodes, results = resu)
    return render_template('findconnection.html', nodes = nodes)


