import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MockJiraClient:
    def __init__(self):
        self.users = ["Mario Rossi", "Luigi Bianchi", "Anna Verdi", "Giulia Neri"]
        
    def get_leave_issues(self, year):
        data = []
        for i, user in enumerate(self.users):
            # Accrued hours: 160, 180, 200, 150
            accrued = [160, 180, 200, 150][i]
            data.append({
                'issue_key': f'LEAVE-{i}',
                'user_name': user,
                'user_id': f'acc-{i}',
                'accrued_hours': accrued,
                'summary': f'Leave for {user} - {year}'
            })
        return pd.DataFrame(data)

    def get_worklogs(self, issue_key, year=2024):
        # Generate some random worklogs
        logs = []
        start_date = datetime(year, 1, 1)
        for _ in range(20):
            days_offset = np.random.randint(0, 365)
            date = start_date + timedelta(days=days_offset)
            hours = np.random.choice([4.0, 8.0])
            logs.append({
                'date': date,
                'hours': hours,
                'comment': 'Vacation'
            })
        return pd.DataFrame(logs)

    def get_team_leave_stats(self, year, parent_issue_key=None):
        df_issues = self.get_leave_issues(year)
        all_logs = []

        for _, row in df_issues.iterrows():
            logs = self.get_worklogs(row['issue_key'], year=year)
            logs['user_name'] = row['user_name']
            logs['accrued_hours'] = row['accrued_hours']
            all_logs.append(logs)
            
        return pd.concat(all_logs, ignore_index=True)
