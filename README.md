# 🛸 Giammario AI Agent

Giammario AI Agent è un assistente virtuale intelligente basato su **Streamlit**, progettato per fornire informazioni dettagliate e professionali su **Giammario de Candia**, attingendo esclusivamente dal suo Curriculum Vitae.

L'obiettivo del progetto è offrire un'interfaccia interattiva e moderna (con tema ispirato ai droni notturni) dove recruiter e aziende possono porre domande specifiche sulle competenze, esperienze e progetti di Giammario.

## 🚀 Funzionalità

- **Risposte basate sul CV**: L'agente estrae il testo dal PDF del CV e lo utilizza come unica fonte di verità per rispondere alle domande.
- **Integrazione AI**: Utilizza la libreria `g4f` per interfacciarsi con vari modelli di linguaggio avanzati (come GPT-4o-mini) con un sistema di fallback automatico.
- **Interfaccia Streamlit**: Un'interfaccia web pulita, reattiva e personalizzata con stili CSS per un'esperienza utente fluida.

## 🛠️ Requisiti

- **Python 3.10** o superiore.
- Un file PDF del CV nominato `CV de Candia.pdf` nella root del progetto.

## 💻 Installazione e Avvio

Segui questi passaggi per eseguire il progetto in locale:

1. **Clona il repository**:
   ```bash
   git clone <url-del-repo>
   cd giammario-ai-agent
   ```

2. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Avvia l'applicazione**:
   ```bash
   streamlit run app.py
   ```

L'app sarà accessibile nel tuo browser all'indirizzo `http://localhost:8501`.

## 🌐 Deploy Online

Puoi pubblicare facilmente questa applicazione online utilizzando **Streamlit Community Cloud**:

1. Carica il codice su un repository **GitHub**.
2. Accedi a [share.streamlit.io](https://share.streamlit.io/).
3. Clicca su "New app" e seleziona il repository, il branch e il file `app.py`.
4. Clicca su **Deploy!**

L'app gestirà automaticamente l'installazione delle dipendenze tramite il file `requirements.txt`.

## 📂 Struttura del Progetto

- `app.py`: Il file principale che contiene la logica dell'interfaccia Streamlit, l'estrazione del testo dal PDF e l'integrazione con l'AI.
- `CV de Candia.pdf`: Il documento sorgente contenente le informazioni professionali.
- `requirements.txt`: Elenco delle librerie Python necessarie (Streamlit, g4f, pdfplumber, ecc.).

## ⚠️ Limiti Attuali

- **Fonte Unica**: L'agente risponde solo in base alle informazioni presenti nel file PDF fornito. Se un'informazione non è presente, l'agente dichiarerà di non averla disponibile.
- **Dipendenza da Provider Gratuiti**: Utilizzando `g4f`, la disponibilità dei modelli dipende dai provider gratuiti esterni, che potrebbero talvolta essere instabili o lenti.

## 🔮 Sviluppi Futuri

- [ ] **Integrazione API Ufficiali**: Supporto per OpenAI API o Anthropic per una maggiore stabilità.
- [ ] **Cronologia Chat**: Implementazione della memoria della conversazione per sessione.
- [ ] **Multi-documento**: Capacità di analizzare più file contemporaneamente (es. portfolio, certificazioni).
- [ ] **Miglioramento UI**: Aggiunta di elementi grafici avanzati legati al mondo dei droni e della tecnologia.

---
*Sviluppato con passione per presentare il profilo professionale di Giammario de Candia.*
