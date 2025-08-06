# Importação de Bibliotecas
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Ignorar avisos para um painel mais limpo
warnings.filterwarnings('ignore')

# --------------------------------------------------------------------------------
# 1. Configuração do Streamlit e Carregamento de Dados
# --------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Painel Epidemiológico Interativo")

# Título principal do aplicativo
st.title("🔬 Painel de Análise de Doenças Arboviroses (Interativo)")
st.markdown("Uma ferramenta visual e interativa para análise, predição e mapeamento de dados epidemiológicos.")

# Seus dados em formato JSON (corrigido)
dados_json = """
[
{"data": "2023-03-02", "municipio": "Fortaleza", "doenca": "Dengue", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 3},
{"data": "2023-05-15", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 2},
{"data": "2023-06-01", "municipio": "Sobral", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 1},
{"data": "2023-08-20", "municipio": "Crato", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 4},
{"data": "2023-04-10", "municipio": "Caucaia", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "5 a 9 anos", "total_casos": 2},
{"data": "2023-07-28", "municipio": "Maracanaú", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 1},
{"data": "2023-10-03", "municipio": "Itapipoca", "doenca": "Dengue", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 6},
{"data": "2023-12-11", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 1},
{"data": "2024-01-25", "municipio": "Quixadá", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 5},
{"data": "2024-03-14", "municipio": "Canindé", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 3},
{"data": "2024-04-09", "municipio": "Crateús", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "80 anos ou mais", "total_casos": 1},
{"data": "2024-06-21", "municipio": "Russas", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-02-18", "municipio": "Aracati", "doenca": "Dengue", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 3},
{"data": "2023-06-10", "municipio": "Tianguá", "doenca": "Zika", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 4},
{"data": "2023-07-05", "municipio": "Fortaleza", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 2},
{"data": "2023-08-12", "municipio": "Caucaia", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "5 a 9 anos", "total_casos": 1},
{"data": "2023-09-19", "municipio": "Juazeiro do Norte", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 2},
{"data": "2023-10-30", "municipio": "Maracanaú", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 5},
{"data": "2023-12-15", "municipio": "Sobral", "doenca": "Dengue", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 4},
{"data": "2024-02-07", "municipio": "Crato", "doenca": "Zika", "sexo": "Masculino", "faixa": "70 a 79 anos", "total_casos": 1},
{"data": "2024-03-22", "municipio": "Iguatu", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2024-05-01", "municipio": "Maranguape", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2024-06-16", "municipio": "Quixadá", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 2},
{"data": "2023-01-09", "municipio": "Canindé", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 1},
{"data": "2023-02-24", "municipio": "Crateús", "doenca": "Dengue", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 3},
{"data": "2023-03-11", "municipio": "Russas", "doenca": "Zika", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 1},
{"data": "2023-04-30", "municipio": "Aracati", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 2},
{"data": "2023-06-04", "municipio": "Tianguá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 2},
{"data": "2023-07-20", "municipio": "Fortaleza", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 1},
{"data": "2023-08-17", "municipio": "Caucaia", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 4},
{"data": "2023-09-02", "municipio": "Juazeiro do Norte", "doenca": "Dengue", "sexo": "Feminino", "faixa": "80 anos ou mais", "total_casos": 2},
{"data": "2023-10-10", "municipio": "Crato", "doenca": "Zika", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 1},
{"data": "2023-11-26", "municipio": "Itapipoca", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "5 a 9 anos", "total_casos": 3},
{"data": "2024-01-12", "municipio": "Maranguape", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 2},
{"data": "2024-02-27", "municipio": "Iguatu", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 1},
{"data": "2024-04-14", "municipio": "Quixadá", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 2},
{"data": "2024-05-20", "municipio": "Canindé", "doenca": "Dengue", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 1},
{"data": "2024-06-07", "municipio": "Crateús", "doenca": "Zika", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-01-21", "municipio": "Russas", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 2},
{"data": "2023-02-03", "municipio": "Aracati", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 1},
{"data": "2023-03-18", "municipio": "Tianguá", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 1},
{"data": "2023-04-26", "municipio": "Fortaleza", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 2},
{"data": "2023-06-13", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 4},
{"data": "2023-07-09", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 3},
{"data": "2023-08-25", "municipio": "Crato", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 2},
{"data": "2024-06-13", "municipio": "Crateús", "doenca": "Chikungunya", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 4},
{"data": "2024-10-29", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 5},
{"data": "2024-03-26", "municipio": "Crateús", "doenca": "Zika", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 1},
{"data": "2025-04-12", "municipio": "Russas", "doenca": "Dengue", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 6},
{"data": "2023-09-16", "municipio": "Tianguá", "doenca": "Zika", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 7},
{"data": "2024-02-11", "municipio": "Canindé", "doenca": "Chikungunya", "sexo": "Masculino", "faixa": "5 a 9 anos", "total_casos": 6},
{"data": "2023-04-13", "municipio": "Caucaia", "doenca": "Zika", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 2},
{"data": "2024-01-10", "municipio": "Quixadá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 2},
{"data": "2025-01-22", "municipio": "Maracanaú", "doenca": "Zika", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 1},
{"data": "2023-05-14", "municipio": "Maracanaú", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 7},
{"data": "2024-08-01", "municipio": "Canindé", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 6},
{"data": "2024-06-19", "municipio": "Quixadá", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 6},
{"data": "2025-07-02", "municipio": "Fortaleza", "doenca": "Zika", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 7},
{"data": "2023-01-14", "municipio": "Crato", "doenca": "Dengue", "sexo": "Feminino", "faixa": "5 a 9 anos", "total_casos": 3},
{"data": "2023-01-14", "municipio": "Juazeiro do Norte", "doenca": "Febre Amarela", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 5},
{"data": "2023-01-04", "municipio": "Juazeiro do Norte", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 7},
{"data": "2023-10-12", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 5},
{"data": "2024-07-19", "municipio": "Tianguá", "doenca": "Zika", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 3},
{"data": "2023-12-14", "municipio": "Fortaleza", "doenca": "Febre Oropouche", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 7},
{"data": "2024-04-30", "municipio": "Maracanaú", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 1},
{"data": "2023-01-26", "municipio": "Maranguape", "doenca": "Zika", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 3},
{"data": "2023-09-20", "municipio": "Crateús", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "80 anos ou mais", "total_casos": 2},
{"data": "2025-06-28", "municipio": "Fortaleza", "doenca": "Zika", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 4},
{"data": "2024-08-24", "municipio": "Crato", "doenca": "Encefalite", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 1},
{"data": "2023-10-23", "municipio": "Quixadá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 1},
{"data": "2024-01-21", "municipio": "Sobral", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 4},
{"data": "2023-01-13", "municipio": "Fortaleza", "doenca": "Zika", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2024-01-08", "municipio": "Fortaleza", "doenca": "Chikungunya", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 7},
{"data": "2025-07-30", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 4},
{"data": "2023-08-03", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 3},
{"data": "2024-03-10", "municipio": "Tianguá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 5},
{"data": "2025-03-06", "municipio": "Russas", "doenca": "Chikungunya", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 4},
{"data": "2023-02-26", "municipio": "Canindé", "doenca": "Dengue", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 3},
{"data": "2025-01-26", "municipio": "Maranguape", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 2},
{"data": "2023-10-10", "municipio": "Caucaia", "doenca": "Febre Oropouche", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 4},
{"data": "2025-06-21", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 2},
{"data": "2024-12-16", "municipio": "Russas", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 6},
{"data": "2023-04-11", "municipio": "Crato", "doenca": "Dengue", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 2},
{"data": "2025-03-30", "municipio": "Sobral", "doenca": "Febre Amarela", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 7},
{"data": "2025-03-18", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 7},
{"data": "2025-02-25", "municipio": "Crateús", "doenca": "Dengue", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 7},
{"data": "2024-07-21", "municipio": "Aracati", "doenca": "Zika", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 1},
{"data": "2024-07-23", "municipio": "Caucaia", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 3},
{"data": "2023-01-21", "municipio": "Canindé", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 6},
{"data": "2024-10-17", "municipio": "Juazeiro do Norte", "doenca": "Febre Amarela", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 1},
{"data": "2024-11-23", "municipio": "Fortaleza", "doenca": "Chikungunya", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 3},
{"data": "2023-07-08", "municipio": "Sobral", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "5 a 9 anos", "total_casos": 2},
{"data": "2024-03-05", "municipio": "Maranguape", "doenca": "Dengue", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 5},
{"data": "2023-12-20", "municipio": "Crateús", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 1},
{"data": "2023-10-08", "municipio": "Aracati", "doenca": "Zika", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 4},
{"data": "2024-05-21", "municipio": "Tianguá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 6},
{"data": "2023-09-12", "municipio": "Iguatu", "doenca": "Dengue", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 3},
{"data": "2024-07-07", "municipio": "Maracanaú", "doenca": "Febre Oropouche", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2024-04-28", "municipio": "Canindé", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 4},
{"data": "2023-06-05", "municipio": "Crato", "doenca": "Dengue", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 5},
{"data": "2023-03-23", "municipio": "Fortaleza", "doenca": "Zika", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 1},
{"data": "2023-11-19", "municipio": "Sobral", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 3},
{"data": "2024-01-18", "municipio": "Juazeiro do Norte", "doenca": "Dengue", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 4},
{"data": "2023-09-01", "municipio": "Caucaia", "doenca": "Febre Oropouche", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 5},
{"data": "2023-05-08", "municipio": "Maranguape", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 6},
{"data": "2024-06-28", "municipio": "Iguatu", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 2},
{"data": "2023-08-16", "municipio": "Quixadá", "doenca": "Dengue", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 1},
{"data": "2024-10-07", "municipio": "Canindé", "doenca": "Zika", "sexo": "Masculino", "faixa": "70 a 79 anos", "total_casos": 7},
{"data": "2025-03-09", "municipio": "Crateús", "doenca": "Febre Amarela", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 3},
{"data": "2024-05-30", "municipio": "Tianguá", "doenca": "Febre Oropouche", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-12-25", "municipio": "Fortaleza", "doenca": "Encefalite", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 4},
{"data": "2023-10-18", "municipio": "Maracanaú", "doenca": "Dengue", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 6},
{"data": "2023-02-22", "municipio": "Sobral", "doenca": "Zika", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 5},
{"data": "2024-04-07", "municipio": "Juazeiro do Norte", "doenca": "Chikungunya", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 3},
{"data": "2023-01-30", "municipio": "Crato", "doenca": "Febre Amarela", "sexo": "Feminino", "faixa": "5 a 9 anos", "total_casos": 7},
{"data": "2023-08-23", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 2},
{"data": "2023-07-04", "municipio": "Maranguape", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 1},
{"data": "2024-11-11", "municipio": "Iguatu", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 3},
{"data": "2023-06-16", "municipio": "Quixadá", "doenca": "Dengue", "sexo": "Feminino", "faixa": "80 anos ou mais", "total_casos": 2},
{"data": "2023-04-09", "municipio": "Canindé", "doenca": "Zika", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 3},
{"data": "2023-11-21", "municipio": "Crateús", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 6},
{"data": "2024-09-28", "municipio": "Tianguá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 4},
{"data": "2024-02-14", "municipio": "Fortaleza", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "15 a 19 anos", "total_casos": 3},
{"data": "2023-05-25", "municipio": "Caucaia", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 5},
{"data": "2024-12-01", "municipio": "Juazeiro do Norte", "doenca": "Dengue", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 6},
{"data": "2023-08-14", "municipio": "Maracanaú", "doenca": "Zika", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 4},
{"data": "2024-07-02", "municipio": "Sobral", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 1},
{"data": "2024-06-10", "municipio": "Crato", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 2},
{"data": "2023-09-29", "municipio": "Tianguá", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-11-03", "municipio": "Fortaleza", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 1},
{"data": "2024-05-19", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2023-10-05", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 4},
{"data": "2024-01-27", "municipio": "Maranguape", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 5},
{"data": "2024-09-05", "municipio": "Quixadá", "doenca": "Dengue", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 4},
{"data": "2024-11-16", "municipio": "Sobral", "doenca": "Zika", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2023-12-03", "municipio": "Crato", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 1},
{"data": "2023-08-21", "municipio": "Maranguape", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 2},
{"data": "2023-06-17", "municipio": "Tianguá", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 4},
{"data": "2023-05-10", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 3},
{"data": "2024-07-15", "municipio": "Fortaleza", "doenca": "Zika", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 5},
{"data": "2024-02-23", "municipio": "Juazeiro do Norte", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 7},
{"data": "2023-09-25", "municipio": "Maracanaú", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "15 a 19 anos", "total_casos": 2},
{"data": "2024-03-17", "municipio": "Canindé", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 1},
{"data": "2024-10-20", "municipio": "Quixadá", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2023-01-08", "municipio": "Crateús", "doenca": "Dengue", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 4},
{"data": "2024-12-07", "municipio": "Russas", "doenca": "Zika", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 6},
{"data": "2023-03-19", "municipio": "Aracati", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 2},
{"data": "2023-11-02", "municipio": "Tianguá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "70 a 79 anos", "total_casos": 1},
{"data": "2024-05-12", "municipio": "Fortaleza", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "80 anos ou mais", "total_casos": 3},
{"data": "2024-09-28", "municipio": "Caucaia", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 4},
{"data": "2023-07-29", "municipio": "Juazeiro do Norte", "doenca": "Dengue", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 5},
{"data": "2024-11-10", "municipio": "Maranguape", "doenca": "Zika", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-10-05", "municipio": "Crato", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2023-08-18", "municipio": "Quixadá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 4},
{"data": "2024-01-15", "municipio": "Canindé", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 6},
{"data": "2023-12-01", "municipio": "Sobral", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 2},
{"data": "2023-05-30", "municipio": "Russas", "doenca": "Dengue", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 1},
{"data": "2024-04-04", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Masculino", "faixa": "80 anos ou mais", "total_casos": 3},
{"data": "2023-06-15", "municipio": "Crateús", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 5},
{"data": "2023-03-22", "municipio": "Fortaleza", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 4},
{"data": "2024-07-11", "municipio": "Maracanaú", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-01-19", "municipio": "Tianguá", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2024-08-08", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 6},
{"data": "2023-09-02", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 1},
{"data": "2024-02-27", "municipio": "Crato", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 4},
{"data": "2023-11-06", "municipio": "Quixadá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "70 a 79 anos", "total_casos": 3},
{"data": "2023-10-14", "municipio": "Canindé", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "80 anos ou mais", "total_casos": 2},
{"data": "2024-06-02", "municipio": "Sobral", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "0 a 4 anos", "total_casos": 1},
{"data": "2023-07-13", "municipio": "Russas", "doenca": "Dengue", "sexo": "Feminino", "faixa": "10 a 14 anos", "total_casos": 5},
{"data": "2023-12-28", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Masculino", "faixa": "20 a 29 anos", "total_casos": 7},
{"data": "2024-10-03", "municipio": "Crateús", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "30 a 39 anos", "total_casos": 6},
{"data": "2023-05-18", "municipio": "Fortaleza", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "40 a 49 anos", "total_casos": 4},
{"data": "2024-08-30", "municipio": "Maranguape", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "50 a 59 anos", "total_casos": 3},
{"data": "2023-06-28", "municipio": "Tianguá", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "60 a 69 anos", "total_casos": 2},
{"data": "2023-04-05", "municipio": "Caucaia", "doenca": "Dengue", "sexo": "Feminino", "faixa": "70 a 79 anos", "total_casos": 1},
{"data": "2024-11-19", "municipio": "Juazeiro do Norte", "doenca": "Zika", "sexo": "Masculino", "faixa": "80 anos ou mais", "total_casos": 3},
{"data": "2023-08-12", "municipio": "Crato", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "0 a 4 anos", "total_casos": 5},
{"data": "2024-01-20", "municipio": "Quixadá", "doenca": "Febre Amarela", "sexo": "Masculino", "faixa": "10 a 14 anos", "total_casos": 4},
{"data": "2023-03-15", "municipio": "Canindé", "doenca": "Febre Oropouche", "sexo": "Feminino", "faixa": "20 a 29 anos", "total_casos": 2},
{"data": "2023-11-29", "municipio": "Sobral", "doenca": "Encefalite", "sexo": "Masculino", "faixa": "30 a 39 anos", "total_casos": 3},
{"data": "2024-09-17", "municipio": "Russas", "doenca": "Dengue", "sexo": "Feminino", "faixa": "40 a 49 anos", "total_casos": 5},
{"data": "2023-12-11", "municipio": "Iguatu", "doenca": "Zika", "sexo": "Masculino", "faixa": "50 a 59 anos", "total_casos": 6},
{"data": "2024-05-09", "municipio": "Crateús", "doenca": "Chikungunya", "sexo": "Feminino", "faixa": "60 a 69 anos", "total_casos": 4}
]
"""

