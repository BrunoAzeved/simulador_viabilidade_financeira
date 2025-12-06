import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuração da Página
st.set_page_config(page_title="Simulador: Creta vs BYD King", layout="wide")

st.title("🚗 Simulador de Viabilidade Financeira: Troca de Carro")
st.markdown("Analise o **Payback**, **ROE** e o **Custo Total de Propriedade** ajustando as variáveis abaixo.")

# --- SIDEBAR: VARIÁVEIS DE ENTRADA ---
st.sidebar.header("1. Perfil de Uso")
km_mensal = st.sidebar.number_input("KM Rodados por Mês", value=1500, step=50)
pct_estrada = st.sidebar.slider("% Uso em Estrada", 0, 100, 50)
pct_cidade = 100 - pct_estrada

st.sidebar.header("2. Dados Econômicos")
preco_gasolina = st.sidebar.number_input("Preço Gasolina (R$/L)", value=6.00)
preco_kwh = st.sidebar.number_input("Preço Energia (R$/kWh)", value=0.90)
taxa_cdi = st.sidebar.number_input("Taxa de Rendimento Anual (CDB %)", value=11.25) / 100

st.sidebar.header("3. Carro Atual (Ex: Creta)")
nome_carro1 = st.sidebar.text_input("Nome Carro Atual", "Hyundai Creta 1.6")
valor_venda_carro1 = st.sidebar.number_input("Valor de Venda (R$)", value=75000)
consumo_cidade_carro1 = st.sidebar.number_input(f"Consumo Cidade {nome_carro1} (km/l)", value=8.5)
consumo_estrada_carro1 = st.sidebar.number_input(f"Consumo Estrada {nome_carro1} (km/l)", value=11.0)
ipva_carro1 = st.sidebar.number_input(f"IPVA Anual {nome_carro1} (R$)", value=3000)
seguro_carro1 = st.sidebar.number_input(f"Seguro Anual {nome_carro1} (R$)", value=3800)
manutencao_carro1 = st.sidebar.number_input(f"Manutenção/Risco Anual {nome_carro1} (R$)", value=6000)

st.sidebar.header("4. Carro Novo (Ex: BYD King)")
nome_carro2 = st.sidebar.text_input("Nome Carro Novo", "BYD King GS")
valor_compra_carro2 = st.sidebar.number_input("Preço de Compra (R$)", value=145000)
consumo_ev_kwh = st.sidebar.number_input("Consumo Elétrico (kWh/100km)", value=14.0) # Aprox King
consumo_hibrido_estrada = st.sidebar.number_input(f"Consumo Híbrido Estrada (km/l)", value=20.0)
ipva_carro2 = st.sidebar.number_input(f"IPVA Anual {nome_carro2} (R$)", value=5800)
seguro_carro2 = st.sidebar.number_input(f"Seguro Anual {nome_carro2} (R$)", value=7000)
manutencao_carro2 = st.sidebar.number_input(f"Manutenção Anual {nome_carro2} (R$)", value=1000)

# --- CÁLCULOS ---

# 1. Distâncias
km_cidade = km_mensal * (pct_cidade / 100)
km_estrada = km_mensal * (pct_estrada / 100)

# 2. Custos Combustível Mensal - Carro 1 (Combustão)
custo_cidade_c1 = (km_cidade / consumo_cidade_carro1) * preco_gasolina
custo_estrada_c1 = (km_estrada / consumo_estrada_carro1) * preco_gasolina
total_combustivel_c1_mensal = custo_cidade_c1 + custo_estrada_c1

# 3. Custos Combustível Mensal - Carro 2 (PHEV)
# Assumindo cidade 100% elétrico e estrada híbrido
custo_cidade_c2 = (km_cidade / 100) * consumo_ev_kwh * preco_kwh
custo_estrada_c2 = (km_estrada / consumo_hibrido_estrada) * preco_gasolina
total_combustivel_c2_mensal = custo_cidade_c2 + custo_estrada_c2

# 4. Anualização
custo_combustivel_c1_anual = total_combustivel_c1_mensal * 12
custo_combustivel_c2_anual = total_combustivel_c2_mensal * 12
economia_combustivel_anual = custo_combustivel_c1_anual - custo_combustivel_c2_anual

# 5. Custos Fixos Totais
fixo_c1 = ipva_carro1 + seguro_carro1 + manutencao_carro1
fixo_c2 = ipva_carro2 + seguro_carro2 + manutencao_carro2
delta_fixo = fixo_c2 - fixo_c1 # Quanto o Carro 2 é mais caro nos fixos (ou mais barato se negativo)

