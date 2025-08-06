pip i matplotlib seaborn folium prophet
# Importação de Bibliotecas
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from prophet import Prophet
import warnings
import base64

# Ignorar avisos para um painel mais limpo
warnings.filterwarnings('ignore')

# --------------------------------------------------------------------------------
# 1. Configuração do Streamlit e Carregamento de Dados
# --------------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Painel Epidemiológico")

# Título principal do aplicativo
st.title("🔬 Painel de Análise Epidemiológica de Doenças Arboviroses")
st.markdown("Uma ferramenta interativa para análise e predição de doenças epidemiológicas com foco em visualizações, correlação e tendências.")

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
    df.rename(columns={'data': 'Data Notificação', 'municipio': 'Município', 'doenca': 'doença',
                       'sexo': 'Sexo', 'faixa': 'Faixa Etária', 'total_casos': 'Quantidade de casos'}, inplace=True)
    df['Data Notificação'] = pd.to_datetime(df['Data Notificação'])
    return df

df_original = load_data()

# Dicionário de cores para consistência visual
cores_doencas = {
    "Dengue": "#0072B2",
    "Zika": "#D55E00",
    "Chikungunya": "#009E73",
    "Febre Amarela": "#F0E442",
    "Febre Oropouche": "#CC79A7",
    "Encefalite": "#999999"
}

# Dicionário de coordenadas de municípios do Ceará
coordenadas_ceara = {
    "Fortaleza": [-3.7319, -38.5267],
    "Juazeiro do Norte": [-7.2098, -39.3175],
    "Sobral": [-3.6888, -40.3541],
    "Crato": [-7.2343, -39.4005],
    "Caucaia": [-3.7381, -38.6534],
    "Maracanaú": [-3.8732, -38.6258],
    "Itapipoca": [-3.1469, -39.5708],
    "Iguatu": [-6.3622, -39.2978],
    "Quixadá": [-4.9744, -39.0189],
    "Canindé": [-4.3547, -39.3156],
    "Crateús": [-5.1783, -40.6844],
    "Russas": [-4.9411, -37.9831],
    "Aracati": [-4.5617, -37.7694],
    "Tianguá": [-3.2167, -40.9756],
    "Maranguape": [-3.8828, -38.6811]
}

# Adicionar coordenadas ao DataFrame
df_original['Latitude'] = df_original['Município'].map(lambda x: coordenadas_ceara.get(x, [None, None])[0])
df_original['Longitude'] = df_original['Município'].map(lambda x: coordenadas_ceara.get(x, [None, None])[1])
df_com_coords = df_original.dropna(subset=['Latitude', 'Longitude'])

# --------------------------------------------------------------------------------
# 2. Sidebar para Filtros
# --------------------------------------------------------------------------------

st.sidebar.header("Filtros de Análise")
doenca_selecionada = st.sidebar.selectbox("Selecione a Doença", ['Todas'] + sorted(df_original['doença'].unique()))
municipio_selecionado = st.sidebar.selectbox("Selecione o Município", ['Todos'] + sorted(df_original['Município'].unique()))
periodos_predicao = st.sidebar.slider("Períodos para Predição (Meses)", min_value=1, max_value=12, value=6)

df_filtrado = df_original.copy()
if doenca_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['doença'] == doenca_selecionada]
if municipio_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Município'] == municipio_selecionado]

# --------------------------------------------------------------------------------
# 3. Métricas Principais
# --------------------------------------------------------------------------------

st.header("Resumo dos Dados")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Casos", f"{df_filtrado['Quantidade de casos'].sum():,}")
with col2:
    st.metric("Total de Doenças", df_filtrado['doença'].nunique())
with col3:
    st.metric("Total de Municípios", df_filtrado['Município'].nunique())
with col4:
    st.metric("Período de Análise", f"{df_filtrado['Data Notificação'].min().strftime('%Y-%m-%d')} a {df_filtrado['Data Notificação'].max().strftime('%Y-%m-%d')}")

# --------------------------------------------------------------------------------
# 4. Análise Exploratória e Comparativa
# --------------------------------------------------------------------------------

st.header("Análise Exploratória")

with st.expander("Gráficos de Distribuição de Casos"):
    col1_a, col2_a = st.columns(2)
    with col1_a:
        st.subheader("Casos por Doença")
        fig, ax = plt.subplots(figsize=(10, 6))
        casos_por_doenca_plot = df_filtrado.groupby('doença')['Quantidade de casos'].sum().sort_values(ascending=False)
        casos_por_doenca_plot.plot(kind='bar', ax=ax, color=[cores_doencas.get(d, 'gray') for d in casos_por_doenca_plot.index])
        ax.set_title('Total de Casos por Doença')
        ax.set_xlabel('Doença')
        ax.set_ylabel('Quantidade de Casos')
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)

    with col2_a:
        st.subheader("Casos por Município")
        fig, ax = plt.subplots(figsize=(10, 6))
        casos_por_municipio_plot = df_filtrado.groupby('Município')['Quantidade de casos'].sum().sort_values(ascending=False)
        casos_por_municipio_plot.plot(kind='barh', ax=ax, color=sns.color_palette("viridis", len(casos_por_municipio_plot)))
        ax.set_title('Municípios com Maior Incidência de Casos')
        ax.set_xlabel('Quantidade de Casos')
        ax.set_ylabel('Município')
        st.pyplot(fig)

