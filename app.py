import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da Página
st.set_page_config(page_title="Simulador Avançado: Creta vs BYD", layout="wide")

st.title("🚗 Simulador Financeiro com Juros Compostos")
st.markdown("Comparativo considerando o **Custo de Oportunidade Exponencial** do capital investido.")

# --- SIDEBAR: VARIÁVEIS DE ENTRADA ---
st.sidebar.header("1. Perfil de Uso")
km_mensal = st.sidebar.number_input("KM Rodados por Mês", value=1500, step=50)
pct_estrada = st.sidebar.slider("% Uso em Estrada", 0, 100, 50)
pct_cidade = 100 - pct_estrada

st.sidebar.header("2. Dados Econômicos")
preco_gasolina = st.sidebar.number_input("Preço Gasolina (R$/L)", value=6.00)
preco_kwh = st.sidebar.number_input("Preço Energia (R$/kWh)", value=0.90)
taxa_cdi = st.sidebar.number_input("Taxa Selic/CDI Anual (%)", value=11.25) / 100
anos_analise = st.sidebar.slider("Horizonte de Análise (Anos)", 1, 15, 10)

st.sidebar.header("3. Carro Atual (Creta)")
valor_venda_carro1 = st.sidebar.number_input("Valor de Venda (R$)", value=75000)
consumo_cidade_carro1 = st.sidebar.number_input(f"Consumo Cidade Creta (km/l)", value=8.5)
consumo_estrada_carro1 = st.sidebar.number_input(f"Consumo Estrada Creta (km/l)", value=11.0)
fixo_carro1 = st.sidebar.number_input("Custo Fixo Anual Creta (IPVA+Seguro+Manut)", value=12800) 
# Soma aproximada: 3k IPVA + 3.8k Seguro + 6k Manut = 12.8k

st.sidebar.header("4. Carro Novo (BYD King)")
valor_compra_carro2 = st.sidebar.number_input("Preço de Compra (R$)", value=145000)
consumo_ev_kwh = st.sidebar.number_input("Consumo Elétrico (kWh/100km)", value=14.0)
consumo_hibrido_estrada = st.sidebar.number_input(f"Consumo Híbrido Estrada (km/l)", value=20.0)
fixo_carro2 = st.sidebar.number_input("Custo Fixo Anual BYD (IPVA+Seguro+Manut)", value=13800)
# Soma aproximada: 5.8k IPVA + 7k Seguro + 1k Manut = 13.8k

# --- CÁLCULOS OPERACIONAIS (MENSAL/ANUAL) ---

# 1. Distâncias
km_cidade = km_mensal * (pct_cidade / 100)
km_estrada = km_mensal * (pct_estrada / 100)

# 2. Custos Combustível Anual - Creta
custo_cidade_c1 = (km_cidade / consumo_cidade_carro1) * preco_gasolina
custo_estrada_c1 = (km_estrada / consumo_estrada_carro1) * preco_gasolina
total_combustivel_c1_anual = (custo_cidade_c1 + custo_estrada_c1) * 12

# 3. Custos Combustível Anual - BYD
custo_cidade_c2 = (km_cidade / 100) * consumo_ev_kwh * preco_kwh
custo_estrada_c2 = (km_estrada / consumo_hibrido_estrada) * preco_gasolina
total_combustivel_c2_anual = (custo_cidade_c2 + custo_estrada_c2) * 12

# 4. Economia Operacional Líquida
# (Economia Gasolina) - (Diferença de Custo Fixo)
economia_gasolina = total_combustivel_c1_anual - total_combustivel_c2_anual
diferenca_fixo = fixo_carro2 - fixo_carro1 # Quanto o BYD é mais caro nos fixos
beneficio_liquido_anual = economia_gasolina - diferenca_fixo

# --- CÁLCULO FINANCEIRO (JUROS COMPOSTOS) ---

investimento_inicial = valor_compra_carro2 - valor_venda_carro1

# Listas para os gráficos
anos = list(range(anos_analise + 1))
saldo_devedor = [] # O "Buraco" financeiro considerando juros
economia_acumulada_sem_juros = [] # Apenas a soma do dinheiro economizado (visão linear)
custo_oportunidade_acumulado = [] # Quanto o dinheiro teria rendido

saldo_atual = -investimento_inicial
capital_hipotetico = investimento_inicial # O dinheiro rendendo no banco

saldo_devedor.append(saldo_atual)
custo_oportunidade_acumulado.append(0)
economia_acumulada_sem_juros.append(0)

