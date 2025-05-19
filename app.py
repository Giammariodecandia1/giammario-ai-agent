import streamlit as st
from g4f.client import Client
import pdfplumber

# --- SETUP INTERFACCIA ---
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

# --- PREPARAZIONE PROMPT ---
prompt_base = f"""
Sei un assistente AI progettato per rispondere a domande su Giammario de Candia, basandoti esclusivamente sulle informazioni seguenti:

{cv_text}

Rispondi in modo chiaro, professionale e conciso, come se fossi l'addetto HR che lo presenta.
"""

# --- FALLBACK AI ENGINE ---
def chiedi_con_fallback(messages, modelli=["gpt-4o-mini", "claude-3-haiku", "mistral-7b"]):
    for modello in modelli:
        try:
            st.info(f"💡 Sto provando con: `{modello}`", icon="ℹ️")
            client = Client()
            risposta = client.chat.completions.create(
                model=modello,
                messages=messages
            ).choices[0].message.content.strip()
            if risposta:
                return risposta, modello
        except Exception as e:
            st.warning(f"⚠️ Fallito con `{modello}`: {e}")
            continue
    return None, None

# --- CHAT ---
query = st.text_input("📨 Scrivi la tua domanda su Giammario:")

if query:
    with st.spinner("Sto pensando..."):
        messages = [
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": query},
        ]
        risposta, modello_usato = chiedi_con_fallback(messages)

        if risposta:
            st.success(f"📌 Risposta dell'agente (modello: `{modello_usato}`):")
            st.markdown(
                f"<div style='background-color:#1f2937;padding:10px;border-radius:10px;'>{risposta}</div>",
                unsafe_allow_html=True
            )
        else:
            st.error("❌ Nessun modello ha risposto. Riprova più tardi.")

# --- FOOTER ---
st.markdown("""
    <hr style="margin-top: 40px;">
    <p style='text-align: center; font-size: 12px;'>Powered by g4f • Tema droni notturni • Codice sviluppato per Giammario</p>
""", unsafe_allow_html=True)
