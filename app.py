import flask
import requests
import json
from flask import request

def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("ž", "j"),
        ("(", " "),
        (")", " "),
        (".", " "),
        ("/", ""),
        ("-", " "),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def buscar_libro(nombre_libro):
    if ' ' in nombre_libro:
        consulta_texto = nombre_libro.replace(' ', '+')
    else:
        consulta_texto = nombre_libro
    result = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={consulta_texto}")
    book = result.json()
    items = book["items"]
    encoded = json.dumps(items)
    decoded = json.loads(encoded)
    titulo = decoded[0]['volumeInfo']['title']
    try:
        autor = decoded[0]['volumeInfo']['authors'][0]
    except:
        autor = 'Anonimo'
    enlace = decoded[0]['volumeInfo']['infoLink']
    data = [titulo, autor, enlace]
    return data

app = flask.Flask(__name__)

@app.route('/')
@app.route('/home')
def home():
    return "Aqui no encontraras lo que buscas"

@app.route('/dialogflow', methods=['POST'])
def webhook():
    req = request.get_json(silent=True,force=True)
    fulfillmentText = ''
    query_result = req.get('queryResult')
    libros_recomendados = [" "]
    if query_result.get('action') == 'buscar.libro':
        nombre_libro = str(query_result.get('parameters').get('nombre'))
        datos = buscar_libro(nombre_libro)
        resultado = datos[0]
        autor = datos[1]
        enlace = datos[2]
        if ' ' in resultado:
            resultado2 = normalize(resultado)
            resultado2 = resultado2.replace('  ', ' ')
            resultado2 = resultado2.replace(' ', '_')
        else:
            resultado2 = normalize(resultado)
        fulfillmentText = f'''
¿Es esto lo que buscas? : {resultado} del autor {autor}.
Mayor detalle en : {enlace}
- Si. /Sugiero_{resultado2}
- No. /Buscar_nuevamente'''
    elif query_result.get('action') == 'recomendar.libro':
        libro_recomendado = str(query_result.get('parameters').get('nombre_libro'))
        if '_' in libro_recomendado:
            libro_recomendado = libro_recomendado.replace('_', ' ')
        datos = buscar_libro(libro_recomendado)
        titulo = datos[0]
        autor = datos[1]
        fulfillmentText = f'''Recomendaste el libro {titulo} del autor {autor}
- /Buscar_nuevamente'''
    elif query_result.get('action') == 'input.welcome':
        fulfillmentText = '''Hola soy ChatBook estoy aquí para ayudarte sugerir libros al CIFIIS
Para empezar haz clic aquí --> /buscarlibro'''
    elif query_result.get('action') == 'input.unknown':
        fulfillmentText = '''Lo lamento, no pude entender, por favor intenta de nuevo...
Haciendo clic aquí --> /buscarlibro'''
    return {
        'fulfillmentText': fulfillmentText
    }

if __name__ == "__main__":
    app.secret_key = 'ItIsASecret'
    app.debug = True
    app.run()
