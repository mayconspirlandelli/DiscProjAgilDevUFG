"""
Script para capturar screenshots de páginas web usando Playwright.
Playwright gerencia automaticamente os drivers do navegador, eliminando problemas com chromedriver.

Instalação:
    pip install playwright
    playwright install chromium
"""

from playwright.sync_api import sync_playwright
import os
import time


def capturar_screenshot(
    url: str, 
    nome_arquivo: str = "screenshot.png", 
    tempo_espera: int = 3,
    largura: int = 1920,
    altura: int = 1080,
    pagina_completa: bool = False
) -> bool:
    """
    Navega até uma URL e captura um screenshot da página usando Playwright.
    
    Args:
        url (str): URL da página a ser capturada
        nome_arquivo (str): Nome do arquivo PNG a ser salvo (padrão: "screenshot.png")
        tempo_espera (int): Tempo em segundos para aguardar o carregamento da página (padrão: 3)
        largura (int): Largura da janela do navegador em pixels (padrão: 1920)
        altura (int): Altura da janela do navegador em pixels (padrão: 1080)
        pagina_completa (bool): Se True, captura a página inteira com scroll (padrão: False)
    
    Returns:
        bool: True se o screenshot foi capturado com sucesso, False caso contrário
    """
    
    try:
        # Cria o diretório se não existir
        diretorio = os.path.dirname(nome_arquivo)
        if diretorio and not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"Diretório criado: {diretorio}")
        
        with sync_playwright() as p:
            # Inicia o navegador Chromium em modo headless
            print("Iniciando navegador...")
            browser = p.chromium.launch(headless=True)
            
            # Cria uma nova página com as dimensões especificadas
            page = browser.new_page(viewport={'width': largura, 'height': altura})
            
            # Navega para a URL
            print(f"Navegando para: {url}")
            page.goto(url, wait_until="networkidle")
            
            # Aguarda o tempo adicional especificado
            if tempo_espera > 0:
                print(f"Aguardando {tempo_espera} segundos...")
                time.sleep(tempo_espera)
            
            # Captura o screenshot
            print(f"Capturando screenshot...")
            page.screenshot(path=nome_arquivo, full_page=pagina_completa)
            
            # Fecha o navegador
            browser.close()
            
            # Obtém o caminho completo do arquivo
            caminho_completo = os.path.abspath(nome_arquivo)
            print(f"✓ Screenshot salvo com sucesso em: {caminho_completo}")
            return True
        
    except Exception as e:
        print(f"✗ Erro ao capturar screenshot: {str(e)}")
        print("\nCertifique-se de que o Playwright está instalado:")
        print("  pip install playwright")
        print("  playwright install chromium")
        return False


def capturar_multiplos_screenshots(urls: list, prefixo: str = "screenshot", pasta: str = "screenshots"):
    """
    Captura screenshots de múltiplas URLs.
    
    Args:
        urls (list): Lista de URLs para capturar
        prefixo (str): Prefixo para os nomes dos arquivos (padrão: "screenshot")
        pasta (str): Pasta onde salvar os arquivos (padrão: "screenshots")
    
    Returns:
        dict: Dicionário com URLs como chaves e status (True/False) como valores
    """
    
    resultados = {}
    
    for i, url in enumerate(urls, 1):
        print(f"\n--- Capturando {i}/{len(urls)} ---")
        nome_arquivo = os.path.join(pasta, f"{prefixo}_{i}.png")
        sucesso = capturar_screenshot(url, nome_arquivo)
        resultados[url] = sucesso
    
    # Resumo
    print("\n" + "="*50)
    print("RESUMO")
    print("="*50)
    sucessos = sum(resultados.values())
    print(f"Total: {len(urls)} | Sucesso: {sucessos} | Falha: {len(urls) - sucessos}")
    
    return resultados


# Exemplo de uso
if __name__ == "__main__":
    # Exemplo 1: Capturar uma única URL
    ##url = "https://www.example.com"
    
    #url = "https://www.instagram.com/p/DKHZC2qNEbO/"
    url = "https://www.instagram.com/p/DRaYqKWjwTm"

    capturar_screenshot(url, "exemplo.png", tempo_espera=2)
    
    # Exemplo 2: Capturar página completa (com scroll)
    # capturar_screenshot(url, "exemplo_completo.png", pagina_completa=True)
    
    # Exemplo 3: Capturar múltiplas URLs
    # urls = [
    #     "https://www.google.com",
    #     "https://www.github.com",
    #     "https://www.python.org"
    # ]
    # capturar_multiplos_screenshots(urls)