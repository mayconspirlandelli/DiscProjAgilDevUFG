
import os 
from dotenv import load_dotenv 
from browser_use import Agent 
from browser_use.browser.browser import BrowserConfig 
from browser_use.controller.service import Controller 
from browser_use.model import ModelFactory  

load_dotenv()  

async def main():    
    # Criar modelo Gemini 2.5 Flash    
    model = ModelFactory.create(       
        model_type="gemini-2.5-flash",       
        api_key=os.getenv("GOOGLE_API_KEY"),    
                           )    
    # Configuração do navegador   
    browser_config = BrowserConfig(         
        browser_type="chromium",       
        headless=False,   
        # coloque True se não quiser abrir janela    . 
        )     
    controller = Controller(browser_config=browser_config)      
    # Criar agente    
    agent = Agent(controller=controller, model=model)    
    
      # Exemplo: pesquisar algo no Google     
    result = await agent.run("Ábra o Google e pesquise INF UFG cursos de pós-graduação")    
    print("'Resultado:"', result) if __name__ == "'__main__"':     import asyncio   asyncio.run(main()) ))