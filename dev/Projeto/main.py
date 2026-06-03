# arquivo: main.py
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Importações dos nossos módulos locais
from configuracao import CAMINHO_EXCEL, PROMPT_SISTEMA
from gerenciador_excel import mapear_fontes, preparar_destino, salvar_modificacoes
from processador_pdf import extrair_texto_pdf
from agente_ia import analisar_documento

def executar_pipeline():
    # Inicializa as configurações da API
    load_dotenv()
    cliente_ia = OpenAI()

    print("📊 Preparando planilhas...")
    mapa_cve_pdf = mapear_fontes(CAMINHO_EXCEL)
    df_destino = preparar_destino(CAMINHO_EXCEL)
    cache_ia = {}

    print(f"Iniciando loop de processamento...")
    
    for indice, linha in df_destino.iterrows():
        cve_atual = linha['Número de CVE']
        
        if pd.isna(cve_atual) or str(cve_atual).strip() == "":
            continue
            
        cve_atual = str(cve_atual).strip()
        
        if cve_atual in mapa_cve_pdf:
            caminho_pdf = mapa_cve_pdf[cve_atual]
            print(f"\n🔄 Processando linha {indice + 1} - CVE: {cve_atual}")
            
            # Checa o cache primeiro
            if cve_atual in cache_ia:
                df_destino.iloc[indice, 9] = cache_ia[cve_atual]['titulo']
                df_destino.iloc[indice, 10] = cache_ia[cve_atual]['exploracao']
                continue
                
            try:
                # 1. Lê o PDF
                texto_bruto = extrair_texto_pdf(caminho_pdf)
                
                if texto_bruto.strip() == "":
                    print(f"   ❌ Texto do PDF retornou vazio: {caminho_pdf}")
                    continue
                    
                # 2. Chama a IA
                print("   🤖 ChatGPT analisando documento...")
                dados_ia = analisar_documento(cliente_ia, PROMPT_SISTEMA, texto_bruto)
                
                # 3. Atualiza o DataFrame
                df_destino.iloc[indice, 9] = dados_ia.get('titulo')
                df_destino.iloc[indice, 10] = dados_ia.get('exploracao')
                
                # 4. Alimenta o cache
                cache_ia[cve_atual] = {
                    'titulo': dados_ia.get('titulo'),
                    'exploracao': dados_ia.get('exploracao')
                }
                print("   ✅ Salvo na memória!")
                
            except Exception as e:
                print(f"   ❌ Falha ao processar o arquivo {caminho_pdf}: {e}")

    # Finalização
    print("\n💾 Gravando modificações no Excel...")
    salvar_modificacoes(df_destino, CAMINHO_EXCEL)
    print("🚀 Concluído! A aba 'Security Updates' foi atualizada com sucesso.")

if __name__ == "__main__":
    executar_pipeline()
    