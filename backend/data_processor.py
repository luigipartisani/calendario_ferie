import pandas as pd
import calendar
from datetime import datetime

MESI_ITALIANI = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno',
                 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre']

class DataProcessor:
    @staticmethod
    def create_calendar_grid(year, df_logs):
        """
        Transforms worklogs into a structured grid for the calendar.
        Structure: List of monthly dataframes.
        Each monthly dataframe: Index=User, Columns=Day (1 to N)
        """
        if df_logs.empty:
            return {}

        monthly_grids = {}
        
        # Ensure dates are in datetime format
        df_logs['date'] = pd.to_datetime(df_logs['date'])
        
        # Filter by year if necessary
        df_year = df_logs[df_logs['date'].dt.year == year].copy()
        
        # Get list of all users to ensure consistency across months
        all_users = sorted(df_year['user_name'].unique())

        for month in range(1, 13):
            month_name = MESI_ITALIANI[month - 1]
            last_day = calendar.monthrange(year, month)[1]
            days = list(range(1, last_day + 1))
            
            # Create an empty grid for the month
            grid = pd.DataFrame(0.0, index=all_users, columns=days)
            
            # Filter logs for this month
            df_month = df_year[df_year['date'].dt.month == month]
            
            # Populate the grid
            for _, row in df_month.iterrows():
                grid.at[row['user_name'], row['date'].day] += row['hours']
                
            monthly_grids[month_name] = grid
            
        return monthly_grids

    @staticmethod
    def get_user_stats(df_logs):
        """
        Calculates total used vs accrued hours for each user.
        """
        if df_logs.empty:
            return pd.DataFrame()
            
        # Sum used hours per user
        used = df_logs.groupby('user_name')['hours'].sum().reset_index(name='used_hours')
        
        # Accrued hours are the same for all logs of a user, so we take the first
        accrued = df_logs.groupby('user_name')['accrued_hours'].first().reset_index(name='accrued_hours')
        
        stats = pd.merge(used, accrued, on='user_name')
        stats['remaining_hours'] = stats['accrued_hours'] - stats['used_hours']
        stats['status'] = stats.apply(
            lambda x: 'Exceeded' if x['used_hours'] > x['accrued_hours'] 
            else ('Limited' if x['used_hours'] == x['accrued_hours'] else 'OK'), 
            axis=1
        )
        return stats
