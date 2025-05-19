import streamlit as st
from g4f.client import Client
from g4f import Provider
import pdfplumber
import time, json, os, datetime

# --- UI SETUP ---
st.set_page_config(page_title="Giammario AI", page_icon="🛸", layout="centered")
st.markdown("""
    <style>
    body {
        background-color: #0c0f13;
        color: #f2f2f2;
        font-family: 'Segoe UI', sans-serif;
    }
    .stTextInput>div>div>input {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #00bfff;'>🛸 Giammario Drone AI Assistant</h1>
    <p style='text-align: center;'>Chiedimi qualsiasi cosa sul profilo di Giammario de Candia!</p>
""", unsafe_allow_html=True)

# --- LETTURA CV ---
def estrai_testo_cv(path):
    try:
        with pdfplumber.open(path) as pdf:
            return "\n".join([page.extract_text() for page in pdf if page.extract_text()])
    except Exception as e:
        return f"⚠️ Errore nella lettura del CV: {e}"

cv_text = estrai_testo_cv("Cv de Candia .pdf")

# --- PROMPT BASE ---
prompt_base = f"""
Sei un assistente AI progettato per rispondere a domande su Giammario de Candia, basandoti esclusivamente sulle informazioni seguenti:

{cv_text}

Rispondi in modo chiaro, professionale e sintetico, come se fossi l'addetto HR che lo presenta. Non inventare nulla. Se la risposta non è presente nel CV, dì semplicemente 'Informazione non disponibile'.
"""

# --- FILTRO PROVIDER & MODELLI ---
def get_modelli_filtrati_da_provider():
    modelli_validi = set()
    provider_blacklist = ("aichatos", "deepseek", "yichat", "qwen", "chatglm", "spark", "baichuan", "yi", "zhipu")

    for name in dir(Provider):
        if name.startswith("_") or name.lower().startswith(provider_blacklist):
            continue
        provider = getattr(Provider, name)
        try:
            models = provider.get_models()
            validi = [
                m for m in models
                if isinstance(m, str)
                and m.strip()
                and m.isascii()
                and len(m) >= 6
            ]
            modelli_validi.update(validi)
        except:
            continue
    return sorted(modelli_validi)

# --- CACHE MODELLI ---
def aggiorna_modelli_cache():
    today = datetime.date.today().isoformat()
    cache_file = "modelli_cache.json"

    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            dati = json.load(f)
        if dati.get("data") == today:
            return dati["modelli"]

    modelli = get_modelli_filtrati_da_provider()
    with open(cache_file, "w") as f:
        json.dump({"data": today, "modelli": modelli}, f)
    return modelli

# --- FALLBACK SEQUENZA ---
def chiedi_con_fallback(messages, timeout_sec=30):
    priorita = ["gpt-4o-mini"]
    altri = [m for m in aggiorna_modelli_cache() if m not in priorita]
    modelli = priorita + altri

    for modello in modelli:
        try:
            st.info(f"💡 Sto provando con: `{modello}`", icon="ℹ️")
            client = Client()
            start = time.time()
            risposta = client.chat.completions.create(
                model=modello,
                messages=messages
            ).choices[0].message.content.strip()
            elapsed = time.time() - start
            if elapsed > timeout_sec:
                st.warning(f"⏱️ Timeout superato ({int(elapsed)}s), passo al prossimo modello...")
                continue
            if risposta:
                return risposta, modello
        except Exception as e:
            st.warning(f"⚠️ Fallito con `{modello}`: {e}")
            continue
    return None, None

# --- UI CHAT ---
query = st.text_input("📨 Scrivi la tua domanda su Giammario:")

if query:
    with st.spinner("Sto pensando..."):
        messages = [
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": f"Rispondi in meno di 300 parole. {query}"},
        ]
        risposta, modello_usato = chiedi_con_fallback(messages)

        if risposta:
            st.success(f"📌 Risposta dell'agente (modello: `{modello_usato or 'sconosciuto'}`):")
            st.markdown(
                f"<div style='background-color:#1f2937;padding:10px;border-radius:10px;'>{risposta}</div>",
                unsafe_allow_html=True
            )
        else:
            st.error("❌ Nessun modello ha risposto. Il sistema potrebbe essere sovraccarico o bloccato. Riprova più tardi.")

# --- FOOTER ---
st.markdown("""
    <hr style="margin-top: 40px;">
    <p style='text-align: center; font-size: 12px;'>Powered by g4f • Tema droni notturni • Codice sviluppato per Giammario</p>
""", unsafe_allow_html=True)
