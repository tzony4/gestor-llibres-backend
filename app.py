from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from flask_cors import CORS
import json
import os

# Llegeix la variable d'entorn amb el contingut JSON
firebase_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if not firebase_json:
    raise ValueError("La variable d'entorn GOOGLE_APPLICATION_CREDENTIALS_JSON no està definida.")

# Carrega el JSON directament com a diccionari
cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gestorllibres-12a81-default-rtdb.europe-west1.firebasedatabase.app/'  # ⚠️ Substitueix per l’URL real de la teva base de dades
})

app = Flask(__name__)
CORS(app)  # Permet connexions des del teu frontend

ref = db.reference('llibres')

@app.route('/afegir', methods=['POST'])
def afegir_llibre():
    dades = request.json
    if 'titol' in dades and 'autor' in dades and 'any' in dades:
        ref.push({
            'titol': dades['titol'],
            'autor': dades['autor'],
            'any': dades['any']
        })
        return jsonify({'status': 'ok'}), 201
    return jsonify({'error': 'Dades incompletes'}), 400

@app.route('/llista', methods=['GET'])
def llista_llibres():
    tots = ref.get()
    resultat = []
    if tots:
        for id_llibre, dades in tots.items():
            resultat.append({
                'id': id_llibre,
                'titol': dades['titol'],
                'autor': dades['autor'],
                'any': dades['any']
            })
    return jsonify(resultat)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
