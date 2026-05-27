import os
import json
import pandas as pd
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from openai import OpenAI

# Inicializa as configurações da API da OpenAI
load_dotenv()
cliente_ia = OpenAI()

caminho_excel = r"C:\Users\24.00824-9\Downloads\Security Updates 2026-05-27-111710am.xlsx"

# ==============================================================================
# 1. MAPEAMENTO DAS FONTES (Planilha1)
# ==============================================================================
df_fontes = pd.read_excel(
    caminho_excel, 
    sheet_name='Planilha1', 
    header=None, 
    names=['CVE', 'Caminho_PDF']
)
df_fontes = df_fontes.drop_duplicates(subset=['CVE']).dropna()

# Cria o dicionário de busca rápida para os caminhos locais dos PDFs
mapa_cve_pdf = dict(zip(df_fontes['CVE'].astype(str), df_fontes['Caminho_PDF']))


# ==============================================================================
# 2. PREPARAÇÃO DO DESTINO (Security Updates)
# ==============================================================================
df_destino = pd.read_excel(caminho_excel, sheet_name='Security Updates')

# Garante que o DataFrame tenha pelo menos 11 colunas para injetar na J e K
while len(df_destino.columns) < 11:
    df_destino[f'Temporaria_{len(df_destino.columns)}'] = ""

# Força os nomes exatos nas posições J (índice 9) e K (índice 10)
colunas = list(df_destino.columns)
colunas[9] = 'Título da Vulnerabilidade' # Coluna J
colunas[10] = 'Exploração'                # Coluna K
df_destino.columns = colunas

cache_ia = {}


# ==============================================================================
# 3. PROMPT DA IA (Com trava de segurança para Perguntas Frequentes)
# ==============================================================================
prompt_sistema = """
Você é um extrator de dados de relatórios de segurança. Sua tarefa é copiar dados textualmente, SEM ALTERAR NADA, SEM RESUMIR e SEM EXPLICAR.

1. "titulo": Extraia o título principal da vulnerabilidade.
2. "exploracao": Localize a tabela ou seção de "Exploração". Você deve montar uma ÚNICA LINHA de texto corrido (sem nenhuma quebra de linha ou caractere \\n), contendo exatamente os três campos abaixo com seus respectivos valores separados por vírgula, seguindo estritamente este padrão:

Publicly disclosed: [Valor], Exploited: [Valor], Exploitability assessment: [Valor]

Regra estrita para o 'Exploitability assessment': 
- Copie o texto, frase ou parágrafo curto que descreve o risco de explorabilidade desse campo na tabela (exemplos comuns: "Não aplicável", "Probabilidade maior de exploração", "Probabilidade menor de exploração", "Exploitation More Likely").
- Se o campo estiver explicitamente em branco, omitido na tabela, ou se o texto saltar direto para títulos de outras seções (como 'Perguntas frequentes'), preencha o valor deste campo como "Não aplicável".

Você DEVE responder estritamente no formato JSON válido:
{
  "titulo": "Texto do título",
  "exploracao": "Publicly disclosed: No, Exploited: No, Exploitability assessment: Não aplicável"
}
Não use blocks de marcação markdown (como ```json). Se não encontrar os dados de exploração, retorne null.
"""


# ==============================================================================
# 4. LOOP DE PROCESSAMENTO (Lendo com PdfReader e salvando nas colunas J e K)
# ==============================================================================
for indice, linha in df_destino.iterrows():
    cve_atual = linha['Número de CVE']
    
    if pd.isna(cve_atual) or str(cve_atual).strip() == "":
        continue
        
    cve_atual = str(cve_atual).strip()
    
    if cve_atual in mapa_cve_pdf:
        caminho_pdf = mapa_cve_pdf[cve_atual]
        print(f"🔄 Processando linha {indice + 1} - CVE: {cve_atual}")
        
        if cve_atual in cache_ia:
            df_destino.iloc[indice, 9] = cache_ia[cve_atual]['titulo']
            df_destino.iloc[indice, 10] = cache_ia[cve_atual]['exploracao']
            continue
            
        try:
            leitor_pdf = PdfReader(caminho_pdf)
            texto_bruto = ""
            
            for pagina in leitor_pdf.pages:
                texto_extraido = pagina.extract_text()
                if texto_extraido:
                    texto_bruto += texto_extraido + "\n"
            
            if texto_bruto.strip() == "":
                print(f"   ❌ Texto do PDF retornou vazio: {caminho_pdf}")
                continue
                
            print("   🤖 ChatGPT extraindo dados com validação de quebra de seção...")
            resposta = cliente_ia.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Extraia o título e copie a tabela deste texto:\n\n{texto_bruto}"}
                ],
                temperature=0.0
            )
            
            dados_ia = json.loads(resposta.choices[0].message.content)
            
            # Alimenta as colunas J (9) e K (10)
            df_destino.iloc[indice, 9] = dados_ia.get('titulo')
            df_destino.iloc[indice, 10] = dados_ia.get('exploracao')
            
            cache_ia[cve_atual] = {
                'titulo': dados_ia.get('titulo'),
                'exploracao': dados_ia.get('exploracao')
            }
            print("   ✅ Dados copiados para a memória!")
            
        except Exception as e:
            print(f"   ❌ Falha ao processar o arquivo {caminho_pdf}: {e}")


# ==============================================================================
# 5. GRAVAÇÃO DOS DADOS DE VOLTA NA ABA "Security Updates"
# ==============================================================================
print("\n💾 Gravando modificações no Excel...")

with pd.ExcelWriter(caminho_excel, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_destino.to_excel(writer, sheet_name='Security Updates', index=False)

print("🚀 Concluído! A aba 'Security Updates' foi atualizada protegendo os dados contra invasão de outras seções.")