# Local Inference on GPU
# Model page: https://huggingface.co/vzani/portuguese-fake-news-classifier-bertimbau-fake-br

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

model_name = (
    "vzani/portuguese-fake-news-classifier-bertimbau-fake-br"  
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

clf = pipeline("text-classification", model=model, tokenizer=tokenizer)  # type: ignore

def predict(text: str) -> tuple[bool, float]:
    result = clf(text)[0]
    
    true_false = True if result["label"] == "LABEL_1" else False  # noqa: SIM210
    return true_false, result["score"]


if __name__ == "__main__":
    text = "BOMBA! A Dilma vai taxar ainda mais os pobres!"
    print(predict(text))

