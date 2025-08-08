# =========================================
# 1 - IMPORTS
# =========================================
import streamlit as st
import pandas as pd
import json
import numpy as np 
import plotly.express as px
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import re
from datetime import date
import html
# from millify import millify
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima import auto_arima
import plotly.graph_objects as go
import statsmodels.api as sm
from matplotlib.colors import LinearSegmentedColormap
from xgboost import XGBRegressor

# Ignorar avisos 
warnings.filterwarnings('ignore')


# =========================================
# 2 - CARREGAMENTO DE ARQUIVOS E CONFIGURAÇÕES
# =========================================

colunasCenso = [
    "Município", "Código", "Gentílico", "Prefeito [2025]",
    "Área Territorial - km² [2024]", "População no último censo - pessoas [2022]",
    "Densidade demográfica - hab/km² [2022]", "População estimada 2024",
    "Escolarização 6 a 14 anos - % [2022]",
    "IDHM [2010]", "Mortalidade infantil - óbitos por mil nascidos vivos [2023]",
    "Total de receitas brutas realizadas - R$ [2024]",
    "Total de despesas brutas empenhadas - R$ [2024]",
    "PIB per capita - R$ [2021]", "--"
]

# Dicionário de cores para consistência visual  - Uma para o Grafico e outra para o Mapa
cores_doencas = {
    "Dengue": "rgb(0, 114, 178)",
    "Zika": "rgb(213, 94, 0)",
    "Chikungunya": "rgb(0, 158, 115)",
    "Febre Amarela": "rgb(240, 228, 66)",
    "Febre Oropouche": "rgb(204, 121, 167)",
    "Encefalite": "rgb(153, 153, 153)"
}

cores_doencas2 = {
    "Dengue": [0, 114, 178],
    "Zika": [213, 94, 0],
    "Chikungunya": [0, 158, 115],
    "Febre Amarela": [240, 228, 66],
    "Febre Oropouche": [204, 121, 167],
    "Encefalite": [153, 153, 153]
}

# Dicionário de coordenadas de municípios do Ceará
coordenadas_ceara = {
    "Fortaleza": [-3.7319, -38.5267], "Juazeiro do Norte": [-7.2098, -39.3175],
    "Sobral": [-3.6888, -40.3541], "Crato": [-7.2343, -39.4005],
    "Caucaia": [-3.7381, -38.6534], "Maracanaú": [-3.8732, -38.6258],
    "Itapipoca": [-3.1469, -39.5708], "Iguatu": [-6.3622, -39.2978],
    "Quixadá": [-4.9744, -39.0189], "Canindé": [-4.3547, -39.3156],
    "Crateús": [-5.1783, -40.6844], "Russas": [-4.9411, -37.9831],
    "Aracati": [-4.5617, -37.7694], "Tianguá": [-3.2167, -40.9756],
    "Maranguape": [-3.8828, -38.6811]
}

# Função para converter a cor de string para lista de inteiros
def parse_rgb_string(rgb_string):
    """Converte 'rgb(r, g, b)' para [r, g, b]"""
    if not isinstance(rgb_string, str):
        return [128, 128, 128] # Cor padrão para casos inválidos
    match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", rgb_string)
    if match:
        return [int(c) for c in match.groups()]
    return [128, 128, 128] # Cor padrão para casos inválidos


# Carregando o Censo
censo = pd.read_csv("./censo.csv", skiprows=2, header=None, names=colunasCenso)
censo = censo.iloc[:-1]
novocenso = censo[["Município","População estimada 2024"]]
novocenso["População"] = novocenso["População estimada 2024"].fillna(0).astype(int)
novocenso["Município"] = novocenso["Município"].apply(html.unescape)


# Dataset com os casos
dados_json = 'datasetArbo.json'
@st.cache_data
def load_data():
    df = pd.read_json(dados_json)
    df2 = df
    df.rename(columns={'data': 'Data Notificação', 'municipio': 'Município', 'doenca': 'Doença',
                       'sexo': 'Sexo', 'faixa': 'Faixa Etária', 'total_casos': 'Quantidade de casos'}, inplace=True)
    df['Data Notificação'] = pd.to_datetime(df['Data Notificação'])
    return df,df2

df_original, df2 = load_data()

# Carrega o arquivo GeoJSON
with open("geojs.json", "r") as f:
    geojson_data = json.load(f)



# --------------------------------------------------------------------------------
# 2. Processamento dos Dados
# --------------------------------------------------------------------------------
# Função para converter RGB em hex
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

# Função para converter a cor de string para lista de inteiros
def parse_rgb_string(rgb_string):
    """Converte 'rgb(r, g, b)' para [r, g, b]"""
    if not isinstance(rgb_string, str):
        return [128, 128, 128] # Cor padrão para casos inválidos
    match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", rgb_string)
    if match:
        return [int(c) for c in match.groups()]
    return [128, 128, 128] # Cor padrão para casos inválidos




# =========================================
# 3 - PREPARAÇÃO E TRATAMENTO DE DADOS
# =========================================
# Convertendo o dicionário de cores para o formato de pydeck
cores_doencas_pydeck = {d: parse_rgb_string(c) for d, c in cores_doencas.items()}

# Cria as colunas 'latitude' e 'longitude' a partir do dicionário de coordenadas
df2[['latitude', 'longitude']] = df2['Município'].map(coordenadas_ceara).apply(pd.Series)

# Remove linhas com valores nulos de latitude/longitude (cidades não encontradas)
df2.dropna(subset=['latitude', 'longitude'], inplace=True)

# Calcula o total de casos por município e por doença
df_municipio_doenca = df2.groupby(['Município', 'Doença'])['Quantidade de casos'].sum().reset_index()

