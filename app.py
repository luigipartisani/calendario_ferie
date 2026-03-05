import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

from backend.jira_client import JiraLeaveClient
from backend.mock_jira import MockJiraClient
from backend.data_processor import DataProcessor, MESI_ITALIANI
from frontend.components import render_calendar_month, render_summary_grid

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Calendario ferie/permessi",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
    <style>
        .block-container { padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
    </style>
""", unsafe_allow_html=True)

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
    # Check for credentials or mock mode
    use_mock = os.getenv("JIRA_USE_MOCK", "false").lower().strip("'").strip('"') == "true"
    if not os.getenv("JIRA_API_TOKEN") and not use_mock:
        st.warning("Jira API Token not found. Please check your `.env` file or set JIRA_USE_MOCK=true.")
        st.stop()

    st.sidebar.header("Configurazione")
    available_years = sorted(
        [int(k.split("_")[-1]) for k in os.environ if k.startswith("JIRA_PERMITS_ISSUE_") and k.split("_")[-1].isdigit()],
        reverse=True
    )
    if not available_years:
        st.warning("Nessuna variabile `JIRA_PERMITS_ISSUE_YYYY` trovata nel file `.env`.")
        st.stop()
    selected_year = st.sidebar.selectbox("Seleziona anno", available_years)
    st.title(f"📅 Calendario ferie/permessi {selected_year}")
    show_permessi = st.sidebar.toggle("Mostra `Permessi Speciali`", value=True)
    if st.sidebar.button("🔄 Refresh dati"):
        fetch_data.clear()

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
        if "selected_users" not in st.session_state:
            st.session_state["selected_users"] = all_users
        selected_users = sorted(st.sidebar.multiselect("Filtra utenti", all_users, key="selected_users"))

        month_names = MESI_ITALIANI

        render_summary_grid(grids_ferie, grids_permessi, stats_ferie, stats_permessi, selected_users, month_names)

        st.divider()
        tab_mesi, tab_anno = st.tabs(["Mesi", "Anno completo"])

        def render_month(month_name, show_legend=True):
            grid_f = grids_ferie.get(month_name, pd.DataFrame())
            grid_p = grids_permessi.get(month_name, pd.DataFrame())
            if not grid_f.empty:
                grid_f = grid_f.loc[grid_f.index.isin(selected_users)]
            if not grid_p.empty:
                grid_p = grid_p.loc[grid_p.index.isin(selected_users)]
            render_calendar_month(month_name, grid_f, grid_p, stats_ferie, show_legend=show_legend)

        with tab_mesi:
            month_tabs = st.tabs(month_names)
            for i, month_name in enumerate(month_names):
                with month_tabs[i]:
                    render_month(month_name)

        with tab_anno:
            st.caption("🔵 Ferie/Permessi   🟠 Permessi Speciali   🟣 Entrambi")
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
