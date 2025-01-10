from flask import Flask, render_template, jsonify, request
import json
import random
import funcions_joc as fj
import networkx as nx
import math
from fuzzywuzzy import process

app = Flask(__name__)

with open('./fitxers/divisions-administratives-v2r1-comarques-250000-20240705.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

K = 1.33
G = nx.read_graphml('./grafs/comarques.graphml')
comarques = list(G.nodes())

random.shuffle(comarques)
inici, desti, camins = fj.generacio_inici_desti(G, comarques)
cami = [inici, desti]

minim_torns = len(camins[0])
torns_totals = math.ceil(minim_torns * K + 1)
torns = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/init')
def init():
    return jsonify({
        "inici": inici,
        "desti": desti,
        "geojson": data,
        "torns_totals": torns_totals,
        "torns": torns,
        "comarques": comarques
    })

@app.route('/suggestions')
def get_suggestions():
    query = request.args.get('query', '').lower()
    suggestions = [c for c in comarques if query in c.lower()][:5]
    return jsonify(suggestions)

@app.route('/guess', methods=['POST'])
def guess():
    global cami, torns
    comarca_input = request.json.get('comarca').strip()

    millor_comarca, similitud = process.extractOne(comarca_input, comarques)

    if similitud >= 80:
        comarca = millor_comarca
        if comarca not in cami:
            cami.append(comarca)
            color = fj.calcul_proximitat(G, comarca, camins, colors=False)
            torns += 1

            if fj.solucio_trobada(cami, G):
                return jsonify({
                    "success": True,
                    "message": "Has trobat la solució!",
                    "encerts": cami,
                    "finalitzat": True,
                    "torns": torns,
                    "minim_torns": minim_torns - 2,
                    "torns_totals": torns_totals,
                    "color": color,
                    "comarca": comarca  # Return exact comarca name
                })
            
            return jsonify({
                "success": True,
                "encerts": cami,
                "torns": torns,
                "torns_totals": torns_totals,
                "color": color,
                "comarca": comarca  # Return exact comarca name
            })

if __name__ == '__main__':
    app.run(debug=True)