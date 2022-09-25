import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import plotly.graph_objects as go


st.set_page_config(page_title='Dashboard: O Terço Final no Futebol', page_icon=None, layout='wide',
                   initial_sidebar_state='auto', menu_items=None)

hide_streamlit_style = '''
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            '''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

df = pd.read_csv('finalizacoes.csv', index_col=0)

avg_goals = (len(df[df['Resultado'] == 'Gol']) / len(df)) * 100
attack_type_list = sorted(df['Tipo de Ataque'].unique())
shot_zones_list = df['Zona de Finalização'].unique()
body_parts_list = df['Parte do Corpo'].unique()
touches_list = df['Toques na Bola'].unique()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header('FILTROS')

    at_container = st.container()
    cols = st.columns(2)
    best_attack = cols[0].checkbox('Melhores Ataques', value=True)
    worst_attack = cols[1].checkbox('Piores Ataques', value=True)
    at_club_list = ['Adversário']
    if best_attack:
        at_club_list.append('Bayern')
        at_club_list.append('Liverpool')
        at_club_list.append('Man City')
    if worst_attack:
        at_club_list.append('Arminia')
        at_club_list.append('Genoa')
        at_club_list.append('Norwich')
    club_at = at_container.multiselect(
        'FINALIZAÇÕES FEITAS:', 
        df['Clube Atacante'].unique(), 
        at_club_list, 
        help='Finalizações feitas pelos 3 melhores e 3 piores ataques das 5 maiores ligas da Europa na temporada 2021/2022')

    df_container = st.container()
    cols = st.columns(2)
    best_defense = cols[0].checkbox('Melhores Defesas', value=True)
    worst_defense = cols[1].checkbox('Piores Defesas', value=True)
    df_club_list = ['Adversário']
    if best_defense:
        df_club_list.append('Man City')
        df_club_list.append('Liverpool')
        df_club_list.append('Sevilla')
    if worst_defense:
        df_club_list.append('Norwich')
        df_club_list.append('Greuther Furth')
        df_club_list.append('Bordeaux')
    club_df = df_container.multiselect(
        'FINALIZAÇÕES SOFRIDAS:', 
        df['Clube Defensor'].unique(), 
        df_club_list, 
        help='Finalizações sofridas pelas 3 melhores e 3 piores defesas das 5 maiores ligas da Europa na temporada 2021/2022')

    result_container = st.container()
    cols = st.columns(2)
    goal = cols[0].checkbox('Gol', value=True)
    non_goal = cols[1].checkbox('Não gol', value=True)
    results_list = []
    if goal:
        results_list.append('Gol')
    if non_goal:
        results_list.append('Certa')
        results_list.append('Trave')
        results_list.append('Fora')
        results_list.append('Bloqueada')
    result = result_container.multiselect(
        'RESULTADO:', ['Gol', 'Certa', 'Trave', 'Fora', 'Bloqueada'], results_list)

    type_of_attack = st.multiselect('TIPOS DE ATAQUE:', attack_type_list, attack_type_list)
    if type_of_attack == ['Contra Ataque'] and club_df == ['Adversário']:
        min_ca, max_ca = st.select_slider('JOGADORES NO TERÇO FINAL:',
                                          ['1', '2', '3', '4', '5', '6'], 
                                          value=('1', '6'), 
                                          help='Escolha entre 1 e 6 ou mais jogadores no terço final no momento da finalização')
        df = df[df['Jogadores no Terço Final'].between(int(min_ca), int(max_ca))]
    if type_of_attack == ['Contra Ataque'] and club_at == ['Adversário']:
        min_ca, max_ca = st.select_slider('JOGADORES RECOMPONDO AO TERÇO INICIAL:',
                                          ['1', '2', '3', '4', '5', '6'],
                                          value=('1', '6'),
                                          help='Escolha entre 1 e 6 ou mais defensores no terço inicial no momento da finalização')
        df = df[df['Jogadores Recompondo'].between(int(min_ca), int(max_ca))]
    shot_zone = st.multiselect(
        'ZONAS DE FINALIZAÇÃO:', shot_zones_list, shot_zones_list)
    if shot_zone == ['Zona vermelha'] and club_df == ['Adversário']:
        min_rz, max_rz = st.select_slider('ATACANTES NA ZONA VERMELHA:',
                                          ['1', '2', '3', '4', '5', '6'], 
                                          value=('1', '6'), 
                                          help='Escolha entre 1 e 6 ou mais jogadores na zona vermelha no momento da finalização')
        df = df[df['Jogadores na ZV'].between(int(min_rz), int(max_rz))]
    if shot_zone == ['Zona vermelha'] and club_at == ['Adversário']:
        min_rz, max_rz = st.select_slider('DEFENSORES NA ZONA VERMELHA:',
                                          ['1', '2', '3', '4', '5', '6'],
                                          value=('1', '6'),
                                          help='Escolha entre 1 e 6 ou mais defensores na zona vermelha no momento da finalização')
        df = df[df['Jogadores Protegendo ZV'].between(int(min_rz), int(max_rz))]

    actions = st.multiselect(
        'AÇÕES RELEVANTES:', 
        ['Cruzamento simples', 'Cruzamento profundidade', 'Cruzamento pé contrário', 'Passe funil', 'Inversão', 
        'Erro adversário', 'Rebote', 'Troca de passes', 'Lançamento', 'Pivô', 'Individual direto', 'Individual indireto', 
        'Passe profundidade']
    )
    and_or_or = st.radio('Selecionar finalizações que tenham:', ['Todas as ações', 'Qualquer das ações', 'Nenhuma das ações'])
    body_part = st.multiselect('PARTE DO CORPO:', body_parts_list, body_parts_list)
    touches = st.multiselect('TOQUES NA BOLA:', touches_list, touches_list)

