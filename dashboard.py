import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Dashboard Socioeconômico",
    page_icon="🏘️",
    layout="wide"
)

# ==================== CARREGAR DADOS ====================
@st.cache_data
def carregar_dados():
    # IMPORTANTE: Substitua pelo caminho do seu arquivo Excel
    df = pd.read_excel('teste2-conteudo.xlsx')  
    
    # Recriar variáveis se necessário
    if 'num_banheiros' not in df.columns:
        df['num_banheiros'] = df['Quantos banheiros possuem na sua residência?'].str.extract(r'(\d+)').astype(float).fillna(0)
        df['num_chuveiros'] = df['Quantos chuveiros possuem na sua residência?'].str.extract(r'(\d+)').astype(float).fillna(0)
        df['num_torneiras'] = df['Quantas torneiras possuem na residência?'].str.extract(r'(\d+)').astype(float).fillna(0)
        df['capacidade_litros'] = df['Qual a capacidade de armazenamento em média?'].str.extract(r'(\d+)').astype(float).fillna(0)
    
    if 'indice_saneamento' not in df.columns:
        df['indice_saneamento'] = (
            (df['num_banheiros'] / df['num_banheiros'].max() * 2.5) +
            (df['num_torneiras'] / df['num_torneiras'].max() * 2.5) +
            (df['capacidade_litros'] / df['capacidade_litros'].max() * 2.5) +
            (df['num_chuveiros'] / df['num_chuveiros'].max() * 2.5)
        )
    
    if 'vulnerabilidade' not in df.columns:
        df['vulnerabilidade'] = 0
        df.loc[df['OBSERVAÇÃO DO ENTREVISTADOR: Padrão de acabamento do imóvel'].str.contains(
            r'sem reboco|madeira|tijolo aparente', case=False, na=False), 'vulnerabilidade'] += 4
        df.loc[df['Escolaridade'] == 'Não alfabetizado', 'vulnerabilidade'] += 3
        df.loc[df['Qual a sua ocupação'] == 'Desempregado', 'vulnerabilidade'] += 3
        df.loc[df['num_banheiros'] == 0, 'vulnerabilidade'] += 3
    
    return df

# Carregar dados
df = carregar_dados()

# ==================== HEADER ====================
st.title("🏘️ Dashboard de Análise Socioeconômica e Infraestrutura Urbana")
st.markdown("---")

# ==================== MÉTRICAS PRINCIPAIS ====================
st.header("📊 Indicadores Gerais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total de Entrevistas",
        value=len(df),
        delta=f"{df['Zona'].nunique()} zonas"
    )

with col2:
    cobertura_esgoto = (df['Tem coleta de esgoto?'] == 'Sim').mean() * 100
    st.metric(
        label="Cobertura de Esgoto",
        value=f"{cobertura_esgoto:.1f}%",
        delta=f"{cobertura_esgoto - 54:.1f}% vs média nacional",
        delta_color="inverse"
    )

with col3:
    sem_banheiro = (df['num_banheiros'] == 0).sum()
    st.metric(
        label="Residências SEM Banheiro",
        value=sem_banheiro,
        delta=f"{sem_banheiro/len(df)*100:.1f}% do total",
        delta_color="inverse"
    )

with col4:
    vulnerabilidade_media = df['vulnerabilidade'].mean()
    st.metric(
        label="Vulnerabilidade Média",
        value=f"{vulnerabilidade_media:.2f}/10",
        delta="Escala 0-10"
    )

st.markdown("---")

# ==================== FILTRO LATERAL ====================
st.sidebar.header("🔍 Filtros")
zona_selecionada = st.sidebar.multiselect(
    "Selecione a(s) Zona(s):",
    options=df['Zona'].unique(),
    default=df['Zona'].unique()
)

# Filtrar dados
df_filtrado = df[df['Zona'].isin(zona_selecionada)]

st.sidebar.markdown(f"**{len(df_filtrado)} registros** selecionados")