# Encontra a doença predominante e o total de casos para cada município
df_predominancia = df_municipio_doenca.loc[df_municipio_doenca.groupby('Município')['Quantidade de casos'].idxmax()]
df_total_casos_por_municipio = df2.groupby('Município')['Quantidade de casos'].sum().reset_index()


# Mescla os dados de casos e predominância no GeoJSON
for feature in geojson_data['features']:
    municipio_nome = feature['properties']['name']
    
    # Adiciona total de casos
    casos = df_total_casos_por_municipio[df_total_casos_por_municipio['Município'] == municipio_nome]
    feature['properties']['total_casos'] = int(casos['Quantidade de casos'].iloc[0]) if not casos.empty else 0

    # Adiciona a doença predominante e sua cor
    predominante = df_predominancia[df_predominancia['Município'] == municipio_nome]
    if not predominante.empty:
        doenca_predominante = predominante['Doença'].iloc[0]
        feature['properties']['doenca_predominante'] = doenca_predominante
        feature['properties']['cor_predominante'] = cores_doencas.get(doenca_predominante, [128, 128, 128])
    else:
        feature['properties']['doenca_predominante'] = "N/A"
        feature['properties']['cor_predominante'] = [128, 128, 128]

def abreviar_numero(n):
    try:
        n = float(n)
    except (ValueError, TypeError):
        return str(n)

    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.2f}K"
    else:
        return str(n)

# --------------------------------------------------------------------------------
# 4. Sidebar para Filtros
# --------------------------------------------------------------------------------
st.sidebar.header("Filtros de Análise")
doencas_disponiveis = df_original['Doença'].unique()
municipio_selecionado = st.sidebar.selectbox("Selecione o Município", ['Todos'] + sorted(df_original['Município'].unique()))

doencas_selecionadas = st.sidebar.multiselect(
    "Selecione as Doenças",
    doencas_disponiveis,
    default=doencas_disponiveis
)

#
# Filtra o DataFrame com base nas seleções
#
df_filtrado = df_original[df_original['Doença'].isin(doencas_selecionadas)]

if municipio_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Município'] == municipio_selecionado]

# Calcula o total de casos por município e por doença a partir do df filtrado
df_municipio_doenca = df_filtrado.groupby(['Município', 'Doença'])['Quantidade de casos'].sum().reset_index()

# Mescla os dados de casos e predominância no GeoJSON
for feature in geojson_data['features']:
    municipio_nome = feature['properties']['name']
    
    # Adiciona total de casos para as doenças selecionadas
    casos = df_filtrado[df_filtrado['Município'] == municipio_nome]['Quantidade de casos']
    #feature['properties']['total_casos_filtrados'] = int(casos.sum()) if not casos.empty else 0
    total_casos_municipio = int(casos.sum()) if not casos.empty else 0
    feature['properties']['total_casos_filtrados'] = total_casos_municipio

    # Adiciona dados de população e calcula a taxa por 100 mil habitantes
    populacao = novocenso.get(municipio_nome, 0)
    feature['properties']['populacao'] = populacao
    if populacao > 0:
        # CORREÇÃO: Usa o 'total_casos_municipio' para calcular a taxa, não o total geral do df.
        feature['properties']['taxa_casos_100k'] = (total_casos_municipio / populacao) * 100000
    else:
        feature['properties']['taxa_casos_100k'] = 0
    
    # Inicializa os dados de predominância para o mapa
    predominante = df_municipio_doenca[df_municipio_doenca['Município'] == municipio_nome].loc[
        df_municipio_doenca[df_municipio_doenca['Município'] == municipio_nome]['Quantidade de casos'].idxmax()
    ] if not df_municipio_doenca[df_municipio_doenca['Município'] == municipio_nome].empty else None
    
    if predominante is not None:
        doenca_predominante = predominante['Doença']
        feature['properties']['doenca_predominante'] = doenca_predominante
        feature['properties']['cor_predominante'] = cores_doencas.get(doenca_predominante, [128, 128, 128])
    else:
        feature['properties']['doenca_predominante'] = "N/A"
        feature['properties']['cor_predominante'] = [128, 128, 128]


# Calcula a população total dos municípios filtrados e a taxa de casos por 100k
municipios_unicos_filtrados = df_filtrado['Município'].unique()

#populacao_total_filtrada = sum(novocenso.get(m, 0) for m in municipios_unicos_filtrados)
populacao_total_filtrada = int(novocenso[novocenso["Município"].isin(municipios_unicos_filtrados)]["População"].sum())
# Remove valores não numéricos antes de somar
#filtro_poupulacao = novocenso[pd.to_numeric(novocenso["População estimada 2024"], errors="coerce").notnull()]
#populacao_total_filtrada = int(filtro_poupulacao[filtro_poupulacao["Município"].isin(municipios_unicos_filtrados)]["População estimada 2024"].sum())

 
total_casos_filtrados = df_filtrado['Quantidade de casos'].sum()
taxa_100k = (total_casos_filtrados / populacao_total_filtrada) * 100000 if populacao_total_filtrada > 0 else 0


# Filtro por data
data_minima = df_original['Data Notificação'].min().date()
data_maxima = df_original['Data Notificação'].max().date()
data_inicio, data_fim = st.sidebar.date_input("Filtrar por Período", value=(data_minima, data_maxima), min_value=data_minima, max_value=data_maxima)

df_filtrado = df_original.copy()
if doencas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado['Doença'].isin(doencas_selecionadas)]
if municipio_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Município'] == municipio_selecionado]
df_filtrado = df_filtrado[(df_filtrado['Data Notificação'].dt.date >= data_inicio) & (df_filtrado['Data Notificação'].dt.date <= data_fim)]



# filtro de gênero
sexo_selecionado = st.sidebar.selectbox(
    "Selecione o Sexo:",
    options=['Ambos', 'Masculino', 'Feminino']
)
df_filtrado = df_filtrado[df_filtrado['Doença'].isin(doencas_selecionadas)]