# Carregar e preparar os dados
@st.cache_data
def load_data():
    df = pd.read_json(dados_json)
    df.rename(columns={'data': 'Data Notificação', 'municipio': 'Município', 'doenca': 'Doença',
                       'sexo': 'Sexo', 'faixa': 'Faixa Etária', 'total_casos': 'Quantidade de casos'}, inplace=True)
    df['Data Notificação'] = pd.to_datetime(df['Data Notificação'])
    return df

df_original = load_data()

# Dicionário de cores para consistência visual
cores_doencas = {
    "Dengue": "rgb(0, 114, 178)",
    "Zika": "rgb(213, 94, 0)",
    "Chikungunya": "rgb(0, 158, 115)",
    "Febre Amarela": "rgb(240, 228, 66)",
    "Febre Oropouche": "rgb(204, 121, 167)",
    "Encefalite": "rgb(153, 153, 153)"
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

# --------------------------------------------------------------------------------
# 2. Sidebar para Filtros
# --------------------------------------------------------------------------------

st.sidebar.header("Filtros de Análise")
doencas_disponiveis = sorted(df_original['Doença'].unique())
doencas_selecionadas = st.sidebar.multiselect("Selecione as Doenças", doencas_disponiveis, default=doencas_disponiveis)
municipio_selecionado = st.sidebar.selectbox("Selecione o Município", ['Todos'] + sorted(df_original['Município'].unique()))

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

# --------------------------------------------------------------------------------
# 3. Resumo dos Dados (Melhorado)
# --------------------------------------------------------------------------------

st.header("Resumo dos Dados")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"**Total de Casos:** <br><div style='font-size: 2.5em; font-weight: bold; color: #0072B2;'>{df_filtrado['Quantidade de casos'].sum():,}</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"**Doenças Selecionadas:** <br><div style='font-size: 2.5em; font-weight: bold; color: #D55E00;'>{df_filtrado['Doença'].nunique()}</div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"**Municípios:** <br><div style='font-size: 2.5em; font-weight: bold; color: #009E73;'>{df_filtrado['Município'].nunique()}</div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"**Período de Análise:** <br><div style='font-size: 1.5em; font-weight: bold;'>{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# 4. Análise Exploratória e Comparativa (Gráficos interativos com Plotly)
# --------------------------------------------------------------------------------

st.header("Análise Exploratória")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Casos por Doença")
    casos_por_doenca_plot = df_filtrado.groupby('Doença')['Quantidade de casos'].sum().reset_index()
    fig_doenca = px.bar(casos_por_doenca_plot, x='Doença', y='Quantidade de casos',
                        color='Doença', color_discrete_map={d: cores_doencas[d] for d in doencas_disponiveis},
                        title='Total de Casos por Doença',
                        labels={'Quantidade de casos': 'Total de Casos', 'Doença': 'Doença'})
    fig_doenca.update_layout(height=400)
    st.plotly_chart(fig_doenca, use_container_width=True)

with col_b:
    st.subheader("Casos por Município")
    casos_por_municipio_plot = df_filtrado.groupby('Município')['Quantidade de casos'].sum().reset_index()
    fig_municipio = px.bar(casos_por_municipio_plot, x='Quantidade de casos', y='Município',
                           title='Municípios com Maior Incidência', orientation='h',
                           labels={'Quantidade de casos': 'Total de Casos', 'Município': 'Município'})
    fig_municipio.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_municipio, use_container_width=True)

with st.expander("Análise Detalhada por Sexo e Faixa Etária"):
    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Casos por Doença e Sexo")
        fig_sexo = px.bar(df_filtrado, y='Doença', x='Quantidade de casos', color='Sexo',
                          title='Casos por Doença e Sexo', orientation='h',
                          labels={'Quantidade de casos': 'Total de Casos'},
                          color_discrete_map={'Masculino': '#1f77b4', 'Feminino': '#ff7f0e'})
        fig_sexo.update_layout(height=400)
        st.plotly_chart(fig_sexo, use_container_width=True)

    with col_d:
        st.subheader("Casos por Doença e Faixa Etária")
        faixas_ordenadas = sorted(df_filtrado['Faixa Etária'].unique())
        fig_faixa = px.bar(df_filtrado, y='Doença', x='Quantidade de casos', color='Faixa Etária',
                           title='Casos por Doença e Faixa Etária', orientation='h',
                           category_orders={'Faixa Etária': faixas_ordenadas},
                           labels={'Quantidade de casos': 'Total de Casos'},
                           color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_faixa.update_layout(height=400)
        st.plotly_chart(fig_faixa, use_container_width=True)


# --------------------------------------------------------------------------------
# 5. Tendências e Correlação (Melhorado)
# --------------------------------------------------------------------------------

st.header("Tendências Temporais e Correlação")

with st.expander("Tendência Temporal de Casos"):
    st.subheader("Tendência Temporal de Casos por Doença (Interativo)")
    casos_por_data_doenca = df_filtrado.groupby([pd.Grouper(key='Data Notificação', freq='M'), 'Doença'])['Quantidade de casos'].sum().reset_index()
    fig_tendencia = px.line(casos_por_data_doenca, x='Data Notificação', y='Quantidade de casos', color='Doença',
                           title='Tendência de Casos ao Longo do Tempo',
                           color_discrete_map={d: cores_doencas[d] for d in doencas_disponiveis})
    st.plotly_chart(fig_tendencia, use_container_width=True)

with st.expander("Matriz de Correlação entre Doenças"):
    st.subheader("Matriz de Correlação entre Doenças")
    casos_pivot = df_original.pivot_table(index='Data Notificação', columns='Doença', values='Quantidade de casos', fill_value=0, aggfunc='sum')
    if casos_pivot.shape[0] > 1 and casos_pivot.shape[1] > 1:
        # Filtra a matriz para incluir apenas as doenças selecionadas
        matriz_correlacao = casos_pivot[doencas_selecionadas].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(matriz_correlacao, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        ax.set_title('Matriz de Correlação entre Doenças (filtrada)')
        st.pyplot(fig)
    else:
        st.warning("Não há dados suficientes ou doenças selecionadas para calcular uma matriz de correlação significativa.")

# --------------------------------------------------------------------------------
# 6. Análise Geográfica com Mapas (Melhorado com st.map e Pydeck)
# --------------------------------------------------------------------------------

st.header("Análise Geográfica")

# Adicionar coordenadas ao DataFrame
df_com_coords = df_filtrado.copy()
df_com_coords['Latitude'] = df_com_coords['Município'].map(lambda x: coordenadas_ceara.get(x, [None, None])[0])
df_com_coords['Longitude'] = df_com_coords['Município'].map(lambda x: coordenadas_ceara.get(x, [None, None])[1])
df_com_coords.dropna(subset=['Latitude', 'Longitude'], inplace=True)

if not df_com_coords.empty:
    df_mapa = df_com_coords.groupby(['Município', 'Latitude', 'Longitude', 'Doença'])['Quantidade de casos'].sum().reset_index()

    st.subheader("Mapa de Incidência por Município (Cores por Doença)")
    # Atribui a cor predominante da doença a cada ponto do mapa
    df_mapa['cor_hex'] = df_mapa['Doença'].map(cores_doencas)
    df_mapa[['r', 'g', 'b']] = df_mapa['cor_hex'].str.extract(r'rgb\((\d+), (\d+), (\d+)\)').astype(int)

    st.map(df_mapa,
           latitude='Latitude',
           longitude='Longitude',
           size='Quantidade de casos',
           color='cor_hex')


    st.subheader("Mapa de Calor (Gradiente de Cor por Incidência)")

    # Criação do mapa de calor com Pydeck para personalização de cores
    if len(doencas_selecionadas) == 1:
        # Mapa com gradiente de uma única cor para uma doença selecionada
        doenca_unica = doencas_selecionadas[0]
        cor_base = list(map(int, cores_doencas[doenca_unica].strip('rgb()').split(',')))
        color_range = [
            [cor_base[0], cor_base[1], cor_base[2], 0],
            [cor_base[0], cor_base[1], cor_base[2], 50],
            [cor_base[0], cor_base[1], cor_base[2], 100],
            [cor_base[0], cor_base[1], cor_base[2], 150],
            [cor_base[0], cor_base[1], cor_base[2], 200],
            [cor_base[0], cor_base[1], cor_base[2], 255]
        ]
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df_com_coords,
            get_position="[Longitude, Latitude]",
            aggregation='SUM',
            get_weight="Quantidade de casos",
            opacity=0.8,
            color_range=color_range,
        )
    else:
        # Mapa de calor padrão com múltiplas doenças
        layer = pdk.Layer(
            "HeatmapLayer",
            data=df_com_coords,
            get_position="[Longitude, Latitude]",
            aggregation='SUM',
            get_weight="Quantidade de casos",
            opacity=0.8
        )

    # Configuração da visualização do mapa com Pydeck
    view_state = pdk.ViewState(
        latitude=df_com_coords['Latitude'].mean(),
        longitude=df_com_coords['Longitude'].mean(),
        zoom=7,
        pitch=50,
    )

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        map_style='mapbox://styles/mapbox/light-v9'
    )

    st.pydeck_chart(r)

else:
    st.warning("Nenhum dado com coordenadas geográficas disponível para mapeamento com os filtros selecionados.")


# Fim do script
st.markdown("---")
st.markdown("Desenvolvido para análise epidemiológica.")
