# Calendario Ferie/Permessi

Applicazione web per la visualizzazione centralizzata delle ferie e dei permessi del team, basata su dati Jira.

## Avvio in locale

```bash
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
streamlit run app.py
```

## Avvio con Docker

```bash
docker compose up --build
```

L'applicazione è disponibile su `http://localhost:8511`.

## Configurazione (.env)

```env
JIRA_URL=https://<istanza>.atlassian.net
JIRA_EMAIL=utente@dominio.it
JIRA_API_TOKEN=<token>
JIRA_USE_MOCK=false

# Per ogni anno aggiungere le due variabili corrispondenti:
JIRA_PERMITS_ISSUE_2026=VAR-64
JIRA_SPECIAL_PERMITS_ISSUE_2026=VAR-76

# JIRA_PERMITS_ISSUE_2027=VAR-XX
# JIRA_SPECIAL_PERMITS_ISSUE_2027=VAR-YY
```

La combo "Anno" mostra automaticamente solo gli anni per cui è definita la variabile `JIRA_PERMITS_ISSUE_YYYY`.

## Filtro per progetto Jira

Passando il parametro `project_key` nell'URL, l'app filtra gli utenti in base ai membri del progetto Jira indicato e li preseleziona automaticamente:

```
http://localhost:8511/?project_key=ADI
```

## Modalità mock

Impostare `JIRA_USE_MOCK=true` nel `.env` per usare dati di test senza credenziali Jira reali.