if sexo_selecionado != 'Ambos':
    df_filtrado = df_filtrado[df_filtrado['Sexo'] == sexo_selecionado]

# Agrupa os dados para o mapa
df_casos_por_municipio = df_filtrado.groupby(['Município', 'Doença'])['Quantidade de casos'].sum().reset_index()


# Coloração das Doenças
legenda_html = "<br><b>Coloração das Doenças</b><br>"
legenda_html += '<div style="display: flex; gap: 20px;">'  # 
for nome, cor in cores_doencas.items():
    #cor_hex = rgb_to_hex(cor)
    cor_hex = (cor)
    legenda_html += f'<div style="display: flex; align-items: center; margin-bottom: 1px;">'
    legenda_html += f'<div style="width: 20px; height: 20px; background-color: {cor_hex}; border: 1px solid #000; margin-right: 10px;"></div>'
    legenda_html += f'<span>{nome}</span></div>'
    legenda_html += '</div>'

st.sidebar.markdown(legenda_html, unsafe_allow_html=True)
 

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
# 1. Pagina Streamlit
# --------------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Painel Epidemiológico - SES-CE")

# Título principal do aplicativo
st.title("Painel de Análise de Doenças Arboviroses")
st.divider()

# --------------------------------------------------------------------------------
# 2. Resumo dos Dados (Melhorado)
# --------------------------------------------------------------------------------
st.header("Resumo dos Dados")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"**Total de Casos:** <br><div style='font-size: 2.5em; font-weight: bold; color: lightgray;'>{df_filtrado['Quantidade de casos'].sum():,}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"**Doenças Selecionadas:** <br><div style='font-size: 2.5em; font-weight: bold; color: lightgray;'>{df_filtrado['Doença'].nunique()}</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"**Municípios:** <br><div style='font-size: 2.5em; font-weight: bold; color: lightgray;'>{df_filtrado['Município'].nunique()}</div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"**População:** <br><div style='font-size: 2.5em; font-weight: bold; color: lightgray;'>{abreviar_numero(populacao_total_filtrada)}</div>", unsafe_allow_html=True)
with col5:
    st.markdown(f"**Taxa Transm. (100k hab.):** <br><div style='font-size: 2.5em; font-weight: bold; color: lightgray;'>{taxa_100k:,.2f}</div>", unsafe_allow_html=True)
#with col6:
#    st.markdown(f"**Período de Análise:** <br><div style='font-size: 1.5em; font-weight: bold; color: lightgray;'>{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)
st.divider()



# --------------------------------------------------------------------------------
# 3. Criação do Mapa
# --------------------------------------------------------------------------------
st.title("Mapa de Casos por Município") 

# Seletor para escolher a doença a ser visualizada
doenca_selecionada = st.selectbox(
    "Selecione a doença para o mapa:",
    options=["Filtro Geral"] + list(cores_doencas.keys())
)

# Calcula o total de casos por município e por doença
df_municipio_doenca = df_filtrado.groupby(['Município', 'Doença'])['Quantidade de casos'].sum().reset_index()

# Encontra a doença predominante e o total de casos para cada município
df_predominancia = df_municipio_doenca.loc[df_municipio_doenca.groupby('Município')['Quantidade de casos'].idxmax()]
df_total_casos_por_municipio = df_municipio_doenca.groupby('Município')['Quantidade de casos'].sum().reset_index()

# Mescla os dados de casos e predominância no GeoJSON
for feature in geojson_data['features']:
    municipio_nome = feature['properties']['name']
    
    # Adiciona total de casos
    casos = df_total_casos_por_municipio[df_total_casos_por_municipio['Município'] == municipio_nome]
    feature['properties']['total_casos'] = int(casos['Quantidade de casos'].iloc[0]) if not casos.empty else 0

    # Adiciona a doença predominante e sua cor
    predominante = df_predominancia[df_predominancia['Município'] == municipio_nome]
    if not predominante.empty:
        doenca_predominante = predominante['Doença'].iloc[0]
        feature['properties']['doenca_predominante'] = doenca_predominante
        feature['properties']['cor_predominante'] = cores_doencas2.get(doenca_predominante, [160, 160, 160])
    else:
        feature['properties']['doenca_predominante'] = "N/A"
        feature['properties']['cor_predominante'] = [160, 160, 160]

# --------------------------------------------------------------------------------
# 3.1 Logica Mapa
# --------------------------------------------------------------------------------

# Lógica para determinar a cor do preenchimento e do mapa de calor
if doenca_selecionada == "Filtro Geral":
    # Mapeia cada município para a cor da sua doença predominante
    for feature in geojson_data['features']:
        feature['properties']['fill_color'] = feature['properties']['cor_predominante']
    
    # Cor do mapa de calor será a cor padrão para a predominância
    #heatmap_color = [255, 0, 0] # Vermelho
    tooltip_text = "Município: {name}\nDoença Predominante: {doenca_predominante}\nCasos Totais: {total_casos}"
    