# Applying filters to DataFrame
df = df[df['Clube Atacante'].isin(club_at) & 
        df['Clube Defensor'].isin(club_df) & 
        df['Tipo de Ataque'].isin(type_of_attack) &
        df['Zona de Finalização'].isin(shot_zone) &
        df['Resultado'].isin(result) &
        df['Parte do Corpo'].isin(body_part) &
        df['Toques na Bola'].isin(touches)]
if len(actions) > 0:
    df.dropna(subset='Ações Relevantes', inplace=True)
    if and_or_or == 'Todas as ações':
        df = df[df['Ações Relevantes'].apply(lambda x: all(action in x for action in actions))]
    elif and_or_or == 'Qualquer das ações':
        df = df[df['Ações Relevantes'].apply(lambda x: any(action in x for action in actions))]
    else:
        df = df[df['Ações Relevantes'].apply(lambda x: not any(action in x for action in actions))]

# --- DASHBOARD ---
if club_at == []:
    st.error('Selecione ao menos um clube finalizador')
elif club_df == []:
    st.error('Selecione ao menos um clube que sofreu as finalizações')
elif result == []:
    st.error('Selecione ao menos um resultado')
elif type_of_attack == []:
    st.error('Selecione ao menos um tipo de ataque')
elif shot_zone == []:
    st.error('Selecione ao menos uma zona de finalização')
elif body_part == []:
    st.error('Selecione ao menos uma parte do corpo')
elif touches == []:
    st.error('Selecione ao menos uma quantidade de toques na bola')
