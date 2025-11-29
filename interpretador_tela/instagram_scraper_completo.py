""" 
Sistema Completo de Scraping e Análise do Instagram com OCR
1. Recebe URL do Instagram
2. Captura screenshot da página
3. Extrai texto usando OCR (Tesseract)
4. Estrutura informações em JSON
5. Exporta resultados

Instalação:
    pip install playwright pillow pytesseract
    playwright install chromium
    
    # Instalar Tesseract no sistema:
    # macOS: brew install tesseract tesseract-lang
    # Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por
    # Windows: baixe de https://github.com/UB-Mannheim/tesseract/wiki
"""

from playwright.sync_api import sync_playwright, Page
from PIL import Image
import pytesseract
import json
import os
import re
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


def extrair_texto_ocr(caminho_imagem: str, idioma: str = 'por+eng') -> dict:
    """
    Extrai texto de uma imagem usando OCR (Tesseract).
    
    Args:
        caminho_imagem (str): Caminho para o arquivo de imagem
        idioma (str): Idioma(s) para OCR (padrão: 'por+eng' para português e inglês)
                     Opções: 'por', 'eng', 'por+eng', etc.
    
    Returns:
        dict: Dicionário com texto extraído e informações estruturadas
    """
    
    print(f"\n📸 Extraindo texto da imagem: {caminho_imagem}")
    
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
    
    print(f"🔍 Processando com Tesseract OCR (idioma: {idioma})...")
    
    try:
        # Configura o Tesseract para português e inglês
        config_tesseract = f'--oem 3 --psm 6'
        
        # Extrai texto da imagem
        print("📖 Extraindo texto...")
        texto_completo = pytesseract.image_to_string(img, lang=idioma, config=config_tesseract)
        
        # Extrai dados detalhados (com posições)
        print("📍 Extraindo posições do texto...")
        dados_detalhados = pytesseract.image_to_data(img, lang=idioma, config=config_tesseract, output_type=pytesseract.Output.DICT)
        
        # Organiza os textos extraídos
        textos_completos = []
        textos_por_posicao = []
        
        n_boxes = len(dados_detalhados['text'])
        for i in range(n_boxes):
            texto = dados_detalhados['text'][i].strip()
            if texto:  # Ignora textos vazios
                confianca = int(dados_detalhados['conf'][i])
                if confianca > 0:  # Ignora textos com confiança inválida
                    textos_completos.append(texto)
                    textos_por_posicao.append({
                        "texto": texto,
                        "confianca": round(confianca / 100, 2),  # Normaliza para 0-1
                        "posicao": {
                            "x": dados_detalhados['left'][i],
                            "y": dados_detalhados['top'][i],
                            "largura": dados_detalhados['width'][i],
                            "altura": dados_detalhados['height'][i]
                        }
                    })
        
        # Limpa o texto completo
        texto_completo = texto_completo.strip()
        
        print(f"✓ OCR concluído! {len(textos_completos)} palavras/blocos encontrados")
        
        # Tenta extrair informações específicas do Instagram
        dados = extrair_informacoes_instagram(texto_completo, textos_completos)
        
        # Adiciona dados do OCR
        dados["ocr_texto_completo"] = texto_completo
        dados["ocr_textos_individuais"] = textos_completos
        dados["ocr_detalhes"] = textos_por_posicao
        dados["ocr_total_blocos"] = len(textos_completos)
        dados["arquivo_screenshot"] = caminho_imagem
        dados["timestamp_analise"] = datetime.now().isoformat()
        dados["metodo_extracao"] = "Tesseract OCR"
        dados["idioma_ocr"] = idioma
        
        return dados
        
    except Exception as e:
        print(f"✗ Erro ao processar OCR: {e}")
        print("\nDica: Certifique-se de que o Tesseract está instalado:")
        print("  macOS: brew install tesseract tesseract-lang")
        print("  Linux: sudo apt-get install tesseract-ocr tesseract-ocr-por")
        import traceback
        traceback.print_exc()
        return {}