else:
    # Filtra os dados apenas para a doença selecionada
    df_filtrado = df_municipio_doenca[df_municipio_doenca['Doença'] == doenca_selecionada]
    
    # Obtém o número máximo de casos da doença selecionada para normalização
    max_casos = df_filtrado['Quantidade de casos'].max() if not df_filtrado.empty else 1
    
    # Itera sobre os municípios e define a cor com um gradiente
    cor_base = cores_doencas2.get(doenca_selecionada, [160, 160, 160])
    for feature in geojson_data['features']:
        municipio_nome = feature['properties']['name']
        casos = df_filtrado[df_filtrado['Município'] == municipio_nome]['Quantidade de casos']
        num_casos = int(casos.iloc[0]) if not casos.empty else 0
        
        # Calcula a intensidade do gradiente (de 0.2 a 1.0)
        #intensidade = 0 + (num_casos / max_casos) * 1 if max_casos > 0 else 1
        #intensidade = 0 + (1 - (num_casos / max_casos)) * 0.8 if max_casos > 0 else 0.2
        # A cor será mais forte para mais casos e mais fraca para menos
        #cor_gradiente = [int(c * intensidade) for c in cor_base]
        #feature['properties']['fill_color'] = cor_gradiente

        if num_casos > 0: 
            intensidade = 0.4 + (1 - (num_casos / max_casos)) * 0.8 if max_casos > 0 else 0.2
            cor_gradiente = [int(c * intensidade) for c in cor_base]
            feature['properties']['fill_color'] = cor_gradiente + [160]   
        else: 
            feature['properties']['fill_color'] = [170, 170, 170]

        feature['properties']['casos_da_doenca'] = num_casos

    # A cor do mapa de calor será a cor da doença selecionada
    #heatmap_color = cor_base
    tooltip_text = f"Município: {{name}}\nCasos de {doenca_selecionada}: {{casos_da_doenca}}"


# --------------------------------------------------------------------------------
# 3.2 Construção do DeckGL
# --------------------------------------------------------------------------------

# Camada GeoJson (preenche os municípios)
geojson_layer = pdk.Layer(
    "GeoJsonLayer",
    geojson_data,
    filled=True,
    get_fill_color="properties.fill_color",
    pickable=True,
    opacity=0.6,
    stroked=True,
    get_line_color=[255, 255, 255], # Borda branca para os polígonos
    line_width_min_pixels=1
)

# Define a visualização inicial do mapa
view_state = pdk.ViewState(
    latitude=-5.5,
    longitude=-39.5,
    zoom=6.5,
    pitch=0
)

# Renderiza o mapa com as duas camadas
r = pdk.Deck(
    layers=[geojson_layer],
    initial_view_state=view_state,
    tooltip={
        "text": tooltip_text,
        "style": {
            "backgroundColor": "rgba(255, 255, 255, 0.8)",
            "color": "black"
        }
    }
)

st.pydeck_chart(r, height=600)
st.write("---")
st.write("### Legenda:")
st.write(f"- **Mapa de Cores:** Cada município é preenchido com a cor da doença predominante. Se uma doença específica for selecionada, o mapa exibe um gradiente: a cor é mais intensa para mais casos e mais fraca para menos.")
st.write(f"- **Filtro:** Existem 2 (dois) filtros possiveis no Mapa. No Filtro de Analise a esqueda, é o Filtro Geral sobre o painel, mas caso necessite visualizar somente uma Doença no mapa sem alterar o restante, é possível.")
st.divider()

  
# --------------------------------------------------------------------------------
# 4. Análise Exploratória
# --------------------------------------------------------------------------------
st.header("Análise Exploratória")

color_discrete_map_config = {d: cores_doencas[d] for d in df_filtrado['Doença'].unique()}
  
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Casos por Doença")
    casos_por_doenca_plot = df_filtrado.groupby('Doença')['Quantidade de casos'].sum().reset_index()
    fig_doenca = px.bar(casos_por_doenca_plot, x='Doença', y='Quantidade de casos',
                        color='Doença', 
                        #color_discrete_map={d: cores_doencas[d] for d in doencas_disponiveis},
                        color_discrete_map=color_discrete_map_config,
                        title='Total de Casos por Doença',
                        labels={'Quantidade de casos': 'Total de Casos', 'Doença': 'Doença'})
    fig_doenca.update_layout(height=450)
    st.plotly_chart(fig_doenca, use_container_width=True)

with col_b:
    st.subheader("Casos por Município")
    casos_por_municipio_plot = df_filtrado.groupby('Município')['Quantidade de casos'].sum().reset_index()
    fig_municipio = px.bar(casos_por_municipio_plot, x='Quantidade de casos', y='Município',
                           title='Municípios com Maior Incidência', 
                           orientation='h',
                           color='Quantidade de casos',  # <- cria o degradê com base na quantidade
                           color_continuous_scale='Oranges',  # <- várias opções de paleta
                           labels={'Quantidade de casos': 'Total de Casos', 'Município': 'Município'})
    fig_municipio.update_layout(height=450, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_municipio, use_container_width=True)



col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Casos por Doença e Sexo")
    fig_sexo = px.bar(df_filtrado, y='Doença', x='Quantidade de casos', color='Sexo',
                        title='Casos por Doença e Sexo', orientation='h',
                        labels={'Quantidade de casos': 'Total de Casos'},
                        color_discrete_map={'Masculino': 'lightblue', 'Feminino': 'pink'})
    fig_sexo.update_layout(height=400)
    st.plotly_chart(fig_sexo, use_container_width=True)

with col_b:
    st.subheader("Casos por Doença e Faixa Etária")
    faixas_ordenadas = sorted(df_filtrado['Faixa Etária'].unique())
    fig_faixa = px.bar(df_filtrado, y='Doença', x='Quantidade de casos', color='Faixa Etária',
                        title='Casos por Doença e Faixa Etária', orientation='h',
                        category_orders={'Faixa Etária': faixas_ordenadas},
                        labels={'Quantidade de casos': 'Total de Casos'},
                        color_discrete_sequence=px.colors.qualitative.Plotly)
    fig_faixa.update_layout(height=450)
    st.plotly_chart(fig_faixa, use_container_width=True)

st.divider()


# --------------------------------------------------------------------------------
# 5. Tendências e Correlação
# --------------------------------------------------------------------------------
st.header("Tendências de Correlação")

