from flask import Flask, render_template, request, send_from_directory, jsonify, Response
import requests
import re
import os
import sqlite3

app = Flask(__name__)

NOME_SITE = "Cine Mega"
SITE_URL = "https://www.cinemega.online"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
KOYEB_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

# Servidores para busca em tempo real (caso não ache no DB)
SERVIDORES = [
    {"host": "http://cinevexio.top:80", "user": "175473583", "pass": "643238922"},
    {"host": "http://serv99.xyz:8880", "user": "1764371", "pass": "2419902"}
]

def buscar_filme(titulo):
    try:
        # Pega as duas primeiras palavras do título para uma busca precisa
        palavras = titulo.split()
        termo_busca = " ".join(palavras[:2]) if len(palavras) > 1 else palavras[0]
        termo_limpo = re.sub(r'[^\w\s]', '', termo_busca).strip()
        
        conn = sqlite3.connect('filmes.db')
        c = conn.cursor()
        
        # SQL OTIMIZADO: Já filtra MP4 e remove canais direto na consulta
        query = """
            SELECT url FROM playlist 
            WHERE nome LIKE ? 
            AND url LIKE '%.mp4%' 
            AND nome NOT LIKE '%Cine Sky%' 
            AND nome NOT LIKE '%24h%' 
            AND nome NOT LIKE '%LIVE%'
            LIMIT 1
        """
        c.execute(query, (f"%{termo_limpo}%",))
        resultado = c.fetchone()
        conn.close()

        if resultado:
            return f"{KOYEB_URL}/proxy?url={resultado[0]}"

        # Se não achou no DB, tenta uma busca ultra rápida na API do Servidor 1
        for srv in SERVIDORES:
            try:
                url_api = f"{srv['host']}/player_api.php?username={srv['user']}&password={srv['pass']}&action=get_vod_streams"
                r = requests.get(url_api, timeout=2).json() # Timeout curto para não travar o Chrome
                for item in r:
                    nome_item = item.get('name', '').lower()
                    if termo_limpo.lower() in nome_item:
                        stream_id = item.get('stream_id')
                        video_url = f"{srv['host']}/movie/{srv['user']}/{srv['pass']}/{stream_id}.mp4"
                        return f"{KOYEB_URL}/proxy?url={video_url}"
            except: continue
    except: pass
    return None

@app.route("/")
def home():
    q = request.args.get("q")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}" if q else f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR"
    try:
        res = requests.get(url, timeout=5).json().get("results", [])
    except: res = []
    return render_template("index.html", filmes=res[:20], img=IMG, nome_site=NOME_SITE)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        data = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos", timeout=5).json()
        play_link = buscar_filme(data.get('title', ''))
        trailer = next((v['key'] for v in data.get('videos', {}).get('results', []) if v['type'] == 'Trailer'), None)
        return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, nome_site=NOME_SITE, trailer_key=trailer)
    except:
        return "Erro ao carregar detalhes", 404

# --- ROTAS DE SUPORTE ---
@app.route('/sw.js')
def sw(): return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/robots.txt')
def robots():
    return Response(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", mimetype="text/plain")

@app.route('/sitemap.xml')
def sitemap():
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>{SITE_URL}/</loc></url>\n</urlset>'
    return Response(xml, mimetype="application/xml")

@app.after_request
def add_cache_headers(response):
    if request.path.endswith((".js", ".css", ".png", ".jpg", ".jpeg", ".webp")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
