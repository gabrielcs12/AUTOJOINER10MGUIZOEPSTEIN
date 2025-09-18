import requests
import time
import re

TOKEN = "MTM5OTIxOTY4ODM1NzIzNjgzNw.GZa-1X.6KtkRU8vQgFmRYUuGv1u4hWw6Qmgt8avxwJyIk"
CANAL_ID = "1412641270274326528"
WEBHOOK_URL = "https://dadarida-autojoin10.onrender.com/webhook"
API_KEY = "key123"

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0",
    "X-API-KEY": API_KEY,
}

last_message_id = None
print("⏳ Coletor iniciado...")

def extract_job_ids(text: str):
    """Procura todos os UUIDs no texto (formato xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)."""
    return re.findall(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text)

def extract_join_links(text: str):
    """Procura links do tipo join.html?placeId=...&jobId=..."""
    return re.findall(r"https?://[^\s]+join\.html\?placeId=\d+&jobId=[0-9a-fA-F\-]+", text)

def extract_fern_links(text: str):
    """Procura links do Fern Joiner (placeId + gameInstanceId)."""
    return re.findall(r"https?://fern\.wtf/joiner\?placeId=\d+&gameInstanceId=[0-9a-fA-F\-]+", text)

while True:
    url = f"https://discord.com/api/v10/channels/{CANAL_ID}/messages?limit=5"
    if last_message_id:
        url += f"&after={last_message_id}"

    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            messages = r.json()
            if not messages:
                print("ℹ️ Nenhuma mensagem nova encontrada")
            else:
                messages.reverse()
                for msg in messages:
                    content = msg.get("content", "")
                    job_ids = extract_job_ids(content)
                    join_links = extract_join_links(content)
                    fern_links = extract_fern_links(content)

                    payload = {
                        "content": content,
                        "job_ids": job_ids,        # sempre lista
                        "join_links": join_links,  # sempre lista
                        "fern_links": fern_links   # agora também coleta Fern
                    }

                    requests.post(WEBHOOK_URL, json=payload, headers={"X-API-KEY": API_KEY})
                    last_message_id = msg["id"]

                    if job_ids or join_links or fern_links:
                        print(f"✅ Enviado ao backend | IDs: {job_ids} | Links: {join_links} | Fern: {fern_links}")
                    else:
                        print(f"⚠️ Enviado sem JobId/Link: {content[:50]}...")
        else:
            print(f"❌ Erro ao buscar mensagens: {r.status_code} {r.text}")
    except Exception as e:
        print("Erro:", e)

    time.sleep(3)