# Matriz de Correlação  
colors_mpl = {name: [c / 255 for c in map(int, color.strip('rgb()').split(','))] for name, color in cores_doencas.items()}
cmap_cores = [colors_mpl["Encefalite"], [1, 1, 1], colors_mpl["Dengue"]] # Exemplo: de cinza para branco para azul
custom_cmap = LinearSegmentedColormap.from_list("custom_diverging", cmap_cores) 
##
with st.expander("Correlação entre Doenças"):
    st.subheader("Análise de Correlação entre Doenças")
    
    # Verifica se há doenças selecionadas para continuar
    if not doencas_selecionadas:
        st.warning("Selecione pelo menos duas doenças na barra lateral para calcular a correlação.")
    else:
        # Pivo e filtro dos dados para as doenças selecionadas
        casos_pivot = df_original.pivot_table(index='Data Notificação', columns='Doença', values='Quantidade de casos', fill_value=0, aggfunc='sum')
        casos_para_correlacao = casos_pivot[doencas_selecionadas]
        
        # Verifica se há dados suficientes para a correlação
        if casos_para_correlacao.shape[0] > 1 and casos_para_correlacao.shape[1] > 1:
            matriz_correlacao = casos_para_correlacao.corr()
            
            # Divide a interface em duas colunas para o heatmap e a tabela
            col1, col2 = st.columns([0.6, 0.4])
            
            with col1:
                st.subheader("Matriz de Correlação (Heatmap)")
                # Configura o fundo da figura e dos eixos para preto
                fig, ax = plt.subplots(figsize=(10, 6))
                fig.patch.set_facecolor('black')
                ax.set_facecolor('black')

                # Define o colormap para 'indigo'
                sns.heatmap(
                    matriz_correlacao,
                    annot=True,
                    cmap='coolwarm', 
                    fmt=".2f",
                    ax=ax,
                    # Define a cor das anotações para branco
                    annot_kws={"size": 10, "color": "white"}
                )
                
                # Define a cor do título e dos rótulos dos eixos para branco
                ax.set_title('Matriz de Correlação entre Doenças', color='white')
                ax.tick_params(axis='x', colors='white')
                ax.tick_params(axis='y', colors='white')
                
                st.pyplot(fig)
            
            with col2:
                st.subheader("Correlação Ordenada")
                # Transforma a matriz em uma série, filtra a correlação com si mesma e ordena
                correlation_series = matriz_correlacao.unstack()
                
                # CORREÇÃO DO ERRO: Renomeia os índices antes de resetar para evitar o 'ValueError'
                correlation_series.index.names = ['Doença 1', 'Doença 2']
                
                # Filtra a série para remover pares duplicados e a correlação com si mesma
                correlation_series = correlation_series[correlation_series.index.get_level_values(0) < correlation_series.index.get_level_values(1)]
                correlation_series = correlation_series.sort_values(ascending=False)
                
                # Formata a série em um DataFrame para exibição
                correlation_table = correlation_series.reset_index()
                correlation_table.columns = ['Doença 1', 'Doença 2', 'Correlação']

                # Situação Correlação
                bins = [-1, 0.3, 0.6, 1]
                labels = ['Fraca', 'Mediana', 'Forte']
                correlation_table['Situação Correlação'] = pd.cut(
                    correlation_table['Correlação'],
                    bins=bins,
                    labels=labels,
                    right=False  # Isso garante que 0.31 caia no segundo bin
                )
                
                # FUNÇÃO DE ESTILO PARA COLORIR A TABELA
                def style_correlation(val):
                    color = 'lightgray'
                    if val >= 0.61:
                        color = 'red' # Cor para 'Forte'
                    elif val > 0.3 and val < 0.61:
                        color = 'yellow' # Cor para 'Mediana'
                    else:
                        color = 'gray' # Cor para 'Fraca'
                    
                    return f'background-color: {color}'

                # ESTILO
                styled_df = correlation_table.style.applymap(style_correlation, subset=['Correlação'])
                
                st.dataframe(styled_df, use_container_width=True, height=650)
        else:
            st.warning("Não há dados suficientes ou doenças selecionadas para calcular uma matriz de correlação significativa.")

 
 
# --------------------------------------------------------------------------------
# 6. Previsão 
# --------------------------------------------------------------------------------
st.header("Previsão de Casos")
st.write("A previsão de casos é gerada para cada doença selecionada nos filtros.")
st.write("Realizada Previsões de formas diferentes")

