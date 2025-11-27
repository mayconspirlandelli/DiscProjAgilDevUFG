from browser_use import Agent, ChatOllama, Browser
import asyncio

	
tarefa = """
    1. Go to reddit https://www.reddit.com/search/?q=browser+agent&type=communities 
    2. Click directly on the first 5 communities to open each in new tabs
    3. Find out what the latest post is about, and switch directly to the next tab
    4. Return the latest post summary for each page
    """

tarefa = """"
    1. Ir para o site https://inf.ufg.br/docentes.
    2. Nesta pagina voce encontra o corpo docentes de um universiade . 
    3. Quero que extrair o nome completo de 5 docentes
    """ 


async def example():
    
    # browser = Browser(
    #     window_size={"width": 1000, "height": 700},  # Set window size
    #     browser_type="chromium", 
    #     headless=False)
    
    #llm = ChatOllama(model="qwen3:1.7b")
    llm = ChatOllama(model="gemma3:270m") #executou com gemma mas deu muitos eeros falta GPU.


    agent = Agent(
        #task="Nesta pagina voce encontra o corpo docentes de um universiade https://inf.ufg.br/docentes. Quero que extrair o nome completo de 5 docentes",
        task=tarefa,
        #browser=browser,
        llm=llm
    )

    history = await agent.run()
    return history

if __name__ == "__main__":
    history = asyncio.run(example())
    print(history)



# import asyncio
# from dotenv import load_dotenv
# load_dotenv()

# from browser_use import Agent, BrowserProfile, ChatOllama, Browser

# # Speed optimization instructions for the model
# SPEED_OPTIMIZATION_PROMPT = """
# Speed optimization instructions:
# - Be extremely concise and direct in your responses
# - Get to the goal as quickly as possible
# - Use multi-action sequences whenever possible to reduce steps
# """


# async def main():
# 	# 1. Use fast LLM - Llama 4 on Groq for ultra-fast inference
# 	from browser_use import ChatGroq

# 	# llm = ChatGroq(
# 	# 	model='meta-llama/llama-4-maverick-17b-128e-instruct',
# 	# 	temperature=0.0,
# 	# )
	
# 	llm = ChatOllama(model="qwen3:1.7b")
# 	# from browser_use import ChatGoogle

# 	# llm = ChatGoogle(model='gemini-flash-lite-latest')

# 	# 2. Create speed-optimized browser profile
# 	# browser_profile = BrowserProfile(
# 	# 	minimum_wait_page_load_time=0.1,
# 	# 	wait_between_actions=0.1,
# 	# 	headless=False,
# 	# )

# 	# 3. Define a speed-focused task
# 	task = """
# 	1. Go to reddit https://www.reddit.com/search/?q=browser+agent&type=communities 
# 	2. Click directly on the first 5 communities to open each in new tabs
#     3. Find out what the latest post is about, and switch directly to the next tab
# 	4. Return the latest post summary for each page
# 	"""

# 	# 4. Create agent with all speed optimizations
# 	agent = Agent(
# 		task=task,
# 		llm=llm,
# 		flash_mode=True,  # Disables thinking in the LLM output for maximum speed
# 		#browser_profile=browser_profile,
# 		extend_system_message=SPEED_OPTIMIZATION_PROMPT,
# 	)

# 	await agent.run()


# if __name__ == '__main__':
# 	asyncio.run(main())