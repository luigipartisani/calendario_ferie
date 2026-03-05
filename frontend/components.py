import streamlit as st
import pandas as pd
import calendar

def _format_hours(val):
    if val == 0:
        return ""
    hours = int(val)
    minutes = round((val - hours) * 60)
    return f"{hours}:{minutes:02d}"

def _build_combined(grid_ferie, grid_permessi):
    all_users = sorted(set(
        (grid_ferie.index.tolist() if not grid_ferie.empty else []) +
        (grid_permessi.index.tolist() if not grid_permessi.empty else [])
    ))
    all_days = sorted(set(
        (grid_ferie.columns.tolist() if not grid_ferie.empty else []) +
        (grid_permessi.columns.tolist() if not grid_permessi.empty else [])
    ))
    gf = grid_ferie.reindex(index=all_users, columns=all_days, fill_value=0.0) if not grid_ferie.empty else pd.DataFrame(0.0, index=all_users, columns=all_days)
    gp = grid_permessi.reindex(index=all_users, columns=all_days, fill_value=0.0) if not grid_permessi.empty else pd.DataFrame(0.0, index=all_users, columns=all_days)

    str_days = [str(d) for d in all_days]
    all_cols = str_days + ['Totale']
    display_df = pd.DataFrame('', index=all_users, columns=all_cols)
    style_df = pd.DataFrame('', index=all_users, columns=all_cols)

    for user in all_users:
        total_ferie = 0.0
        for day, sday in zip(all_days, str_days):
            fv = gf.at[user, day]
            pv = gp.at[user, day]
            parts = []
            if fv > 0:
                parts.append(_format_hours(fv))
            if pv > 0:
                parts.append(_format_hours(pv))
            display_df.at[user, sday] = "+".join(parts)
            total_ferie += fv
            if fv > 0 and pv > 0:
                style_df.at[user, sday] = 'background-color: #7B2D8B; color: white;'
            elif fv > 0:
                style_df.at[user, sday] = 'background-color: #0068C9; color: white;'
            elif pv > 0:
                style_df.at[user, sday] = 'background-color: #FF8C00; color: white;'
        display_df.at[user, 'Totale'] = _format_hours(total_ferie) if total_ferie > 0 else ''
        style_df.at[user, 'Totale'] = 'background-color: #3d3d3d; color: white; font-weight: bold;' if total_ferie > 0 else ''

    return display_df, style_df

def render_calendar_month(month_name, grid_ferie, grid_permessi, stats_df, show_legend=True):
    st.subheader(month_name)

    if grid_ferie.empty and grid_permessi.empty:
        return

    display_df, style_df = _build_combined(grid_ferie, grid_permessi)
    styled = display_df.style.apply(lambda _: style_df, axis=None)
    col_config = {col: st.column_config.TextColumn(col, width=40) for col in display_df.columns if col != 'Totale'}
    col_config['Totale'] = st.column_config.TextColumn('Totale', width=65)
    col_config["_index"] = st.column_config.TextColumn("", width=150)
    st.dataframe(styled, column_config=col_config, width='stretch')

    if show_legend:
        st.caption("🔵 Ferie/Permessi   🟠 Permessi Speciali   🟣 Entrambi")

def render_summary_grid(grids_ferie, grids_permessi, stats_ferie, stats_permessi, selected_users, month_names):
    month_abbr = [m[:3] for m in month_names]
    col_labels = month_abbr + ['Totale', 'Maturato', 'Residuo']

    numeric = pd.DataFrame(0.0, index=selected_users, columns=col_labels)

    for month_name, abbr in zip(month_names, month_abbr):
        gf = grids_ferie.get(month_name, pd.DataFrame())
        gp = grids_permessi.get(month_name, pd.DataFrame())
        for user in selected_users:
            val = 0.0
            if not gf.empty and user in gf.index:
                val += gf.loc[user].sum()
            numeric.at[user, abbr] = val

    numeric['Totale'] = numeric[month_abbr].sum(axis=1)

    for user in selected_users:
        accrued = 0.0
        if not stats_ferie.empty:
            row = stats_ferie[stats_ferie['user_name'] == user]
            if not row.empty:
                accrued += row.iloc[0]['accrued_hours']
        if not stats_permessi.empty:
            row = stats_permessi[stats_permessi['user_name'] == user]
            if not row.empty:
                accrued += row.iloc[0]['accrued_hours']
        numeric.at[user, 'Maturato'] = accrued
        numeric.at[user, 'Residuo'] = accrued - numeric.at[user, 'Totale']

    display_df = numeric.apply(lambda col: col.map(_format_hours))
    style_df = pd.DataFrame('', index=selected_users, columns=col_labels)
    for col in month_abbr:
        for user in selected_users:
            if numeric.at[user, col] > 0:
                style_df.at[user, col] = 'background-color: #0068C9; color: white;'
    for user in selected_users:
        style_df.at[user, 'Totale'] = 'background-color: #3d3d3d; color: white; font-weight: bold;'
        style_df.at[user, 'Maturato'] = 'background-color: #1a5276; color: white; font-weight: bold;'
        residuo = numeric.at[user, 'Residuo']
        style_df.at[user, 'Residuo'] = (
            'background-color: #1e8449; color: white; font-weight: bold;' if residuo > 0
            else 'background-color: #922b21; color: white; font-weight: bold;'
        )

    styled = display_df.style.apply(lambda _: style_df, axis=None)
    col_config = {col: st.column_config.TextColumn(col, width=50) for col in month_abbr}
    col_config['Totale'] = st.column_config.TextColumn('Totale', width=65)
    col_config['Maturato'] = st.column_config.TextColumn('Maturato', width=65)
    col_config['Residuo'] = st.column_config.TextColumn('Residuo', width=65)
    col_config['_index'] = st.column_config.TextColumn('', width=150)
    st.subheader("Riepilogo annuale")
    st.dataframe(styled, column_config=col_config, width='stretch')