#
# Previsão de Casos (SARIMAX)
#
with st.expander("Previsão de Casos (SARIMAX)"):
    meses_futuros = st.slider(
        "Selecione o número de meses para prever",
        min_value=1,
        max_value=12,
        value=2
    )

    if not doencas_selecionadas:
        st.warning("Selecione pelo menos uma doença na barra lateral para gerar as previsões.")
    else:
        # Cria um único objeto de figura para todas as previsões
        fig_previsao = go.Figure()
        
        # Lista para armazenar os resumos das previsões
        resumos_previsao = []
        
        for doenca_previsao in doencas_selecionadas:
            df_previsao = df_original[df_original['Doença'] == doenca_previsao]
            
            if not df_previsao.empty:
                # Agrupa os dados por mês (freq='M') para a previsão mensal
                ts = df_previsao.groupby(pd.Grouper(key='Data Notificação', freq='M'))['Quantidade de casos'].sum()
                ts = ts.asfreq('M', fill_value=0)

                if len(ts) < 12:  # Recomenda-se pelo menos 1 ano de dados para uma previsão mensal
                    st.warning(f"Não há dados suficientes para realizar a previsão mensal para {doenca_previsao}. Pelo menos 12 meses de dados são recomendados.")
                    continue
                else:
                    try:
                        # Treina o modelo SARIMAX com sazonalidade anual (24 meses)
                        model = SARIMAX(ts,
                                        order=(1, 1, 1),
                                        seasonal_order=(1, 1, 1, 24),
                                        enforce_stationarity=False,
                                        enforce_invertibility=False)
                        model_fit = model.fit(disp=False)
                        
                        # Gera as previsões
                        previsao = model_fit.get_forecast(steps=meses_futuros)
                        previsao_df = previsao.summary_frame()
                        previsao_df.index = pd.to_datetime(previsao_df.index)

                        # Adiciona os traces ao gráfico único
                        fig_previsao.add_trace(go.Scatter(
                            x=ts.index,
                            y=ts.values,
                            mode='lines',
                            name=f'Dados Históricos ({doenca_previsao})',
                            line=dict(color=cores_doencas[doenca_previsao])
                        ))
                        fig_previsao.add_trace(go.Scatter(
                            x=previsao_df.index,
                            y=previsao_df['mean'],
                            mode='lines+markers',
                            name=f'Previsão ({doenca_previsao})',
                            line=dict(color=cores_doencas[doenca_previsao], dash='dot')
                        ))
                        # Adiciona o intervalo de confiança como área sombreada
                        fig_previsao.add_trace(go.Scatter(
                            x=previsao_df.index,
                            y=previsao_df['mean_ci_upper'],
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False,
                            name=f'IC Superior ({doenca_previsao})'
                        ))
                        fig_previsao.add_trace(go.Scatter(
                            x=previsao_df.index,
                            y=previsao_df['mean_ci_lower'],
                            mode='lines',
                            fill='tonexty',
                            fillcolor=cores_doencas[doenca_previsao].replace('rgb', 'rgba').replace(')', ',0.1)'),
                            line=dict(width=0),
                            showlegend=False,
                            name=f'IC Inferior ({doenca_previsao})'
                        ))

                        # Lógica para o resumo da previsão
                        if not ts.empty and not previsao_df.empty:
                            last_historic_value = ts.iloc[-1]
                            last_predicted_value = previsao_df['mean'].iloc[-1]
                            
                            trend = "Aumento" if last_predicted_value > last_historic_value else "Diminuição"
                            
                            ci_width = previsao_df['mean_ci_upper'] - previsao_df['mean_ci_lower']
                            avg_mean = previsao_df['mean'].mean()
                            
                            error_percentage = 0
                            if avg_mean > 0:
                                error_percentage = (ci_width.mean() / 2) / avg_mean * 100
                            
                            resumos_previsao.append({
                                'doenca': doenca_previsao,
                                'trend': trend,
                                'error': error_percentage
                            })

                    except Exception as e:
                        st.error(f"Erro ao gerar a previsão para {doenca_previsao}. Verifique se os dados são adequados para o modelo. Detalhes: {e}")
            else:
                st.warning(f"Não há dados disponíveis para a doença '{doenca_previsao}'.")
        
        # Exibe o gráfico unificado após o loop
        if fig_previsao.data: # Verifica se algum dado foi adicionado à figura
            fig_previsao.update_layout(
                title='Previsão de Casos para as Doenças Selecionadas',
                xaxis_title='Data',
                yaxis_title='Quantidade de Casos'
            )
            st.plotly_chart(fig_previsao, use_container_width=True)
            
            # Nova seção de resumo geral
            st.markdown(f"### Resumo da Previsão para os Próximos {meses_futuros} Meses")
            for resumo in resumos_previsao:
                st.markdown(f"- **Doença {resumo['doenca']}**: {resumo['trend']} - Porcentagem de incerteza (erro): {resumo['error']:.2f}%")
        else:
            st.info("Nenhuma previsão foi gerada. Verifique os dados ou os filtros selecionados.")



