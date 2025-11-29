"""
Analisador de Screenshots do Instagram usando Ollama com Qwen3-VL
Extrai informações de posts do Instagram e exporta para JSON.

Instalação:
    pip install ollama pillow
    ollama pull qwen3-vl:2b
"""

import ollama
from PIL import Image
import json
import os
import base64
from io import BytesIO
from datetime import datetime
def analisar_instagram(caminho_imagem: str, modelo: str = "qwen3-vl:2b") -> dict:
    """
    Analisa um screenshot do Instagram e extrai informações estruturadas.
    
    Args:
        caminho_imagem (str): Caminho para o arquivo de imagem
        modelo (str): Nome do modelo Ollama a usar
    
    Returns:
        dict: Dicionário com as informações extraídas
    """

    modelo = "gemma3:4b"
    
    print(f"Verificando imagem: {caminho_imagem}")
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"✗ Erro: Arquivo '{caminho_imagem}' não encontrado!")
        return {}
    
    print(f"✓ Imagem encontrada: {caminho_imagem}")
    
    try:
        # Carrega a imagem e converte para base64
        with open(caminho_imagem, 'rb') as f:
            image_data = f.read()
        
        # Verifica dimensões da imagem
        img = Image.open(caminho_imagem)
        print(f"✓ Imagem carregada: {img.size[0]}x{img.size[1]} pixels")
    except Exception as e:
        print(f"✗ Erro ao abrir imagem: {e}")
        return {}
    
    print(f"\nUsando modelo Ollama: {modelo}")
    
    try:
        # Prompt estruturado para extrair informações do Instagram
        prompt = """Analise este screenshot de uma rede social e extraia as seguintes informações :

{
  "rede_social": "nome da rede social (Instagram, Facebook, etc)",
  "usuario": "nome do usuário ou conta",
  "curtidas": "número de curtidas (extraia apenas o número)",
  "legenda": "texto da legenda do post",
  "descricao_imagem": "descrição detalhada do conteúdo visual da imagem do post",
  "comentarios": "número de comentários se visível",
  "data_post": "data do post se visível",
  "hashtags": "lista de hashtags usadas no post",
  "localizacao": "localização do post se visível",
  "outros_detalhes": "quaisquer outros detalhes relevantes extraídos do screenshot, faca uma descrição detalhada do conteúdo visual e textual do post. Transcreve se houver textos visíveis na imagem. Descreve as pessoas, objetos, cores predominantes, expressões faciais, ambiente e qualquer outro elemento visual importante."
}

Responda APENAS com o JSON, sem texto adicional."""
        
        print("\nProcessando imagem...")
        
        # Gera a análise usando Ollama
        response = ollama.chat(
            model=modelo,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [caminho_imagem]
            }]
        )
        
        # Extrai o texto da resposta
        resposta_texto = response['message']['content']
        
        print("✓ Análise concluída!\n")
        
        # Tenta parsear o JSON da resposta
        try:
            # Remove possíveis marcadores de código
            resposta_limpa = resposta_texto.strip()
            if resposta_limpa.startswith("```json"):
                resposta_limpa = resposta_limpa[7:]
            if resposta_limpa.startswith("```"):
                resposta_limpa = resposta_limpa[3:]
            if resposta_limpa.endswith("```"):
                resposta_limpa = resposta_limpa[:-3]
            
            resposta_limpa = resposta_limpa.strip()
            
            # Parse do JSON
            dados = json.loads(resposta_limpa)
            
            # Adiciona metadados
            dados["arquivo_original"] = caminho_imagem
            dados["timestamp_analise"] = datetime.now().isoformat()
            
            return dados
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Aviso: Resposta não está em formato JSON válido")
            print(f"Resposta bruta: {resposta_texto}")
            
            # Retorna estrutura básica com a resposta como texto
            return {
                "arquivo_original": caminho_imagem,
                "timestamp_analise": datetime.now().isoformat(),
                "resposta_bruta": resposta_texto,
                "erro": "Falha ao parsear JSON"
            }
        
    except Exception as e:
        print(f"✗ Erro ao processar imagem: {e}")
        import traceback
        traceback.print_exc()
        return {}


