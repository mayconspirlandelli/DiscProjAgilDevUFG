"""
Classificador de Fake News em Português
==========================================

Este módulo implementa um classificador de notícias falsas usando o modelo BERTimbau
treinado no dataset Fake.Br. Pode ser usado como servidor MCP (Model Context Protocol).

Modelo: vzani/portuguese-fake-news-classifier-bertimbau-fake-br
Fonte: https://huggingface.co/vzani/portuguese-fake-news-classifier-bertimbau-fake-br
"""

from typing import Tuple, Optional
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FakeNewsClassifier:
    """
    Classificador de notícias falsas para textos em português.
    
    Utiliza o modelo BERTimbau fine-tuned no dataset Fake.Br para identificar
    se um texto é uma notícia falsa ou verdadeira.
    
    Attributes:
        model_name (str): Nome do modelo no HuggingFace Hub
        tokenizer: Tokenizador do modelo
        model: Modelo de classificação
        clf: Pipeline de classificação configurado
    """
    
    def __init__(self, model_name: str = "vzani/portuguese-fake-news-classifier-bertimbau-fake-br"):
        """
        Inicializa o classificador carregando o modelo e tokenizador.
        
        Args:
            model_name: Nome do modelo no HuggingFace Hub
        """
        self.model_name = model_name
        logger.info(f"Carregando modelo: {model_name}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.clf = pipeline(
                "text-classification", 
                model=self.model, 
                tokenizer=self.tokenizer,
                device=-1  # Usar GPU (device=0), ou -1 para CPU
            )
            logger.info("Modelo carregado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo: {e}")
            raise
    
    def predict(self, text: str, return_raw: bool = False) -> Tuple[bool, float]:
        """
        Classifica um texto como notícia falsa ou verdadeira.
        
        Este método pode ser invocado via MCP (Model Context Protocol) para 
        integração com sistemas externos.
        
        Args:
            text: Texto da notícia a ser classificada
            return_raw: Se True, retorna o resultado bruto do modelo
        
        Returns:
            Tupla contendo:
                - bool: True se é fake news (LABEL_1), False se é verdadeira (LABEL_0)
                - float: Score de confiança da predição (0.0 a 1.0)
        
        Raises:
            ValueError: Se o texto estiver vazio
            Exception: Se houver erro na inferência
        
        Examples:
            >>> classifier = FakeNewsClassifier()
            >>> is_fake, confidence = classifier.predict("BOMBA! Notícia sensacionalista!")
            >>> print(f"Fake: {is_fake}, Confiança: {confidence:.2%}")
            Fake: True, Confiança: 95.32%
        """
        if not text or not text.strip():
            raise ValueError("O texto não pode estar vazio")
        
        try:
            result = self.clf(text)[0]
            
            if return_raw:
                return result
            
            # LABEL_1 = Fake News, LABEL_0 = Notícia Verdadeira
            is_fake_news = result["label"] == "LABEL_1"
            confidence_score = result["score"]
            
            logger.info(
                f"Predição: {'FAKE' if is_fake_news else 'REAL'} "
                f"(confiança: {confidence_score:.2%})"
            )
            
            return is_fake_news, confidence_score
            
        except Exception as e:
            logger.error(f"Erro durante a predição: {e}")
            raise
    
    def predict_batch(self, texts: list[str]) -> list[Tuple[bool, float]]:
        """
        Classifica múltiplos textos em lote (mais eficiente).
        
        Args:
            texts: Lista de textos a serem classificados
        
        Returns:
            Lista de tuplas (is_fake, confidence) para cada texto
        """
        if not texts:
            return []
        
        try:
            results = self.clf(texts)
            return [
                (result["label"] == "LABEL_1", result["score"])
                for result in results
            ]
        except Exception as e:
            logger.error(f"Erro durante a predição em lote: {e}")
            raise


# Instância global para uso como servidor MCP
_classifier: Optional[FakeNewsClassifier] = None


def get_classifier() -> FakeNewsClassifier:
    """
    Retorna a instância singleton do classificador.
    Útil para implementação de servidor MCP.
    """
    global _classifier
    if _classifier is None:
        _classifier = FakeNewsClassifier()
    return _classifier


# Interface MCP simplificada
def predict(text: str) -> Tuple[bool, float]:
    """
    Interface simplificada para invocação via MCP.
    
    Args:
        text: Texto a ser classificado
    
    Returns:
        Tupla (is_fake_news, confidence_score)
    """
    classifier = get_classifier()
    return classifier.predict(text)


def main():
    """Função principal para teste do classificador."""
    classifier = FakeNewsClassifier()
    
    # Exemplos de teste
    test_cases = [
        "BOMBA! A Dilma vai taxar ainda mais os pobres!",
        "O Congresso Nacional aprovou hoje o projeto de lei orçamentária de 2024.",
        "URGENTE: Descoberto método secreto para emagrecer 20kg em uma semana!",
        "A taxa Selic foi mantida em 11,75% ao ano pelo Banco Central."
    ]
    
    print("\n" + "="*70)
    print("CLASSIFICADOR DE FAKE NEWS EM PORTUGUÊS")
    print("="*70 + "\n")
    
    for text in test_cases:
        is_fake, confidence = classifier.predict(text)
        status = "🚨 FAKE NEWS" if is_fake else "✅ NOTÍCIA REAL"
        
        print(f"{status} (Confiança: {confidence:.2%})")
        print(f"Texto: {text[:80]}{'...' if len(text) > 80 else ''}")
        print("-" * 70)


if __name__ == "__main__":
    main()