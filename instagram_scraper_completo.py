"""
Sistema Completo de Scraping e Análise do Instagram
1. Recebe URL do Instagram
2. Captura screenshot da página
3. Analisa a imagem com Ollama/Qwen
4. Extrai informações estruturadas
5. Exporta para JSON

Instalação:
    pip install playwright ollama pillow
    playwright install chromium
    ollama pull qwen3-vl:2b
"""

from playwright.sync_api import sync_playwright, Page
import ollama
from PIL import Image
import json
import os
import time
from datetime import datetime


def fechar_popups(page: Page, tempo_espera: int = 2) -> bool:
    """
    Tenta identificar e fechar popups comuns na página.
    """
    popup_fechado = False
    
    seletores_fechar = [
        'button[aria-label*="close" i]',
        'button[aria-label*="fechar" i]',
        '[class*="close" i]',
        '[class*="dismiss" i]',
        'button:has-text("×")',
        'svg[aria-label="Close"]',
        'button:has(svg[aria-label="Close"])',
    ]
    
    print("Verificando popups...")
    
    for seletor in seletores_fechar:
        try:
            if page.locator(seletor).first.is_visible(timeout=1000):
                print(f"  ✓ Popup encontrado e fechado")
                page.locator(seletor).first.click()
                popup_fechado = True
                time.sleep(0.5)
                break
        except:
            continue
    
    if popup_fechado:
        time.sleep(tempo_espera)
    else:
        print("  Nenhum popup detectado")
    
    return popup_fechado


def capturar_screenshot_instagram(url: str, nome_arquivo: str = None) -> str:
    """
    Captura screenshot de uma URL do Instagram.
    
    Args:
        url (str): URL do post do Instagram
        nome_arquivo (str): Nome do arquivo para salvar (opcional)
    
    Returns:
        str: Caminho do arquivo salvo
    """
    
    if nome_arquivo is None:
        # Gera nome baseado no timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"instagram_{timestamp}.png"
    
    print(f"🌐 Acessando URL: {url}")
    
    try:
        with sync_playwright() as p:
            # Inicia o navegador
            print("Iniciando navegador...")
            browser = p.chromium.launch(headless=True)
            
            # Cria uma nova página
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Navega para a URL
            print(f"Navegando para: {url}")
            page.goto(url, wait_until="networkidle")
            
            # Tenta fechar popups
            fechar_popups(page, tempo_espera=1)
            
            # Aguarda um pouco para garantir carregamento completo
            print("Aguardando carregamento completo...")
            time.sleep(3)
            
            # Captura o screenshot
            print(f"Capturando screenshot...")
            page.screenshot(path=nome_arquivo, full_page=False)
            
            # Fecha o navegador
            browser.close()
            
            caminho_completo = os.path.abspath(nome_arquivo)
            print(f"✓ Screenshot salvo em: {caminho_completo}")
            return caminho_completo
        
    except Exception as e:
        print(f"✗ Erro ao capturar screenshot: {e}")
        import traceback
        traceback.print_exc()
        return ""


