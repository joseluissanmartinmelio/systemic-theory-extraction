import re
import time
from deep_translator import GoogleTranslator
from openai import OpenAI
import os
import pandas as pd
from pathlib import Path

# relative directory
parent_path = Path(__file__).resolve().parent.parent

# client configuration with API key and Deepseek base URL
api_key = ""

client = OpenAI(
    api_key=os.getenv(api_key), 
    base_url="https://api.deepseek.com/v1"
)

# metadata of project
author_year = ""
section_text = ""
project_name = author_year + "_" + section_text
source_text = ""

# variable containing a raw free text
raw_text = ""

# preprocessing function: eliminates line breaks and redundant spaces
def preprocess_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# function for fragmenting text into segments of up to 3500 characters
def fragment_text(text, max_length=3500):
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

# function to translate each fragment sequentially using deep_translator
def translate_fragments(fragments, source_lang='en', target_lang='es'):
    translated_fragments = []
    for fragment in fragments:
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(fragment)
        translated_fragments.append(translated)
        time.sleep(2) # control de api rate limit
    return translated_fragments

# function to query the deepseek api using the “deepseek-chat” model.
def summarize_text(text):
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un asistente experto en análisis académico. Tu tarea es leer un texto académico, comprenderlo profundamente y extraer las ideas principales "
                "de todos los autores citados, respetando estrictamente el siguiente formato:\n\n"
                "'Autores~Fecha~Idea'.\n\n"
                "Resume cada idea de forma clara, incluyendo todos los detalles relevantes, pero sin extenderte innecesariamente.\n\n"
                "Si un autor es citado más de una vez con ideas diferentes, incluye un item de la lista por cada idea.\n\n"
                "No incluyas ideas del narrador principal del texto dentro de las ideas de cada autor.\n\n"
                "Debido a lo anterior, generaras un resumen general del texto, más extenso para incluir afirmaciones detalladas debido al volumen de ideas, dado que debes consolidar los enunciados de todo el texto con indicaciones específicas no generalidades, "
                "que será atribuido al narrador principal del texto, con el formato 'narrador~1900~resumen detallado'.\n\n"
                "Presenta la información en forma de lista ordenada sin numeración solo con el indicador de inicio '-'.\n\n"
                "Por favor, realiza el proceso indicado sin entregar ningun otro tipo de información adicional:\n\n"
            )
        },
        {
            "role": "user",
            "content": text
        }
    ]
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.75,
        seed=1367
    )
    return response.choices[0].message.content

# consulted_text to .txt
def save_to_txt(text, filename="consulted_text.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write(text)

# consulted_text to df
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
            authors = re.sub(r'\([^)]*\)', '', authors_raw).strip()
            data.append({
                'autores': authors,
                'year': year.strip(),
                'description': description.strip()
            })
    
    # create the df
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    cleaned_text = preprocess_text(raw_text)
    fragments = fragment_text(cleaned_text, max_length=3500)
    translated_fragments = translate_fragments(fragments, source_lang='en', target_lang='es')
    processed_text = " ".join(translated_fragments).replace("\n", " ").strip()
    consulted_text = summarize_text(processed_text)

    save_to_txt(consulted_text, filename= parent_path / f"docs/{project_name}.txt")

    df = parse_text_to_df(consulted_text)
    df['section'] = project_name
    df['source'] = source_text

    df.to_csv(parent_path / f"docs/{project_name}.csv", index=False, encoding='utf-8-sig')