with st.expander("Análise por Sexo e Faixa Etária"):
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), sharey=True)
    sns.countplot(data=df_filtrado, y='doença', hue='Sexo', ax=axes[0], palette={'Feminino': 'pink', 'Masculino': 'lightblue'})
    axes[0].set_title('Casos por Doença e Sexo')
    axes[0].set_xlabel('Quantidade de Casos')
    axes[0].set_ylabel('Doença')

    sns.countplot(data=df_filtrado, y='doença', hue='Faixa Etária', ax=axes[1], palette='tab20')
    axes[1].set_title('Casos por Doença e Faixa Etária')
    axes[1].set_xlabel('Quantidade de Casos')
    axes[1].set_ylabel('')
    axes[1].legend(title='Faixa Etária', bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

# --------------------------------------------------------------------------------
# 5. Tendências e Correlação
# --------------------------------------------------------------------------------

st.header("Tendências Temporais e Correlação")

with st.expander("Tendências de Casos ao Longo do Tempo"):
    st.subheader("Tendência Temporal de Casos por Doença")
    fig, ax = plt.subplots(figsize=(14, 8))
    casos_por_data_doenca = df_filtrado.groupby(['Data Notificação', 'doença'])['Quantidade de casos'].sum().unstack(fill_value=0)
    for doenca in casos_por_data_doenca.columns:
        ax.plot(casos_por_data_doenca.index, casos_por_data_doenca[doenca], marker='o', linestyle='-', label=doenca, color=cores_doencas.get(doenca, 'gray'))
    ax.set_title('Tendência Temporal de Casos por Doença')
    ax.set_xlabel('Data de Notificação')
    ax.set_ylabel('Quantidade de Casos')
    ax.legend(title='Doença')
    ax.grid(True)
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

with st.expander("Matriz de Correlação entre Doenças"):
    st.subheader("Matriz de Correlação")
    casos_pivot = df_original.pivot_table(index='Data Notificação', columns='doença', values='Quantidade de casos', fill_value=0, aggfunc='sum')
    if casos_pivot.shape[0] > 1 and casos_pivot.shape[1] > 1:
        matriz_correlacao = casos_pivot.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(matriz_correlacao, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
        ax.set_title('Matriz de Correlação entre Doenças')
        st.pyplot(fig)
    else:
        st.warning("Não há dados suficientes para calcular uma matriz de correlação significativa.")

# --------------------------------------------------------------------------------
# 6. Predição de Casos com Prophet
# --------------------------------------------------------------------------------

st.header("Predição de Casos com Prophet")

@st.cache_data
def run_prophet_prediction(df, doenca_nome, periodos):
    df_prophet = df.pivot_table(index='Data Notificação', columns='doença', values='Quantidade de casos', fill_value=0, aggfunc='sum')[[doenca_nome]].reset_index()
    df_prophet.columns = ['ds', 'y']
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

    if len(df_prophet) < 2:
        return None, None

    modelo = Prophet(daily_seasonality=False)
    modelo.fit(df_prophet)
    futuro = modelo.make_future_dataframe(periods=periodos, freq='M')
    previsao = modelo.predict(futuro)
    return modelo, previsao

if doenca_selecionada != 'Todas':
    modelo, previsao = run_prophet_prediction(df_original, doenca_selecionada, periodos_predicao)
    if modelo and previsao is not None:
        st.subheader(f"Previsão para {doenca_selecionada} nos Próximos {periodos_predicao} Meses")
        fig1 = modelo.plot(previsao)
        st.pyplot(fig1)

        fig2 = modelo.plot_components(previsao)
        st.pyplot(fig2)
    else:
        st.info(f"Dados insuficientes para realizar a predição para {doenca_selecionada}.")
else:
    st.info("Selecione uma doença no painel lateral para visualizar a predição.")

# --------------------------------------------------------------------------------
# 7. Análise Geográfica com Mapas
# --------------------------------------------------------------------------------

st.header("Análise Geográfica")

# Mapa de Calor
st.subheader("Mapa de Calor de Incidência")
if not df_com_coords.empty:
    m = folium.Map(location=[-5.0, -39.5], zoom_start=7)
    HeatMap(data=df_com_coords[['Latitude', 'Longitude', 'Quantidade de casos']].dropna(), radius=20).add_to(m)
    # Salvar o mapa como HTML e exibi-lo no Streamlit
    map_html = m._repr_html_()
    st.components.v1.html(map_html, height=500, width=700)
else:
    st.warning("Nenhum dado com coordenadas geográficas disponível para mapeamento.")

# Mapa de Marcadores
st.subheader("Mapa de Marcadores Detalhado")
if not df_com_coords.empty:
    m_marcadores = folium.Map(location=[-5.0, -39.5], zoom_start=7)
    for _, row in df_com_coords.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            tooltip=f"<b>Município:</b> {row['Município']}<br><b>Doença:</b> {row['doença']}<br><b>Casos:</b> {row['Quantidade de casos']}<br><b>Data:</b> {row['Data Notificação'].strftime('%Y-%m-%d')}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m_marcadores)
    map_html_marcadores = m_marcadores._repr_html_()
    st.components.v1.html(map_html_marcadores, height=500, width=700)
else:
    st.warning("Nenhum dado com coordenadas geográficas disponível para mapeamento.")

# Fim do script
st.markdown("---")
st.markdown("Desenvolvido para análise epidemiológica.")
