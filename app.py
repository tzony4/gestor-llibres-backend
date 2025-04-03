from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
from flask_cors import CORS
from firebase_admin import auth as firebase_auth
from functools import wraps
from flask import request, abort
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

def verificar_token(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        id_token = auth_header.replace('Bearer ', '')
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            request.uid = decoded_token['uid']
            request.email = decoded_token.get('email')
            return f(*args, **kwargs)
        except Exception as e:
            print("Token invàlid o inexistent:", e)
            abort(401)  # Unauthorized
    return decorador

app = Flask(__name__)
CORS(app)  # Permet connexions des del teu frontend

ref = db.reference('llibres')

@app.route('/afegir', methods=['POST'])
@verificar_token
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

@app.route('/esborrar/<id_llibre>', methods=['DELETE'])
@verificar_token
def esborrar_llibre(id_llibre):
    try:
        ref.child(id_llibre).delete()
        return jsonify({'status': 'eliminat'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/llista', methods=['GET'])
@verificar_token
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
