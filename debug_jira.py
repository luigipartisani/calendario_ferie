import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

def test_token(token_name):
    url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv(token_name, "").strip("'").strip('"')
    
    if not token:
        print(f"\n--- Testing {token_name}: No token found ---")
        return False

    print(f"\n--- Testing {token_name} ---")
    print(f"Connecting to {url} as {email}...")
    print(f"Token (first 5 chars): {token[:5]}...")
    
    try:
        jira = JIRA(server=url, basic_auth=(email, token))
        # Try to get own user info to verify auth
        user = jira.myself()
        print(f"Auth Success! Authenticated as: {user.get('displayName')} ({user.get('emailAddress')})")
        
        parent_key = os.getenv("JIRA_PARENT_ISSUE")
        print(f"Searching for parent issue: {parent_key}")
        try:
            parent = jira.issue(parent_key)
            print(f"Parent found: {parent.fields.summary}")
            return True
        except Exception as e:
            print(f"Error finding parent {parent_key}: {e}")
            return True # Auth worked, but issue might be inaccessible
            
    except Exception as e:
        print(f"Auth Failed: {e}")
        return False

def debug_parent(jira, parent_key):
    print(f"\n=== Parent issue: {parent_key} ===")
    try:
        parent = jira.issue(parent_key)
        print(f"Summary: {parent.fields.summary}")
    except Exception as e:
        print(f"ERROR fetching {parent_key}: {e}")
        return

    for jql in [f'parent = "{parent_key}"', f'issueFunction in subtasksOf("{parent_key}")']:
        print(f"\n--- JQL: {jql} ---")
        try:
            issues = jira.search_issues(jql, maxResults=100)
            print(f"Found {len(issues)} issues")
            for issue in issues:
                assignee = getattr(issue.fields.assignee, 'displayName', 'Unassigned')
                print(f"  {issue.key} - {issue.fields.summary} - Assignee: {assignee}")
                worklogs = jira.worklogs(issue.key)
                print(f"  Worklogs: {len(worklogs)}")
                for wl in worklogs[:3]:
                    print(f"    - {wl.started[:10]} | {wl.timeSpentSeconds/3600:.1f}h")
        except Exception as e:
            print(f"ERROR: {e}")

def debug_leave_data():
    load_dotenv()
    url = os.getenv("JIRA_URL")
    email = os.getenv("JIRA_EMAIL")
    token = os.getenv("JIRA_API_TOKEN", "").strip("'").strip('"')

    jira = JIRA(server=url, basic_auth=(email, token))

    debug_parent(jira, os.getenv("JIRA_PARENT_ISSUE"))
    debug_parent(jira, os.getenv("JIRA_SPECIAL_PERMITS_ISSUE"))

if __name__ == "__main__":
    t1 = test_token("JIRA_API_TOKEN")
    if not t1:
        test_token("JIRA_API_TOKEN_")
    else:
        debug_leave_data()
