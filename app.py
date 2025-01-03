from flask import Flask, render_template, request, redirect, url_for,send_file,session,jsonify
import networkx as nx
import funcions_joc as fj
import random
import math

app = Flask(__name__)
app.secret_key = 'una_clau_secreta_per_sessions'

# Càrrega del graf
G = nx.read_graphml('web/grafs/comarques.graphml')
comarques = list(G.nodes())

# Constants
K = 1.2

@app.route('/', methods=['GET'])
def init_game():
    # Generar inici, destí i camins
    random.shuffle(comarques)
    inici, desti, camins = fj.generacio_inici_desti(G, comarques)

    # Guardar l'estat del joc a la sessió
    session['inici'] = inici
    session['desti'] = desti
    session['camins'] = camins
    session['cami'] = [inici]
    session['torns_totals'] = math.ceil(len(camins[0]) * K)
    session['torns'] = 0


    return render_template('index.html',inici=inici, desti=desti, camins=camins, cami=[inici], torns=0, torns_totals=math.ceil(len(camins[0]) * K))

if __name__ == '__main__':
    app.run(debug=True)