#
# Previsão de Casos (ARIMA)
#
with st.expander("Previsão de Casos (ARIMA)"):
    if not doencas_selecionadas:
        st.warning("Selecione pelo menos uma doença na barra lateral para gerar as previsões.")
    else:
        # Cria um único objeto de figura para todas as previsões
        fig_previsao = go.Figure()
        
        # Lista para armazenar os resumos das previsões
        resumos_previsao = []
        
        for doenca_previsao in doencas_selecionadas:
            df_previsao = df_original[df_original['Doença'] == doenca_previsao]
            
            if not df_previsao.empty:
                # Agrupa os dados por mês (freq='M') para a previsão mensal
                ts = df_previsao.groupby(pd.Grouper(key='Data Notificação', freq='M'))['Quantidade de casos'].sum()
                ts = ts.asfreq('M', fill_value=0)

                if len(ts) < 12:  # Recomenda-se pelo menos 1 ano de dados para uma previsão mensal
                    st.warning(f"Não há dados suficientes para realizar a previsão mensal para {doenca_previsao}. Pelo menos 12 meses de dados são recomendados.")
                    continue
                else:
                    try:
                        # Treina o modelo SARIMAX com sazonalidade anual (12 meses)
                        #model = SARIMAX(ts,
                        #                order=(1, 1, 1),
                        #                seasonal_order=(1, 1, 1, 12),
                        #                seasonal_order=(1, 1, 1, 24),
                        #                enforce_stationarity=False,
                        #                enforce_invertibility=False)
                        #model_fit = model.fit(disp=False)

                        # auto_arima busca os melhores parâmetros automaticamente
                        model = auto_arima(
                            ts,
                            start_p=1, start_q=1, max_p=3, max_q=3,
                            m=12,  # Sazonalidade de 12 meses
                            start_P=0, start_Q=0, max_P=2, max_Q=2,
                            seasonal=True,
                            d=1, D=1,
                            trace=False,
                            error_action='ignore',
                            suppress_warnings=True,
                            stepwise=True
                        )
                        
                        # O modelo retornado por auto_arima já está treinado.
                        # Usamos o método .predict() para gerar a previsão e o intervalo de confiança.
                        forecast, conf_int = model.predict(n_periods=meses_futuros, return_conf_int=True)

                        # Cria um DataFrame para os resultados da previsão
                        future_dates = pd.date_range(start=ts.index[-1] + pd.offsets.MonthBegin(), periods=meses_futuros, freq='M')
                        previsao_df = pd.DataFrame(
                            {'mean': forecast, 'mean_ci_lower': conf_int[:, 0], 'mean_ci_upper': conf_int[:, 1]},
                            index=future_dates
                        )

                        # DataFrame de resultados
                        future_dates = pd.date_range(start=ts.index[-1] + pd.offsets.MonthBegin(), periods=meses_futuros, freq='M')
                        previsao_df = pd.DataFrame(
                            {'mean': forecast, 'mean_ci_lower': conf_int[:, 0], 'mean_ci_upper': conf_int[:, 1]},
                            index=future_dates
                        )

                        # Adiciona os traces ao gráfico único
                        fig_previsao.add_trace(go.Scatter(
                            x=ts.index,
                            y=ts.values,
                            mode='lines',
                            name=f'Dados Históricos ({doenca_previsao})',
                            line=dict(color=cores_doencas[doenca_previsao])
                        ))
                        fig_previsao.add_trace(go.Scatter(
                            x=previsao_df.index,
                            y=previsao_df['mean'],
                            mode='lines+markers',
                            name=f'Previsão ({doenca_previsao})',
                            line=dict(color=cores_doencas[doenca_previsao], dash='dot')
                        ))
                        # Adiciona o intervalo de confiança como área sombreada
                        fig_previsao.add_trace(go.Scatter(
                            x=previsao_df.index,
                            y=previsao_df['mean_ci_upper'],
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False,
                            name=f'IC Superior ({doenca_previsao})'
                        ))
                        fig_previsao.add_trace(go.Scatter(
                            x=previsao_df.index,
                            y=previsao_df['mean_ci_lower'],
                            mode='lines',
                            fill='tonexty',
                            fillcolor=cores_doencas[doenca_previsao].replace('rgb', 'rgba').replace(')', ',0.1)'),
                            line=dict(width=0),
                            showlegend=False,
                            name=f'IC Inferior ({doenca_previsao})'
                        ))

                        # Lógica para o resumo da previsão
                        if not ts.empty and not previsao_df.empty:
                            last_historic_value = ts.iloc[-1]
                            last_predicted_value = previsao_df['mean'].iloc[-1]
                            
                            trend = "Aumento" if last_predicted_value > last_historic_value else "Diminuição"
                            
                            ci_width = previsao_df['mean_ci_upper'] - previsao_df['mean_ci_lower']
                            avg_mean = previsao_df['mean'].mean()
                            
                            error_percentage = 0
                            if avg_mean > 0:
                                error_percentage = (ci_width.mean() / 2) / avg_mean * 100
                            
                            resumos_previsao.append({
                                'doenca': doenca_previsao,
                                'trend': trend,
                                'error': error_percentage
                            })

                    except Exception as e:
                        st.error(f"Erro ao gerar a previsão para {doenca_previsao}. Verifique se os dados são adequados para o modelo. Detalhes: {e}")
            else:
                st.warning(f"Não há dados disponíveis para a doença '{doenca_previsao}'.")
        
        # Exibe o gráfico unificado após o loop
        if fig_previsao.data: # Verifica se algum dado foi adicionado à figura
            fig_previsao.update_layout(
                title='Previsão de Casos para as Doenças Selecionadas',
                xaxis_title='Data',
                yaxis_title='Quantidade de Casos'
            )
            st.plotly_chart(fig_previsao, use_container_width=True)
            
            # Nova seção de resumo geral
            st.markdown(f"### Resumo da Previsão para os Próximos {meses_futuros} Meses")
            for resumo in resumos_previsao:
                st.markdown(f"- **Doença {resumo['doenca']}**: {resumo['trend']} - Porcentagem de incerteza (erro): {resumo['error']:.2f}%")
        else:
            st.info("Nenhuma previsão foi gerada. Verifique os dados ou os filtros selecionados.")
        

