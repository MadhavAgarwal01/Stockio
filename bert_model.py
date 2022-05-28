# import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from statistics import variance,mean
import time

def get_sentiment_score(text_list):
    start_time = time.time()

    tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
    model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

    variance_list = []
    sentiment_score_list = []
    for text in text_list:
        tokens = tokenizer.encode(text, return_tensors='pt')
        result = model(tokens)
        values = [val.item() for val in result.logits[0]]

        sentiment_score_list.append(round((int(torch.argmax(result.logits))+1)/5,2))
        variance_list.append(round(variance(values),2))
    
    avg_result = []
    avg_result.append(round(mean(sentiment_score_list),2))
    avg_result.append(round(mean(variance_list),2))

    print("--- %s seconds ---" % (time.time() - start_time))

    return avg_result


