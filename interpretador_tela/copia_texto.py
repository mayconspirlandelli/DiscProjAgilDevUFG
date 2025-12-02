# Instalação das dependências
"""
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
pip install selenium pyperclip
"""
from playwright.sync_api import sync_playwright, Page
import pyperclip
import time
import os




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



def copiar_texto_url(url, nome_arquivo="texto_copiado.txt", tempo_espera=3):
    """
    Navega até uma URL, copia todo o texto da página e salva em um arquivo TXT.
    
    Args:
        url (str): URL da página para copiar o texto
        nome_arquivo (str): Nome do arquivo TXT de saída (padrão: "texto_copiado.txt")
        tempo_espera (int): Tempo em segundos para aguardar o carregamento (padrão: 3)
    
    Returns:
        bool: True se o texto foi copiado com sucesso, False caso contrário
    """
   
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
            
            # Seleciona todo o texto (CTRL + A)
            print("Selecionando todo o texto (Ctrl+A)...")
            page.keyboard.press('Control+A')
            time.sleep(1)
            
            # Copia o texto (CTRL + C)
            print("Copiando texto (Ctrl+C)...")
            page.keyboard.press('Control+C')
            time.sleep(1)
            
            # Captura o texto da página usando innerText
            print("✂️ Extraindo texto da página...")
            texto_copiado = page.evaluate('document.body.innerText')

            # Fecha o navegador
            browser.close()
            
            print(f"✓ Texto capturado: {len(texto_copiado)} caracteres")
            
            # Salva o texto no arquivo
            print(f"Salvando texto no arquivo...")
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(texto_copiado)
            
            caminho_completo = os.path.abspath(nome_arquivo)
            linhas = len(texto_copiado.split('\n'))
            
            print(f"✓ Texto salvo com sucesso!")
            print(f"  Arquivo: {caminho_completo}")
            print(f"  Linhas: {linhas}")
            print(f"  Caracteres: {len(texto_copiado)}")
            return True
        
    except Exception as e:
        print(f"✗ Erro ao capturar texto: {e}")
        import traceback
        traceback.print_exc()
        return False



    
    # try:
    #     # Inicializa o driver
    #     print("Inicializando Chromium...")
    #     service = Service("/usr/bin/chromedriver")
    #     driver = webdriver.Chrome(service=service, options=chrome_options)
        
    #     print(f"Navegando para: {url}")
    #     driver.get(url)
        
    #     # Aguarda o carregamento da página
    #     print(f"Aguardando {tempo_espera} segundos para carregar...")
    #     time.sleep(tempo_espera)
        
    #     # Seleciona todo o texto (CTRL + A)
    #     print("Selecionando todo o texto (CTRL + A)...")
    #     actions = ActionChains(driver)
    #     actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
    #     time.sleep(1)
        
    #     # Copia o texto (CTRL + C)
    #     print("Copiando texto (CTRL + C)...")
    #     actions.key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
    #     time.sleep(1)
        
    #     # Obtém o texto da área de transferência
    #     texto_copiado = pyperclip.paste()
        
    #     if not texto_copiado:
    #         print("⚠ Nenhum texto foi copiado. Tentando método alternativo...")
    #         # Método alternativo: pegar o texto diretamente do body
    #         texto_copiado = driver.find_element("tag name", "body").text
        
    #     # Cria o diretório se não existir
    #     diretorio = os.path.dirname(nome_arquivo)
    #     if diretorio and not os.path.exists(diretorio):
    #         os.makedirs(diretorio)
        
    #     # Salva o texto no arquivo (equivalente a CTRL + V)
    #     print(f"Salvando texto no arquivo (CTRL + V simulado)...")
    #     with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
    #         arquivo.write(texto_copiado)
        
    #     # Obtém o caminho completo do arquivo
    #     caminho_completo = os.path.abspath(nome_arquivo)
    #     linhas = len(texto_copiado.split('\n'))
    #     caracteres = len(texto_copiado)
        
    #     print(f"✓ Texto copiado e salvo com sucesso!")
    #     print(f"  Arquivo: {caminho_completo}")
    #     print(f"  Linhas: {linhas}")
    #     print(f"  Caracteres: {caracteres}")
    #     return True


# Exemplo de uso
if __name__ == "__main__":
    # URL da página que você quer copiar o texto
    #url = "https://www.example.com"
    url = "https://www.instagram.com/p/DRQSqrukTEc/"
   
    
    # Nome do arquivo de saída
    arquivo_saida = "texto_copiado.txt"
    # ou salvar em uma pasta: arquivo_saida = "./textos/pagina.txt"
    
    # Copia o texto da URL e salva no arquivo
    copiar_texto_url(url, arquivo_saida, tempo_espera=3)