def analisar_imagem_instagram(caminho_imagem: str, modelo: str = "gemma3:4b") -> dict:
    """
    Analisa o screenshot do Instagram usando Ollama.
    
    Args:
        caminho_imagem (str): Caminho para o arquivo de imagem
        modelo (str): Nome do modelo Ollama a usar
    
    Returns:
        dict: Dicionário com as informações extraídas
    """
    
    print(f"\n📸 Analisando imagem: {caminho_imagem}")
    
    if not os.path.exists(caminho_imagem):
        print(f"✗ Erro: Arquivo não encontrado!")
        return {}
    
    try:
        # Verifica dimensões da imagem
        img = Image.open(caminho_imagem)
        print(f"✓ Imagem carregada: {img.size[0]}x{img.size[1]} pixels")
    except Exception as e:
        print(f"✗ Erro ao abrir imagem: {e}")
        return {}
    
    print(f"🤖 Usando modelo Ollama: {modelo}")
    
    try:
        # Prompt estruturado para extrair informações do Instagram
        prompt = """Analise este screenshot do Instagram e extraia TODAS as informações visíveis em formato JSON:

{
  "rede_social": "Instagram",
  "usuario": "nome do usuário/conta",
  "nome_perfil": "nome completo se visível",
  "curtidas": "número de curtidas (apenas números)",
  "comentarios": "número de comentários",
  "compartilhamentos": "número de compartilhamentos se visível",
  "salvamentos": "número de salvamentos se visível",
  "legenda": "texto completo da legenda do post",
  "hashtags": ["lista", "de", "hashtags"],
  "mencoes": ["@usuarios", "mencionados"],
  "localizacao": "localização marcada",
  "data_post": "data/horário do post",
  "tipo_conteudo": "foto/vídeo/carrossel/reels",
  "descricao_visual": "descrição MUITO detalhada da imagem: pessoas, objetos, cores, ambiente, expressões, textos visíveis na imagem, logos, marcas, etc.",
  "transcricao_textos": "TODOS os textos visíveis na imagem (não apenas a legenda)",
  "outros_detalhes": "qualquer outra informação relevante"
}

IMPORTANTE: 
- Transcreva TODO o texto visível no screenshot
- Seja extremamente detalhado na descrição visual
- Extraia TODOS os números (curtidas, comentários, etc)
- Liste TODAS as hashtags e menções
- Se algo não estiver visível, use "não visível"

Responda APENAS com o JSON válido, sem texto adicional."""
        
        print("\n🔍 Processando imagem com IA...")
        
        # Gera a análise usando Ollama
        response = ollama.chat(
            model=modelo,
            messages=[{
                'role': 'user',
                'content': prompt,
                'images': [caminho_imagem]
            }]
        )
        
        resposta_texto = response['message']['content']
        print("✓ Análise concluída!")
        
        # Parse do JSON
        try:
            # Remove marcadores de código
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
            dados["arquivo_screenshot"] = caminho_imagem
            dados["timestamp_analise"] = datetime.now().isoformat()
            dados["modelo_usado"] = modelo
            
            return dados
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Aviso: Resposta não está em formato JSON válido")
            print(f"Tentando salvar resposta bruta...")
            
            return {
                "arquivo_screenshot": caminho_imagem,
                "timestamp_analise": datetime.now().isoformat(),
                "modelo_usado": modelo,
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
    Salva os dados em arquivo JSON.
    """
    
    if arquivo_saida is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_saida = f"instagram_analise_{timestamp}.json"
    
    try:
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        caminho_completo = os.path.abspath(arquivo_saida)
        print(f"✓ JSON salvo em: {caminho_completo}")
        return caminho_completo
        
    except Exception as e:
        print(f"✗ Erro ao salvar JSON: {e}")
        return ""


def processar_url_instagram(url: str, salvar_screenshot: bool = True, arquivo_json: str = None) -> dict:
    """
    Processo completo: captura screenshot e analisa.
    
    Args:
        url (str): URL do post do Instagram
        salvar_screenshot (bool): Se True, mantém o screenshot salvo
        arquivo_json (str): Nome do arquivo JSON de saída (opcional)
    
    Returns:
        dict: Dados extraídos
    """
    
    print("="*60)
    print("INSTAGRAM SCRAPER & ANALYZER")
    print("="*60)
    
    # 1. Captura screenshot
    screenshot = capturar_screenshot_instagram(url)
    
    if not screenshot:
        print("✗ Falha ao capturar screenshot")
        return {}
    
    # 2. Analisa a imagem
    dados = analisar_imagem_instagram(screenshot)
    
    if not dados:
        print("✗ Falha ao analisar imagem")
        return {}
    
    # 3. Adiciona URL original aos dados
    dados["url_original"] = url
    
    # 4. Salva JSON
    arquivo_salvo = salvar_json(dados, arquivo_json)
    
    # 5. Remove screenshot se não for para manter
    if not salvar_screenshot and screenshot:
        try:
            os.remove(screenshot)
            print(f"🗑️  Screenshot temporário removido")
        except:
            pass
    
    # 6. Exibe resumo
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE")
    print("="*60)
    print(f"📱 Rede Social: {dados.get('rede_social', 'N/A')}")
    print(f"👤 Usuário: {dados.get('usuario', 'N/A')}")
    print(f"❤️  Curtidas: {dados.get('curtidas', 'N/A')}")
    print(f"💬 Comentários: {dados.get('comentarios', 'N/A')}")
    print(f"📝 Legenda: {str(dados.get('legenda', 'N/A'))[:100]}...")
    print(f"📸 Screenshot: {screenshot}")
    print(f"📄 JSON: {arquivo_salvo}")
    print("="*60)
    
    return dados


def processar_multiplas_urls(urls: list, arquivo_json: str = "instagram_multiplos.json") -> list:
    """
    Processa múltiplas URLs do Instagram.
    
    Args:
        urls (list): Lista de URLs
        arquivo_json (str): Arquivo JSON para salvar todos os resultados
    
    Returns:
        list: Lista com todos os dados extraídos
    """
    
    resultados = []
    
    for i, url in enumerate(urls, 1):
        print(f"\n\n{'#'*60}")
        print(f"PROCESSANDO {i}/{len(urls)}")
        print(f"{'#'*60}\n")
        
        dados = processar_url_instagram(url, salvar_screenshot=True, arquivo_json=None)
        
        if dados:
            resultados.append(dados)
    
    # Salva todos os resultados
    if resultados:
        try:
            with open(arquivo_json, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            
            print(f"\n\n✓ Todos os resultados salvos em: {os.path.abspath(arquivo_json)}")
            print(f"Total de posts processados: {len(resultados)}")
        except Exception as e:
            print(f"✗ Erro ao salvar resultados consolidados: {e}")
    
    return resultados


# Exemplo de uso
if __name__ == "__main__":
    # URL do post do Instagram para processar
    url_instagram = "https://www.instagram.com/p/DCiaBn_t46t/"
    
    # Processa uma única URL
    resultado = processar_url_instagram(
        url_instagram,
        salvar_screenshot=True,  # Mantém o screenshot
        arquivo_json="resultado_instagram.json"  # Nome do arquivo JSON
    )
    
    if resultado:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Falha no processo")
    
    # Exemplo: Processar múltiplas URLs
    # urls = [
    #     "https://www.instagram.com/p/exemplo1/",
    #     "https://www.instagram.com/p/exemplo2/",
    #     "https://www.instagram.com/p/exemplo3/"
    # ]
    # processar_multiplas_urls(urls)
