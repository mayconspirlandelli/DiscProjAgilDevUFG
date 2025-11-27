# # Instalação das dependências (execute esta célula primeiro no Colab)
# """
# !apt-get update
# !apt-get install -y chromium-browser chromium-chromedriver
# !pip install selenium
# """

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# import time

# def capturar_screenshot(url, nome_arquivo="screenshot.png", tempo_espera=3):
#     """
#     Navega até uma URL e captura um screenshot da página.
    
#     Args:
#         url (str): URL da página a ser capturada
#         nome_arquivo (str): Nome do arquivo PNG a ser salvo (padrão: "screenshot.png")
#         tempo_espera (int): Tempo em segundos para aguardar o carregamento da página (padrão: 3)
    
#     Returns:
#         bool: True se o screenshot foi capturado com sucesso, False caso contrário
#     """
    
#     # Configurações do Chromium para Google Colab
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument("--disable-software-rasterizer")
    
#     # Caminho do Chromium e ChromeDriver no Colab
#     chrome_options.binary_location = "/usr/bin/chromium-browser"
    
#     driver = None
    
#     try:
#         # Inicializa o driver do Chromium
#         service = Service("/usr/bin/chromedriver")
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         print(f"Navegando para: {url}")
#         driver.get(url)
        
#         # Aguarda o carregamento da página
#         time.sleep(tempo_espera)
        
#         # Captura o screenshot
#         print(f"Capturando screenshot...")
#         driver.save_screenshot(nome_arquivo)
        
#         print(f"Screenshot salvo com sucesso em: {nome_arquivo}")
#         return True
        
#     except Exception as e:
#         print(f"Erro ao capturar screenshot: {str(e)}")
#         return False
        
#     finally:
#         # Fecha o navegador
#         if driver:
#             driver.quit()


# # Exemplo de uso no Google Colab
# if __name__ == "__main__":
#     # URL da página que você quer capturar
#     url = "https://www.instagram.com/p/DRaYqKWjwTm"
    
#     # Nome do arquivo de saída
#     arquivo_saida = "pagina_capturada.png"
    
#     # Captura o screenshot
#     capturar_screenshot(url, arquivo_saida, tempo_espera=300)
    
#     # # Para visualizar a imagem no Colab
#     # from IPython.display import Image, display
#     # display(Image(filename=arquivo_saida))



# PASSO 1: Execute estes comandos no terminal do Codespace para instalar o Chromium
"""
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
pip install selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os

def capturar_screenshot(url, nome_arquivo="screenshot.png", tempo_espera=3, modo_headless=True):
    """
    Navega até uma URL e captura um screenshot da página.
    
    Args:
        url (str): URL da página a ser capturada
        nome_arquivo (str): Nome do arquivo PNG a ser salvo (padrão: "screenshot.png")
        tempo_espera (int): Tempo em segundos para aguardar o carregamento da página (padrão: 3)
        modo_headless (bool): Se True, executa sem abrir janela (padrão: True)
    
    Returns:
        bool: True se o screenshot foi capturado com sucesso, False caso contrário
    """
    
    # Configurações do Chromium para Codespaces (ambiente Linux)
    chrome_options = Options()
    
    if modo_headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Caminho do Chromium no Linux (Codespaces)
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    #chrome_options.binary_location = "/usr/local/python/3.12.1/lib/python3.12/site-packages/chromium"
    
    driver = None
    
    try:
        # Inicializa o driver do Chromium
        print("Inicializando Chromium...")
        service = Service("/usr/bin/chromedriver")
        #service = Service("/usr/local/python/3.12.1/lib/python3.12/site-packages/chromium")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Navegando para: {url}")
        driver.get(url)
        
        # Aguarda o carregamento da página
        print(f"Aguardando {tempo_espera} segundos para carregar...")
        time.sleep(tempo_espera)
        
        # Captura o screenshot
        print(f"Capturando screenshot...")
        
        # Cria o diretório se não existir
        diretorio = os.path.dirname(nome_arquivo)
        if diretorio and not os.path.exists(diretorio):
            os.makedirs(diretorio)
        
        driver.save_screenshot(nome_arquivo)
        
        # Obtém o caminho completo do arquivo
        caminho_completo = os.path.abspath(nome_arquivo)
        print(f"✓ Screenshot salvo com sucesso em: {caminho_completo}")
        print(f"  Você pode baixar o arquivo pelo explorador de arquivos do VSCode")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao capturar screenshot: {str(e)}")
        print("\nDica: Certifique-se de que executou os comandos de instalação:")
        print("  sudo apt-get update")
        print("  sudo apt-get install -y chromium-browser chromium-chromedriver")
        print("  pip install selenium")
        return False
        
    finally:
        # Fecha o navegador
        if driver:
            driver.quit()
            print("Navegador fechado.")


# Exemplo de uso no GitHub Codespaces
if __name__ == "__main__":
    # URL da página que você quer capturar
    url = "https://www.example.com"
    
    # Nome do arquivo de saída
    arquivo_saida = "screenshot.png"
    # ou salvar em uma pasta: arquivo_saida = "./capturas/pagina.png"
    
    # Captura o screenshot (sempre em modo headless no Codespaces)
    capturar_screenshot(url, arquivo_saida, tempo_espera=3, modo_headless=True)