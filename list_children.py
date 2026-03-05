import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

def list_children():
    url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN", "").strip("'").strip('"')
    parent_key = os.getenv("JIRA_PARENT_ISSUE")
    
    print(f"Connecting to {url}...")
    jira = JIRA(server=url, basic_auth=(email, token))
    
    jql = f'parent = "{parent_key}"'
    print(f"Executing JQL: {jql}")
    issues = jira.search_issues(jql)
    print(f"Found {len(issues)} issues.")
    
    for issue in issues:
        print(f"- {issue.key}: {issue.fields.summary}")
        # Check if it has worklogs
        wls = jira.worklogs(issue.key)
        print(f"  Worklogs found: {len(wls)}")

if __name__ == "__main__":
    list_children()
