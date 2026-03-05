# Holiday Calendar

A centralized calendar for team leave/vacation visualization using Streamlit and Jira API.

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.template` to `.env`
   - Fill in your Jira credentials:
     - `JIRA_URL`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
     - `JIRA_EMAIL`: Your Jira account email
     - `JIRA_API_TOKEN`: Your Jira API token

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Requirements
- Each team member has 12 rows (one for each month).
- Each row has columns for each day of the month.
- Grouping is by month.
- Coloring based on leave duration.
- Visual highlight for exceeding accrued hours.
