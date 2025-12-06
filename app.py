import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configuração da Página
st.set_page_config(page_title="Simulador Master: Creta vs BYD", layout="wide")

st.title("📈 Simulador com Reinvestimento de Economia")
st.markdown("""
Esta ferramenta simula o cenário onde **toda a economia gerada** (combustível + manutenção) 
é imediatamente **reinvestida** na mesma taxa do CDI.
""")

# --- SIDEBAR: VARIÁVEIS ---
st.sidebar.header("1. Premissas de Mercado")
taxa_cdi_anual = st.sidebar.number_input("Taxa CDI Anual (%)", value=11.25, step=0.1)
preco_gasolina = st.sidebar.number_input("Preço Gasolina (R$)", value=6.00)
preco_kwh = st.sidebar.number_input("Preço Energia (R$)", value=0.90)
anos = st.sidebar.slider("Tempo de Análise (Anos)", 1, 10, 5)

st.sidebar.header("2. Perfil de Uso")
km_mensal = st.sidebar.number_input("KM Mensal", value=1500)
pct_estrada = st.sidebar.slider("% em Estrada", 0, 100, 50)

st.sidebar.header("3. O Creta (Carro Atual)")
venda_creta = st.sidebar.number_input("Valor Venda Creta (R$)", value=75000)
consumo_creta_cid = st.sidebar.number_input("Consumo Cidade Creta (km/l)", value=8.5)
consumo_creta_est = st.sidebar.number_input("Consumo Estrada Creta (km/l)", value=11.0)
# Custos Anuais Creta
ipva_creta = st.sidebar.number_input("IPVA Creta (Anual)", value=3000)
seguro_creta = st.sidebar.number_input("Seguro Creta (Anual)", value=3800)
manut_creta = st.sidebar.number_input("Manutenção/Risco Creta (Anual)", value=6000)

st.sidebar.header("4. O BYD King (Novo)")
compra_byd = st.sidebar.number_input("Valor Compra BYD (R$)", value=145000)
consumo_byd_kwh = st.sidebar.number_input("Consumo EV (kWh/100km)", value=14.0)
consumo_byd_hibrido = st.sidebar.number_input("Consumo Híbrido Est (km/l)", value=20.0)
# Custos Anuais BYD
ipva_byd = st.sidebar.number_input("IPVA BYD (Anual)", value=5800)
seguro_byd = st.sidebar.number_input("Seguro BYD (Anual)", value=7000)
manut_byd = st.sidebar.number_input("Manutenção BYD (Anual)", value=1000)

# --- CÁLCULOS ---

# 1. Taxas e Distâncias
taxa_mensal = (1 + taxa_cdi_anual/100)**(1/12) - 1
km_cid = km_mensal * ((100-pct_estrada)/100)
km_est = km_mensal * (pct_estrada/100)

# 2. Custo Combustível Mensal
# Creta
gasto_creta_mes = ((km_cid/consumo_creta_cid) + (km_est/consumo_creta_est)) * preco_gasolina
# BYD
gasto_byd_mes = ((km_cid/100)*consumo_byd_kwh*preco_kwh) + ((km_est/consumo_byd_hibrido)*preco_gasolina)

# 3. Custo Fixo Mensalizado (Provisão)
fixo_creta_mes = (ipva_creta + seguro_creta + manut_creta) / 12
fixo_byd_mes = (ipva_byd + seguro_byd + manut_byd) / 12

# 4. Fluxo de Caixa Mensal
# A "Economia Total" é a diferença de tudo que sai do bolso
fluxo_saida_creta = gasto_creta_mes + fixo_creta_mes
fluxo_saida_byd = gasto_byd_mes + fixo_byd_mes
economia_mensal_total = fluxo_saida_creta - fluxo_saida_byd

# --- SIMULAÇÃO MÊS A MÊS ---

meses = anos * 12
saldo_comparativo = [] # Saldo da diferença patrimonial
investimento_inicial = compra_byd - venda_creta

# Começamos com um "buraco" de -70k (que é o dinheiro que tiramos do investimento)
saldo_atual = -investimento_inicial 

eixo_x = []

for m in range(meses + 1):
    eixo_x.append(m)
    saldo_comparativo.append(saldo_atual)
    
    # Lógica do Reinvestimento:
    # 1. O saldo devedor cresce (custo de oportunidade)
    # 2. A economia mensal entra abatendo esse saldo (como se fosse um aporte)
    # Matematicamente: Investir a economia é igual a abater o custo de oportunidade
    
    juros = saldo_atual * taxa_mensal
    saldo_atual = saldo_atual + juros + economia_mensal_total

# --- RESULTADOS ---

st.divider()
col1, col2, col3, col4 = st.columns(4)

col1.metric("Economia Mensal Total", f"R$ {economia_mensal_total:,.2f}", 
            help="Soma da economia de gasolina + provisão de manutenção/seguro/IPVA mensalizados.")
col2.metric("Custo Capital (Inicial)", f"R$ {-investimento_inicial:,.2f}")

saldo_final = saldo_comparativo[-1]
cor_final = "green" if saldo_final > 0 else "red"
col3.metric(f"Saldo Final em {anos} Anos", f"R$ {saldo_final:,.2f}", delta_color="normal" if saldo_final > 0 else "inverse")

payback_mes = next((i for i, x in enumerate(saldo_comparativo) if x >= 0), None)
payback_texto = f"{payback_mes} meses ({payback_mes/12:.1f} anos)" if payback_mes else "Não atingido no período"
col4.metric("Payback (Tempo de Retorno)", payback_texto)

st.divider()

# --- GRÁFICO ---

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=eixo_x, 
    y=saldo_comparativo,
    mode='lines',
    name='Diferença Patrimonial',
    fill='tozeroy',
    line=dict(color='green' if saldo_final > 0 else 'crimson', width=3)
))

fig.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Ponto de Equilíbrio (Zero)")

fig.update_layout(
    title="Evolução Patrimonial: Investindo a Economia Mensalmente",
    xaxis_title="Meses",
    yaxis_title="Saldo Acumulado (R$)",
    template="plotly_dark",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.info(f"""
**Como ler este gráfico:**
- A linha começa negativa em **R$ {-investimento_inicial:,.0f}** (o valor que você desembolsou).
- Todo mês, a linha sobe impulsionada pela **Economia Mensal de R$ {economia_mensal_total:,.2f}**.
- A inclinação da curva considera que essa economia está **rendendo juros compostos** (amortizando o custo de oportunidade).
- Se a linha cruzar o zero, a troca do carro se pagou financeiramente.
""")
