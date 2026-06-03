# arquivo: agente_ia.py
import json

def analisar_documento(cliente_ia, prompt, texto_bruto):
    """Envia o texto para a IA e retorna um dicionário Python (JSON decodificado)."""
    resposta = cliente_ia.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Extraia o título e os dados de exploração deste texto:\n\n{texto_bruto}"}
        ],
        temperature=0.0
    )
    
    resultado_texto = resposta.choices[0].message.content
    print(f"   📥 Resposta da IA: {resultado_texto}")
    
    return json.loads(resultado_texto)