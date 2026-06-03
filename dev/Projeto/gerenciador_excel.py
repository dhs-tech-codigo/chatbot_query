# arquivo: gerenciador_excel.py
import pandas as pd

def mapear_fontes(caminho_excel):
    """Lê a Planilha1 e retorna um dicionário conectando CVE ao caminho do PDF."""
    df_fontes = pd.read_excel(
        caminho_excel, 
        sheet_name='Planilha1', 
        header=None, 
        names=['CVE', 'Caminho_PDF']
    )
    df_fontes = df_fontes.drop_duplicates(subset=['CVE']).dropna()
    return dict(zip(df_fontes['CVE'].astype(str), df_fontes['Caminho_PDF']))

def preparar_destino(caminho_excel):
    """Lê a aba Security Updates e garante as colunas J e K."""
    df_destino = pd.read_excel(caminho_excel, sheet_name='Security Updates')

    while len(df_destino.columns) < 11:
        df_destino[f'Temporaria_{len(df_destino.columns)}'] = ""

    colunas = list(df_destino.columns)
    colunas[9] = 'Título da Vulnerabilidade'
    colunas[10] = 'Exploração'
    df_destino.columns = colunas
    
    return df_destino

def salvar_modificacoes(df_destino, caminho_excel):
    """Salva o DataFrame de volta na aba Security Updates."""
    with pd.ExcelWriter(caminho_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_destino.to_excel(writer, sheet_name='Security Updates', index=False)