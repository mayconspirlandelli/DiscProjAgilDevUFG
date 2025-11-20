# from crewai import Agent, Task, Crew, Process
# from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool
# from crewai import LLM
# import json
# from dotenv import load_dotenv
# import os
# from pydantic import BaseModel
# from crewai_tools import FirecrawlSearchTool

# # Página de exemplo (troque pela URL que desejar)
# #url = "https://escoladepos.ufg.br/cursos/atendimento-de-criancas-e-adolescentes-vitimas-ou-testemunhas-de-violencia/"
# url = "https://escoladepos.ufg.br/cursos/banco-de-dados-com-big-data/"

# # Carregar variáveis de ambiente do arquivo .env
# load_dotenv()  # Isso carrega as variáveis do .env para os.environ

# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# llm = LLM(
#     model="gemini/gemini-2.0-flash",
#     temperature=0,
#     api_key=GOOGLE_API_KEY,
# )

# # llmGemma = LLM(
# #     model="ollama/gemma3:270m",
# #     base_url="http://localhost:11434",
# #     temperature=0
# # )


# # Ferramenta para raspagem de site
# scraper_tool = ScrapeWebsiteTool()


# # Agente que usa a ferramenta de scraping
# agente_extracao = Agent(
#     role="Agente de Coleta de Informações de Sites",
#     goal="Extrair informacoes dos curso de pós-graduação da UFG. Voce deve caputra informaçoes sobre o curso, como nome, descrição, data de início e valor.",
#     backstory="Especialista em web scraping de lojas online e coleta de informações relevantes.",
#     verbose=True,
#     memory=True,
#     llm=llm,
#     tools=[scraper_tool]
# )


# # Tarefa que instrui o agente a usar a ferramenta
# extrair_informacoes_site = Task(
#     description=f"""
#     Acesse o site {url} e extraia informaçoes relativas ao curso de pós-graduação da UFG.
#     Para cada curso, colete:
#     - Nome do curso
#     - Descrição resumida
#     - Carga horário do curso
#     - Curso é on-line, presencial ou híbrido
#     - Informações sobre o curso
#     - Edital está diponível ou não.
#     - Data de início do curso
#     - Qual valor da mensalidade do curso.

#     Formate a saída como uma lista em JSON.
#     """,
#     expected_output="Uma lista JSON contendo nome, descrição e preço de cada produto.",
#     tools=[scraper_tool],
#     agent=agente_extracao
# )

# agente_formatador_json = Agent(
#     role="Agente Responsavel por Formatação JSON",
#     goal="Extrair lista de produtos, descrições e preços de um site de e-commerce",
#     backstory="Especialista em web scraping de lojas online e coleta de informações relevantes.",
#     verbose=True,
#     memory=True,
#     llm=llm,
#         tools=[scraper_tool]
# )

# formatar_json = Task(
#     description=f"""
#     Formate a saída como uma lista em JSON com os seguintes campos para cada produto coletado:
#     - Nome do curso,
#     - Descrição resumida,
#     - Carga horário do curso,
#     - Curso é on-line, presencial ou híbrido,
#     - Informações sobre o curso,
#     - Edital está diponível ou não,
#     - Data de início do curso,
#     - Qual valor da mensalidade do curso.
#     """,
#     expected_output="Uma lista JSON contendo todos as informações coletadas do site.",
#     tools=[scraper_tool],
#     llm=llm,
#     agent=agente_formatador_json
# )

# # Criar a equipe e processar
# equipe = Crew(
#     agents=[agente_extracao, agente_formatador_json],
#     tasks=[extrair_informacoes_site, formatar_json],
#     process=Process.sequential,
#     #llm=llmGemma,
#     verbose=True
# )


# # Executar
# resultado = equipe.kickoff(inputs={'url': url})

# print(resultado)

# with open("resultado_scraping.json", "w", encoding="utf-8") as f:
#      json.dump(saida_json, f, ensure_ascii=False, indent=2)

# print("✅ Resultado salvo em 'resultado_scraping.json'")




# ================================================

from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from crewai import LLM
import json
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import List

# Página de exemplo (troque pela URL que desejar)
#url = "https://escoladepos.ufg.br/cursos/atendimento-de-criancas-e-adolescentes-vitimas-ou-testemunhas-de-violencia/"
url = "https://escoladepos.ufg.br/cursos/banco-de-dados-com-big-data/"

# Carregar variáveis de ambiente
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


USE_LOCAL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

if USE_LOCAL:
    llm = LLM(
        #model="ollama/gemma3:270m",
        model="ollama/qwen3:1.7b",
        base_url="http://localhost:11434",
        temperature=0
    )
else:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    llm = LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0,
        api_key=GOOGLE_API_KEY,
    )


# Modelo Pydantic para estruturar a saída
class CursoInfo(BaseModel):
    nome: str
    descricao: str
    carga_horaria: str
    modalidade: str
    informacoes_adicionais: str
    edital_disponivel: str
    data_inicio: str
    valor_mensalidade: str

