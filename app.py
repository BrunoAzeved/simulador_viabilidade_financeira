import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Compra vs. Assinatura de Carro", layout="wide")

st.title("🚗 Comparador: Comprar ou Assinar?")
st.markdown("""
Esta ferramenta compara o custo total de propriedade de um carro comprado (à vista ou financiado) 
versus o custo de um serviço de assinatura mensal, considerando o **custo de oportunidade** do seu dinheiro.
""")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("🔧 Parâmetros de Comparação")
meses = st.sidebar.slider("Período da análise (meses)", 12, 60, 36)
taxa_selic = st.sidebar.number_input("Rendimento mensal esperado do investimento (%)", value=0.8, step=0.1) / 100

st.sidebar.subheader("💰 Cenário: Compra")
valor_carro = st.sidebar.number_input("Preço do carro (R$)", value=100000)
entrada = st.sidebar.number_input("Valor da entrada (ou valor total se à vista) (R$)", value=100000)
depreciacao_anual = st.sidebar.number_input("Depreciação anual estimada (%)", value=10.0) / 100

# Custos recorrentes da compra
ipva_anual = st.sidebar.number_input("IPVA + Licenciamento anual (R$)", value=4000)
seguro_anual = st.sidebar.number_input("Seguro anual (R$)", value=3500)
manutencao_anual = st.sidebar.number_input("Manutenção/Revisão anual (R$)", value=1500)

st.sidebar.subheader("🏢 Cenário: Assinatura")
mensalidade_assinatura = st.sidebar.number_input("Valor da mensalidade (R$)", value=2500)
taxa_adesao = st.sidebar.number_input("Taxa de adesão/inicial (R$)", value=0)

# --- CÁLCULOS ---

# 1. Cálculo Compra
custo_recorrente_mensal_compra = (ipva_anual + seguro_anual + manutencao_anual) / 12
valor_final_carro = valor_carro * ((1 - depreciacao_anual) ** (meses / 12))

# Custo de oportunidade (se o valor da entrada estivesse investido)
valor_investido_acumulado = entrada * ((1 + taxa_selic) ** meses)
custo_oportunidade_entrada = valor_investido_acumulado - entrada

total_gasto_compra = (custo_recorrente_mensal_compra * meses) + (valor_carro - entrada) # simplificado sem juros de financiamento
total_perda_compra = (valor_carro - valor_final_carro) + (custo_recorrente_mensal_compra * meses) + custo_oportunidade_entrada

# 2. Cálculo Assinatura
total_gasto_assinatura = taxa_adesao + (mensalidade_assinatura * meses)
# Custo de oportunidade da assinatura: O que você faria com o dinheiro da ENTRADA se não comprasse o carro
rendimento_capital_na_assinatura = entrada * ((1 + taxa_selic) ** meses) - entrada
custo_efetivo_assinatura = total_gasto_assinatura - rendimento_capital_na_assinatura

# --- RESULTADOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Resumo de Custos (Total no Período)")
    df_compra = pd.DataFrame({
        "Categoria": ["Depreciação", "Manutenção/Taxas/Seguro", "Custo de Oportunidade"],
        "Valor (R$)": [valor_carro - valor_final_carro, custo_recorrente_mensal_compra * meses, custo_oportunidade_entrada]
    })
    st.write("**Custo Total da Compra:**")
    st.write(f"R$ {total_perda_compra:,.2f}")
    st.table(df_compra)

with col2:
    st.subheader("📊 Resumo Assinatura")
    df_assin_table = pd.DataFrame({
        "Categoria": ["Mensalidades Totais", "Taxa de Adesão", "Rendimento do Capital (Ganho)"],
        "Valor (R$)": [mensalidade_assinatura * meses, taxa_adesao, -rendimento_capital_na_assinatura]
    })
    st.write("**Custo Efetivo da Assinatura:**")
    st.write(f"R$ {custo_efetivo_assinatura:,.2f}")
    st.table(df_assin_table)

# --- GRÁFICO ---
st.divider()
st.subheader("📈 Evolução do Custo Acumulado")

meses_lista = list(range(1, meses + 1))
custo_compra_evolucao = [
    (valor_carro - (valor_carro * ((1 - depreciacao_anual) ** (m / 12)))) + 
    (custo_recorrente_mensal_compra * m) + 
    (entrada * ((1 + taxa_selic) ** m) - entrada)
    for m in meses_lista
]
custo_assinatura_evolucao = [
    (mensalidade_assinatura * m) + taxa_adesao - (entrada * ((1 + taxa_selic) ** m) - entrada)
    for m in meses_lista
]

fig = go.Figure()
fig.add_trace(go.Scatter(x=meses_lista, y=custo_compra_evolucao, name="Custo Compra (Deprec + Taxas + Oportunidade)"))
fig.add_trace(go.Scatter(x=meses_lista, y=custo_assinatura_evolucao, name="Custo Assinatura (Mensalidade - Rendimento)"))

fig.update_layout(xaxis_title="Meses", yaxis_title="Custo Acumulado (R$)", hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

# --- CONCLUSÃO ---
st.divider()
if total_perda_compra < custo_efetivo_assinatura:
    st.success(f"✅ Financeiramente, **COMPRAR** é mais vantajoso por uma diferença de R$ {custo_efetivo_assinatura - total_perda_compra:,.2f}")
else:
    st.success(f"✅ Financeiramente, **ASSINAR** é mais vantajoso por uma diferença de R$ {total_perda_compra - custo_efetivo_assinatura:,.2f}")

st.info("""
**Nota:** Este cálculo considera que o valor que você usaria para comprar o carro ficaria investido caso você optasse pela assinatura. 
Se você não possui o dinheiro para comprar à vista e teria que financiar, a assinatura tende a ser ainda mais vantajosa devido aos juros bancários.
""")