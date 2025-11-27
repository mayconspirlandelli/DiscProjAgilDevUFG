from browser_use import Agent, ChatGoogle, Browser, ChatGroq
#from dotenv import load_dotenv 
#import google.generativeai as genai
from dotenv import load_dotenv 
import os 
import asyncio


load_dotenv() 

api_key = os.getenv("GOOGLE_API_KEY") 
print("API_KEY:", api_key is not None) 
# para verificar se foi lida)


async def main():

    # browser = Browser(    
    #     executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",     
    #     user_data_dir="~/Library/Application Support/Google/Chrome",     
    #     profile_directory="Default", )   

    browser = Browser(
        window_size={"width": 500, "height": 700},  # Set window size
        #browser_type="chromium", 
        headless=False)
    
    llm = ChatGoogle(model="google/gemini-2.5-flash", 
                     api_key=os.getenv("GOOGLE_API_KEY"))

   # llm = ChatGroq(model="meta-llama/llama-4-maverick-17b-128e-instruct", 
   #                api_key=os.getenv("GROQ_API_KEY"))
    

    agent = Agent(     
        #task="Pesquise no yahoo.com.br os top 5 assuntos mais pesquisados no Brasil e me retorna em uma lista.",  
        #task="Pesquise no X.com os 5 assuntos do momento no Brasil e me retorna em uma lista.",
        #task="Pesquise no ifood.com.br, 5 lojas de doces no endereco Rua Pedroso Alvarenga, 1192 – Itaim Bibi, São Paulo – SP ",
        task="Liste 5 trends no site https://trends.google.com.br/trending?geo=BR&hl=pt-BR&category=14&hours=168", 
        llm=llm,

        browser=browser,
        #api_key=api_key,
    )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

#agent.run_sync())