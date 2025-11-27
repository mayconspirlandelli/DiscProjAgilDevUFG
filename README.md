# DiscProjAgilDevUFG
Projeto Ágil da Disciplina de Pós UFG Agentes Inteligentes

Agente para monitorar palavras trends e analisar desinformaçao em posts de redes socias.


# Instalaçao de pacotes
# Adiciona Crewai no projeto
uv add crewai 

# Instalar tools 
pip install 'crewai[tools]' ou uv add crewai-tools

# Instalar Ollama 
curl -fsSL https://ollama.com/install.sh | sh

#Rodar o serviço
ollama serve &

# Download do modelo
ollama pull gemma3:270m


#Rodar o exmplo do crewai
sudo uv run agents-crew/scrapeWeb.py


#Instala modelo Small 
pip install litellm

# Para instalar o Modelo do Hugginface 
pip install -U transformers

#Para usar Browser-Use
uv add browser-use
uv sync

# Install Chromium browser: 
uvx browser-use install