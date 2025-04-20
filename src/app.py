import re
import time
import os
from pathlib import Path
import pandas as pd
from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from openai import OpenAI

import os, sys

BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
TEMPLATES_DIR = os.path.join(BASE_PATH, "templates")

app = Flask(__name__, template_folder=TEMPLATES_DIR)

#app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'docs'

# make sure the directory to save files exists
os.makedirs('docs', exist_ok=True)

# functions creation

def preprocess_text(text):
#remove line breaks and redundant spaces
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fragment_text(text, max_length=3500):
# split the text into chunks of up to 3500 characters. if a period is found within the limit, use that as the split point.
    fragments = []
    start = 0
    while start < len(text):
        if start + max_length >= len(text):
            fragments.append(text[start:].strip())
            break
        substring = text[start:start+max_length]
        last_period = substring.rfind('.')
        if last_period == -1:
            fragments.append(substring.strip())
            start += max_length
        else:
            fragment = text[start:start+last_period+1]
            fragments.append(fragment.strip())
            start += last_period + 1
    return fragments

def translate_fragments(fragments, source_lang='en', target_lang='es'):
# translate each fragment sequentially using deep_translator
    translated_fragments = []
    for fragment in fragments:
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(fragment)
        translated_fragments.append(translated)
        time.sleep(2) # control the rate limit of api
    return translated_fragments

def summarize_text(processed_text, api_key):
# query the deepseek api using the 'deepseek-chat' model and return the summarized text
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente experto en análisis académico de literatura. Tu tarea es leer un texto académico, comprenderlo profundamente y extraer las ideas principales "
                "de todos los autores citados, respetando estrictamente el siguiente formato:\n\n"
                "'Autores~Fecha~Idea'.\n\n"
                "Resume cada idea de forma clara, incluyendo todos los detalles relevantes y capturando la mayor cantidad de información, pero sin extenderte innecesariamente.\n\n"
                "Si un autor es citado más de una vez con ideas diferentes, incluye un item de la lista por cada idea.\n\n"
                "No incluyas ideas del narrador principal del texto dentro de las ideas de cada autor.\n\n"
                "Debido a lo anterior, generaràs un resumen detallado del texto, consolidando todas las ideas expresadas del narrador y los autores. No incluyas generalidades; incorpora afirmaciones específicas y representativas del contenido completo, dada la alta densidad de información, "
                "que será atribuido al narrador principal del texto, con el formato 'narrador~1900~resumen detallado'.\n\n"
                "Presenta la información en forma de lista ordenada sin numeración solo con el indicador de inicio '-'.\n\n"
                "Por favor, realiza el proceso indicado sin entregar ningun otro tipo de información adicional:\n\n"
            )
        },
        {
            "role": "user",
            "content": processed_text
        }
    ]
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.75,
        seed=1367
    )
    return response.choices[0].message.content

def save_to_txt(text, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

def parse_text_to_df(text):
    data = []
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith('-'):
            line = line[1:].strip()
        parts = line.split("~", maxsplit=2)
        if len(parts) == 3:
            authors_raw, year, description = parts
            # Elimina posibles paréntesis en el campo de autores
            authors = re.sub(r'\([^)]*\)', '', authors_raw).strip()
            data.append({
                'autores': authors,
                'year': year.strip(),
                'description': description.strip()
            })
    df = pd.DataFrame(data)
    return df

# application routes

@app.route('/', methods=['GET', 'POST'])
def index():
    consulted_text = ""
    if request.method == 'POST':
# data capture from the form
        author_year = request.form.get('author_year', '')
        section_text = request.form.get('section_text', '')
        source_text = request.form.get('source_text', '')
        api_key = request.form.get('api_key', '')
        raw_text = request.form.get('raw_text', '')
        
# project name definition
        project_name = f"{author_year}_{section_text}"
        
# raw text processing
        cleaned_text = preprocess_text(raw_text)
        fragments = fragment_text(cleaned_text, max_length=3500)
        translated_fragments = translate_fragments(fragments, source_lang='en', target_lang='es')
        processed_text = " ".join(translated_fragments).replace("\n", " ").strip()
        consulted_text = summarize_text(processed_text, api_key=api_key)
        
# automatic creation and saving of .txt and .csv files
        txt_filename = Path("docs") / f"{project_name}.txt"
        save_to_txt(consulted_text, filename=txt_filename)
        
        df = parse_text_to_df(consulted_text)
        df['section'] = project_name
        df['source'] = source_text
        csv_filename = Path("docs") / f"{project_name}.csv"
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    return render_template('index.html', consulted_text=consulted_text)

if __name__ == '__main__':
    app.run(debug=True)
