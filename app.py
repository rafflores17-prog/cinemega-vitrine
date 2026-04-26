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

SERVIDORES = [
    {"host": "http://cinevexio.top:80", "user": "175473583", "pass": "643238922"},
    {"host": "http://serv99.xyz:8880", "user": "1764371", "pass": "2419902"},
    {"host": "http://stmax.top:80", "user": "lucas6043", "pass": "px2926br"},
    {"host": "http://koquwz.com:80", "user": "471204", "pass": "epp4Jx"},
    {"host": "http://techon.one:80", "user": "003008", "pass": "440144634"}
]

# ================================
# FILTRAGEM INTELIGENTE DE LINKS
# ================================
def buscar_filme(titulo):
    links_encontrados = []
    # Limpeza básica do título para busca
    titulo_limpo = re.sub(r'[^\w\s]', '', titulo).lower().strip()
    
    # Palavras que indicam que é canal de TV ou lixo (Ignorar)
    blacklist = ['cine sky', '24h', 'live', 'canais', 'top filmes', 'streaming']

    try:
        conn = sqlite3.connect('filmes.db')
        c = conn.cursor()
        # Busca mais ampla no banco de dados
        c.execute("SELECT nome, url FROM playlist WHERE nome LIKE ?", (f"%{titulo_limpo}%",))
        resultados_db = c.fetchall()
        conn.close()
        
        for nome, url in resultados_db:
            nome_low = nome.lower()
            # Pula se estiver na blacklist
            if any(word in nome_low for word in blacklist):
                continue
            
            # Dá pontuação: MP4 e Dublado ganham mais pontos
            score = 0
            if url.endswith(('.mp4', '.mkv')): score += 10
            if "/movie/" in url: score += 5
            if "legendado" in nome_low or "(l)" in nome_low:
                score += 2 # Legendado é bom
            else:
                score += 5 # Dublado é prioridade
                
            links_encontrados.append({'url': url, 'score': score})
    except: pass

    # Se não achou no DB, tenta nas APIs dos servidores (Simultâneo)
    if not links_encontrados:
        for srv in SERVIDORES:
            url_api = f"{srv['host']}/player_api.php?username={srv['user']}&password={srv['pass']}&action=get_vod_streams"
            try:
                r = requests.get(url_api, timeout=4)
                for item in r.json():
                    nome_item = item.get('name', '').lower()
                    if titulo_limpo in nome_item:
                        if any(word in nome_item for word in blacklist): continue
                        
                        video_url = f"{srv['host']}/movie/{srv['user']}/{srv['pass']}/{item.get('stream_id')}.mp4"
                        score = 8 # API de VOD geralmente é certeira
                        if "legendado" in nome_item or "(l)" in nome_item: score -= 1
                        links_encontrados.append({'url': video_url, 'score': score})
            except: continue

    if links_encontrados:
        # Ordena pelo melhor link (maior score)
        links_encontrados.sort(key=lambda x: x['score'], reverse=True)
        melhor_link = links_encontrados[0]['url']
        return f"{KOYEB_URL}/proxy?url={melhor_link}"
    
    return None

# ================================
# ROTAS FLASK
# ================================
@app.route("/")
def home():
    q = request.args.get("q")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}" if q else f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR"
    res = requests.get(url, timeout=10).json().get("results", [])
    return render_template("index.html", filmes=res[:20], img=IMG, nome_site=NOME_SITE)

@app.route("/filme/<int:id>")
def detalhes(id):
    # Puxa dados completos, incluindo duração (runtime) e gêneros
    data = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos", timeout=10).json()
    play_link = buscar_filme(data.get('title', ''))
    trailer = next((v['key'] for v in data.get('videos', {}).get('results', []) if v['type'] == 'Trailer'), None)
    
    return render_template("detalhes.html", 
                           filme=data, 
                           img=IMG, 
                           bg=BG, 
                           play_link=play_link, 
                           nome_site=NOME_SITE, 
                           trailer_key=trailer)

@app.after_request
def add_cache_headers(response):
    if request.path.endswith((".js", ".css", ".png", ".jpg", ".jpeg", ".webp", ".svg")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/robots.txt')
def robots():
    conteudo = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(conteudo, mimetype="text/plain")

@app.route('/sitemap.xml')
def sitemap():
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += f'<url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>\n'
    try:
        res = requests.get(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR", timeout=5).json().get("results", [])
        for filme in res:
            xml += f'<url><loc>{SITE_URL}/filme/{filme["id"]}</loc><priority>0.8</priority></url>\n'
    except: pass
    xml += '</urlset>'
    return Response(xml, mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
