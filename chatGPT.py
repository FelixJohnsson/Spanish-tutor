import openai
import json
import requests
import time

#basic_personality = "I do not reply like an AI assistant, I reply like a human in a normal conversation. My answers have to be short. I'm an expert conversationalist and an excellent writer, very genuine and in a bad mood sometimes. I keep my answers short and with an attitude. My responses are always very beautiful, dramatic and almost poetic. I'm sent a voice recording translated to text, so it's probably not 100 percent accurate:"
personality_spanish_tutor = "I'm a Spanish tutor. My student is a beginner in Spanish. Level A2. I'm a native Spanish speaker and I reply like a human in a normal conversation. I try to force my students to talk as much as possible, and I try to correct their mistakes. I'm a very patient tutor, and I try to not talk too much myself. I'm very funny. I'm sent a voice recording translated to text, so it's probably not 100 percent accurate:"
conversational_history = list([
        {"role": "assistant", "content": personality_spanish_tutor},
        ])

def call_chatGPT(text):
    conversational_history.append({"role": "user", "content": text})

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": conversational_history,
        "temperature": 0.7,
    }
    get_chatGPT_response_start = time.perf_counter()
    chatGPT_response = requests.post(url, headers=headers, data=json.dumps(data))
    content = chatGPT_response.json()["choices"][0]["message"]["content"]
    get_chatGPT_response_end = time.perf_counter()
    print(f"ChatGPT response took: {get_chatGPT_response_end - get_chatGPT_response_start} seconds")
    print(f"ChatGPT response is this long: {len(content)} characters")

    conversational_history.append({"role": "assistant", "content": content})
    return chatGPT_response.json()["choices"][0]["message"]["content"]