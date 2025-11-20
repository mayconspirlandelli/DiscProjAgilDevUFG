"""
Agente CrewAI para análise de tendências políticas no Google Trends
Busca e analisa os top trends de política das últimas 24 horas no Brasil
"""

import os
import json
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, LLM, Process
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


# ==============================
# Modelos de Dados
# ==============================

class TrendKeyword(BaseModel):
    """Modelo para uma palavra-chave de tendência"""
    termo: str = Field(description="Palavra-chave ou frase em alta")
    volume: Optional[str] = Field(default=None, description="Volume de buscas estimado")
    resumo: str = Field(description="Breve contexto sobre a tendência")
    relevancia: str = Field(description="Nível de relevância: Alta, Média ou Baixa")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class TrendsReport(BaseModel):
    """Modelo para o relatório completo de tendências"""
    data_coleta: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    categoria: str = Field(default="Política")
    pais: str = Field(default="Brasil")
    periodo: str = Field(default="24 horas")
    keywords: list[TrendKeyword] = Field(default_factory=list)
    total_trends: int = Field(default=0)


# ==============================
# Configuração de LLM
# ==============================

def get_llm(provider: Literal["gemini", "openai", "llama", "gemma"] = "gemini") -> LLM:
    """
    Configura o LLM baseado no provider escolhido.
    
    Args:
        provider: Provedor do modelo (gemini, openai, llama, gemma)
    
    Returns:
        Instância configurada do LLM
    
    Raises:
        EnvironmentError: Se a API key não estiver configurada
        ValueError: Se o provider não for suportado
    """
    
    llm_configs = {
        "gemini": {
            "model": "gemini/gemini-2.0-flash",
            "api_key": os.getenv("GEMINI_API_KEY"),
            "temperature": 0.3,  # Menor temperatura para respostas mais consistentes
        },
        "openai": {
            "model": "gpt-4o-mini",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "temperature": 0.3,
        },
        "gemma": {
            "model": "ollama/gemma3:270m",
            "base_url": "http://localhost:11434",
            "temperature": 0.3,
        },
        "qwen": {
            "model": "ollama/qwen3:1.7b",
            "base_url": "http://localhost:11434",
            "temperature": 0.3,
        }
    }
    
    if provider not in llm_configs:
        raise ValueError(
            f"Provider '{provider}' não suportado. "
            f"Use: {', '.join(llm_configs.keys())}"
        )
    
    config = llm_configs[provider]
    
    # Verificar API key para providers cloud
    if provider in ["gemini", "openai"]:
        if not config["api_key"]:
            raise EnvironmentError(
                f"{provider.upper()}_API_KEY não configurada no arquivo .env"
            )
    
    return LLM(**config)


# ==============================
# Ferramentas
# ==============================

def criar_ferramentas():
    """Cria e configura as ferramentas necessárias"""
    return [
        ScrapeWebsiteTool(
            #website_url="https://trends.google.com.br/trending"
            website_url="https://trends.google.com.br/trending?geo=BR&hl=pt-BR&hours=24&category=14"
            #url = f"https://trends.google.com.br/trending?geo={geo}&hl={hl}&hours={hours}&category={category}"
        )
    ]


# ==============================
# Agentes
# ==============================

def criar_agente_coletor(llm: LLM) -> Agent:
    """Cria o agente responsável por coletar dados do Google Trends"""
    return Agent(
        name="ColetorTrends",
        role="Especialista em Coleta de Dados de Tendências",
        goal=(
            "Extrair com precisão todas as palavras-chave e tendências políticas "
            "em alta no Google Trends Brasil nas últimas 24 horas"
        ),
        backstory=(
            "Você é um especialista em web scraping e análise de dados públicos. "
            "Sua missão é coletar informações estruturadas do Google Trends, "
            "garantindo que todos os dados relevantes sejam capturados com precisão."
        ),
        tools=criar_ferramentas(),
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        llm=llm
    )


def criar_agente_analista(llm: LLM) -> Agent:
    """Cria o agente responsável por analisar e filtrar tendências"""
    return Agent(
        name="AnalistaTrends",
        role="Analista de Tendências Políticas",
        goal=(
            "Analisar, filtrar e classificar as tendências políticas mais relevantes, "
            "fornecendo contexto e avaliando o impacto de cada tendência"
        ),
        backstory=(
            "Você é um analista político experiente com profundo conhecimento do "
            "cenário político brasileiro. Sua expertise permite identificar quais "
            "tendências são verdadeiramente relevantes e fornecer contexto valioso."
        ),
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        llm=llm
    )


# ==============================
# Tasks
# ==============================

def criar_task_coleta(agente: Agent, parametros: dict) -> Task:
    """Cria a task de coleta de dados"""
    url = (
        f"https://trends.google.com.br/trending?"
        f"geo={parametros['geo']}&"
        f"hl={parametros['hl']}&"
        f"hours={parametros['hours']}&"
        f"category={parametros['category']}"
    )
    
    return Task(
        description=(
            f"1. Acesse a URL: {url}\n"
            f"2. Extraia TODAS as tendências políticas listadas\n"
            f"3. Para cada tendência, capture:\n"
            f"   - Termo/palavra-chave exata\n"
            f"   - Volume de buscas (se disponível)\n"
            f"   - Descrição ou contexto apresentado\n"
            f"4. Organize os dados de forma estruturada\n"
            f"5. Certifique-se de capturar no mínimo 2 tendências\n"
        ),
        agent=agente,
        expected_output=(
            "Uma lista detalhada em formato JSON contendo todas as tendências "
            "encontradas, com os campos: termo, volume, contexto"
        )
    )


