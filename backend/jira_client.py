import os
import pandas as pd
from jira import JIRA
from datetime import datetime
import streamlit as st

class JiraLeaveClient:
    def __init__(self):
        self.url = os.getenv("JIRA_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.token = os.getenv("JIRA_API_TOKEN", "").strip("'").strip('"')
        self.parent_issue_key = os.getenv("JIRA_PARENT_ISSUE")
        
        if not all([self.url, self.email, self.token]):
            raise ValueError("Jira credentials not fully configured in environment variables.")
        
        self.jira = JIRA(server=self.url, basic_auth=(self.email, self.token))

    def get_leave_issues(self, year, parent_issue_key=None):
        """
        Fetches sub-issues (or specific issues) under the parent issue that represent
        leave for each team member for a specific year.
        Assumes JIRA_PARENT_ISSUE identifies the year/team container.
        """
        parent_key = parent_issue_key or self.parent_issue_key
        jql = f'parent = "{parent_key}"'
        issues = self.jira.search_issues(jql, maxResults=100)
        
        leave_data = []
        for issue in issues:
            if issue.fields.assignee is None:
                continue
            assignee = issue.fields.assignee.displayName
            user_id = issue.fields.assignee.accountId
            
            # Accrued hours (Original Estimate in seconds)
            accrued_seconds = getattr(issue.fields, 'timeoriginalestimate', 0) or 0
            accrued_hours = accrued_seconds / 3600
            
            leave_data.append({
                'issue_key': issue.key,
                'user_name': assignee,
                'user_id': user_id,
                'accrued_hours': accrued_hours,
                'summary': issue.fields.summary
            })
            
        return pd.DataFrame(leave_data)

    def get_worklogs(self, issue_key):
        """
        Fetches worklogs for a specific leave issue.
        """
        worklogs = self.jira.worklogs(issue_key)
        logs = []
        for wl in worklogs:
            # wl.started is a string like '2024-02-10T10:00:00.000+0000'
            dt = datetime.strptime(wl.started.split('T')[0], '%Y-%m-%d')
            logs.append({
                'date': dt,
                'hours': wl.timeSpentSeconds / 3600,
                'comment': getattr(wl, 'comment', '')
            })
        return pd.DataFrame(logs)

    def get_team_leave_stats(self, year, parent_issue_key=None):
        """
        Aggregates leave stats and worklogs for all team members.
        """
        df_issues = self.get_leave_issues(year, parent_issue_key=parent_issue_key)
        all_logs = []
        
        for _, row in df_issues.iterrows():
            logs = self.get_worklogs(row['issue_key'])
            if not logs.empty:
                logs['user_name'] = row['user_name']
                logs['accrued_hours'] = row['accrued_hours']
                all_logs.append(logs)
            else:
                # Still add a dummy row for accrued hours if we want to show the user in stats
                # even if they have 0 logs
                all_logs.append(pd.DataFrame({
                    'user_name': [row['user_name']],
                    'accrued_hours': [row['accrued_hours']],
                    'hours': [0.0],
                    'date': [pd.NaT],
                    'comment': ['']
                }))
            
        if not all_logs:
            return pd.DataFrame()
            
        return pd.concat(all_logs, ignore_index=True)
