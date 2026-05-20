import pandas as pd
from PyPDF2 import PdfReader
import os
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI
import pdfplumber

#exemplo de como por caminho
#caminho_arquivo = r'C:\Users\24.00824-9\chatbot_query\dev\exemplos\nota-fiscal-notebook-dell.pdf'
#colocar antes de tudo no terminal pip install -r requirements.txt
# 1. Lê a planilha avisando que não tem título (header=None) 
# e já cria os nomes das colunas (names=['CVE', 'Caminho_PDF'])
df = pd.read_excel(
    r"C:\Users\24.00824-9\Downloads\Security Updates 2026-05-20-113839am.xlsx", 
    sheet_name='Planilha1',
    header=None, 
    names=['CVE', 'Caminho_PDF']
)

# 2. Remove as linhas onde o 'CVE' se repete (mantém apenas a primeira ocorrência)
df_unicos = df.drop_duplicates(subset=['CVE'])
df_unicos = df_unicos.dropna()

# 3. Pega apenas a coluna dos PDFs e transforma na lista que o seu loop vai usar
lista_pdfs_para_ia = df_unicos['Caminho_PDF'].tolist()

# Exibe o resultado para você conferir se deu certo
print(f"📊 Total de PDFs únicos encontrados: {len(lista_pdfs_para_ia)}")
print(lista_pdfs_para_ia)

for item in lista_pdfs_para_ia:
    leitor_pdf = PdfReader(item)

    texto_bruto =''

    for pagina in leitor_pdf.pages:
        texto_extraido = pagina.extract_text()
        if texto_extraido:
            texto_bruto += texto_extraido + "\n"

    print(texto_bruto)

