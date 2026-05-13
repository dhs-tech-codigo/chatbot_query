import pandas as pd

#exemplo de como por caminho
#caminho_arquivo = r'C:\Users\24.00824-9\chatbot_query\dev\exemplos\nota-fiscal-notebook-dell.pdf'
#colocar antes de tudo no terminal pip install -r requirements.txt
# 1. Lê a planilha avisando que não tem título (header=None) 
# e já cria os nomes das colunas (names=['CVE', 'Caminho_PDF'])
df = pd.read_excel(
    r"C:\Users\24.00824-9\Downloads\Security Updates 2026-05-13-113944am.xlsx", 
    sheet_name='Planilha1',
    header=None, 
    names=['CVE', 'Caminho_PDF']
)

# 2. Remove as linhas onde o 'CVE' se repete (mantém apenas a primeira ocorrência)
df_unicos = df.drop_duplicates(subset=['CVE'])

# 3. Pega apenas a coluna dos PDFs e transforma na lista que o seu loop vai usar
lista_pdfs_para_ia = df_unicos['Caminho_PDF'].tolist()

# Exibe o resultado para você conferir se deu certo
print(f"📊 Total de PDFs únicos encontrados: {len(lista_pdfs_para_ia)}")
print(lista_pdfs_para_ia)