payback_encontrado = False
ano_payback = 0

for ano in range(1, anos_analise + 1):
    # 1. O Saldo Devedor cresce pelos juros (você deixou de ganhar esse rendimento)
    juros_sobre_saldo = saldo_atual * taxa_cdi
    
    # 2. Você abate do saldo a economia que fez no ano
    saldo_atual = saldo_atual + juros_sobre_saldo + beneficio_liquido_anual
    saldo_devedor.append(saldo_atual)
    
    # Verifica Payback
    if saldo_atual >= 0 and not payback_encontrado:
        payback_encontrado = True
        ano_payback = ano
        
    # Cálculos auxiliares para gráfico comparativo
    capital_hipotetico = capital_hipotetico * (1 + taxa_cdi)
    custo_oportunidade_acumulado.append(capital_hipotetico - investimento_inicial)
    economia_acumulada_sem_juros.append(beneficio_liquido_anual * ano)

# --- DASHBOARD ---

col1, col2, col3, col4 = st.columns(4)
col1.metric("Economia Gasolina (Ano)", f"R$ {economia_gasolina:,.2f}")
col2.metric("Diferença Custos Fixos (Ano)", f"R$ {diferenca_fixo:,.2f}", help="IPVA/Seguro mais caros vs Manutenção mais barata")
col3.metric("Benefício Líquido (Ano)", f"R$ {beneficio_liquido_anual:,.2f}", help="O que sobra no bolso por ano (sem contar juros)")
col4.metric("Investimento Inicial", f"R$ {investimento_inicial:,.2f}")

st.divider()

# --- VEREDITO COMPOSTO ---
st.subheader("📊 Análise de Viabilidade Real")

if payback_encontrado:
    st.success(f"✅ O carro SE PAGA em {ano_payback} anos (considerando juros compostos).")
    msg_veredito = "Financeiramente VIÁVEL a longo prazo."
else:
    st.error(f"❌ O carro NÃO SE PAGA em {anos_analise} anos.")
    msg_veredito = "Financeiramente INVIÁVEL (Os juros do investimento ganham da economia)."

st.markdown(f"""
    > **Resumo:** {msg_veredito}  
    > Para o BYD valer a pena financeiramente, a linha verde (Saldo) precisa cruzar a linha zero para cima.
    > Se a linha continuar caindo, significa que os juros sobre os R$ {investimento_inicial/1000:.0f}k crescem mais rápido do que você consegue economizar em gasolina.
""")

# --- GRÁFICOS ---

tab1, tab2 = st.tabs(["Curva de Payback Real", "Batalha: Juros vs Economia"])

with tab1:
    fig_payback = go.Figure()
    
    # Linha do Saldo
    fig_payback.add_trace(go.Scatter(
        x=anos, y=saldo_devedor, 
        mode='lines+markers', 
        name='Saldo Financeiro Real',
        line=dict(color='green' if payback_encontrado else 'red', width=4)
    ))
    
    # Linha Zero
    fig_payback.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Ponto de Equilíbrio")
    
    fig_payback.update_layout(
        title="Evolução do Saldo (Considerando Juros Compostos)",
        xaxis_title="Anos",
        yaxis_title="Saldo (R$)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_payback, use_container_width=True)
    st.caption("Nota: Se a linha aponta para baixo, o 'buraco' está aumentando: você perde mais dinheiro deixando de investir do que economiza andando.")

with tab2:
    # Gráfico comparando as forças
    fig_batalha = go.Figure()
    
    fig_batalha.add_trace(go.Scatter(
        x=anos, y=custo_oportunidade_acumulado,
        mode='lines', name='Ganho Perdido (CDB Acumulado)',
        line=dict(color='red', dash='dot'),
        fill='tozeroy'
    ))
    
    fig_batalha.add_trace(go.Scatter(
        x=anos, y=economia_acumulada_sem_juros,
        mode='lines', name='Economia Acumulada do Carro',
        line=dict(color='blue', width=3)
    ))
    
    fig_batalha.update_layout(
        title="A Batalha: O que o dinheiro renderia (Vermelho) vs. O que o carro economiza (Azul)",
        xaxis_title="Anos",
        yaxis_title="Valor Acumulado (R$)"
    )
    st.plotly_chart(fig_batalha, use_container_width=True)
    st.info("Se a área vermelha for maior que a linha azul, o banco ganha do carro.")