# ==================== GRÁFICOS ====================
st.header("📈 Visualizações")

# Abas para organizar os gráficos
tab1, tab2, tab3, tab4 = st.tabs(["🚰 Serviços Básicos", "📍 Por Zona", "👥 Perfil Social", "🎯 Priorização"])

# TAB 1: Serviços Básicos
with tab1:
    st.subheader("Cobertura de Serviços Básicos de Infraestrutura")
    
    servicos = {
        'Água\nEncanada': (df_filtrado['Tem água encanada?'] == 'Sim').mean() * 100,
        'Coleta de\nEsgoto': (df_filtrado['Tem coleta de esgoto?'] == 'Sim').mean() * 100,
        'Coleta de\nLixo': (df_filtrado['Tem coleta de lixo?'] == 'Sim').mean() * 100,
        'Energia\nRegularizada': (df_filtrado['Tem energia elétrica regularizada?'] == 'Sim').mean() * 100
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    cores = ['#e74c3c', '#c0392b', '#27ae60', '#2ecc71']
    bars = ax.bar(servicos.keys(), servicos.values(), color=cores, edgecolor='black', linewidth=1.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1.5,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax.set_ylabel('Cobertura (%)', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)

# TAB 2: Por Zona
with tab2:
    st.subheader("Cobertura de Água e Esgoto por Zona")
    
    zonas_plot = df_filtrado['Zona'].unique()
    agua_por_zona = [(df_filtrado[df_filtrado['Zona']==z]['Tem água encanada?'] == 'Sim').mean()*100 for z in zonas_plot]
    esgoto_por_zona = [(df_filtrado[df_filtrado['Zona']==z]['Tem coleta de esgoto?'] == 'Sim').mean()*100 for z in zonas_plot]
    
    x = np.arange(len(zonas_plot))
    largura = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - largura/2, agua_por_zona, largura, label='Água Encanada', color='#3498db', edgecolor='black')
    bars2 = ax.bar(x + largura/2, esgoto_por_zona, largura, label='Coleta de Esgoto', color='#e74c3c', edgecolor='black')
    
    ax.set_ylabel('Cobertura (%)', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(zonas_plot)
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)

# TAB 3: Perfil Social
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição de Escolaridade")
        escolaridade = df_filtrado['Escolaridade'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(escolaridade.values, labels=escolaridade.index, autopct='%1.1f%%', startangle=90)
        ax.set_title('Escolaridade', fontweight='bold')
        st.pyplot(fig)
    
    with col2:
        st.subheader("Situação Ocupacional")
        ocupacao = df_filtrado['Qual a sua ocupação'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.barh(ocupacao.index, ocupacao.values, color=['#27ae60', '#e74c3c', '#3498db', '#95a5a6'], edgecolor='black')
        ax.set_xlabel('Quantidade', fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        st.pyplot(fig)

# TAB 4: Priorização
with tab4:
    st.subheader("Top 10 Bairros Prioritários para Intervenção")
    
    bairros_ranking = df_filtrado.groupby('Endereço (BAIRRO)').agg({
        'vulnerabilidade': 'mean',
        'num_banheiros': 'mean'
    }).round(2).sort_values('vulnerabilidade', ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    cores = plt.cm.Reds(bairros_ranking['vulnerabilidade'] / 10)
    
    ax.barh(range(len(bairros_ranking)), bairros_ranking['vulnerabilidade'], 
            color=cores, edgecolor='black', linewidth=1.5)
    ax.set_yticks(range(len(bairros_ranking)))
    ax.set_yticklabels(bairros_ranking.index, fontweight='bold')
    ax.set_xlabel('Vulnerabilidade (0-10)', fontweight='bold')
    ax.set_xlim(0, 10)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    st.pyplot(fig)

st.markdown("---")
st.caption("Dashboard desenvolvido com Streamlit | Análise de Infraestrutura Urbana")
