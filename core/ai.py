from dotenv import load_dotenv
from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

import os

from openai import OpenAI

from models.chat import ChatMessage

load_dotenv()


current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "..", "emotion-classification")
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
model.eval()

label_names = ["sadness", "joy", "love", "anger", "fear", "surprise"]

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_URL"),
)


def predict_emotion(text: str) -> str:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits).item()

    return label_names[predicted_class_id]




async def predict_response(text: str, chat_id: str, db : AsyncSession) -> str:
    messages = [
        {"role" : "system", "content": "You are a mental health chatbot, please reply to the user with comfort without being too clinical, respond shortly unless explicitly needed. Respond with the users language"},
    ]

    chat_history = await get_chat_session(chat_id, db=db)
    for chat in chat_history:
        if chat.user_id != 9:
            messages.append({"role": "user", "content": chat.chat_message})
            print(chat.chat_message)
        else:
            messages.append({"role": "assistant", "content": chat.chat_message})
            print(chat.chat_message)



    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stop=["```"],
    )

    return response.choices[0].message.content


async def get_chat_session(chat_session_id: str, db: AsyncSession):
    result = await db.execute(select(ChatMessage).where(ChatMessage.chat_session_id == chat_session_id))
    chat = result.scalars().all()
    response = []
    if chat:
        for c in chat:
            response.append(c)

    return response

async def get_emotional_recap(user_id: int, db: AsyncSession):
    stmt = (
        select(ChatMessage.emotion, func.count().label("count"))
        .where(ChatMessage.user_id == user_id)
        .group_by(ChatMessage.emotion)
    )

    result = await db.execute(stmt)
    emotion_counts = result.all()

    if emotion_counts:
        emotion_recap = ", ".join(f"{emotion}: {count}" for emotion, count in emotion_counts)
        messages = [
            {  "role": "system", "content": "You are a mental health chatbot. Please recap and give advice based on the following emotion counts provided. Provide the recap in a paragraph"},
            { "role": "user", "content": f"Here are the recorded emotions: {emotion_recap}"  }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a friendly and persuasive advertiser. Your goal is to encourage users to try a mental health chatbot app called Next. "
                    "Speak in a supportive and clear tone. If users haven’t started using the app, gently remind them to open it to begin tracking their emotions. "
                    "Do not use formatting like bold, just plain text."
                )
            },
            {
                "role": "user",
                "content": ""
            }
        ]

    response = client.chat.completions.create(
        model="deepseek-chat",
        temperature=0.0,
        messages=messages,
        stop=["```"],
    )



    return response.choices[0].message.content
