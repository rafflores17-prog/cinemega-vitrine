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

# 🚀 AQUI FICA O LINK DO SEU MOTOR (KOYEB)
# Troque pela URL real do seu aplicativo no Koyeb
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

# ================================
# CACHE INTELIGENTE
# ================================
@app.after_request
def add_cache_headers(response):
    if request.path.endswith((".js", ".css", ".png", ".jpg", ".jpeg", ".webp", ".svg")):
        response.headers["Cache-Control"] = "public, max-age=86400"
    else:
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route("/health")
def health():
    return "OK"

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
# SEO E SITEMAP
# ================================
@app.route('/robots.txt')
def robots():
    conteudo = "User-agent: *\nAllow: /\nDisallow: /static/\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(conteudo, mimetype="text/plain")

@app.route('/sitemap.xml')
def sitemap():
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<url><loc>{SITE_URL}/</loc><changefreq>hourly</changefreq><priority>1.0</priority></url>\n</urlset>"""
    return Response(xml, mimetype="application/xml")

# ================================
# BUSCAR FILME (A VITRINE MANDA PRO MOTOR)
# ================================
def buscar_filme(titulo):
    try:
        palavra_chave = titulo.split(':')[0].strip()
        titulo_busca_db = f"%{palavra_chave}%"
        
        conn = sqlite3.connect('filmes.db')
        c = conn.cursor()
        c.execute("SELECT url, nome FROM playlist WHERE nome LIKE ? ORDER BY LENGTH(nome) ASC LIMIT 1", (titulo_busca_db,))
        resultado = c.fetchone()
        conn.close()
        
        if resultado:
            # A MÁGICA ESTÁ AQUI: Vercel manda o vídeo pro Koyeb processar!
            return f"{KOYEB_URL}/proxy?url={resultado[0]}"
    except Exception as e:
        print("Aviso Local DB:", e)

    titulo_busca_api = re.sub(r'[^\w\s]', '', titulo).lower().strip()
    headers_api = {"User-Agent": random.choice(AGENTES_VIP)}
    
    for srv in SERVIDORES:
        url_api = f"{srv['host']}/player_api.php?username={srv['user']}&password={srv['pass']}&action=get_vod_streams"
        try:
            r = requests.get(url_api, headers=headers_api, timeout=10)
            if r.status_code != 200: continue
            
            matches_api = []
            for item in r.json():
                nome_limpo = re.sub(r'[^\w\s]', '', item.get('name', '')).lower()
                if titulo_busca_api in nome_limpo:
                    matches_api.append(item)
            
            if matches_api:
                matches_api.sort(key=lambda x: len(x.get('name', '')))
                item_escolhido = matches_api[0]
                video_url = f"{srv['host']}/movie/{srv['user']}/{srv['pass']}/{item_escolhido.get('stream_id')}.mp4"
                
                # A MÁGICA ESTÁ AQUI: Vercel manda o vídeo pro Koyeb processar!
                return f"{KOYEB_URL}/proxy?url={video_url}"
        except Exception:
            continue
    return None

# ================================
# ROTAS PRINCIPAIS
# ================================
@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
    else:
        url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR"
    
    res = requests.get(url, timeout=10).json().get("results", [])
    return render_template("index.html", filmes=res[:20], img=IMG, nome_site=NOME_SITE)

@app.route("/filme/<int:id>")
def detalhes(id):
    data = requests.get(f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos", timeout=10).json()
    play_link = buscar_filme(data.get('title', ''))
    trailer = next((v['key'] for v in data.get('videos', {}).get('results', []) if v['type'] == 'Trailer'), None)
    return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, nome_site=NOME_SITE, trailer_key=trailer)

# Para o Vercel, não precisamos do app.run() no final!
