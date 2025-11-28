"""
Script para capturar screenshots de páginas web usando Playwright.
Playwright gerencia automaticamente os drivers do navegador, eliminando problemas com chromedriver.

Instalação:
    pip install playwright
    playwright install chromium
"""

from playwright.sync_api import sync_playwright, Page
import os
import time


def fechar_popups(page: Page, tempo_espera: int = 2) -> bool:
    """
    Tenta identificar e fechar popups comuns na página.
    
    Args:
        page (Page): Objeto da página do Playwright
        tempo_espera (int): Tempo em segundos para aguardar após fechar popups (padrão: 2)
    
    Returns:
        bool: True se algum popup foi fechado, False caso contrário
    """
    popup_fechado = False
    
    # Lista de seletores comuns para botões de fechar popup
    seletores_fechar = [
        # Botões de fechar genéricos
        'button[aria-label*="close" i]',
        'button[aria-label*="fechar" i]',
        'button[title*="close" i]',
        'button[title*="fechar" i]',
        '[class*="close" i]',
        '[class*="dismiss" i]',
        '[id*="close" i]',
        
        # Ícones de X
        'button:has-text("×")',
        'button:has-text("✕")',
        'a:has-text("×")',
        
        # Botões específicos de redes sociais
        'button[aria-label="Close"]',
        'div[role="button"][aria-label="Close"]',
        
        # Instagram específico
        'svg[aria-label="Close"]',
        'button:has(svg[aria-label="Close"])',
        
        # LinkedIn específico
        '.msg-overlay-bubble-header__control--close',
        'button[data-test-modal-close-btn]',
        
        # Botões de "Não aceitar" cookies
        'button:has-text("Reject")',
        'button:has-text("Decline")',
        'button:has-text("Rejeitar")',
        'button:has-text("Recusar")',
    ]
    
    print("Verificando popups...")
    
    for seletor in seletores_fechar:
        try:
            # Verifica se o elemento existe e está visível
            if page.locator(seletor).first.is_visible(timeout=1000):
                print(f"  ✓ Popup encontrado: {seletor}")
                page.locator(seletor).first.click()
                popup_fechado = True
                print(f"  ✓ Popup fechado!")
                time.sleep(0.5)  # Pequena pausa após fechar
                break
        except:
            # Continua tentando outros seletores
            continue
    
    # Verifica por overlays/modals e tenta pressionar ESC
    try:
        if page.locator('[role="dialog"]').first.is_visible(timeout=1000):
            print("  ✓ Modal detectado, pressionando ESC...")
            page.keyboard.press('Escape')
            popup_fechado = True
            time.sleep(0.5)
    except:
        pass
    
    if popup_fechado:
        print(f"Aguardando {tempo_espera} segundos após fechar popup...")
        time.sleep(tempo_espera)
    else:
        print("  Nenhum popup detectado")
    
    return popup_fechado


def capturar_screenshot(
    url: str, 
    nome_arquivo: str = "screenshot.png", 
    tempo_espera: int = 3,
    largura: int = 1920,
    altura: int = 1080,
    pagina_completa: bool = False,
    fechar_popup: bool = True
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
        fechar_popup (bool): Se True, tenta detectar e fechar popups automaticamente (padrão: True)
    
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
            
            # Tenta fechar popups se habilitado
            if fechar_popup:
                fechar_popups(page, tempo_espera=1)
            
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
    
    url = "https://www.instagram.com/p/DKHZC2qNEbO/"
    #url = "https://www.instagram.com/p/DRaYqKWjwTm"
    #url = "https://www.linkedin.com/posts/elisa-terumi-rubel-schneider_google-colab-dentro-do-vs-code-o-google-activity-7400117889040678912-W9zY?utm_source=share&utm_medium=member_desktop&rcm=ACoAAAS2RwkBTxVnriY6_cELObq4OH4SM9JAILQ"

    capturar_screenshot(url, "exemplo4.png", tempo_espera=5, pagina_completa=False)
    
    # Exemplo 2: Capturar página completa (com scroll)
    # capturar_screenshot(url, "exemplo_completo.png", pagina_completa=True)
    
    # Exemplo 3: Capturar múltiplas URLs
    # urls = [
    #     "https://www.google.com",
    #     "https://www.github.com",
    #     "https://www.python.org"
    # ]
    # capturar_multiplos_screenshots(urls)
