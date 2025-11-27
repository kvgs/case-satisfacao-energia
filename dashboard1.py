import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== 
# CONFIGURAÇÃO DA PÁGINA
# ====================
st.set_page_config(
    page_title="Análise de Satisfação - Energia Elétrica",
    page_icon="⚡",
    layout="wide"
)

# ==================== 
# CARREGAR DADOS
# ====================
@st.cache_data
def load_data():
    df = pd.read_csv('dados_processados.csv', encoding='utf-8-sig')
    
    # Renomear coluna de satisfação se necessário
    col_satisfacao = [col for col in df.columns if 'satisfação geral' in col.lower()]
    if len(col_satisfacao) > 0:
        df = df.rename(columns={col_satisfacao[0]: 'SATISFACAO_GERAL'})
    
    # Criar Comprometimento se não existe
    if 'Comprometimento (%)' not in df.columns:
        df['Comprometimento (%)'] = (
            (df['Quanto mais ou menos você paga por mês em sua conta de luz?'] / 
             df['Qual a renda mensal da sua família?'] * 100)
            .round(2)
        )
    
    return df

try:
    df = load_data()
    st.success(f"✅ Dados carregados: {len(df)} respondentes")
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

# ==================== 
# TÍTULO E INTRODUÇÃO
# ====================
st.title("⚡ Análise de Satisfação - Energia Elétrica")
st.markdown("### Dashboard Interativo - Pesquisa de Satisfação do Cliente")
st.markdown("---")

# ==================== 
# MÉTRICAS PRINCIPAIS (KPIs)
# ====================
st.subheader("📊 Indicadores Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    satisfacao_media = df['SATISFACAO_GERAL'].mean()
    st.metric(
        "Satisfação Média", 
        f"{satisfacao_media:.1f}/10",
        delta=f"{satisfacao_media - 5:.1f} vs neutro (5.0)",
        help="Média geral de satisfação em escala de 1 a 10"
    )

with col2:
    renda_pc_media = df['Renda Per Capita'].mean()
    st.metric(
        "Renda Per Capita Média", 
        f"R$ {renda_pc_media:.0f}",
        help="Renda familiar dividida pelo número de moradores"
    )

with col3:
    comprometimento_medio = df['Comprometimento (%)'].mean()
    st.metric(
        "Comprometimento Médio", 
        f"{comprometimento_medio:.1f}%",
        delta=f"{comprometimento_medio - 10:.1f}% vs ideal (10%)",
        delta_color="inverse",
        help="Percentual da renda gasto com energia elétrica"
    )

with col4:
    pobreza_energetica = (df['Comprometimento (%)'] > 10).sum()
    pct_pobreza = (pobreza_energetica/len(df)*100)
    st.metric(
        "Pobreza Energética", 
        f"{pobreza_energetica} pessoas",
        delta=f"{pct_pobreza:.0f}% do total",
        delta_color="inverse",
        help="Pessoas que gastam mais de 10% da renda com energia"
    )

st.markdown("---")

# ==================== 
# SEÇÃO 1: PERFIL DEMOGRÁFICO
# ====================
st.subheader("👥 Perfil Demográfico da Amostra")

col1, col2 = st.columns(2)

with col1:
    # Gráfico de Gênero
    genero_data = df['Com qual gênero você se identifica?'].value_counts()
    fig_genero = px.pie(
        values=genero_data.values,
        names=genero_data.index,
        title="Distribuição por Gênero",
        color_discrete_sequence=['#FF6B6B', '#4ECDC4']
    )
    fig_genero.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_genero, use_container_width=True)
    
    # Gráfico de Escolaridade
    escolaridade_data = df['Qual é o seu grau de escolaridade?'].value_counts()
    fig_escolaridade = px.bar(
        x=escolaridade_data.values,
        y=escolaridade_data.index,
        orientation='h',
        title="Distribuição por Escolaridade",
        labels={'x': 'Quantidade', 'y': 'Escolaridade'},
        color=escolaridade_data.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_escolaridade, use_container_width=True)

with col2:
    # Gráfico de Faixa Etária
    idade_data = df['Qual é a sua idade?'].value_counts().sort_index()
    fig_idade = px.bar(
        x=idade_data.index,
        y=idade_data.values,
        title="Distribuição por Faixa Etária",
        labels={'x': 'Faixa Etária', 'y': 'Quantidade'},
        color=idade_data.values,
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_idade, use_container_width=True)
    
    # Gráfico de Estados
    estado_data = df['ESTADO'].value_counts()
    fig_estado = px.bar(
        x=estado_data.index,
        y=estado_data.values,
        title="Distribuição por Estado",
        labels={'x': 'Estado', 'y': 'Quantidade'},
        color=estado_data.values,
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig_estado, use_container_width=True)

