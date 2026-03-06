import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json
from dotenv import load_dotenv

from backend.jira_client import JiraLeaveClient
from backend.mock_jira import MockJiraClient
from backend.data_processor import DataProcessor, MESI_ITALIANI
from frontend.components import render_calendar_month, render_summary_grid
from backend.exporter import generate_xlsx


st.set_page_config(
    page_title="Calendario ferie/permessi",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
    <style>
        .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; max-width: 100%; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_email_to_name(emails_tuple):
    use_mock = os.getenv("JIRA_USE_MOCK", "false").lower().strip("'").strip('"') == "true"
    if not os.getenv("JIRA_API_TOKEN") or use_mock:
        client = MockJiraClient()
    else:
        client = JiraLeaveClient()
    return client.resolve_emails_to_names(list(emails_tuple))

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(year, parent_issue, special_parent):
    use_mock = os.getenv("JIRA_USE_MOCK", "false").lower().strip("'").strip('"') == "true"
    if not os.getenv("JIRA_API_TOKEN") or use_mock:
        client = MockJiraClient()
    else:
        client = JiraLeaveClient()
    df_ferie = client.get_team_leave_stats(year, parent_issue_key=parent_issue) if parent_issue else pd.DataFrame()
    df_permessi = client.get_team_leave_stats(year, parent_issue_key=special_parent) if special_parent else pd.DataFrame()
    return df_ferie, df_permessi

def main():
    load_dotenv(override=True)
    # Check for credentials or mock mode
    use_mock = os.getenv("JIRA_USE_MOCK", "false").lower().strip("'").strip('"') == "true"
    if not os.getenv("JIRA_API_TOKEN") and not use_mock:
        st.warning("Jira API Token not found. Please check your `.env` file or set JIRA_USE_MOCK=true.")
        st.stop()

    st.sidebar.header("Impostazioni")
    available_years = sorted(
        [int(k.split("_")[-1]) for k in os.environ if k.startswith("JIRA_PERMITS_ISSUE_") and k.split("_")[-1].isdigit()],
        reverse=True
    )
    if not available_years:
        st.warning("Nessuna variabile `JIRA_PERMITS_ISSUE_YYYY` trovata nel file `.env`.")
        st.stop()
    selected_year = st.sidebar.selectbox("Anno", available_years)
    st.title(f"📅 Calendario ferie/permessi {selected_year}")
    show_permessi = st.sidebar.toggle("Mostra 'Permessi speciali'", value=True)
    if st.sidebar.button("🔄 Ricarica"):
        fetch_data.clear()
        fetch_email_to_name.clear()
    st.sidebar.markdown("---")

    try:
        with st.spinner("Caricamento dati da Jira..."):
            parent_issue = os.getenv(f"JIRA_PERMITS_ISSUE_{selected_year}")
            special_parent = os.getenv(f"JIRA_SPECIAL_PERMITS_ISSUE_{selected_year}", os.getenv("JIRA_SPECIAL_PERMITS_ISSUE"))
            df_ferie, df_permessi = fetch_data(selected_year, parent_issue, special_parent)

        if df_ferie.empty and df_permessi.empty:
            st.info(f"Nessun dato trovato per il {selected_year}.")
            return

        processor = DataProcessor()
        grids_ferie = processor.create_calendar_grid(selected_year, df_ferie) if not df_ferie.empty else {}
        grids_permessi = processor.create_calendar_grid(selected_year, df_permessi) if (show_permessi and not df_permessi.empty) else {}
        stats_ferie = processor.get_user_stats(df_ferie) if not df_ferie.empty else pd.DataFrame()
        stats_permessi = processor.get_user_stats(df_permessi) if (show_permessi and not df_permessi.empty) else pd.DataFrame()

        # Filters
        all_users = sorted(set(
            (stats_ferie['user_name'].tolist() if not stats_ferie.empty else []) +
            (stats_permessi['user_name'].tolist() if not stats_permessi.empty else [])
        ))

        project_key = st.query_params.get("project_key")
        if project_key:
            team_config_raw = os.getenv("TEAM_PROJECT_KEY")
            if not team_config_raw:
                st.error(f"Variabile `TEAM_PROJECT_KEY` non configurata nel file `.env`.")
                st.stop()
            try:
                team_list = json.loads(team_config_raw)
                project_emails = next(
                    (entry["users"] for entry in team_list if entry["project_key"] == project_key),
                    None
                )
                if project_emails is None:
                    st.error(f"Progetto `{project_key}` non trovato in `TEAM_PROJECT_KEY`.")
                    st.stop()
                email_to_name = fetch_email_to_name(tuple(sorted(project_emails)))
                allowed = {email_to_name[e] for e in project_emails if e in email_to_name}
                all_users = [u for u in all_users if u in allowed]
            except json.JSONDecodeError:
                st.error("Formato non valido per la variabile `TEAM_PROJECT_KEY`. Verificare che sia un JSON corretto.")
                st.stop()

        if st.session_state.get("_project_key") != project_key:
            st.session_state["_project_key"] = project_key
            st.session_state.pop("selected_users", None)

        if "selected_users" not in st.session_state:
            st.session_state["selected_users"] = all_users if project_key else []
        selected_users = sorted(st.sidebar.multiselect("Utenti", all_users, key="selected_users", placeholder="Nessuno"))

        month_names = MESI_ITALIANI

        render_summary_grid(grids_ferie, grids_permessi, stats_ferie, stats_permessi, selected_users, month_names)

        if selected_users:
            xlsx_data = generate_xlsx(selected_year, grids_ferie, selected_users)
            st.sidebar.download_button(
                label="📥 Esporta xlsx",
                data=xlsx_data,
                file_name=f"ferie_{selected_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.divider()
        tab_mesi, tab_anno = st.tabs(["Mesi", "Anno completo"])

        def render_month(month_name, show_legend=True):
            grid_f = grids_ferie.get(month_name, pd.DataFrame())
            grid_p = grids_permessi.get(month_name, pd.DataFrame())
            if not grid_f.empty:
                grid_f = grid_f.loc[grid_f.index.isin(selected_users)]
            if not grid_p.empty:
                grid_p = grid_p.loc[grid_p.index.isin(selected_users)]
            render_calendar_month(month_name, grid_f, grid_p, stats_ferie, year=selected_year, show_legend=show_legend)

        with tab_mesi:
            st.caption("🔵 Ferie/Permessi   🟠 Permessi Speciali   🟣 Entrambi   🔴 Sabato/Domenica/Festivo")
            month_tabs = st.tabs(month_names)
            for i, month_name in enumerate(month_names):
                with month_tabs[i]:
                    render_month(month_name, show_legend=False)

        with tab_anno:
            st.caption("🔵 Ferie/Permessi   🟠 Permessi Speciali   🟣 Entrambi   🔴 Sabato/Domenica/Festivo")
            for month_name in month_names:
                render_month(month_name, show_legend=False)

    except Exception as e:
        err = str(e)
        if "401" in err:
            st.error("⛔ Autenticazione Jira fallita (HTTP 401): il token API non è valido o è scaduto. Aggiorna `JIRA_API_TOKEN` nel file `.env`.")
        elif "403" in err:
            st.error("⛔ Accesso negato (HTTP 403): l'utente non ha i permessi necessari per accedere a questa risorsa Jira.")
        elif "404" in err:
            st.error(f"⛔ Issue non trovata (HTTP 404): verifica che `JIRA_PARENT_ISSUE` ({os.getenv('JIRA_PARENT_ISSUE')}) esista e sia accessibile.")
        else:
            st.error(f"Si è verificato un errore: {e}")
            st.exception(e)

if __name__ == "__main__":
    main()
