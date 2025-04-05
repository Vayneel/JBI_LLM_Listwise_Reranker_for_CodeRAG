from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class Embedder:
    __device: torch.device = "cuda" if torch.cuda.is_available() else "cpu"
    __debug: bool

    def __init__(self, model_name: str = "microsoft/codebert-base", debug: bool = False):
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.__model = AutoModel.from_pretrained(model_name).to(self.__device)
        self.__model.eval()
        self.__debug = debug


    def get_token_usage(self, text: str):
        return len(self.__tokenizer.tokenize(text))


    def embed_text(self, text: str):
        tokens = self.__tokenizer(text, return_tensors="pt", truncation=True, padding=True,
                                           max_length=512).to(self.__device)
        if self.__debug: print("embedding chunk: \n{\n", text, "\n}")
        with torch.no_grad():
            outputs = self.__model(**tokens)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embeddings.cpu().numpy()