else:
    cols = st.columns(2)

    shots = len(df)
    goals = len(df[df['Resultado'] == 'Gol'])
    cols[0].metric(label='FINALIZAÇÕES', value=shots, help='Total de finalizações')
    if shots > 0:
        cols[0].metric(label='GOLS', value=goals, delta=str(round((((((goals / shots) * 100)) / avg_goals) - 1) * 100)) + '%', 
                help='Total de gols. Valor percentual mostra a comparação da eficiência dessa situação filtrada com a média geral de eficiência das finalizações')


    graph = cols[0].selectbox('Selecione um gráfico:', ['Resultado', 'Tipo de Ataque', 'Zona de Finalização', 'Ações Relevantes', 'Parte do Corpo', 'Toques na Bola'])
    fixed_range = cols[0].checkbox('Fixar eixo', value=True)

    # Graph configurations
    graph_height = 340
    plot_bg_color = '#0e1117'
    accent_color = '#3CCC3C'
    goal_color = '#ffffff'
    title_font_size = 14
    text_font_color = '#ffffff'
    text_font_size = 14
    margin = dict(l=0, r=0, b=0, t=0)


    # --- HISTOGRAMS ---
    def result_hist():
        fig = px.histogram(df, x='Resultado', text_auto=True, color='Resultado', color_discrete_map={
            'Gol': goal_color, 'Certa': accent_color, 'Trave': accent_color, 'Fora': accent_color, 'Bloqueada': accent_color})
        if fixed_range:
            fig.update_yaxes(visible=False, fixedrange=True, range=[0, 1257])
        else:
            fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_xaxes(title=None, fixedrange=True)
        fig.update_layout(margin=margin,
                        height=graph_height, 
                        plot_bgcolor=plot_bg_color,
                        xaxis={'categoryarray': ['Gol', 'Certa', 'Trave', 'Fora', 'Bloqueada']},
                        showlegend=False)
        fig.update_traces(textfont_color=text_font_color,
                        textfont_size=text_font_size,
                        textposition='outside',
                        hovertemplate=None,
                        hoverinfo='skip')
        return(fig)


    def attack_type_hist():
        fig = px.histogram(df, x='Tipo de Ataque', text_auto=True)
        if fixed_range:
            fig.update_yaxes(visible=False, fixedrange=True, range=[0, 1790])
        else:
            fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_xaxes(title=None, tickangle=0, fixedrange=True)
        fig.update_layout(margin=margin,
                        height=graph_height,
                        plot_bgcolor=plot_bg_color,
                        xaxis={'categoryarray': attack_type_list},
                        showlegend=False)
        fig.update_traces(textfont_color=text_font_color,
                        textfont_size=text_font_size,
                        textposition='outside',
                        marker_color=accent_color,
                        hovertemplate=None,
                        hoverinfo='skip')
        return(fig)


    def shot_zone_hist():
        fig = px.histogram(df,
                        x='Zona de Finalização',
                        color='Zona de Finalização',
                        color_discrete_map={
                            'Zona vermelha': '#ff4b4b', 'Zona amarela': '#CCCC00', 'Zona verde': accent_color},
                        text_auto=True)
        if fixed_range:
            fig.update_yaxes(visible=False, fixedrange=True, range=[0, 1834])
        else:
            fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_xaxes(title=None, fixedrange=True)
        fig.update_layout(margin=margin,
                        height=graph_height,
                        plot_bgcolor=plot_bg_color,
                        xaxis={'categoryarray': [
                            'Zona vermelha', 'Zona amarela', 'Zona verde']},
                        showlegend=False)
        fig.update_traces(textfont_color=text_font_color,
                        textfont_size=text_font_size,
                        textposition='outside',
                        hovertemplate=None,
                        hoverinfo='skip')
        return(fig)

    def actions_hist():
        actions_list = ['Troca de passes', 'Rebote', 'Pivô', 'Passe profundidade', 'Passe funil', 
                        'Lançamento', 'Inversão', 'Individual indireto', 'Individual direto', 
                        'Erro adversário', 'Cruzamento simples', 'Cruzamento profundidade', 'Cruzamento pé contrário']
        actions_count = [df['Ações Relevantes'].str.contains(x).sum() for x in actions_list]
        actions_df = pd.DataFrame(list(zip(actions_list, actions_count)), columns=['Ações', 'Total'])
        fig = px.bar(actions_df, x='Total', y='Ações', text_auto=True)
        if fixed_range:
            fig.update_xaxes(visible=False, fixedrange=True, range=[0, 1252])
        else:
            fig.update_xaxes(visible=False, fixedrange=True)
        fig.update_yaxes(title=None, fixedrange=True)
        fig.update_layout(margin=margin,
                          height=graph_height,
                          plot_bgcolor=plot_bg_color,
                          showlegend=False)
        fig.update_traces(textfont_color=text_font_color,
                          textfont_size=text_font_size,
                          textposition='outside',
                          marker_color=accent_color,
                          marker_line_width=0,
                          hovertemplate=None,
                          hoverinfo='skip')
        return(fig)

    def body_part_hist():
        fig = px.histogram(df, x='Parte do Corpo', text_auto=True)
        if fixed_range:
            fig.update_yaxes(visible=False, fixedrange=True, range=[0, 3710])
        else:
            fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_xaxes(title=None, fixedrange=True)
        fig.update_layout(margin=margin,
                        height=graph_height,
                        plot_bgcolor=plot_bg_color,
                        xaxis={'categoryarray': ['Pé', 'Cabeça', 'Outra']},
                        showlegend=False)
        fig.update_traces(textfont_color=text_font_color,
                        textfont_size=text_font_size,
                        textposition='outside',
                        marker_color=accent_color,
                        hovertemplate=None,
                        hoverinfo='skip')
        return(fig)


    def touches_hist():
        fig = px.histogram(df,
                        x='Toques na Bola',
                        text_auto=True)
        if fixed_range:
            fig.update_yaxes(visible=False, fixedrange=True, range=[0, 1632])
        else:
            fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_xaxes(title=None, fixedrange=True)
        fig.update_layout(margin=margin,
                        height=graph_height,
                        plot_bgcolor=plot_bg_color,
                        xaxis={'categoryarray': [
                            '1', '2', '3+']},
                        showlegend=False)
        fig.update_traces(textfont_color=text_font_color,
                        textfont_size=text_font_size,
                        textposition='outside',
                        marker_color=accent_color,
                        hovertemplate=None,
                        hoverinfo='skip')
        return(fig)


    if graph == 'Resultado':
        cols[0].plotly_chart(result_hist(), 
                            config={'displaylogo': False, 'modeBarButtonsToRemove': ['zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'resetScale']},  
                            use_container_width=True)
    elif graph == 'Tipo de Ataque':
        cols[0].plotly_chart(attack_type_hist(), 
                            config={'displaylogo': False, 'modeBarButtonsToRemove': ['zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'resetScale']}, 
                            use_container_width=True)
    elif graph == 'Zona de Finalização':
        cols[0].plotly_chart(shot_zone_hist(), 
                            config={'displaylogo': False, 'modeBarButtonsToRemove': ['zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'resetScale']}, 
                            use_container_width=True)
    elif graph == 'Ações Relevantes':
        cols[0].plotly_chart(actions_hist(),
                             config={'displaylogo': False, 'modeBarButtonsToRemove': [
                                 'zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'resetScale']},
                             use_container_width=True)
    elif graph == 'Parte do Corpo':
        cols[0].plotly_chart(body_part_hist(), 
                            config={'displaylogo': False, 'modeBarButtonsToRemove': ['zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'resetScale']}, 
                            use_container_width=True)
    elif graph == 'Toques na Bola':
        cols[0].plotly_chart(touches_hist(), 
                            config={'displaylogo': False, 'modeBarButtonsToRemove': ['zoom', 'pan', 'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'resetScale']}, 
                            use_container_width=True)

    field_image = Image.open('campo_vertical.png')
    goal_image = Image.open('gol.png')

    tabs = cols[1].tabs(['Finalizações', 'Assistências', 'Direção no Gol'])

    # Graph configurations
    map_height = 520
    goal_marker_size = 6
    non_goal_marker_size = 5
    field_dict = dict(source=field_image,
                    xref='x',
                    yref='y',
                    x=0.02,
                    y=0.99,
                    sizex=0.96,
                    sizey=0.98,
                    sizing='stretch',
                    opacity=0.2,
                    layer='above')

    # --- SHOT MAP ---
    shot_location = tabs[0].checkbox('Local')
    shot_heatmap = tabs[0].checkbox('Mapa de Calor')

    shot_fig = go.Figure()
    if shot_location:
        shot_fig.add_trace(go.Scatter(
            x=df.loc[df['Resultado'] == 'Bloqueada', 'Local da Finalização X'],
            y=df.loc[df['Resultado'] == 'Bloqueada', 'Local da Finalização Y'],
            mode='markers',
            marker_symbol='x-open',
            marker_color=accent_color,
            marker_size=non_goal_marker_size,
            legendrank=5,
            name='Bloqueada',
            customdata=df.loc[df['Resultado'] == 'Bloqueada', ['Clube Atacante', 
                                                            'Clube Defensor', 
                                                            'Tipo de Ataque', 
                                                            'Parte do Corpo', 
                                                            'Toques na Bola']],
            hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' + 
                        '<br>Tipo de Ataque: %{customdata[2]}' + 
                        '<br>Parte do Corpo: %{customdata[3]}' + 
                        '<br>Toques na Bola: %{customdata[4]}'))
        shot_fig.add_trace(go.Scatter(
            x=df.loc[df['Resultado'] == 'Fora', 'Local da Finalização X'],
            y=df.loc[df['Resultado'] == 'Fora', 'Local da Finalização Y'],
            mode='markers',
            marker_symbol='x-open',
            marker_color=accent_color,
            marker_size=non_goal_marker_size,
            legendrank=4,
            name='Fora',
            customdata=df.loc[df['Resultado'] == 'Fora', ['Clube Atacante',
                                                        'Clube Defensor',
                                                        'Tipo de Ataque',
                                                        'Parte do Corpo',
                                                        'Toques na Bola']],
            hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' +
                        '<br>Tipo de Ataque: %{customdata[2]}' +
                        '<br>Parte do Corpo: %{customdata[3]}' +
                        '<br>Toques na Bola: %{customdata[4]}'))
        shot_fig.add_trace(go.Scatter(
            x=df.loc[df['Resultado'] == 'Trave', 'Local da Finalização X'],
            y=df.loc[df['Resultado'] == 'Trave', 'Local da Finalização Y'],
            mode='markers',
            marker_symbol='x-open',
            marker_color=accent_color,
            marker_size=non_goal_marker_size,
            legendrank=3,
            name='Trave',
            customdata=df.loc[df['Resultado'] == 'Trave', ['Clube Atacante',
                                                        'Clube Defensor',
                                                        'Tipo de Ataque',
                                                        'Parte do Corpo',
                                                        'Toques na Bola']],
            hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' +
                        '<br>Tipo de Ataque: %{customdata[2]}' +
                        '<br>Parte do Corpo: %{customdata[3]}' +
                        '<br>Toques na Bola: %{customdata[4]}'))
        shot_fig.add_trace(go.Scatter(
            x=df.loc[df['Resultado'] == 'Certa', 'Local da Finalização X'],
            y=df.loc[df['Resultado'] == 'Certa', 'Local da Finalização Y'],
            mode='markers',
            marker_symbol='circle-open',
            marker_color=accent_color,
            marker_size=non_goal_marker_size,
            legendrank=2,
            name='Certa',
            customdata=df.loc[df['Resultado'] == 'Certa', ['Clube Atacante',
                                                        'Clube Defensor',
                                                        'Tipo de Ataque',
                                                        'Parte do Corpo',
                                                        'Toques na Bola']],
            hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' +
                        '<br>Tipo de Ataque: %{customdata[2]}' +
                        '<br>Parte do Corpo: %{customdata[3]}' +
                        '<br>Toques na Bola: %{customdata[4]}'))
        shot_fig.add_trace(go.Scatter(
            x=df.loc[df['Resultado'] == 'Gol', 'Local da Finalização X'], 
            y=df.loc[df['Resultado'] == 'Gol', 'Local da Finalização Y'],
            mode='markers',
            marker_symbol='circle',
            marker_color=goal_color,
            marker_size=goal_marker_size,
            legendrank=1,
            name='Gol',
            customdata=df.loc[df['Resultado'] == 'Gol', ['Clube Atacante',
                                                        'Clube Defensor',
                                                        'Tipo de Ataque',
                                                        'Parte do Corpo',
                                                        'Toques na Bola']],
            hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' +
                        '<br>Tipo de Ataque: %{customdata[2]}' +
                        '<br>Parte do Corpo: %{customdata[3]}' +
                        '<br>Toques na Bola: %{customdata[4]}'))
    if shot_heatmap:
        shot_fig.add_trace(go.Histogram2dContour(x=df['Local da Finalização X'],
                                                y=df['Local da Finalização Y'],
                                                ncontours=100,
                                                showscale=False,
                                                line={'width': 0},
                                                colorscale=[
                                                    [0, plot_bg_color], [1, accent_color]],
                                                hoverinfo='none'))
    shot_fig.update_xaxes(range=[0.044, 0.956],
                            visible=False, constrain='domain')
    shot_fig.update_yaxes(range=[0.051, 0.949], visible=False,
                            scaleanchor='x', scaleratio=1.54)
    shot_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                        height=map_height,
                        plot_bgcolor=plot_bg_color,
                        legend=dict(yanchor='middle', y=0.5, xanchor='right', x=1))
    shot_fig.add_layout_image(field_dict)

    tabs[0].plotly_chart(shot_fig, 
                         config={'displaylogo': False, 'modeBarButtonsToRemove': [
                             'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', ]},
                        use_container_width=True)

    # --- ASSIST MAP ---
    assist_location = tabs[1].checkbox('Local e Direção')
    assist_heatmap = tabs[1].checkbox('Mapa de Calor ')

    assist_fig = go.Figure()
    if assist_location:
        assist_df = df[['Local da Assistência X', 'Local da Assistência Y',
                        'Local da Finalização X', 'Local da Finalização Y', 
                        'Resultado']].dropna()
        for i in assist_df.index:
            assist_x = assist_df.at[i, 'Local da Assistência X']
            assist_y = assist_df.at[i, 'Local da Assistência Y']
            shot_x = assist_df.at[i, 'Local da Finalização X']
            shot_y = assist_df.at[i, 'Local da Finalização Y']
            if assist_df.at[i, 'Resultado'] == 'Gol':
                assist_fig.add_trace(go.Scatter(x=[assist_x, shot_x],
                                                y=[assist_y, shot_y],
                                                marker_color=goal_color, 
                                                hoverinfo='none',
                                                line={'width': 0.5},
                                                marker={'opacity': 0},
                                                showlegend=False))
            else:
                assist_fig.add_trace(go.Scatter(x=[assist_x, shot_x],
                                                y=[assist_y, shot_y],
                                                marker_color=accent_color,
                                                hoverinfo='none',
                                                line={'width': 0.5},
                                                marker={'opacity': 0},
                                                showlegend=False))
        assist_fig.add_trace(go.Scatter(x=assist_df.loc[assist_df['Resultado'] == 'Bloqueada', 'Local da Assistência X'],
                                        y=assist_df.loc[assist_df['Resultado'] == 'Bloqueada', 'Local da Assistência Y'],
                                        mode='markers',
                                        marker_color=accent_color,
                                        marker_symbol='x-open',
                                        marker_size=non_goal_marker_size,
                                        hoverinfo='none',
                                        name='Bloqueada',
                                        legendrank=5))
        assist_fig.add_trace(go.Scatter(x=assist_df.loc[assist_df['Resultado'] == 'Fora', 'Local da Assistência X'],
                                        y=assist_df.loc[assist_df['Resultado'] == 'Fora', 'Local da Assistência Y'],
                                        mode='markers',
                                        marker_color=accent_color,
                                        marker_symbol='x-open',
                                        marker_size=non_goal_marker_size,
                                        hoverinfo='none',
                                        name='Fora',
                                        legendrank=4))
        assist_fig.add_trace(go.Scatter(x=assist_df.loc[assist_df['Resultado'] == 'Trave', 'Local da Assistência X'],
                                        y=assist_df.loc[assist_df['Resultado'] == 'Trave', 'Local da Assistência Y'],
                                        mode='markers',
                                        marker_color=accent_color,
                                        marker_symbol='x-open',
                                        marker_size=non_goal_marker_size,
                                        hoverinfo='none',
                                        name='Trave',
                                        legendrank=3))
        assist_fig.add_trace(go.Scatter(x=assist_df.loc[assist_df['Resultado'] == 'Certa', 'Local da Assistência X'],
                                        y=assist_df.loc[assist_df['Resultado'] == 'Certa', 'Local da Assistência Y'],
                                        mode='markers',
                                        marker_color=accent_color,
                                        marker_symbol='circle-open',
                                        marker_size=non_goal_marker_size,
                                        hoverinfo='none',
                                        name='Certa',
                                        legendrank=2))
        assist_fig.add_trace(go.Scatter(x=assist_df.loc[assist_df['Resultado'] == 'Gol', 'Local da Assistência X'],
                                        y=assist_df.loc[assist_df['Resultado'] == 'Gol', 'Local da Assistência Y'],
                                        mode='markers',
                                        marker_color=goal_color,
                                        marker_symbol='circle',
                                        marker_size=goal_marker_size,
                                        hoverinfo='none',
                                        name='Gol',
                                        legendrank=1))

    if assist_heatmap:
        assist_fig.add_trace(go.Histogram2dContour(x=df['Local da Assistência X'],
                                                y=df['Local da Assistência Y'],
                                                ncontours=100, 
                                                showscale=False, 
                                                line={'width': 0}, 
                                                colorscale=[
                                                    [0, plot_bg_color], [1, accent_color]],
                                                hoverinfo='none'))
        
    assist_fig.update_xaxes(range=[0.044, 0.956], visible=False, constrain='domain')
    assist_fig.update_yaxes(range=[0.051, 0.949], visible=False,
                            scaleanchor='x', scaleratio=1.54)
    assist_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                            height=map_height,
                            plot_bgcolor=plot_bg_color,
                            legend=dict(yanchor='middle', y=0.5,
                                        xanchor='right', x=1),
                            legend_itemclick=False,
                            legend_itemdoubleclick=False)
    assist_fig.add_layout_image(field_dict)

    tabs[1].plotly_chart(assist_fig, config={'displaylogo': False, 'modeBarButtonsToRemove': [
                         'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', ]}, use_container_width=True)

    # --- DIRECTION MAP ---
    direction_location = tabs[2].checkbox('Direção')
    direction_heatmap = tabs[2].checkbox('Mapa de Calor  ')
    loc_container = tabs[2].container()
    tabs[2].image('campo_x.png', use_column_width='always')
    location_x = tabs[2].slider('Posição da Finalização no Eixo X', min_value=0.0,
                   max_value=1.0, value=(0.0, 1.0), step=0.05)
    df = df[df['Local da Finalização X'].between(location_x[0], location_x[1])]

    direction_fig = go.Figure()
    if direction_location:
        direction_fig.add_trace(go.Scatter(x=df.loc[df['Resultado'] == 'Certa', 'Direção da Finalização X'],
                                        y=df.loc[df['Resultado'] == 'Certa', 'Direção da Finalização Y'],
                                        mode='markers',
                                        marker_symbol='circle-open',
                                        marker_color=accent_color,
                                        marker_size=5,
                                        legendrank=2,
                                        name='Certa',
                                        customdata=df.loc[df['Resultado'] == 'Certa', ['Clube Atacante',
                                                                                        'Clube Defensor',
                                                                                        'Tipo de Ataque',
                                                                                        'Parte do Corpo',
                                                                                        'Toques na Bola']],
                                        hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' +
                                        '<br>Tipo de Ataque: %{customdata[2]}' +
                                        '<br>Parte do Corpo: %{customdata[3]}' +
                                        '<br>Toques na Bola: %{customdata[4]}'))
    if direction_location:
        direction_fig.add_trace(go.Scatter(x=df.loc[df['Resultado'] == 'Gol', 'Direção da Finalização X'],
                                        y=df.loc[df['Resultado'] == 'Gol', 'Direção da Finalização Y'], 
                                        mode='markers',
                                        marker_color=goal_color,
                                        marker_size=6,
                                        legendrank=1,
                                        name='Gol',
                                        customdata=df.loc[df['Resultado'] == 'Gol', ['Clube Atacante',
                                                                                        'Clube Defensor',
                                                                                        'Tipo de Ataque',
                                                                                        'Parte do Corpo',
                                                                                        'Toques na Bola']],
                                        hovertemplate='<b>%{customdata[0]} x %{customdata[1]}</b>' +
                                        '<br>Tipo de Ataque: %{customdata[2]}' +
                                        '<br>Parte do Corpo: %{customdata[3]}' +
                                        '<br>Toques na Bola: %{customdata[4]}'))
    if direction_heatmap:
        direction_fig.add_trace(go.Histogram2dContour(x=df['Direção da Finalização X'],
                                                    y=df['Direção da Finalização Y'], 
                                                    ncontours=80, 
                                                    showscale=False, 
                                                    line={'width': 0}, 
                                                    colorscale=[[0, plot_bg_color], [1, accent_color]],
                                                    nbinsx=5,
                                                    nbinsy=5,
                                                    hoverinfo='none'))
    direction_fig.update_xaxes(range=[0, 1], visible=False)
    direction_fig.update_yaxes(range=[0, 1], visible=False, scaleanchor='x', scaleratio=0.33, constrain='domain')
    direction_fig.update_layout(margin=dict(l=0, r=0, b=0, t=0),
                                height=250,
                                plot_bgcolor=plot_bg_color,
                                legend=dict(yanchor='bottom', y=0, xanchor='right', x=1))
    direction_fig.add_layout_image(dict(
                                    source=goal_image,
                                    xref='x',
                                    yref='y',
                                    x=0,
                                    y=1,
                                    sizex=1,
                                    sizey=1,
                                    sizing='stretch',
                                    opacity=0.2,
                                    layer='above'))

    loc_container.plotly_chart(direction_fig, 
                         config={'displaylogo': False, 'modeBarButtonsToRemove': [
                             'zoomIn', 'zoomOut', 'autoScale', 'select2d', 'lasso2d', 'zoom', 'pan', 'resetScale']},
                        use_container_width=True)