def salvar_json(dados: dict, arquivo_saida: str = None) -> str:
    """
    Salva os dados extraídos em arquivo JSON.
    
    Args:
        dados (dict): Dados a serem salvos
        arquivo_saida (str): Nome do arquivo de saída (opcional)
    
    Returns:
        str: Caminho do arquivo salvo
    """
    
    if arquivo_saida is None:
        # Cria nome baseado na imagem original
        arquivo_original = dados.get("arquivo_original", "resultado")
        nome_base = os.path.splitext(os.path.basename(arquivo_original))[0]
        arquivo_saida = f"{nome_base}_instagram.json"
    
    try:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        caminho_completo = os.path.abspath(arquivo_saida)
        print(f"✓ Dados salvos em: {caminho_completo}")
        return caminho_completo
        
    except Exception as e:
        print(f"✗ Erro ao salvar arquivo: {e}")
        return ""


def analisar_multiplas_imagens(caminhos_imagens: list, arquivo_saida: str = "instagram_posts.json") -> list:
    """
    Analisa múltiplos screenshots do Instagram.
    
    Args:
        caminhos_imagens (list): Lista de caminhos para as imagens
        arquivo_saida (str): Nome do arquivo JSON para salvar todos os resultados
    
    Returns:
        list: Lista com os dados extraídos de cada imagem
    """
    
    resultados = []
    
    for i, caminho in enumerate(caminhos_imagens, 1):
        print(f"\n{'='*60}")
        print(f"Processando imagem {i}/{len(caminhos_imagens)}")
        print(f"{'='*60}\n")
        
        dados = analisar_instagram(caminho)
        if dados:
            resultados.append(dados)
            
            print(f"\n--- RESULTADO {i} ---")
            print(json.dumps(dados, ensure_ascii=False, indent=2))
            print(f"-------------------\n")
    
    # Salva todos os resultados em um único arquivo
    if resultados:
        try:
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Todos os resultados salvos em: {os.path.abspath(arquivo_saida)}")
        except Exception as e:
            print(f"✗ Erro ao salvar resultados: {e}")
    
    return resultados


# Exemplo de uso
if __name__ == "__main__":
    # Arquivo de imagem para analisar
    caminho_imagem = "exemplo5.png"
    
    # Se não existir, tenta usar uma das imagens de exemplo
    if not os.path.exists(caminho_imagem):
        print(f"⚠️  Aviso: '{caminho_imagem}' não encontrado.")
        print("Tentando usar imagem de exemplo...\n")
        
        # Tenta as imagens de exemplo
        possiveis_imagens = ["exemplo1.png", "exemplo2.png", "exemplo3.png", "exemplo4.png"]
        for img in possiveis_imagens:
            if os.path.exists(img):
                caminho_imagem = img
                break
        
        if not os.path.exists(caminho_imagem):
            print(f"✗ Erro: Nenhuma imagem encontrada!")
            print("Coloque o arquivo instagram_screenshot.png no diretório atual")
            exit(1)
    
    # Analisa a imagem
    print("="*60)
    print("ANALISADOR DE POSTS DO INSTAGRAM")
    print("="*60)
    
    resultado = analisar_instagram(caminho_imagem)
    
    if resultado:
        # Exibe o resultado
        print("\n" + "="*60)
        print("DADOS EXTRAÍDOS")
        print("="*60)
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        print("="*60)
        
        # Salva em arquivo JSON
        salvar_json(resultado)
        
        print("\n📊 Resumo:")
        print(f"  Rede Social: {resultado.get('rede_social', 'N/A')}")
        print(f"  Usuário: {resultado.get('usuario', 'N/A')}")
        print(f"  Curtidas: {resultado.get('curtidas', 'N/A')}")
        print(f"  Legenda: {resultado.get('legenda', 'N/A')[:100]}...")
    else:
        print("✗ Falha ao analisar a imagem.")
    
    # Exemplo: Analisar múltiplas imagens
    # imagens = ["exemplo1.png", "exemplo2.png", "exemplo3.png"]
    # analisar_multiplas_imagens(imagens)
