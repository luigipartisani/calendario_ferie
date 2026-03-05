# introduzione
Questo documento contiene le istruzioni per la realizzazione di un calendario centralizzato per la visualizzazione delle ferie/permessi del team di sviluppo software.

# strumenti
- python
- venv
- streamlit
- jira api
- altri tool se necessari

# funzionalità
- visualizzazione del calendario annuale con tutti i membri del team
- ogni membro del team ha dodici righe, una per ogni mese
- ogni riga ha tante colonne, una per ogni giorno del mese
- il raggruppamento deve essere per mese, quindi mese#1 e tutti gli utenti, mese#2 e tutti gli utenti, ecc.
- i giorni di ferie/permessi colorano totalmente o parzialmente la cella a seconda della durata del periodo di ferie/permessi
- all'intrno della cella deve essere visibile il numero di ore di ferie/permessi relative a quel giorno
- ogni utente matura un numero di ore di ferie/permessi durante l'anno (diverso da utente a utente)
- è necessaro evidenziare se un utente ha raggiunto il numero massimo di ore di ferie/permessi
- è necessaro evidenziare se un utente ha superato il numero massimo di ore di ferie/permessi (in questo caso colorare la cella di rosso)
- devo poter selezionare gli utenti da visualizzare nel calendario
- devo poter selezionare l'anno da visualizzare nel calendario

# analisi
- i giorni di ferie/permessi sono presi da jira con le api
- per l'autenticazione si userà un token
- le ore di ferie/permessi corrispondono al work log inserito su una issue specifica associata all'utente stesso
- le issue di ciascun utente hanno come parent una issue madre che identifica il tipo di ferie/permessi relativi ad uno specifico anno
- le ore di ferie maturate da ciascun utente sono indicate nella issue specifica nel campo "original estimate"
- le ore di ferie/permessi usufruite da ciascun utente sono indicate nella issue specifica nel campo "time spent". Attenzione perchè questo valore potrebbe non essere aggiornato in tempo reale, quindi bisognerebbe fare una query apposita per recuperare il work log e sommare le ore.

# struttura del progetto
- crea un ambiente virtuale
- installa le dipendenze
- crea un file .env per le credenziali
- crea un file main.py per l'applicazione
- crea un file requirements.txt per le dipendenze
- crea un file .gitignore per ignorare i file non necessari
- crea un file README.md per le istruzioni
- separa in cartelle la logica di backend e frontend
