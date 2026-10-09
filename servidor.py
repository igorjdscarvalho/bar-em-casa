#!/usr/bin/env python3
"""
Bar em Casa — Servidor com Flask, Persistência e Proteção por Senha
Pronto para o Railway
"""

import json
import os
from functools import wraps
from flask import Flask, request, jsonify, Response, send_from_directory

app = Flask(__name__, static_folder=".")

ARQUIVO = "dados.json"

DADOS_INICIAIS = {
    "bottles":  [],
    "history":  [],
    "useCount": {},
    "emptyCount": {},
    "cellar": [],
    "drinks": []
}

# Definição de Usuário e Senha (você pode alterar aqui ou via Variáveis de Ambiente no Railway)
USER_NAME = os.environ.get("APP_USER", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "bar123")

def check_auth(username, password):
    """Verifica se o usuário e senha estão corretos."""
    return username == USER_NAME and password == APP_PASSWORD

def authenticate():
    """Envia cabeçalho para solicitar autenticação no navegador."""
    return Response(
        'Acesso restrito. Insira suas credenciais.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Decorador para proteger as rotas com senha."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def load_data():
    if not os.path.exists(ARQUIVO):
        save_data(DADOS_INICIAIS)
        return DADOS_INICIAIS
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DADOS_INICIAIS

def save_data(data):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Rota principal:serve o seu HTML protegidíssimo por senha
@app.route("/")
@requires_auth
def index():
    return send_from_directory(".", "bar-em-casa-beta3.1.html")

# API para buscar os dados (/dados)
@app.route("/dados", methods=["GET"])
@requires_auth
def get_dados():
    return jsonify(load_data())

# API para salvar os dados (/dados via POST)
@app.route("/dados", methods=["POST"])
@requires_auth
def post_dados():
    try:
        body = request.get_json(force=True)
        if body is not None:
            save_data(body)
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": "JSON inválido"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

if __name__ == "__main__":
    # O Railway define automaticamente a porta pela variável de ambiente PORT
    port = int(os.environ.get("PORT", 8181))
    app.run(host="0.0.0.0", port=port)