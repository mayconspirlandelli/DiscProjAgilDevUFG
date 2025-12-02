"""
Sistema Completo de Scraping e Análise do Instagram
1. Recebe URL do Instagram
2. Captura texto da página com Ctrl+A
3. Processa com Ollama Gemma3:2b
4. Estrutura informações em JSON
5. Exporta resultados

Instalação:
    pip install playwright ollama
    playwright install chromium
    ollama pull gemma3:2b
"""

from playwright.sync_api import sync_playwright, Page
import ollama
import json
import os
import time
from datetime import datetime


# Configuração global do modelo Ollama
MODELO_OLLAMA = "gemma3:4b"  # Opções: "gemma3:2b", "llama3", "qwen3", etc.


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


def capturar_texto_instagram(url: str) -> dict:
    """
    Acessa URL do Instagram, fecha popups e captura todo o texto da página.
    
    Args:
        url (str): URL do post do Instagram
    
    Returns:
        dict: Dicionário com o texto capturado e metadados
    """
    
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
            
            # Aguarda carregamento completo
            print("Aguardando carregamento completo...")
            time.sleep(3)
            
            # Seleciona todo o texto da página (Ctrl+A)
            print("📋 Selecionando todo o texto da página (Ctrl+A)...")
            page.keyboard.press('Control+A')
            time.sleep(1)
            
            # Copia o texto selecionado (Ctrl+C)
            print("📄 Copiando texto (Ctrl+C)...")
            page.keyboard.press('Control+C')
            time.sleep(1)
            
            # Captura o texto da página usando métodos alternativos
            # (clipboard pode não funcionar em headless, então usamos innerText)
            print("✂️ Extraindo texto da página...")
            texto_pagina = page.evaluate('document.body.innerText')
            
            # Fecha o navegador
            browser.close()
            
            print(f"✓ Texto capturado: {len(texto_pagina)} caracteres")
            
            # Salva o texto bruto em JSON temporário
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_temp = f"texto_bruto_{timestamp}.json"
            
            dados_brutos = {
                "url_original": url,
                "texto_bruto": texto_pagina,
                "timestamp_captura": datetime.now().isoformat(),
                "tamanho_texto": len(texto_pagina)
            }
            
            with open(arquivo_temp, 'w', encoding='utf-8') as f:
                json.dump(dados_brutos, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Texto bruto salvo em: {os.path.abspath(arquivo_temp)}")
            
            return dados_brutos
        
    except Exception as e:
        print(f"✗ Erro ao capturar texto: {e}")
        import traceback
        traceback.print_exc()
        return {}


def processar_com_gemma(texto_bruto: str, modelo: str = MODELO_OLLAMA) -> dict:

    """
    Processa o texto bruto com Ollama para extrair e corrigir informações.
    
    Args:
        texto_bruto (str): Texto capturado da página
        modelo (str): Nome do modelo Ollama (usa MODELO_OLLAMA por padrão)
    
    Returns:
        dict: Informações estruturadas e corrigidas
    """
    
    print(f"\n🤖 Processando texto com {modelo}...")
    
    try:
        # Prompt estruturado para o Gemma3:2b
        prompt = f"""Você é um assistente especializado em extrair informações de posts do Instagram.

Analise o seguinte texto capturado de uma página do Instagram e extraia as informações em formato JSON.

IMPORTANTE:
- Corrija TODA a ortografia para português brasileiro correto
- Extraia APENAS as informações visíveis no texto
- Formate números sem separadores (ex: 1234 em vez de 1.234)
- Se alguma informação não estiver disponível, use "não disponível"

Texto capturado:
{texto_bruto}

Retorne APENAS um JSON válido com esta estrutura:
{{
  "rede_social": "Instagram",
  "usuario": "nome do usuário ou conta",
  "legenda": "texto completo da legenda com ortografia corrigida",
  "curtidas": "número de curtidas (apenas números)",
  "comentarios": "número de comentários",
  "data_post": "data ou tempo do post (ex: há 2 dias, há 13 horas, 15 de nov)",
  "hashtags": ["lista", "de", "hashtags"],
  "mencoes": ["@usuario1", "@usuario2"],
  "localizacao": "localização se visível",
  "descricao_conteudo": "breve descrição do que está sendo mostrado no post"
}}

Responda APENAS com o JSON, sem texto adicional antes ou depois."""

        print("📤 Enviando para Gemma3:2b...")
        
        # Chama o Ollama com Gemma3:2b
        response = ollama.chat(
            model=modelo,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        resposta_texto = response['message']['content']
        
        print("✓ Resposta recebida do modelo!")
        
        # Parse do JSON
        try:
            # Remove marcadores de código se existirem
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
            dados["timestamp_processamento"] = datetime.now().isoformat()
            dados["modelo_usado"] = modelo
            dados["metodo_extracao"] = "Captura de texto + Gemma3:2b"
            
            return dados
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Aviso: Resposta não está em formato JSON válido")
            print(f"Resposta bruta:\n{resposta_texto}")
            
            return {
                "timestamp_processamento": datetime.now().isoformat(),
                "modelo_usado": modelo,
                "resposta_bruta": resposta_texto,
                "erro": "Falha ao parsear JSON"
            }
        
    except Exception as e:
        print(f"✗ Erro ao processar com Gemma: {e}")
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


def processar_url_instagram(url: str, arquivo_json: str = None) -> dict:
    """
    Processo completo: captura texto e processa com Gemma3:2b.
    
    Args:
        url (str): URL do post do Instagram
        arquivo_json (str): Nome do arquivo JSON de saída (opcional)
    
    Returns:
        dict: Dados extraídos e processados
    """
    
    print("="*60)
    print("INSTAGRAM SCRAPER + GEMMA3:2B ANALYZER")
    print("="*60)
    
    # 1. Captura texto da página
    dados_brutos = capturar_texto_instagram(url)
    
    if not dados_brutos or not dados_brutos.get('texto_bruto'):
        print("✗ Falha ao capturar texto")
        return {}
    
    # 2. Processa com Gemma3:2b
    dados_processados = processar_com_gemma(dados_brutos['texto_bruto'])
    
    if not dados_processados:
        print("✗ Falha ao processar com Gemma")
        return {}
    
    # 3. Adiciona URL original
    dados_processados["url_original"] = url
    dados_processados["tamanho_texto_capturado"] = dados_brutos.get('tamanho_texto', 0)
    
    # 4. Salva JSON final (com timestamp se não especificado)
    if arquivo_json is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        arquivo_json = f"instagram_analise_{timestamp}.json"
    
    arquivo_salvo = salvar_json(dados_processados, arquivo_json)
    
    # 5. Exibe resumo
    print("\n" + "="*60)
    print("RESUMO DA ANÁLISE")
    print("="*60)
    print(f"📱 Rede Social: {dados_processados.get('rede_social', 'N/A')}")
    print(f"👤 Usuário: {dados_processados.get('usuario', 'N/A')}")
    print(f"❤️  Curtidas: {dados_processados.get('curtidas', 'N/A')}")
    print(f"💬 Comentários: {dados_processados.get('comentarios', 'N/A')}")
    print(f"📅 Data: {dados_processados.get('data_post', 'N/A')}")
    print(f"📝 Legenda: {str(dados_processados.get('legenda', 'N/A'))[:100]}...")
    print(f"📄 JSON: {arquivo_salvo}")
    print("="*60)
    
    return dados_processados


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
        
        dados = processar_url_instagram(url, arquivo_json=None)
        
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
    #url_instagram = "https://www.instagram.com/p/DRnHAAnjqfC"
    #url_instagram = "https://www.instagram.com/p/DRvHsdiDzSd/"
    #url_instagram = "https://www.instagram.com/p/DRDReOkiLJM"
    #url_instagram = "https://www.instagram.com/p/DRvRkdogCF8"
    
    # # Processa uma única URL
    # resultado = processar_url_instagram(
    #     url_instagram,
    #     arquivo_json="resultado_instagram.json"
    # )
    
  
    
    # Exemplo: Processar múltiplas URLs
    urls = [
        # "https://www.instagram.com/p/exemplo1/",
        # "https://www.instagram.com/p/exemplo2/",
        # "https://www.instagram.com/p/exemplo3/"

        "https://www.instagram.com/p/DRvHsdiDzSd/",
        "https://www.instagram.com/p/DRDReOkiLJM",
        "https://www.instagram.com/p/DRvRkdogCF8"        
    ]
    
    resultado = processar_multiplas_urls(urls)

    if resultado:
        print("\n✅ Processo concluído com sucesso!")
    else:
        print("\n❌ Falha no processo")