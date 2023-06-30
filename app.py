from flask import Flask, request, jsonify
import string
import random
import os
import redis
from functools import wraps
from flask_cors import CORS
from flask_restful import Api
import mysql.connector

app = Flask(__name__)
cache = redis.Redis()
api = Api(app)
CORS(app, resources={r"*": {"origins": "*"}})

app = Flask(__name__)
app.config['SECRET_KEY'] = '014dca53-yzfp-3933-z4pf-0218f0f597ed'
app.config['REDIS_HOST'] = 'localhost'
app.config['REDIS_PORT'] = 6379
app.config['REDIS_DB'] = 0

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '15Dev'
MYSQL_DATABASE = 'encurtadorurl'

# Configurando conexão com o Redis
redis_client = redis.Redis(
    host=app.config['REDIS_HOST'],
    port=app.config['REDIS_PORT'],
    db=app.config['REDIS_DB'],
    decode_responses=True
)

# Função para gerar um código de URL encurtada aleatório
def generate_short_url_code():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(6))
    return code

# Função para gerar uma API key
def gerarApiKey():
    key_length = 32
    characters = string.ascii_letters + string.digits
    api_key = ''.join(random.choice(characters) for _ in range(key_length))
    return api_key

# Decorator para autenticação com API Key
def require_api_key(view_func):
    @wraps(view_func)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and redis_client.exists(api_key):
            return view_func(*args, **kwargs)
        else:
            return jsonify({'error': 'API Key inválida'}), 401
    return decorated

# Rota para gerar uma nova API Key
@app.route('/gerarApiKey', methods=['POST'])
def gerarNovaApiKey():
    api_key = gerarApiKey()
    redis_client.set(api_key, "True")
    return jsonify({'api_key': api_key}), 201

# Rota para encurtar a URL
@app.route('/encurtar', methods=['POST'])
@require_api_key
def shorten_url():
    original_url = request.json['url']
    short_code = generate_short_url_code()

    # Conexão com o banco de dados MySQL
    conexaoBD = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    # Inserir os dados na tabela url_shortener
    insert_query = "INSERT INTO tbencurtadorurl (codigo, url_original) VALUES (%s, %s)"
    insert_values = (short_code, original_url)

    cursor = conexaoBD.cursor()
    cursor.execute(insert_query, insert_values)
    conexaoBD.commit()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexaoBD.close()

    return jsonify({'codigo': short_code}), 201

# Rota para redirecionar para a URL original
@app.route('/<codigo>', methods=['GET'])
def codigoParaUrl(codigo):
    # Conexão com o banco de dados MySQL
    conexaoBD = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

    # Buscar a URL original na tabela url_shortener
    select_query = "SELECT url_original FROM tbencurtadorurl WHERE codigo = %s"
    select_value = (codigo,)

    cursor = conexaoBD.cursor()
    cursor.execute(select_query, select_value)
    resultado = cursor.fetchone()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexaoBD.close()

    if resultado is None:
        return jsonify({'error': 'URL encurtada inválida'}), 404

    original_url = resultado[0]

    return jsonify({'original_url': original_url}), 200

if __name__ == '__main__':
    app.run(debug=True)
