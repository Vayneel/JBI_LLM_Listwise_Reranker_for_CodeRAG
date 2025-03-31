from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

class Embedder:
    def __init__(self, model_name="microsoft/codebert-base"):
        self.__tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.__model = AutoModel.from_pretrained(model_name)
        self.__model.eval()


    def get_token_usage(self, text: str):
        return len(self.__tokenizer.tokenize(text))


    # def embed_text(self, text: str):
    #     self.__tokenizer.tokenize(text, return_tensors="pt", , max_length=512)