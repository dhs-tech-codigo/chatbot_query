import os
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
cliente_ia = OpenAI()

# ====================================================================
# TODO 1: LEITURA DO "PDF" (Lendo o texto sujo)
# ====================================================================
# Leia o arquivo 'fatura_suja_01.txt' e guarde todo o conteúdo 
# em uma variável chamada 'texto_bruto'.

caminho_arquivo = r'C:\Users\24.00824-9\chatbot_query\dev\exemplos\nota-fiscal-notebook-dell.pdf'

leitor_pdf = PdfReader(caminho_arquivo)

texto_bruto =''

for pagina in leitor_pdf.pages:
    texto_extraido = pagina.extract_text()
    if texto_extraido:
        texto_bruto += texto_extraido + "\n"

print(texto_bruto)
# texto_bruto = ...

# ====================================================================
# TODO 2: EXTRAÇÃO INTELIGENTE COM IA (Structured Output)
# ====================================================================
# Use a API da OpenAI para analisar o 'texto_bruto'.
# CRIE UM SYSTEM PROMPT EXTREMAMENTE RÍGIDO pedindo que a IA 
# devolva a resposta NO FORMATO JSON com as chaves:
# "nome_empresa", "data_vencimento", "valor" (só os números).

# prompt_sistema = """ ... """
# resposta = ...

prompt_sistema = """
Você é um assistente especializado em extrair dados de notas fiscais.
Retorne um objeto JSON contendo ESTRITAMENTE as seguintes chaves:
- "nome_empresa" (string)
- "data_vencimento" (string no formato DD/MM/AAAA)
- "valor" (número float, apenas o valor monetário usando ponto para decimais)

Se alguma informação não for encontrada, retorne null.
"""

# Chamando a API da OpenAI
resposta = cliente_ia.chat.completions.create(
    model="gpt-3.5-turbo",
    response_format={ "type": "json_object" }, # Garante que a IA devolva um JSON válido
    messages=[
        {"role": "system", "content": prompt_sistema},
        {"role": "user", "content": f"Extraia os dados deste texto:\n\n{texto_bruto}"}
    ],
    temperature=0.1 # Temperatura baixa para garantir precisão e evitar alucinações
)

# Pegando o conteúdo da resposta (que é uma string em formato JSON)
texto_resposta_ia = resposta.choices[0].message.content
# ====================================================================
# TODO 3: CONSOLIDANDO NO PANDAS
# ====================================================================
# 1. Pegue a resposta em JSON gerada pela IA (que é uma string).
# 2. Converta ela em um dicionário Python (use a biblioteca 'json').
# 3. Transforme esse dicionário em uma linha de um DataFrame do Pandas.

import json

json_extraido = json.loads(texto_resposta_ia)
df_resultado = pd.DataFrame([json_extraido])

print("\n📊 Dado Extraído e Estruturado:")
print(df_resultado)
'''
json_extraido = json.loads(...)
df_resultado = pd.DataFrame([json_extraido])
print("\n📊 Dado Extraído e Estruturado:")
print(df_resultado)'''