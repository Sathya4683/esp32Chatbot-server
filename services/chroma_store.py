import json
import chromadb

def query_chromadb(query_text):
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    collection = chroma_client.get_or_create_collection(name="personal_info")
    results = collection.query(
        query_texts=[query_text], 
        n_results=3  
    )
    return results

def save_chat_history(chat_history):
    with open("chat_history.json", "a", encoding="utf-8") as file:
        json.dump(chat_history, file, ensure_ascii=False, indent=4)
        file.write("\n")