def criar_task_analise(agente: Agent) -> Task:
    """Cria a task de análise e filtragem"""
    return Task(
        description=(
            "Analise as tendências coletadas e execute:\n\n"
            "1. FILTRAGEM:\n"
            "   - Remova duplicatas\n"
            "   - Elimine termos irrelevantes ou muito genéricos\n"
            "   - Foque em tendências com impacto político real\n\n"
            "2. ENRIQUECIMENTO:\n"
            "   - Adicione um resumo claro (máx. 50 palavras) para cada tendência\n"
            "   - Classifique a relevância (Alta/Média/Baixa) baseado em:\n"
            "     * Impacto político potencial\n"
            "     * Volume de buscas\n"
            "     * Atualidade do tema\n\n"
            "3. PRIORIZAÇÃO:\n"
            "   - Ordene por relevância (Alta → Baixa)\n"
            "   - Mantenha as 15 tendências mais importantes\n\n"
            "4. VALIDAÇÃO:\n"
            "   - Verifique se todas as informações estão completas\n"
            "   - Garanta que os resumos sejam informativos e objetivos\n"
        ),
        agent=agente,
        expected_output=(
            "Lista final em formato JSON com as 15 principais tendências políticas, "
            "ordenadas por relevância, contendo: termo, volume, resumo (conciso e informativo), "
            "relevancia (Alta/Média/Baixa). Formato:\n"
            '[\n'
            '  {\n'
            '    "termo": "exemplo",\n'
            '    "volume": "50k+",\n'
            '    "resumo": "Breve explicação do contexto",\n'
            '    "relevancia": "Alta"\n'
            '  }\n'
            ']'
        )
    )


# ==============================
# Crew Principal
# ==============================

class TrendsAnalysisCrew:
    """Classe principal para orquestrar a análise de tendências"""
    
    def __init__(self, provider: str = "gemini"):
        """
        Inicializa o crew de análise de tendências
        
        Args:
            provider: Provedor do LLM a ser usado
        """
        self.llm = get_llm(provider)
        self.agente_coletor = criar_agente_coletor(self.llm)
        self.agente_analista = criar_agente_analista(self.llm)
    
    def criar_crew(self, parametros: dict) -> Crew:
        """
        Cria e configura o crew com as tasks necessárias
        
        Args:
            parametros: Dicionário com parâmetros de busca
        
        Returns:
            Crew configurado e pronto para execução
        """
        task_coleta = criar_task_coleta(self.agente_coletor, parametros)
        task_analise = criar_task_analise(self.agente_analista)
        
        return Crew(
            #agents=[self.agente_coletor, self.agente_analista],
            agents=[self.agente_coletor],
            #tasks=[task_coleta, task_analise],
            tasks=[task_coleta],
            process=Process.sequential,
            verbose=True,
            memory=False,  # Desabilita memória para evitar confusão entre execuções
        )
    
    def executar(self, parametros: dict) -> dict:
        """
        Executa a análise de tendências
        
        Args:
            parametros: Parâmetros de busca (geo, hl, hours, category)
        
        Returns:
            Dicionário com os resultados da análise
        """
        print("\n" + "="*60)
        print("🔍 INICIANDO ANÁLISE DE TENDÊNCIAS POLÍTICAS")
        print("="*60 + "\n")
        
        crew = self.criar_crew(parametros)
        resultado = crew.kickoff(inputs=parametros)
        
        return {
            "status": "sucesso",
            "timestamp": datetime.now().isoformat(),
            "parametros": parametros,
            "resultado": resultado
        }
    
    def salvar_resultado(self, resultado: dict, arquivo: str = "trends_report.json"):
        """
        Salva o resultado em arquivo JSON
        
        Args:
            resultado: Dicionário com os resultados
            arquivo: Nome do arquivo de saída
        """
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Resultados salvos em: {arquivo}")
        except Exception as e:
            print(f"\n❌ Erro ao salvar arquivo: {e}")


# ==============================
# Execução Principal
# ==============================

def main():
    """Função principal de execução"""
    
    # Parâmetros de busca
    parametros = {
        "geo": "BR",           # Brasil
        "hl": "pt-BR",         # Português brasileiro
        "hours": "24",         # Últimas 24 horas
        "category": "14",      # Categoria Política (14 = News & Politics)
    }
    
    # Escolha o provider (gemini, openai, llama, gemma)
    #PROVIDER = "gemini"  # Altere conforme necessário
    PROVIDER = "qwen"  # Altere conforme necessário
    
    try:
        # Criar e executar o crew
        trends_crew = TrendsAnalysisCrew(provider=PROVIDER)
        resultado = trends_crew.executar(parametros)
        
        # Exibir resultados
        print("\n" + "="*60)
        print("📊 RESULTADO DA ANÁLISE")
        print("="*60 + "\n")
        print(resultado["resultado"])
        
        # Salvar em arquivo
        trends_crew.salvar_resultado(resultado)
        
    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")
        raise


if __name__ == "__main__":
    main()