# Ferramenta para raspagem
scraper_tool = ScrapeWebsiteTool()

# Agente de extração
agente_extracao = Agent(
    role="Agente de Coleta de Informações de Cursos",
    goal="Extrair informações detalhadas do curso de pós-graduação da UFG",
    backstory="Especialista em web scraping focado em dados educacionais e informações acadêmicas.",
    verbose=True,
    memory=True,
    llm=llm,
    #max_rpm=1,
    tools=[scraper_tool]
)

# Tarefa de extração
extrair_informacoes_site = Task(
    description=f"""
    Acesse o site {url} e extraia TODAS as informações do curso de pós-graduação.
    
    Você DEVE coletar exatamente estes campos:
    - nome: Nome completo do curso
    - descricao: Descrição resumida do curso
    - carga_horaria: Carga horária total (ex: "360 horas")
    - modalidade: Se é online, presencial ou híbrido
    - informacoes_adicionais: Informações relevantes sobre o curso
    - edital_disponivel: "Sim" ou "Não" se há edital disponível
    - data_inicio: Data de início das aulas
    - valor_mensalidade: Valor da mensalidade (ex: "R$ 500,00" ou "Gratuito")
    
    IMPORTANTE: Se alguma informação não estiver disponível no site, use "Não informado".
    """,
    expected_output="Informações estruturadas do curso em formato de dicionário Python",
    tools=[scraper_tool],
    agent=agente_extracao
)

# Agente formatador
agente_formatador_json = Agent(
    role="Especialista em Formatação de Dados",
    goal="Converter as informações extraídas em formato JSON válido e bem estruturado",
    backstory="Especialista em estruturação de dados com foco em precisão e padronização.",
    verbose=True,
    memory=True,
    #max_rpm=1,
    llm=llm
)

# Tarefa de formatação
formatar_json = Task(
    description="""
    Receba as informações extraídas e formate em JSON válido.
    
    O JSON deve ter EXATAMENTE esta estrutura:
    {
        "curso": {
            "nome": "...",
            "descricao": "...",
            "carga_horaria": "...",
            "modalidade": "...",
            "informacoes_adicionais": "...",
            "edital_disponivel": "...",
            "data_inicio": "...",
            "valor_mensalidade": "..."
        }
    }
    
    Retorne APENAS o JSON, sem texto adicional antes ou depois.
    Use "Não informado" para campos sem informação.
    """,
    expected_output="JSON válido contendo todas as informações do curso",
    agent=agente_formatador_json,
    output_file="resultado_scraping.json"  # Salvamento automático
)

# Criar equipe
equipe = Crew(
    agents=[agente_extracao, agente_formatador_json],
    tasks=[extrair_informacoes_site, formatar_json],
    process=Process.sequential,
    verbose=True
)

# Executar
print("🚀 Iniciando extração de dados...")
resultado = equipe.kickoff(inputs={'url': url})

print("\n" + "="*60)
print("📊 RESULTADO DA EXTRAÇÃO")
print("="*60)
print(resultado)

# Salvar resultado em JSON
try:
    # Tentar parsear se o resultado já for uma string JSON
    if isinstance(resultado, str):
        # Remover possíveis marcadores de código markdown
        resultado_limpo = resultado.strip()
        if resultado_limpo.startswith("```"):
            linhas = resultado_limpo.split("\n")
            resultado_limpo = "\n".join(linhas[1:-1])
        
        saida_json = json.loads(resultado_limpo)
    else:
        # Se for objeto, converter para dict
        saida_json = resultado if isinstance(resultado, dict) else {"resultado": str(resultado)}
    
    # Salvar arquivo
    with open("resultado_scraping.json", "w", encoding="utf-8") as f:
        json.dump(saida_json, f, ensure_ascii=False, indent=2)
    
    print("\n✅ Resultado salvo em 'resultado_scraping.json'")
    
    # Mostrar prévia do JSON salvo
    print("\n📄 Prévia do JSON salvo:")
    print(json.dumps(saida_json, ensure_ascii=False, indent=2))

except json.JSONDecodeError as e:
    print(f"\n⚠️ Erro ao parsear JSON: {e}")
    print("Salvando resultado como texto bruto...")
    
    # Salvar como objeto com o resultado bruto
    fallback_json = {
        "status": "warning",
        "mensagem": "Resultado não estava em formato JSON válido",
        "resultado_bruto": str(resultado)
    }
    
    with open("resultado_scraping.json", "w", encoding="utf-8") as f:
        json.dump(fallback_json, f, ensure_ascii=False, indent=2)
    
    print("✅ Resultado salvo em 'resultado_scraping.json' (formato alternativo)")

except Exception as e:
    print(f"\n❌ Erro ao salvar arquivo: {e}")
    print("Resultado bruto:")
    print(resultado)