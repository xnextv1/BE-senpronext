from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

import os

from openai import OpenAI

model_path = os.path.expanduser("~/Public/senpro/BE-senpronext/emotion-classification")
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
model.eval()

label_names = ["sadness", "joy", "love", "anger", "fear", "surprise"]


def predict_emotion(text: str) -> str:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits).item()

    return label_names[predicted_class_id]

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_URL"),
)


def predict_response(texts: [str]) -> str:
    messages = [
        {"role" : "system", "content": "You are a mental health chatbot, please reply to the user with comfort without being too clinical, respond shortly unless explicitly needed. Respond with the users language"},
    ]
    for text in texts:
        messages.append({"role" : "user", "content": text})


    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stop=["```"],
    )

    return response.choices[0].message.content