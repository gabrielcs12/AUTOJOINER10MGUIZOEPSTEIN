import requests
import time
import re

TOKEN = "MTM5OTIxOTY4ODM1NzIzNjgzNw.GcEQAg.x_waQe5z8W1x5scSnUycI6-cXBmxLkBt715B98"
CANAL_ID = "1412641270274326528"
WEBHOOK_URL = "https://autojojn1-10guizo.onrender.com/webhook"
API_KEY = "key123"
PLACE_ID = "109983668079237"

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0",
    "X-API-KEY": API_KEY,
}

last_message_id = None
print("⏳ Coletor iniciado...")

def extract_job_ids(text: str):
    """Procura todos os UUIDs no texto (Server ID)."""
    return re.findall(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", text)

def extract_join_links(text: str):
    """Procura links já prontos do tipo join.html?placeId=...&jobId=..."""
    return re.findall(r"https?://[^\s]+join\.html\?placeId=\d+&jobId=[0-9a-fA-F\-]+", text)

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

                    # extrair job ids e links já prontos
                    job_ids = extract_job_ids(content)
                    join_links = extract_join_links(content)

                    # se houver Job ID mas não houver link, montar o joinlink
                    if job_ids and not join_links:
                        for job_id in job_ids:
                            join_links.append(
                                f"https://nameless-289z.onrender.com/join.html?placeId={PLACE_ID}&jobId={job_id}"
                            )

                    payload = {
                        "content": content,
                        "job_ids": job_ids,
                        "join_links": join_links
                    }

                    requests.post(WEBHOOK_URL, json=payload, headers={"X-API-KEY": API_KEY})
                    last_message_id = msg["id"]

                    if job_ids or join_links:
                        print(f"✅ Enviado ao backend | IDs: {job_ids} | Links: {join_links}")
                    else:
                        print(f"⚠️ Enviado sem JobId/Link: {content[:50]}...")
        else:
            print(f"❌ Erro ao buscar mensagens: {r.status_code} {r.text}")
    except Exception as e:
        print("Erro:", e)

    time.sleep(3)
