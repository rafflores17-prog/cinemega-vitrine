from flask import Flask, render_template, request, send_from_directory, jsonify, Response
import requests
import re
import os
import sqlite3
import random
import glob
from urllib.parse import quote

app = Flask(__name__)

# CONFIGURAÇÕES BÁSICAS
NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
# 🛡️ URL DO SEU PROXY NO KOYEB
KOYEB_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

# SERVIDORES DE APOIO (API)
SERVIDORES = [
    {"host": "http://cinevexio.top:80", "user": "175473583", "pass": "643238922"},
    {"host": "http://serv99.xyz:8880", "user": "1764371", "pass": "2419902"},
    {"host": "http://stmax.top:80", "user": "lucas6043", "pass": "px2926br"}
]

# AGENTES PARA O VÍDEO NÃO TRAVAR NO "CARREGANDO"
AGENTES_VIP = [
    "Dalvik/2.1.0 (Linux; U; Android 14; 2312FPCA6G Build/UP1A.231005.007)",
    "IPTVSmartersPlayer",
    "PurplePlayer/1.0",
    "VLC/3.0.18 LibVLC/3.0.18"
]

def buscar_filme(titulo):
    try:
        # Pega as duas primeiras palavras para busca precisa
        palavras = titulo.split()
        termo = " ".join(palavras[:2]) if len(palavras) > 1 else palavras[0]
        agente = random.choice(AGENTES_VIP)

        # 🔍 1. BUSCA EM TODOS OS BANCOS DATA*.DB
        bancos = glob.glob("data*.db")
        for db_nome in sorted(bancos):
            try:
                conn = sqlite3.connect(db_nome)
                c = conn.cursor()
                # Busca flexível ignorando lixo
                query = "SELECT url FROM playlist WHERE nome LIKE ? AND nome NOT LIKE '%Cine Sky%' LIMIT 1"
                c.execute(query, (f"%{termo}%",))
                resultado = c.fetchone()
                conn.close()

                if resultado:
                    url_v = resultado[0]
                    # Retorna o link formatado para o Proxy com Agente e Referer
                    return f"{KOYEB_URL}/proxy?url={quote(url_v, safe='')}&user_agent={quote(agente)}&referer={quote('http://iptv.com')}"
            except: continue

        # 🔍 2. SE NÃO ACHOU, BUSCA NAS APIS DOS SERVIDORES
        for srv in SERVIDORES:
            try:
                url_api = f"{srv['host']}/player_api.php?username={srv['user']}&password={srv['pass']}&action=get_vod_streams"
                r = requests.get(url_api, timeout=5).json()
                for item in r:
                    if termo.lower() in item.get('name', '').lower():
                        v_url = f"{srv['host']}/movie/{srv['user']}/{srv['pass']}/{item.get('stream_id')}.mp4"
                        return f"{KOYEB_URL}/proxy?url={quote(v_url, safe='')}&user_agent={quote(agente)}"
            except: continue
    except: pass
    return None

@app.route("/")
def home():
    q = request.args.get("q")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}" if q else f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR"
    try:
        res = requests.get(url, timeout=10).json().get("results", [])
    except: res = []
    return render_template("index.html", filmes=res[:20], img=IMG, nome_site=NOME_SITE)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        data = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos", timeout=10).json()
        play_link = buscar_filme(data.get('title', ''))
        trailer = next((v['key'] for v in data.get('videos', {}).get('results', []) if v['type'] == 'Trailer'), None)
        return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, nome_site=NOME_SITE, trailer_key=trailer)
    except: return "Erro ao carregar detalhes", 404

@app.route('/sw.js')
def sw(): return send_from_directory('.', 'sw.js', mimetype='application/javascript')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