# 6. Financeiro
investimento_necessario = valor_compra_carro2 - valor_venda_carro1
custo_oportunidade_anual = investimento_necessario * taxa_cdi

# Resultado Final (Fluxo de Caixa Líquido Anual)
# Economia Combustível + Economia Manutenção (já embutido no fixo) - Custo Fixo Extra - Custo Oportunidade
beneficio_operacional_anual = economia_combustivel_anual - delta_fixo
resultado_liquido_anual = beneficio_operacional_anual - custo_oportunidade_anual

# ROE e Payback
roe = (beneficio_operacional_anual / investimento_necessario) * 100 if investimento_necessario > 0 else 0
payback_anos = investimento_necessario / beneficio_operacional_anual if beneficio_operacional_anual > 0 else 999

# --- DASHBOARD VISUAL ---

col1, col2, col3 = st.columns(3)
col1.metric("Economia Combustível (Mês)", f"R$ {total_combustivel_c1_mensal - total_combustivel_c2_mensal:,.2f}")
col2.metric("Investimento Necessário", f"R$ {investimento_necessario:,.2f}")
col3.metric("Resultado Final Anual", f"R$ {resultado_liquido_anual:,.2f}", 
            delta_color="normal" if resultado_liquido_anual > 0 else "inverse",
            help="Considera combustível, fixos, manutenção e custo de oportunidade do dinheiro.")

st.divider()

# --- VEREDITO ---
st.subheader("🤖 Veredito da IA")

cor_veredito = "red"
texto_veredito = "MANTER O CARRO ATUAL"
if resultado_liquido_anual > 0:
    cor_veredito = "green"
    texto_veredito = f"COMPRAR O {nome_carro2.upper()}"
elif payback_anos < 8 and resultado_liquido_anual > -2000:
    cor_veredito = "orange"
    texto_veredito = f"COMPRA RACIONAL PELA SEGURANÇA (Custo financeiro baixo)"

st.markdown(f"""
    <div style="padding: 20px; background-color: {cor_veredito}; color: white; border-radius: 10px; text-align: center;">
        <h2>{texto_veredito}</h2>
        <p>ROE (Retorno Operacional): <b>{roe:.2f}%</b> a.a. | Payback Estimado: <b>{payback_anos:.1f} anos</b></p>
    </div>
""", unsafe_allow_html=True)

if resultado_liquido_anual < 0:
    st.warning(f"Nota: Financeiramente, você 'paga' R$ {abs(resultado_liquido_anual):.2f} por ano para ter o conforto/segurança do carro novo. Se esse valor for aceitável para você, ignore o financeiro puro.")

st.divider()

# --- GRÁFICOS ---
tab1, tab2 = st.tabs(["Comparativo de Custos Anuais", "Curva de Payback (Tempo)"])

with tab1:
    # Gráfico de Barras Empilhadas (Composição do Custo)
    dados_custo = pd.DataFrame({
        "Carro": [nome_carro1, nome_carro2],
        "Combustível": [custo_combustivel_c1_anual, custo_combustivel_c2_anual],
        "Seguro/IPVA": [ipva_carro1 + seguro_carro1, ipva_carro2 + seguro_carro2],
        "Manutenção/Risco": [manutencao_carro1, manutencao_carro2],
        "Custo Oportunidade (Capital)": [0, custo_oportunidade_anual]
    })
    
    fig_bar = px.bar(dados_custo, x="Carro", y=["Combustível", "Seguro/IPVA", "Manutenção/Risco", "Custo Oportunidade (Capital)"],
                     title="Composição do Custo Total Anual (TCO)",
                     labels={"value": "Custo Anual (R$)", "variable": "Tipo de Despesa"})
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    # Gráfico de Linha (Payback)
    anos = list(range(0, 11))
    fluxo_acumulado = []
    
    saldo = -investimento_necessario
    for ano in anos:
        if ano == 0:
            fluxo_acumulado.append(saldo)
        else:
            saldo += beneficio_operacional_anual # Adiciona a economia operacional anual
            fluxo_acumulado.append(saldo)
            
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=anos, y=fluxo_acumulado, mode='lines+markers', name='Saldo Acumulado'))
    fig_line.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Ponto de Equilíbrio (Zero)")
    
    fig_line.update_layout(title="Curva de Recuperação do Investimento (Sem considerar Rendimento Financeiro)",
                           xaxis_title="Anos", yaxis_title="Saldo Financeiro (R$)")
    st.plotly_chart(fig_line, use_container_width=True)
    st.caption("*Este gráfico mostra em quanto tempo a economia de combustível/manutenção paga a diferença de preço do carro, ignorando juros compostos.")
