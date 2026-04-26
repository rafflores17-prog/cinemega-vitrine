from flask import Flask, render_template, request, send_from_directory, jsonify, Response
import requests
import re
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
    {"host": "http://stmax.top:80", "user": "lucas6043", "pass": "px2926br"}
]

def buscar_filme(titulo):
    try:
        # Pega a primeira palavra do título para busca no DB (ex: Rambo)
        termo_busca = titulo.split(':')[0].split('-')[0].strip()
        
        conn = sqlite3.connect('filmes.db')
        c = conn.cursor()
        # Busca links que tenham o nome e terminem com .mp4 (filtra VOD direto no SQL)
        c.execute("SELECT url FROM playlist WHERE nome LIKE ? AND url LIKE '%.mp4%' LIMIT 5", (f"%{termo_busca}%",))
        resultados = c.fetchall()
        conn.close()

        blacklist = ['cine sky', '24h', 'live', 'canais', 'tv']

        if resultados:
            for res in resultados:
                url = res[0]
                # Se não for canal, retorna o primeiro MP4 que achar
                if not any(word in url.lower() for word in blacklist):
                    return f"{KOYEB_URL}/proxy?url={url}"

        # Se não achou no DB, tenta na API rápida de um servidor
        for srv in SERVIDORES:
            url_api = f"{srv['host']}/player_api.php?username={srv['user']}&password={srv['pass']}&action=get_vod_streams"
            r = requests.get(url_api, timeout=3).json()
            for item in r:
                if termo_busca.lower() in item.get('name', '').lower():
                    stream_id = item.get('stream_id')
                    video_url = f"{srv['host']}/movie/{srv['user']}/{srv['pass']}/{stream_id}.mp4"
                    return f"{KOYEB_URL}/proxy?url={video_url}"
    except:
        pass
    return None

@app.route("/")
def home():
    q = request.args.get("q")
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}" if q else f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR"
    res = requests.get(url, timeout=10).json().get("results", [])
    return render_template("index.html", filmes=res[:20], img=IMG, nome_site=NOME_SITE)

@app.route("/filme/<int:id>")
def detalhes(id):
    data = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos", timeout=10).json()
    play_link = buscar_filme(data.get('title', ''))
    trailer = next((v['key'] for v in data.get('videos', {}).get('results', []) if v['type'] == 'Trailer'), None)
    return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, nome_site=NOME_SITE, trailer_key=trailer)

# Rotas de suporte (Robots, Sitemap, SW) mantidas iguais...
@app.route('/sw.js')
def sw(): return send_from_directory('.', 'sw.js', mimetype='application/javascript')
@app.route('/robots.txt')
def robots(): return Response(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml", mimetype="text/plain")
@app.route('/sitemap.xml')
def sitemap():
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>{SITE_URL}/</loc></url>\n</urlset>'
    return Response(xml, mimetype="application/xml")

if __name__ == "__main__":
    app.run(debug=True)
