import streamlit as st
from g4f.client import Client
from g4f import Provider
import pdfplumber
import time, json, os, datetime

# --- CONFIGURAZIONE ---
CV_PATH = "CV de Candia.pdf"

# --- UI SETUP ---
st.set_page_config(page_title="Giammario AI Assistant", page_icon="💼", layout="wide")

# CSS personalizzato per migliorare l'estetica
st.markdown("""
    <style>
    .main {
        background-color: #0c0f13;
    }
    .stTextInput>div>div>input {
        color: white;
    }
    .stButton>button {
        width: 100%;
        text-align: left;
        border-radius: 5px;
        background-color: #1f2937;
        color: #f2f2f2;
        border: 1px solid #374151;
    }
    .stButton>button:hover {
        border-color: #00bfff;
        color: #00bfff;
    }
    .sidebar .sidebar-content {
        background-color: #111827;
    }
    </style>
""", unsafe_allow_html=True)

# --- LETTURA CV ---
@st.cache_data
def estrai_testo_cv(path):
    if not os.path.exists(path):
        return None, 0
    try:
        with pdfplumber.open(path) as pdf:
            testo = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
            return testo, len(testo)
    except Exception as e:
        return None, 0

cv_text, char_count = estrai_testo_cv(CV_PATH)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🛸 Sistema")
    st.markdown("---")

    # Sezione Info
    st.subheader("📊 Stato del Sistema")
    if char_count > 0:
        st.success(f"✅ CV caricato correttamente")
        st.info(f"📁 **File:** {CV_PATH}")
        st.write(f"📝 **Caratteri estratti:** {char_count}")
    else:
        st.error(f"❌ Errore nel caricamento del CV")
        if not os.path.exists(CV_PATH):
            st.warning(f"File '{CV_PATH}' non trovato.")
        else:
            st.warning("Impossibile estrarre testo dal file. Potrebbe essere un PDF basato su immagini.")

    st.markdown("---")
    st.subheader("💡 Domande Suggerite")

    domande_suggerite = [
        "Qual è il profilo professionale di Giammario?",
        "Che esperienza ha nella gestione di progetti?",
        "Che competenze ha nel settore droni?",
        "Che competenze ha in ambito AI e automazione?",
        "Per quali ruoli potrebbe essere adatto?"
    ]

    for domanda in domande_suggerite:
        if st.button(domanda):
            st.session_state.suggested_query = domanda

# --- HEADER PRINCIPALE ---
st.title("💼 Giammario de Candia - AI Professional Profile")
st.markdown("""
    Benvenuto nell'assistente AI dedicato al profilo professionale di **Giammario de Candia**.
    Questa applicazione utilizza l'intelligenza artificiale per analizzare il CV di Giammario e rispondere alle tue curiosità in modo preciso e professionale.

    *Nota: L'assistente risponde esclusivamente sulla base delle informazioni contenute nel documento ufficiale.*
""")

st.divider()

# --- LOGICA CHAT ---
if "suggested_query" not in st.session_state:
    st.session_state.suggested_query = ""

# Input utente
query = st.text_input("📨 Scrivi la tua domanda su Giammario:", value=st.session_state.suggested_query, placeholder="Esempio: Quali sono le sue competenze tecniche?")

# --- PROMPT BASE ---
prompt_base = f"""
Sei un assistente AI professionale specializzato nel presentare il profilo di Giammario de Candia a recruiter, aziende e potenziali collaboratori.
Il tuo obiettivo è rispondere alle domande basandoti ESCLUSIVAMENTE sulle informazioni contenute nel CV fornito di seguito.

### REGOLE DI COMPORTAMENTO:
1. **Fonte Unica**: Utilizza solo i dati presenti nel testo del CV. Non inventare esperienze, titoli, aziende, competenze o certificazioni.
2. **Onestà**: Se un'informazione non è presente nel CV, rispondi esattamente: "Informazione non disponibile nel CV."
3. **Professionalità**: Mantieni un tono professionale, strutturato e utile. Rispondi come se fossi un esperto HR che presenta il candidato.
4. **Lingua**: Rispondi sempre in italiano, a meno che l'utente non ti rivolga una domanda in un'altra lingua o ti chieda esplicitamente di tradurre.
5. **Adattabilità**: Adatta il focus della risposta in base al contesto della domanda (es. evidenzia aspetti di Project Management se richiesto, o competenze tecniche in ambito Droni/UAV, AI e Automazione se pertinente).
6. **Sintesi**: Sii conciso ma esaustivo. Usa elenchi puntati se aiuta la leggibilità.

### TESTO DEL CV:
{cv_text if cv_text else 'ATTENZIONE: Nessun dato estratto dal CV. Avvisa l\'utente.'}
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
            with st.status(f"💡 Sto interrogando il modello: `{modello}`...", expanded=False) as status:
                client = Client()
                start = time.time()
                risposta = client.chat.completions.create(
                    model=modello,
                    messages=messages
                ).choices[0].message.content.strip()
                elapsed = time.time() - start

                if elapsed > timeout_sec:
                    status.update(label=f"⏱️ Timeout con `{modello}`", state="error")
                    continue

                if risposta:
                    status.update(label=f"✅ Risposta generata con successo!", state="complete")
                    return risposta, modello
        except Exception as e:
            continue
    return None, None

# --- ESECUZIONE QUERY ---
if query:
    with st.spinner("Analisi in corso..."):
        messages = [
            {"role": "system", "content": prompt_base},
            {"role": "user", "content": f"Rispondi in modo professionale. {query}"},
        ]
        risposta, modello_usato = chiedi_con_fallback(messages)

        if risposta:
            st.markdown(f"### 📌 Risposta (Modello: `{modello_usato}`) ")
            st.markdown(
                f"<div style='background-color:#1f2937;padding:20px;border-radius:10px;border-left:5px solid #00bfff;'>{risposta}</div>",
                unsafe_allow_html=True
            )
        else:
            st.error("❌ Al momento non è stato possibile ottenere una risposta. Riprova tra poco.")

# --- FOOTER ---
st.markdown("""
    <br><br>
    <hr style="border: 0.5px solid #374151;">
    <p style='text-align: center; font-size: 12px; color: #9ca3af;'>
        Powered by G4F AI Engine • Sviluppato per Giammario de Candia • © 2024
    </p>
""", unsafe_allow_html=True)
