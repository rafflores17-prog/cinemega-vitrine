From flask import Flask, render_template, request
import requests
import time
from urllib.parse import quote

app = Flask(__name__)

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"

IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"

# URL DO SEU MOTOR NO KOYEB
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

TIMEOUT = 10
CACHE = {}
CACHE_TEMPO = 600

# =========================
# FUNÇÕES DE APOIO
# =========================

def buscar_tmdb(url):
    agora = time.time()
    if url in CACHE:
        dados, timestamp = CACHE[url]
        if agora - timestamp < CACHE_TEMPO:
            return dados
    try:
        res = requests.get(url, timeout=TIMEOUT)
        dados = res.json().get("results", [])
        CACHE[url] = (dados, agora)
        return dados
    except Exception as e:
        print(f"Erro TMDB: {e}")
        return []

def gerar_link_play(titulo):
    """
    AJUSTE MESTRE: Não fazemos mais o requests.head aqui.
    Isso evita que a Vercel bloqueie o link por demora do servidor IPTV.
    """
    return f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"

@app.context_processor
def controle_de_anuncios():
    user_agent = request.headers.get('User-Agent', '').lower()
    is_app = 'wv' in user_agent
    return dict(mostrar_ads=not is_app)

# =========================
# ROTAS DO SITE
# =========================

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        filmes = buscar_tmdb(url)
        return render_template("index.html", filmes=filmes, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca="🔍 Resultados da Busca")

    try:
        destaques = buscar_tmdb(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR")[:5]
        populares = buscar_tmdb(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR")
        comedia = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35")
        ficcao = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=878")
        terror = buscar_tmdb(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27")
    except:
        destaques = populares = comedia = ficcao = terror = []

    return render_template("index.html", destaques=destaques, populares=populares, comedia=comedia, ficcao=ficcao, terror=terror, img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url_detalhes = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        data = requests.get(url_detalhes, timeout=TIMEOUT).json()
        
        titulo_base = data.get("title", "")
        ano = data.get("release_date", "")[:4]
        titulo_busca = f"{titulo_base} ({ano})" if ano else titulo_base

        # LINK DE PLAY DIRETO PRO MOTOR
        play_link = gerar_link_play(titulo_busca)

        generos = [g["name"] for g in data.get("genres", [])]
        duracao = f"{data.get('runtime', 0)} min"
        nota = round(data.get("vote_average", 0), 1)
        
        videos = data.get("videos", {}).get("results", [])
        trailer = next((v["key"] for v in videos if v["site"] == "YouTube"), None)
        recomendados = data.get("recommendations", {}).get("results", [])[:6]

        return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, trailer_key=trailer, recomendados=recomendados, generos=generos, duracao=duracao, nota=nota, nome_site=NOME_SITE)
    except Exception as e:
        print(f"Erro detalhes: {e}")
        return "Erro ao carregar detalhes", 404

@app.route("/health")
def health():
    return {"status": "online", "site": NOME_SITE}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

meu detalhe vercel

<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{{ filme.title }} - Cine Mega</title>

<meta name="clckd" content="5c83dac11e09aed23035106950017f4a" />

<script type="text/javascript" data-cfasync="false">
/*<![CDATA[/* */
(function(){var h=window,g="f4875cdf735c070a6ebae3a0bf13b576",t=[["siteId",5294609],["minBid",0],["popundersPerIP","0"],["delayBetween",0],["default",false],["defaultPerDay",0],["topmostLayer","auto"]],e=["d3d3LmJsb2NrYWRzbm90LmNvbS95aGFtbWVyLm1pbi5jc3M=","ZG5oZmk1bm4yZHQ2Ny5jbG91ZGZyb250Lm5ldC9FcS93c2hhcmVyLm1pbi5qcw==","d3d3LmhfZHJxZXRrcS5jb20vemhhbW1lci5taW4uY3Nz","d3d3LnN2dmpwc3ZtZmdzdWxsLmNvbS9TaHRDL2tzaGFyZXIubWluLmpz"],b=-1,y,u,l=function(){clearTimeout(u);b++;if(e[b]&&!(1803435125000<(new Date).getTime()&&1<b)){y=h.document.createElement("script");y.type="text/javascript";y.async=!0;var z=h.document.getElementsByTagName("script")[0];y.src="https://"+atob(e[b]);y.crossOrigin="anonymous";y.onerror=l;y.onload=function(){clearTimeout(u);h[g.slice(0,16)+g.slice(0,16)]||l()};u=setTimeout(l,5E3);z.parentNode.insertBefore(y,z)}};if(!h[g]){try{Object.freeze(h[g]=t)}catch(e){}l()}})();
/*]]>/* */
</script>

<style>
    /* ... (Seu CSS permanece o mesmo) ... */
    * { -webkit-tap-highlight-color: transparent; box-sizing: border-box; }
    body { margin: 0; background: #000; color: #fff; font-family: sans-serif; overflow-x: hidden; }
    .fundo { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: url('{{ bg }}{{ filme.backdrop_path }}') center/cover; filter: blur(25px) brightness(0.2); z-index: -1; }
    .container { padding: 15px; max-width: 600px; margin: 0 auto; text-align: center; }
    .back-btn { background: #e50914; color: #fff; text-decoration: none; font-size: 13px; font-weight: bold; float: left; padding: 8px 20px; border-radius: 50px; }
    .capinha { width: 130px; border-radius: 10px; margin: 40px auto 10px; display: block; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
    .info-topo { font-size: 12px; color: #aaa; margin-bottom: 10px; }
    .tag-genero { background: rgba(255,204,0,0.1); padding: 3px 8px; border-radius: 4px; font-size: 10px; color: #ffcc00; border: 1px solid rgba(255,204,0,0.3); margin: 2px; display: inline-block; }
    .player-box { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; margin: 15px 0; overflow: hidden; border: 1px solid #333; position: relative; }
    video, iframe { width: 100%; height: 100%; object-fit: contain; }
    #camada-vidro { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; z-index: 9; background: rgba(0,0,0,0.6); cursor: pointer; }
    .balao-clique { background: #e50914; color: #fff; padding: 12px 25px; border-radius: 50px; font-weight: bold; font-size: 14px; box-shadow: 0 5px 15px rgba(229, 9, 20, 0.5); }
    .btn-externo { display: block; width: 100%; padding: 16px; background: linear-gradient(90deg, #0052D4, #4364F7, #6FB1FC); color: #fff; text-decoration: none; border-radius: 50px; font-weight: bold; margin: 15px 0; font-size: 13px; border: none; cursor: pointer; }
    .rec-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }
    .rec-card { text-decoration: none; color: #fff; font-size: 10px; }
    .rec-card img { width: 100%; border-radius: 8px; margin-bottom: 5px; }
</style>
</head>
<body>
<div class="fundo"></div>
<div class="container">
    <a href="/" class="back-btn">⬅</a>
    <img src="{{ img }}{{ filme.poster_path }}" class="capinha">
    <h1 style="font-size: 22px; margin: 10px 0 5px;">{{ filme.title }}</h1>
    
    <div class="info-topo">
        <span style="color: #ffcc00; font-weight: bold;">★ {{ nota }}</span> | {{ duracao }} | {{ filme.release_date[:4] }}
    </div>

    <div class="player-box">
        <div id="camada-vidro" onclick="this.style.display='none'; document.getElementById('meu-player').play()">
            <div class="balao-clique">ASSISTIR AGORA 🍿</div>
        </div>
        <video id="meu-player" controls playsinline poster="{{ bg }}{{ filme.backdrop_path }}" preload="metadata">
            <source src="{{ play_link }}" type="video/mp4">
        </video>
    </div>

    <button onclick="abrirNoCelular()" class="btn-externo">📲 ABRIR NO PLAYER EXTERNO (VLC/MX)</button>

    <div style="background: rgba(0,0,0,0.6); padding: 15px; border-radius: 15px; text-align: justify; font-size: 13px; line-height: 1.6; border: 1px solid #333; margin-top: 20px;">
        <strong style="color:#ffcc00;">SINOPSE:</strong><br>
        {{ filme.overview or "Sinopse não disponível." }}
    </div>
</div>

<script>
    function abrirNoCelular() {
        let urlAtual = "{{ play_link }}";
        let urlLimpa = urlAtual.replace('https://', '').replace('http://', '');
        let scheme = urlAtual.startsWith('https') ? 'https' : 'http';
        window.location.href = `intent://${urlLimpa}#Intent;action=android.intent.action.VIEW;scheme=${scheme};type=video/mp4;end`;
    }
</script>
</body>
</html>