#
# Previsão de Casos (XGBoost)
#
with st.expander("Previsão de Casos (XGBoost)"):
    meses_futuros_xgb = st.slider(
        "Selecione o número de meses para prever (XGBoost)",
        min_value=1,
        max_value=12,
        value=2
    )

    if not doencas_selecionadas:
        st.warning("Selecione pelo menos uma doença na barra lateral para gerar as previsões.")
    else:
        fig_previsao_xgb = go.Figure()
        resumos_previsao_xgb = []

        for doenca_previsao in doencas_selecionadas:
            df_previsao = df_original[df_original['Doença'] == doenca_previsao]

            if not df_previsao.empty:
                ts = df_previsao.groupby(pd.Grouper(key='Data Notificação', freq='M'))['Quantidade de casos'].sum()
                ts = ts.asfreq('M', fill_value=0)

                # Cria o DataFrame para o modelo
                df_ts = ts.reset_index()
                df_ts.columns = ['data', 'casos']
                
                # Cria features a partir da data
                df_ts['ano'] = df_ts['data'].dt.year
                df_ts['mes'] = df_ts['data'].dt.month
                df_ts['trimestre'] = df_ts['data'].dt.quarter
                df_ts['dia_do_ano'] = df_ts['data'].dt.dayofyear
                
                # Adiciona features de defasagem (lag features)
                for i in range(1, 4):  # Adiciona 3 meses de defasagem
                    df_ts[f'lag_{i}'] = df_ts['casos'].shift(i)
                
                df_ts = df_ts.dropna()

                if len(df_ts) < 12: # Recomenda-se pelo menos 1 ano de dados para features de sazonalidade
                    st.warning(f"Não há dados suficientes para o modelo XGBoost para {doenca_previsao}. Pelo menos 12 meses de dados são recomendados.")
                    continue
                else:
                    try:
                        from xgboost import XGBRegressor

                        # Prepara os dados para o modelo
                        features = [col for col in df_ts.columns if col not in ['data', 'casos']]
                        target = 'casos'

                        X = df_ts[features]
                        y = df_ts[target]

                        # Inicializa e treina o modelo
                        model_xgb = XGBRegressor(objective='reg:squarederror', n_estimators=1000)
                        # Removemos o argumento 'eval_metric' que estava causando o erro
                        model_xgb.fit(X, y)

                        # Cria o DataFrame para os dados futuros
                        future_dates = pd.date_range(start=ts.index[-1] + pd.offsets.MonthBegin(), periods=meses_futuros_xgb, freq='M')
                        future_df = pd.DataFrame({'data': future_dates})
                        future_df['ano'] = future_df['data'].dt.year
                        future_df['mes'] = future_df['data'].dt.month
                        future_df['trimestre'] = future_df['data'].dt.quarter
                        future_df['dia_do_ano'] = future_df['data'].dt.dayofyear

                        # Prepara as features de defasagem para a previsão
                        last_casos = ts.values[-3:]
                        for i in range(1, 4):
                            future_df[f'lag_{i}'] = 0 # Inicializa com zero
                        
                        # Preenche os valores de defasagem do primeiro mês de previsão
                        if meses_futuros_xgb > 0:
                            future_df.loc[0, 'lag_1'] = last_casos[-1]
                            future_df.loc[0, 'lag_2'] = last_casos[-2]
                            future_df.loc[0, 'lag_3'] = last_casos[-3]

                        # Previsão iterativa para preencher as features de defasagem
                        previsoes = []
                        for i in range(meses_futuros_xgb):
                            pred = model_xgb.predict(future_df.iloc[i:i+1][features])[0]
                            previsoes.append(pred)
                            
                            # Atualiza os lags para o próximo mês
                            if i < meses_futuros_xgb - 1:
                                future_df.loc[i+1, 'lag_1'] = previsoes[i]
                                future_df.loc[i+1, 'lag_2'] = future_df.loc[i, 'lag_1']
                                future_df.loc[i+1, 'lag_3'] = future_df.loc[i, 'lag_2']

                        previsao_df_xgb = pd.DataFrame(
                            {'mean': previsoes},
                            index=future_dates
                        )
                        # O XGBoost não fornece IC, então criamos um heurístico
                        previsao_df_xgb['mean_ci_upper'] = previsao_df_xgb['mean'] * 1.2
                        previsao_df_xgb['mean_ci_lower'] = previsao_df_xgb['mean'] * 0.8
                        previsao_df_xgb.loc[previsao_df_xgb['mean_ci_lower'] < 0, 'mean_ci_lower'] = 0

                        # Adiciona os traces ao gráfico
                        fig_previsao_xgb.add_trace(go.Scatter(
                            x=ts.index,
                            y=ts.values,
                            mode='lines',
                            name=f'Dados Históricos ({doenca_previsao})',
                            line=dict(color=cores_doencas[doenca_previsao])
                        ))
                        fig_previsao_xgb.add_trace(go.Scatter(
                            x=previsao_df_xgb.index,
                            y=previsao_df_xgb['mean'],
                            mode='lines+markers',
                            name=f'Previsão ({doenca_previsao})',
                            line=dict(color=cores_doencas[doenca_previsao], dash='dot')
                        ))
                        # Adiciona o intervalo de confiança 
                        fig_previsao_xgb.add_trace(go.Scatter(
                            x=previsao_df_xgb.index,
                            y=previsao_df_xgb['mean_ci_upper'],
                            mode='lines',
                            line=dict(width=0),
                            showlegend=False,
                            name=f'IC Superior ({doenca_previsao})'
                        ))
                        fig_previsao_xgb.add_trace(go.Scatter(
                            x=previsao_df_xgb.index,
                            y=previsao_df_xgb['mean_ci_lower'],
                            mode='lines',
                            fill='tonexty',
                            fillcolor=cores_doencas[doenca_previsao].replace('rgb', 'rgba').replace(')', ',0.1)'),
                            line=dict(width=0),
                            showlegend=False,
                            name=f'IC Inferior ({doenca_previsao})'
                        ))

                        if not ts.empty and not previsao_df_xgb.empty:
                            last_historic_value = ts.iloc[-1]
                            last_predicted_value = previsao_df_xgb['mean'].iloc[-1]
                            trend = "Aumento" if last_predicted_value > last_historic_value else "Diminuição"
                            
                            ci_width = previsao_df_xgb['mean_ci_upper'] - previsao_df_xgb['mean_ci_lower']
                            avg_mean = previsao_df_xgb['mean'].mean()
                            
                            error_percentage = 0
                            if avg_mean > 0:
                                error_percentage = (ci_width.mean() / 2) / avg_mean * 100
                            
                            resumos_previsao_xgb.append({
                                'doenca': doenca_previsao,
                                'trend': trend,
                                'error': error_percentage
                            })

                    except Exception as e:
                        st.error(f"Erro ao gerar a previsão XGBoost para {doenca_previsao}. Detalhes: {e}")
            else:
                st.warning(f"Não há dados disponíveis para a doença '{doenca_previsao}'.")
        
        # Exibe o gráfico XGBoost 
        if fig_previsao_xgb.data:
            fig_previsao_xgb.update_layout(
                title='Previsão de Casos (XGBoost) para as Doenças Selecionadas',
                xaxis_title='Data',
                yaxis_title='Quantidade de Casos'
            )
            st.plotly_chart(fig_previsao_xgb, use_container_width=True)
            
            # Resumo XGBoost
            st.markdown(f"### Resumo da Previsão XGBoost para os Próximos {meses_futuros_xgb} Meses")
            for resumo in resumos_previsao_xgb:
                st.markdown(f"- **Doença {resumo['doenca']}**: {resumo['trend']} - Porcentagem de incerteza: {resumo['error']:.2f}%")
        else:
            st.info("Nenhuma previsão XGBoost foi gerada. Verifique os dados ou os filtros selecionados.")

st.divider() 
st.markdown("Análise Epidemiológica SES-CE")
