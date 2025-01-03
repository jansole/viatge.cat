from flask import Flask, render_template, jsonify, request
import json
import random
import funcions_joc as fj
import networkx as nx
import math
from fuzzywuzzy import process

app = Flask(__name__)

# Carregar dades del fitxer JSON
with open('./fitxers/divisions-administratives-v2r1-comarques-250000-20240705.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Variables del joc
### CALAIX DE LES CONSTANTS
K = 1.25
G = nx.read_graphml('./grafs/comarques.graphml')
comarques = list(G.nodes()) # agafem les comarques i desordenem

### INICI DEL JOC
random.shuffle(comarques)
inici, desti, camins = fj.generacio_inici_desti(G, comarques) # generació de cami
cami = [inici, desti] #cami que omplirà l'usuari

minim_torns = len(camins[0])
torns_totals = math.ceil(minim_torns * K + 1)

torns = 0
inputs = []

@app.route('/')
def index():
    # Renderitza el frontend
    return render_template('index.html')

@app.route('/init')
def init():
    # Proporciona dades inicials del joc
    return jsonify({
        "inici": inici,
        "desti": desti,
        "geojson": data,
        "torns_totals": torns_totals,
        "torns": torns
    })

@app.route('/guess', methods=['POST'])
def guess():
    global cami, camins, torns, G
    comarca_input = request.json.get('comarca').strip()

    millor_comarca, similitud = process.extractOne(comarca_input, comarques)  # o rapidfuzz.process.extractOne()

    if similitud >= 80:  # Llindar de similitud (80% de semblança)
        comarca = millor_comarca
        if comarca not in cami:
            cami.append(comarca)
            color = fj.calcul_proximitat(G, comarca, camins, colors=False)
            print(comarca)
            torns += 1
            print(torns, cami)

            if fj.solucio_trobada(cami, G):
                print('trobada oleeeeeeeeeee')
                return jsonify({
                    "success": True,
                    "message": "Has trobat la solució!",
                    "encerts": cami,
                    "finalitzat": True,
                    "torns": torns,
                    "minim_torns": minim_torns - 2,
                    "torns_totals": torns_totals,
                    "color": color
                })
                
            
            return jsonify({"success": True, "encerts": cami, "torns": torns, "torns_totals": torns_totals, "color": color})

        return jsonify({"success": False, "message": "Ja has endevinat aquesta comarca.", "torns": torns, "torns_totals": torns_totals})
    else:
        return jsonify({"success": False, "message": f"Comarca no vàlida o massa diferent: {comarca_input}.", "torns": torns, "torns_totals": torns_totals})

    

if __name__ == '__main__':
    app.run(debug=True)
