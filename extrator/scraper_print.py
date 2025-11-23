# Instalação das dependências (execute esta célula primeiro no Colab)
"""
!apt-get update
!apt-get install -y chromium-browser chromium-chromedriver
!pip install selenium
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def capturar_screenshot(url, nome_arquivo="screenshot.png", tempo_espera=3):
    """
    Navega até uma URL e captura um screenshot da página.
    
    Args:
        url (str): URL da página a ser capturada
        nome_arquivo (str): Nome do arquivo PNG a ser salvo (padrão: "screenshot.png")
        tempo_espera (int): Tempo em segundos para aguardar o carregamento da página (padrão: 3)
    
    Returns:
        bool: True se o screenshot foi capturado com sucesso, False caso contrário
    """
    
    # Configurações do Chromium para Google Colab
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-software-rasterizer")
    
    # Caminho do Chromium e ChromeDriver no Colab
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    driver = None
    
    try:
        # Inicializa o driver do Chromium
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Navegando para: {url}")
        driver.get(url)
        
        # Aguarda o carregamento da página
        time.sleep(tempo_espera)
        
        # Captura o screenshot
        print(f"Capturando screenshot...")
        driver.save_screenshot(nome_arquivo)
        
        print(f"Screenshot salvo com sucesso em: {nome_arquivo}")
        return True
        
    except Exception as e:
        print(f"Erro ao capturar screenshot: {str(e)}")
        return False
        
    finally:
        # Fecha o navegador
        if driver:
            driver.quit()


# Exemplo de uso no Google Colab
if __name__ == "__main__":
    # URL da página que você quer capturar
    url = "https://www.instagram.com/p/DRaYqKWjwTm"
    
    # Nome do arquivo de saída
    arquivo_saida = "pagina_capturada.png"
    
    # Captura o screenshot
    capturar_screenshot(url, arquivo_saida, tempo_espera=300)
    
    # # Para visualizar a imagem no Colab
    # from IPython.display import Image, display
    # display(Image(filename=arquivo_saida))