st.markdown("---")

# ==================== 
# SEÇÃO 2: ANÁLISE DE RENDA
# ====================
st.subheader("💰 Análise de Renda")

col1, col2 = st.columns(2)

with col1:
    # Distribuição de Renda Familiar
    fig_renda = px.histogram(
        df,
        x='Qual a renda mensal da sua família?',
        nbins=30,
        title="Distribuição de Renda Familiar",
        labels={'x': 'Renda Mensal (R$)', 'y': 'Frequência'},
        color_discrete_sequence=['#95E1D3']
    )
    fig_renda.add_vline(
        x=df['Qual a renda mensal da sua família?'].median(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mediana: R$ {df['Qual a renda mensal da sua família?'].median():.0f}"
    )
    st.plotly_chart(fig_renda, use_container_width=True)
    
    # Distribuição por Faixa de Renda
    faixa_renda_order = [
        'Até 600', 'De 601 a 1500', 'De 1501 a 2000', 'De 2001 a 2500',
        'De 2501 a 3000', 'De 3001 a 3500', 'De 3501 a 4000',
        'De 4001 a 4500', 'De 4501 a 5000', 'Acima de 5000'
    ]
    faixa_data = df['Faixa Renda'].value_counts()
    faixa_data_sorted = faixa_data.reindex([f for f in faixa_renda_order if f in faixa_data.index])
    
    fig_faixa = px.bar(
        x=faixa_data_sorted.index,
        y=faixa_data_sorted.values,
        title="Distribuição por Faixa de Renda",
        labels={'x': 'Faixa de Renda', 'y': 'Quantidade'},
        color=faixa_data_sorted.values,
        color_continuous_scale='Teal'
    )
    fig_faixa.update_xaxes(tickangle=45)  # ← CORRIGIDO
    st.plotly_chart(fig_faixa, use_container_width=True)

with col2:
    # Renda Per Capita
    fig_renda_pc = px.box(
        df,
        y='Renda Per Capita',
        title="Distribuição de Renda Per Capita",
        labels={'y': 'Renda Per Capita (R$)'},
        color_discrete_sequence=['#F38181']
    )
    fig_renda_pc.add_hline(
        y=df['Renda Per Capita'].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média: R$ {df['Renda Per Capita'].mean():.0f}"
    )
    st.plotly_chart(fig_renda_pc, use_container_width=True)
    
    # Comprometimento por Faixa de Renda
    comp_por_faixa = df.groupby('Faixa Renda')['Comprometimento (%)'].mean()
    comp_por_faixa_sorted = comp_por_faixa.reindex([f for f in faixa_renda_order if f in comp_por_faixa.index])
    
    fig_comp = px.bar(
        x=comp_por_faixa_sorted.index,
        y=comp_por_faixa_sorted.values,
        title="Comprometimento Médio por Faixa de Renda",
        labels={'x': 'Faixa de Renda', 'y': 'Comprometimento (%)'},
        color=comp_por_faixa_sorted.values,
        color_continuous_scale='RdYlGn_r'
    )
    fig_comp.add_hline(
        y=10,
        line_dash="dash",
        line_color="red",
        annotation_text="Limite ideal: 10%"
    )
    fig_comp.update_xaxes(tickangle=45)  # ← CORRIGIDO
    st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")

# ==================== 
# SEÇÃO 3: ANÁLISE DE SATISFAÇÃO
# ====================
st.subheader("😊 Análise de Satisfação")

col1, col2 = st.columns(2)

with col1:
    # Distribuição de Satisfação Geral
    satisfacao_counts = df['SATISFACAO_GERAL'].value_counts().sort_index()
    
    fig_sat = px.bar(
        x=satisfacao_counts.index,
        y=satisfacao_counts.values,
        title="Distribuição de Notas de Satisfação Geral",
        labels={'x': 'Nota', 'y': 'Quantidade'},
        color=satisfacao_counts.index,
        color_continuous_scale='RdYlGn'
    )
    fig_sat.add_vline(
        x=df['SATISFACAO_GERAL'].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média: {df['SATISFACAO_GERAL'].mean():.1f}"
    )
    st.plotly_chart(fig_sat, use_container_width=True)
    
    # Satisfação por Escolaridade
    sat_escolaridade = df.groupby('Qual é o seu grau de escolaridade?')['SATISFACAO_GERAL'].mean().sort_values()
    
    fig_sat_esc = px.bar(
        x=sat_escolaridade.values,
        y=sat_escolaridade.index,
        orientation='h',
        title="Satisfação Média por Escolaridade",
        labels={'x': 'Satisfação Média', 'y': 'Escolaridade'},
        color=sat_escolaridade.values,
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_sat_esc, use_container_width=True)

with col2:
    # Satisfação por Faixa de Renda
    sat_por_faixa = df.groupby('Faixa Renda')['SATISFACAO_GERAL'].mean()
    sat_por_faixa_sorted = sat_por_faixa.reindex([f for f in faixa_renda_order if f in sat_por_faixa.index])
    
    fig_sat_renda = px.bar(
        x=sat_por_faixa_sorted.index,
        y=sat_por_faixa_sorted.values,
        title="Satisfação Média por Faixa de Renda",
        labels={'x': 'Faixa de Renda', 'y': 'Satisfação Média'},
        color=sat_por_faixa_sorted.values,
        color_continuous_scale='Viridis'
    )
    fig_sat_renda.add_hline(
        y=df['SATISFACAO_GERAL'].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média geral: {df['SATISFACAO_GERAL'].mean():.1f}"
    )
    fig_sat_renda.update_xaxes(tickangle=45)  # ← CORRIGIDO
    st.plotly_chart(fig_sat_renda, use_container_width=True)
    
    # Satisfação por Estado
    sat_estado = df.groupby('ESTADO')['SATISFACAO_GERAL'].mean().sort_values()
    
    fig_sat_estado = px.bar(
        x=sat_estado.index,
        y=sat_estado.values,
        title="Satisfação Média por Estado",
        labels={'x': 'Estado', 'y': 'Satisfação Média'},
        color=sat_estado.values,
        color_continuous_scale='Oranges'
    )
    st.plotly_chart(fig_sat_estado, use_container_width=True)

st.markdown("---")

# ==================== 
# SEÇÃO 4: ANÁLISE DE VULNERABILIDADE
# ====================
st.subheader("⚠️ Análise de Vulnerabilidade")

col1, col2 = st.columns(2)

with col1:
    # Scatter: Renda Per Capita vs Comprometimento
    fig_scatter = px.scatter(
        df,
        x='Renda Per Capita',
        y='Comprometimento (%)',
        color='SATISFACAO_GERAL',
        size='Comprometimento (%)',
        title="Renda Per Capita vs Comprometimento com Energia",
        labels={
            'Renda Per Capita': 'Renda Per Capita (R$)',
            'Comprometimento (%)': 'Comprometimento (%)',
            'SATISFACAO_GERAL': 'Satisfação'
        },
        color_continuous_scale='RdYlGn',
        hover_data=['ESTADO', 'Faixa Renda']
    )
    fig_scatter.add_hline(
        y=10,
        line_dash="dash",
        line_color="red",
        annotation_text="Limite pobreza energética: 10%"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Renda Per Capita por Escolaridade
    renda_escolaridade = df.groupby('Qual é o seu grau de escolaridade?')['Renda Per Capita'].mean().sort_values()
    
    fig_renda_esc = px.bar(
        x=renda_escolaridade.values,
        y=renda_escolaridade.index,
        orientation='h',
        title="Renda Per Capita Média por Escolaridade",
        labels={'x': 'Renda Per Capita (R$)', 'y': 'Escolaridade'},
        color=renda_escolaridade.values,
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig_renda_esc, use_container_width=True)

with col2:
    # Gráfico de Pobreza Energética
    pobreza_labels = ['Pobreza Energética\n(> 10%)', 'Normal\n(≤ 10%)']
    pobreza_values = [
        (df['Comprometimento (%)'] > 10).sum(),
        (df['Comprometimento (%)'] <= 10).sum()
    ]
    
    fig_pobreza = px.pie(
        values=pobreza_values,
        names=pobreza_labels,
        title="Distribuição de Pobreza Energética",
        color_discrete_sequence=['#FF6B6B', '#4ECDC4']
    )
    fig_pobreza.update_traces(textposition='inside', textinfo='percent+label+value')
    st.plotly_chart(fig_pobreza, use_container_width=True)
    
    # Casos Extremos
    st.markdown("#### 🚨 Casos Extremos de Comprometimento")
    extremos = df.nlargest(10, 'Comprometimento (%)')[
        ['ESTADO', 'Renda Per Capita', 'Comprometimento (%)', 'SATISFACAO_GERAL']
    ]
    st.dataframe(
        extremos.style.background_gradient(cmap='Reds', subset=['Comprometimento (%)']),
        use_container_width=True
    )

st.markdown("---")

# ==================== 
# SEÇÃO 5: CORRELAÇÕES E INSIGHTS
# ====================
st.subheader("🔍 Correlações e Insights")

# Colunas de qualidade do serviço
qualidade_cols = [
    'De 1 a 10, qual nota você dá para o fornecimento de energia sem interrupção, ou seja, não faltar luz na sua casa?',
    'De 1 a 10, que nota você dá para a variação da energia, ou seja, sem ficar alternando luz forte com luz fraca na sua casa?',
    'De 1 a 10, qual nota você atribui para a rapidez na volta da energia quando falta energia na sua casa, ou seja, o tempo que leva para a energia voltar, quando falta?'
]

qualidade_cols_short = ['Sem Interrupção', 'Sem Variação', 'Rapidez na Volta']

# Calcular correlações
correlacoes = []
for col in qualidade_cols:
    corr = df[col].corr(df['SATISFACAO_GERAL'])
    correlacoes.append(corr)

# Gráfico de correlações
fig_corr = px.bar(
    x=qualidade_cols_short,
    y=correlacoes,
    title="Correlação entre Qualidade Técnica e Satisfação Geral",
    labels={'x': 'Dimensão de Qualidade', 'y': 'Correlação'},
    color=correlacoes,
    color_continuous_scale='RdBu',
    range_color=[-1, 1]
)
fig_corr.add_hline(y=0, line_dash="dash", line_color="black")
st.plotly_chart(fig_corr, use_container_width=True)

# Insights em caixas
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **💡 Insight 1: Satisfação Baixa**
    
    A satisfação média é de apenas **5.57/10** (55.7%), indicando que mais da metade dos clientes está insatisfeita com o serviço.
    """)

with col2:
    st.warning("""
    **⚠️ Insight 2: Pobreza Energética**
    
    **57% dos respondentes** gastam mais de 10% da renda com energia, caracterizando pobreza energética. Famílias mais pobres chegam a gastar **66%** da renda!
    """)

with col3:
    st.error("""
    **🚨 Insight 3: Qualidade ≠ Satisfação**
    
    A correlação entre qualidade técnica e satisfação é **praticamente ZERO** (0.069, -0.016, 0.041). O problema não é técnico, mas **econômico e de atendimento**!
    """)

st.markdown("---")

# ==================== 
# RODAPÉ
# ====================
st.markdown("### 📌 Conclusões e Recomendações")

st.markdown("""
**Principais Conclusões:**

1. **Satisfação Geral Baixa**: Com média de 5.57/10, há insatisfação significativa entre os clientes.

2. **Pobreza Energética Crítica**: 57% dos respondentes gastam mais de 10% da renda com energia, com casos extremos chegando a 82%.

3. **Inversão de Expectativa**: Famílias mais pobres estão MAIS satisfeitas (6.75/10) que famílias de renda média (4.85/10).

4. **Qualidade Técnica OK**: As notas de qualidade técnica são razoáveis (6.5, 5.6, 6.7), mas isso NÃO está impactando a satisfação geral.

5. **Desigualdade por Escolaridade**: Pessoas com ensino superior ganham 2x mais (R$ 1.862) que as de ensino médio (R$ 882).

**Recomendações:**

- 🎯 **Tarifa Social Ampliada**: Criar programas de subsídio para famílias com comprometimento > 10%
- 💰 **Revisão de Preços**: O problema principal não é técnico, é o **preço da energia**
- 📞 **Melhorar Atendimento**: Investir em canais de comunicação e atendimento ao cliente
- 🔍 **Investigar Faixa Média**: Entender por que clientes de renda média (R$ 3.500-4.000) são os MAIS insatisfeitos
- 📊 **Transparência**: Comunicar melhor os investimentos em qualidade que já estão sendo feitos
""")

st.markdown("---")
st.caption("Dashboard desenvolvido com Streamlit + Plotly | Dados: Pesquisa de Satisfação | 400 respondentes")
