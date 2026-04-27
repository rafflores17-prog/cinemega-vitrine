from flask import Flask, render_template, request, send_from_directory
import requests
from urllib.parse import quote

app = Flask(__name__)

NOME_SITE = "Cine Mega"
TMDB_API_KEY = "c90fb79a2f7d756a49bee848bce5f413"
IMG = "https://image.tmdb.org/t/p/w500"
BG = "https://image.tmdb.org/t/p/original"
MOTOR_URL = "https://brave-jonis-meu-bot-cinema-7ce7d584.koyeb.app"

# 🛡️ O VIGIA: ESCONDE ANÚNCIOS NO APP E MOSTRA NO NAVEGADOR
@app.context_processor
def controle_de_anuncios():
    """ Detecta se o acesso vem do aplicativo (WebView) ou do Chrome/PC """
    user_agent = request.headers.get('User-Agent', '').lower()
    # A sigla 'wv' significa WebView (o sistema usado pelo aplicativo Android/TV)
    is_app = 'wv' in user_agent
    
    # Retorna 'mostrar_ads = True' para o site normal, e 'False' para o App
    return dict(mostrar_ads=not is_app)

@app.route("/")
def home():
    q = request.args.get("q")
    if q:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=pt-BR&query={q}"
        try:
            res = requests.get(url, timeout=10).json().get("results", [])
        except: res = []
        return render_template("index.html", filmes=res, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca="🔍 Resultados da Busca")
    
    try:
        destaques = requests.get(f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=pt-BR").json().get("results", [])[:5]
        populares = requests.get(f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=pt-BR").json().get("results", [])
        comedia = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=35").json().get("results", [])
        ficcao = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=878").json().get("results", [])
        terror = requests.get(f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres=27").json().get("results", [])
    except:
        destaques, populares, comedia, ficcao, terror = [], [], [], [], []
        
    return render_template("index.html", 
                           destaques=destaques, populares=populares, 
                           comedia=comedia, ficcao=ficcao, terror=terror,
                           img=IMG, bg=BG, nome_site=NOME_SITE, busca=False)

# 🔥 NOVA ROTA: FILTROS POR GÊNERO NAS ABAS
@app.route("/genero/<int:gen_id>")
def genero(gen_id):
    nomes_generos = {
        28: "Ação", 12: "Aventura", 16: "Animação", 35: "Comédia", 
        80: "Crime", 99: "Documentário", 18: "Drama", 10751: "Família", 
        14: "Fantasia", 36: "História", 27: "Terror", 10402: "Música", 
        9648: "Mistério", 10749: "Romance", 878: "Ficção Científica", 
        10770: "Cinema TV", 53: "Thriller", 10752: "Guerra", 37: "Faroeste"
    }
    nome_gen = nomes_generos.get(gen_id, "Filmes")
    
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=pt-BR&with_genres={gen_id}"
    try:
        res = requests.get(url, timeout=10).json().get("results", [])
    except: res = []
    
    # Ele usa a mesma tela de busca, mas com o título alterado para o nome do gênero
    return render_template("index.html", filmes=res, img=IMG, bg=BG, nome_site=NOME_SITE, busca=True, titulo_busca=f"📌 Gênero: {nome_gen}")

@app.route("/filme/<int:id>")
def detalhes(id):
    try:
        url_detalhes = f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}&language=pt-BR&append_to_response=videos,recommendations"
        data = requests.get(url_detalhes, timeout=10).json()
        titulo = data.get('title', '')
        play_link = f"{MOTOR_URL}/buscar?titulo={quote(titulo)}"
        generos = [g['name'] for g in data.get('genres', [])]
        duracao = f"{data.get('runtime', 0)} min"
        nota = round(data.get('vote_average', 0), 1)
        videos = data.get('videos', {}).get('results', [])
        trailer = next((v['key'] for v in videos if v['site'] == 'YouTube'), None)
        recomendados = data.get('recommendations', {}).get('results', [])[:6]
        return render_template("detalhes.html", filme=data, img=IMG, bg=BG, play_link=play_link, trailer_key=trailer, recomendados=recomendados, generos=generos, duracao=duracao, nota=nota, nome_site=NOME_SITE)
    except: 
        return "Erro", 404

# ✅ ROTA DO ADS.TXT
@app.route('/ads.txt')
def ads_txt():
    return "google.com, pub-2866002449649160, DIRECT, f08c47fec0942fa0", 200, {'Content-Type': 'text/plain'}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
