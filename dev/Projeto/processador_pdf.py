# arquivo: processador_pdf.py
from PyPDF2 import PdfReader

def extrair_texto_pdf(caminho_pdf):
    """Lê todas as páginas de um PDF e retorna o texto bruto em formato string."""
    leitor_pdf = PdfReader(caminho_pdf)
    texto_bruto = ""
    
    for pagina in leitor_pdf.pages:
        texto_extraido = pagina.extract_text()
        if texto_extraido:
            texto_bruto += texto_extraido + "\n"
            
    return texto_bruto