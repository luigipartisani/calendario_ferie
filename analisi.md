# Calendario Ferie/Permessi

## Introduzione

Applicazione web per la visualizzazione centralizzata delle ferie e dei permessi del team di sviluppo software. I dati vengono recuperati in tempo reale tramite le API di Jira e presentati in formato calendario interattivo.

---

## Stack tecnologico

| Componente | Tecnologia |
|---|---|
| Linguaggio | Python 3.12 |
| UI | Streamlit |
| Dati | Jira REST API v2 (`jira` library) |
| Elaborazione | Pandas |
| Deploy | Docker / Docker Compose |
| Configurazione | python-dotenv |

---

## Struttura del progetto

```
calendario_ferie/
├── app.py                  # Entry point Streamlit
├── backend/
│   ├── jira_client.py      # Client Jira reale
│   ├── mock_jira.py        # Client mock per sviluppo
│   └── data_processor.py   # Elaborazione dati e griglia calendario
├── frontend/
│   └── components.py       # Componenti UI (tabelle, riepilogo)
├── .env                    # Credenziali e configurazione (non versionato)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

---

## Configurazione (.env)

```env
JIRA_URL=https://<istanza>.atlassian.net
JIRA_EMAIL=utente@dominio.it
JIRA_API_TOKEN=<token>
JIRA_USE_MOCK=false

# Per ogni anno, aggiungere le due variabili corrispondenti:
JIRA_PERMITS_ISSUE_2026=VAR-64
JIRA_SPECIAL_PERMITS_ISSUE_2026=VAR-76

JIRA_PERMITS_ISSUE_2027=VAR-XX
JIRA_SPECIAL_PERMITS_ISSUE_2027=VAR-YY
```

La combo "Seleziona anno" nell'interfaccia mostra automaticamente solo gli anni per cui è definita la variabile `JIRA_PERMITS_ISSUE_YYYY`.

---

## Struttura dati Jira

Esistono due tipologie di permessi, ciascuna con una issue padre per anno:

| Tipo | Variabile env | Descrizione |
|---|---|---|
| Ferie / Permessi | `JIRA_PERMITS_ISSUE_YYYY` | Issue padre dei permessi ordinari |
| Permessi Speciali | `JIRA_SPECIAL_PERMITS_ISSUE_YYYY` | Issue padre dei permessi speciali |

Ogni issue padre contiene subtask, uno per utente. Ogni subtask ha:
- **Original Estimate** → ore maturate dall'utente per l'anno
- **Worklog** → singole giornate/ore di assenza loggate dall'utente

I subtask non assegnati vengono ignorati.

---

## Funzionalità dell'applicazione

### Sidebar
- **Seleziona anno** — filtra per anno (solo anni configurati nel `.env`)
- **Mostra Permessi Speciali** — toggle per includere/escludere la seconda tipologia
- **Filtra utenti** — multiselect per visualizzare un sottoinsieme del team
- **Refresh dati** — invalida la cache e ricarica i dati da Jira

### Riepilogo annuale
Griglia in testa alla pagina con:
- **Righe**: utenti selezionati (ordine alfabetico)
- **Colonne mesi**: ore di ferie/permessi loggate per mese (esclusi permessi speciali)
- **Totale**: somma annuale delle ferie/permessi
- **Maturato**: ore stimate (original estimate del subtask)
- **Residuo**: Maturato − Totale (verde se positivo, rosso se ≤ 0)

### Vista "Mesi"
Tab con navigazione mensile. Per ogni mese: tabella utenti × giorni con:
- Celle colorate per tipo: 🔵 Ferie/Permessi, 🟠 Permessi Speciali, 🟣 Entrambi
- Valore in formato `h:mm` (celle vuote se nessuna ora loggata)
- Colonna **Totale** a destra (solo ferie, esclusi permessi speciali)

### Vista "Anno completo"
Stessa struttura della vista Mesi, ma tutti i mesi in sequenza verticale. La legenda dei colori è mostrata una sola volta in cima.

---

## Logica di caching

I dati Jira vengono cachati per 1 ora tramite `@st.cache_data(ttl=3600)`. La chiave di cache include anno, issue padre e issue permessi speciali, quindi il cambio di anno o di configurazione invalida automaticamente la cache. Il pulsante "Refresh dati" invalida la cache manualmente.

---

## Avvio con Docker

```bash
docker compose up --build
```

L'applicazione è disponibile su `http://localhost:8511`.

---

## Avvio in locale

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
streamlit run app.py
```
