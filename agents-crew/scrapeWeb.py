from pydantic import BaseModel
from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import ScrapeWebsiteTool
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()


def get_llm(provider: str = "gemini"):
    """Configura o LLM para usar Gemini ou OpenAI.
    
    Args:
        provider: "gemini" (padrão) ou "openai"
    """
    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY não configurada no .env")
        
        return LLM(
            model="gemini/gemini-2.5-flash",
            api_key=api_key,
            temperature=0.7,
        )
    
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY não configurada no .env")
        
        return LLM(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.7,
        )

    elif provider == "llama":
        return LLM(
            model ="ollama/llama3.1:8b",
            base_url="http://localhost:11434",
            temperature=0.7,
        )

    elif provider == "gemma":
        return LLM(
            #model ="ollama/gemma3:270m",
            model="ollama/qwen3:1.7b",
            base_url="http://localhost:11434",
            temperature=0.7,
        )

    else:
        raise ValueError(f"Provider '{provider}' não suportado. Use 'gemini' ou 'openai'.")



# ==============================
# 1. Ferramenta para Scraping
# ==============================
google_trends_tool = ScrapeWebsiteTool()

# ==============================
# 2. Criando o agente
# ==============================
agente_trends = Agent(
    name="AgenteGoogleTrends",
    role="Analista de Tendências Políticas",
    goal=(
        "Buscar diariamente no Google Trends quais palavras-chave relacionadas "
        "à política estão em alta no Brasil."
    ),
    backstory=(
        "Você é um analista especializado em monitoramento de tendências políticas. "
        "Seu trabalho é analisar dados públicos e identificar padrões relevantes."
    ),
    tools=[google_trends_tool],
    verbose=True,
    allow_delegation=False,
    max_rpm=1,
    llm=get_llm("gemma")
)

# ==============================
# 3. Task (o que o agente fará)
# ==============================
task_buscar_trends = Task(
    description=(
        """Acesse o Google Trends na página: 
        https://trends.google.com.br/trending?geo={geo}&hl={hl}&hours={hours}&category={category}
        e extraia todas as palavras-chave relacionadas à política. 
        Use a ferramenta ScrapeWebsiteTool para ler a página."""
    ),
    agent=agente_trends,
    expected_output=(
        "Uma lista organizada com palavras-chave políticas em alta no dia, "
        "incluindo: termo, pequeno resumo e possível relevância."
    ),
    llm_model=get_llm("gemma")
)

# ==============================
# 4. Rodando o Crew
# ==============================
crew = Crew(
    agents=[agente_trends],
    tasks=[task_buscar_trends],
    process=Process.sequential,
    llm=get_llm("gemma"),
    verbose=True
)

#resultado = crew.run()
#result = ResearchCrew().crew().kickoff(inputs=inputs)
resultado = crew.kickoff(inputs={
    "geo": "BR",
    "hl": "pt-BR",
    "hours": "24",
    "category": "14",     
    })
print("\n========== RESULTADO ==========\n")
print(resultado)