def extrair_informacoes_instagram(texto_completo: str, textos_lista: list) -> dict:
    """
    Extrai informações específicas do Instagram a partir do texto OCR.
    
    Args:
        texto_completo (str): Texto completo extraído
        textos_lista (list): Lista de textos individuais
    
    Returns:
        dict: Informações estruturadas do Instagram
    """
    
    dados = {
        "rede_social": "Instagram",
        "usuario": "não detectado",
        "curtidas": "não detectado",
        "comentarios": "não detectado",
        "legenda": "não detectado",
        "hashtags": [],
        "mencoes": [],
        "data_post": "não detectado",
        "localizacao": "não detectado"
    }
    
    # Extrai hashtags
    hashtags = re.findall(r'#\w+', texto_completo)
    if hashtags:
        dados["hashtags"] = list(set(hashtags))
    
    # Extrai menções
    mencoes = re.findall(r'@\w+', texto_completo)
    if mencoes:
        dados["mencoes"] = list(set(mencoes))
    
    # Tenta identificar números de curtidas
    # Padrões: "1.234 curtidas", "1,234 likes", "1234 curtidas"
    match_curtidas = re.search(r'([\d.,]+)\s*(curtidas?|likes?|gostei)', texto_completo, re.IGNORECASE)
    if match_curtidas:
        dados["curtidas"] = match_curtidas.group(1).replace('.', '').replace(',', '')
    
    # Tenta identificar número de comentários
    match_comentarios = re.search(r'([\d.,]+)\s*(comentários?|comments?)', texto_completo, re.IGNORECASE)
    if match_comentarios:
        dados["comentarios"] = match_comentarios.group(1).replace('.', '').replace(',', '')
    
    # Tenta identificar usuário (geralmente aparece no início)
    # Procura por @ seguido de nome ou nome no início
    for texto in textos_lista[:5]:  # Verifica os primeiros textos
        if texto.startswith('@'):
            dados["usuario"] = texto
            break
        # Verifica se é um nome de usuário (sem espaços, letras e números)
        if re.match(r'^[a-zA-Z0-9_\.]+$', texto) and len(texto) > 2:
            dados["usuario"] = texto
            break
    
    # Tenta identificar data (padrões: "há 2 dias", "2d", "1 semana")
    match_data = re.search(r'(há\s+\d+\s+\w+|\d+[dhms]|há\s+uma?\s+\w+)', texto_completo, re.IGNORECASE)
    if match_data:
        dados["data_post"] = match_data.group(0)
    
    # A legenda geralmente é o texto mais longo após o usuário
    textos_ordenados = sorted(textos_lista, key=len, reverse=True)
    if textos_ordenados:
        # Pega o texto mais longo que não seja hashtag ou menção
        for texto in textos_ordenados:
            if len(texto) > 20 and not texto.startswith('#') and not texto.startswith('@'):
                dados["legenda"] = texto
                break
    
    # Tenta identificar localização
    for texto in textos_lista:
        if any(palavra in texto.lower() for palavra in ['📍', 'em ', 'at ', 'local']):
            dados["localizacao"] = texto
            break
    
    return dados


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
    Processo completo: captura screenshot e extrai texto com OCR.
    
    Args:
        url (str): URL do post do Instagram
        salvar_screenshot (bool): Se True, mantém o screenshot salvo
        arquivo_json (str): Nome do arquivo JSON de saída (opcional)
    
    Returns:
        dict: Dados extraídos
    """
    
    print("="*60)
    print("INSTAGRAM SCRAPER & OCR ANALYZER")
    print("="*60)
    
    # 1. Captura screenshot
    screenshot = capturar_screenshot_instagram(url)
    
    if not screenshot:
        print("✗ Falha ao capturar screenshot")
        return {}
    
    # 2. Extrai texto com OCR
    dados = extrair_texto_ocr(screenshot)
    
    if not dados:
        print("✗ Falha ao extrair texto")
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
    print(f"🔤 Blocos de texto: {dados.get('ocr_total_blocos', 0)}")
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
    url_instagram = "https://www.instagram.com/p/DRnS7SFiGzh/"
    
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
