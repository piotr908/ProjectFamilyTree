from flask import Flask, render_template, request, redirect, url_for
from database import execute_read_query, execute_write_query

app = Flask(__name__)

@app.route('/')
def home():
    query = "MATCH (n) RETURN n.id, n.name, n.MOTHER, n.FATHER, n.PARTNER"
    nodes = execute_read_query(query)
    return render_template('home.html', nodes=nodes)

@app.route('/addperson', methods=['GET', 'POST'])
def add_person():
    query_female = "MATCH (a:Person WHERE a.sex = 'Female') return a.id, a.name"
    females = execute_read_query(query_female)
    query_male = "MATCH (a:Person WHERE a.sex = 'Male') return a.id, a.name"
    males = execute_read_query(query_male)
    query_nodes = "MATCH (n) return n.id, n.name"
    nodes = execute_read_query(query_nodes)

    if request.method == 'POST':
        new_person = {
            'name': request.form.get("name"),
            'sex': request.form.get("sex"),
            'father': request.form.get("father"),
            'mother': request.form.get("mother"),
            'partner': request.form.get("partner")
        }

        if new_person['name']:
            create_query = "CREATE (p1:Person {name: '%s', id: apoc.create.uuid(), sex: '%s'}) RETURN p1.id" % (new_person['name'], new_person['sex'])
            person_id = execute_write_query(create_query)[0][0]

            for role in ['mother', 'father']:
                if new_person[role]:
                    parent_name = execute_read_query(f"MATCH (parent:Person) WHERE parent.id = '{new_person[role]}' RETURN parent.name")[0][0]
                    relation_query = f"""
                    MATCH (parent:Person) WHERE parent.id = '{new_person[role]}'
                    MATCH (person:Person) WHERE person.id = '{person_id}'
                    CREATE (parent)-[:{role.upper()}]->(person)-[:CHILD]->(parent)
                    SET person.{role.upper()} = '{parent_name}'
                    """
                    execute_write_query(relation_query)

                if new_person['partner']:
                    partner_name = execute_read_query(f"MATCH (partner:Person) WHERE partner.id = '{new_person['partner']}' RETURN partner.name")[0][0]
                    partner_query = f"""
                    MATCH (partner:Person) WHERE partner.id = '{new_person['partner']}'
                    MATCH (person:Person) WHERE person.id = '{person_id}'
                    CREATE (partner)-[:PARTNER]->(person)-[:PARTNER]->(partner)
                    SET person.PARTNER = '{partner_name}', partner.PARTNER = '{new_person['name']}'
                    """
                    execute_write_query(partner_query)

        return redirect(url_for('home'))

    return render_template('addPerson.html', females=females, males=males, nodes=nodes)

@app.route('/findrelation', methods=['GET', 'POST'])
def find_relation():
    nodes = execute_read_query("MATCH (n) return n.id, n.name")
    if request.method == 'POST':
        person_1_id, person_2_id = request.form.get("person1"), request.form.get("person2")
        results = []

        if person_1_id and person_2_id:
            relation_query = f"""
            MATCH (startNode:Person{{id:'{person_1_id}'}}), (endNode:Person{{id:'{person_2_id}'}}), p=shortestPath((startNode)-[*..15]-(endNode))
            RETURN [x in nodes(p) | x.id]
            """
            outcome_ids = execute_read_query(relation_query)[0][0]
            for id in outcome_ids:
                person_query = f"MATCH (person:Person) WHERE person.id = '{id}' RETURN person.id, person.name, person.MOTHER, person.FATHER, person.PARTNER"
                results.append(execute_read_query(person_query))

        return render_template('findrelation.html', nodes=nodes, results=results)
    return render_template('findrelation.html', nodes=nodes)

if __name__ == "__main__":
    app.run(debug=True)
