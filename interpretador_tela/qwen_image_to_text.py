"""
Script para transcrever conteúdo de imagens (screenshots) para texto
usando o modelo Qwen2.5-VL do Hugging Face com Pipeline.

Instalação:
    pip install transformers pillow torch
"""

from transformers import pipeline
import os


def transcrever_imagem(
    caminho_imagem: str,
    prompt: str = "Transcreva todo o texto visível nesta imagem. Seja detalhado e preciso."
) -> str:
    """
    Transcreve o conteúdo de uma imagem usando o modelo Qwen VL via pipeline.
    
    Args:
        caminho_imagem (str): Caminho para o arquivo de imagem
        prompt (str): Instrução para o modelo sobre o que fazer com a imagem
    
    Returns:
        str: Texto transcrito da imagem
    """
    
    print(f"Verificando imagem: {caminho_imagem}")
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_imagem):
        print(f"✗ Erro: Arquivo '{caminho_imagem}' não encontrado!")
        return ""
    
    print(f"✓ Imagem encontrada: {caminho_imagem}")
    
    print("\nCarregando modelo Qwen/Qwen2.5-VL-7B-Instruct...")
    print("(Isso pode levar alguns minutos na primeira vez...)")
    
    try:
        # Cria o pipeline para image-text-to-text
        pipe = pipeline(
            "image-text-to-text",
            #model="Qwen/Qwen2.5-VL-7B-Instruct"
        )
        
        print("✓ Modelo carregado com sucesso!")
        
        # Prepara as mensagens no formato esperado
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "url": caminho_imagem},
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        print("\nProcessando imagem...")
        
        # Processa a imagem
        resultado = pipe(messages)
        
        # Extrai o texto do resultado
        texto_transcrito = resultado[0]["generated_text"]
        
        print("✓ Transcrição concluída!\n")
        return texto_transcrito
        
    except Exception as e:
        print(f"✗ Erro ao processar imagem: {e}")
        import traceback
        traceback.print_exc()
        return ""


def salvar_transcricao(caminho_imagem: str, texto: str, arquivo_saida: str = None) -> str:
    """
    Salva a transcrição em um arquivo de texto.
    
    Args:
        caminho_imagem (str): Caminho da imagem original
        texto (str): Texto transcrito
        arquivo_saida (str): Nome do arquivo de saída (opcional)
    
    Returns:
        str: Caminho do arquivo salvo
    """
    
    if arquivo_saida is None:
        # Cria nome baseado na imagem original
        nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
        arquivo_saida = f"{nome_base}_transcricao.txt"
    
    try:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"TRANSCRIÇÃO DE: {caminho_imagem}\n")
            f.write(f"{'='*60}\n\n")
            f.write(texto)
            f.write("\n")
        
        caminho_completo = os.path.abspath(arquivo_saida)
        print(f"✓ Transcrição salva em: {caminho_completo}")
        return caminho_completo
        
    except Exception as e:
        print(f"✗ Erro ao salvar arquivo: {e}")
        return ""


# Exemplo de uso
if __name__ == "__main__":
    # Arquivo de imagem para transcrever
    caminho_imagem = "scheeshop.png"
    
    # Se scheeshop.png não existir, tenta usar uma das imagens de exemplo
    if not os.path.exists(caminho_imagem):
        print(f"⚠️  Aviso: '{caminho_imagem}' não encontrado.")
        print("Tentando usar imagem de exemplo...\n")
        caminho_imagem = "exemplo1.png"
        
        if not os.path.exists(caminho_imagem):
            print(f"✗ Erro: Nenhuma imagem encontrada!")
            print("Coloque o arquivo scheeshop.png no diretório atual ou use exemplo1.png")
            exit(1)
    
    # Prompt personalizado para transcrição de screenshot
    prompt_transcricao = "Analise esta imagem de screenshot e transcreva TODO o texto visível. Seja detalhado, preciso e organize o conteúdo de forma clara."

    # Transcreve a imagem
    print("="*60)
    print("INICIANDO TRANSCRIÇÃO")
    print("="*60)
    
    resultado = transcrever_imagem(caminho_imagem, prompt_transcricao)
    
    if resultado:
        # Exibe o resultado
        print("\n" + "="*60)
        print("TRANSCRIÇÃO")
        print("="*60)
        print(resultado)
        print("="*60)
        
        # Salva em arquivo
        salvar_transcricao(caminho_imagem, resultado)
    else:
        print("✗ Falha ao transcrever a imagem.")