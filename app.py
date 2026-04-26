from flask import Flask, render_template, request, send_from_directory, jsonify, Response
import requests
import re
import os
import random
import sqlite3

app = Flask(__name__)

NOME_SITE = "Cine Mega"
SITE_URL = "https://www.cinemega.online"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"

# 🚀 MOTOR KOYEB CONECTADO
KOYEB_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

SERVIDORES = [
    {"host": "http://cinevexio.top:80", "user": "175473583", "pass": "643238922"},
    {"host": "http://serv99.xyz:8880", "user": "1764371", "pass": "2419902"},
    {"host": "http://stmax.top:80", "user": "lucas6043", "pass": "px2926br"},
    {"host": "http://koquwz.com:80", "user": "471204", "pass": "epp4Jx"},
    {"host": "http://techon.one:80", "user": "003008", "pass": "440144634"}
]

AGENTES_VIP = [
    "EPPIPROPLAYER/1.0.8 (Linux;Android 14) AndroidXMedia3/1.5.1",
    "purpleplayer/1.2.82",
    "Dalvik/2.1.0 (Linux; U; Android 14; 2312FPCA6G Build/UP1A.231005.007)",
    "Dart/3.11 (dart:io)"
]

@app.after_request
def add_cache_headers(response):
    if request.path.endswith((".js", ".css", ".png", ".jpg", ".jpeg", ".webp", ".svg")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/.well-known/assetlinks.json')
def assetlinks():
    return jsonify([{
        "relation": ["delegate_permission/common.handle_all_urls"],
        "target": {
            "namespace": "android_app",
            "package_name": "online.cinemega.www.twa",
            "sha256_cert_fingerprints": ["64:F7:CE:80:D5:1C:79:CE:91:A7:0E:C8:BE:71:49:E6:46:64:F6:D2:96:5F:12:D6:8F:41:DC:57:A9:4E:48:CD"]
        }
    }])

# ================================
# SEO, ROBOTS E SITEMAP DINÂMICO
# ================================
@app.route('/robots.txt')
def robots():
    conteudo = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(conteudo, mimetype="text/plain")

@app.route('/sitemap.xml')
def sitemap():
    """Gera um sitemap real com os links da Home e dos filmes populares"""
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Adiciona a Home
    xml += f'<url><loc>{SITE_URL}/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>\n'
    
    # Tenta pegar os filmes populares do TMDB para colocar no Sitemap
    try:
        res = requests.get(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR", timeout=5).json().get("results", [])
        for filme in res:
            xml += f'<url><loc>{SITE_URL}/filme/{filme["id"]}</loc><priority>0.8</priority></url>\n'
    except:
        pass

    xml += '</urlset>'
    return Response(xml, mimetype="application/xml")

# ================================
# BUSCA E PROXY (VIA KOYEB)
# ================================
def buscar_filme(titulo):
    try:
        palavra_chave = titulo.split(':')[0].strip()
        titulo_busca_db = f"%{palavra_chave}%"
        conn = sqlite3.connect('filmes.db')
        c = conn.cursor()
        c.execute("SELECT url FROM playlist WHERE nome LIKE ? LIMIT 1", (titulo_busca_db,))
        resultado = c.fetchone()
        conn.close()
        if resultado:
            return f"{KOYEB_URL}/proxy?url={resultado[0]}"
    except: pass

    titulo_busca_api = re.sub(r'[^\w\s]', '', titulo).lower().strip()
    for srv in SERVIDORES:
        url_api = f"{srv['host']}/player_api.php?username={srv['user']}&password={srv['pass']}&action=get_vod_streams"
        try:
            r = requests.get(url_api, timeout=5)
            for item in r.json():
                if titulo_busca_api in item.get('name', '').lower():
                    video_url = f"{srv['host']}/movie/{srv['user']}/{srv['pass']}/{item.get('stream_id')}.mp4"
                    return f"{KOYEB_URL}/proxy?url={video_url}"
        except: continue
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
