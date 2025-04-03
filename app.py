from flask import Flask, request, jsonify, abort
import firebase_admin
from firebase_admin import credentials, db, auth as firebase_auth
from flask_cors import CORS
import os
import json
from functools import wraps

# Firebase des de variable d'entorn segura
cred_dict = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://gestorllibres-12a81-default-rtdb.europe-west1.firebasedatabase.app/'  # Canvia per la teva URL real
})

app = Flask(__name__)
CORS(app)
ref = db.reference('socis')

# Middleware per verificar autenticació Firebase
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
            print("Token invàlid:", e)
            abort(401)
    return decorador

# Ruta per afegir un/a soci/a
@app.route('/afegir-soci', methods=['POST'])
@verificar_token
def afegir_soci():
    dades = request.json
    if 'nom' in dades and 'correu' in dades:
        ref.push({
            'nom': dades['nom'],
            'correu': dades['correu'],
            'creat_per': request.email
        })
        return jsonify({'status': 'afegit'}), 201
    return jsonify({'error': 'Dades incompletes'}), 400

# Ruta per llistar socis/es
@app.route('/llista-socis', methods=['GET'])
@verificar_token
def llista_socis():
    tots = ref.get()
    resultat = []
    if tots:
        for id_soci, dades in tots.items():
            resultat.append({
                'id': id_soci,
                'nom': dades['nom'],
                'correu': dades['correu'],
                'creat_per': dades.get('creat_per', '')
            })
    return jsonify(resultat)

# Ruta per eliminar soci/a
@app.route('/esborrar-soci/<id_soci>', methods=['DELETE'])
@verificar_token
def esborrar_soci(id_soci):
    try:
        ref.child(id_soci).delete()
        return jsonify({'status': 'eliminat'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
