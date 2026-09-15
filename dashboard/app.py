import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sheets_client import conectar_planilha, ler_aba_como_lista, ler_aba_como_matriz, escrever_dataframe_na_aba
from src.processamento import (
    lista_para_dataframe,
    adicionar_frequencia,
    montar_tabela_precos,
    adicionar_valor_esperado,
    processar_pagamentos_brutos,
    cruzar_pagamentos_com_alunos,
    adicionar_status_pagamento,
    identificar_pendentes,
    montar_mapa_turmas,
    somar_pagamentos_por_turma,
    calcular_rateio_professoras,
    explodir_pagamentos_por_turma,
    processar_chamadas,
    contar_presencas_por_aluno,
    contar_aulas_por_turma,
    calcular_percentual_presenca,
    calcular_ranking_por_turma,
    calcular_ultima_presenca,
    identificar_alunos_para_inativar,
    identificar_nomes_nao_cadastrados,
    identificar_alunos_em_risco,
    calcular_sequencia_presenca,
    calcular_receita_por_mes,
)


@st.cache_resource
def obter_planilha(sheet_id):
    return conectar_planilha(sheet_id)


st.set_page_config(page_title="Gestão de Aulas", layout="wide")

# --- CSS customizado ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0B1F3F;
    }
    .header-container {
        background-color: #16294F;
        padding: 2.5rem 1rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        text-align: center;
        border: 1px solid #26365E;
    }
    .header-title {
    color: #FFFFFF !important;
    font-size: 4.5rem !important;
    font-weight: 900 !important;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0;
    }
    .header-subtitle {
        color: #D88C9A;
        font-size: 1.1rem;
        font-weight: 700;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-top: 0.7rem;
    }

    div[data-testid="stMetric"] {
        background-color: #16294F;
        border-radius: 16px;
        padding: 1.3rem;
        border: 1px solid #26365E;
    }
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800;
    }
    
    label[data-testid="stMetricLabel"] div[data-testid="stMarkdownContainer"] p {
        color: #D3DAEA !important;
        opacity: 1 !important;
        visibility: visible !important;
        text-transform: uppercase;
        font-size: 0.85rem !important;
        letter-spacing: 1px;
        font-weight: 600 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #16294F;
        border-radius: 16px;
        border: 1px solid #26365E;
        padding: 1.2rem;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] * {
        color: #0B1F3F !important;
        font-size: 1rem !important;
    }

    h3 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 1.6rem !important;
    }
    .main p, .main label, .stMarkdown p {
        color: #D3DAEA;
    }
    hr {
        border-color: #26365E;
    }
    </style>
""", unsafe_allow_html=True)

# --- Cabeçalho ---
col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.image("dashboard/assets/logo.png", width=420)

with col_title:
    st.markdown("""
        <div class="header-container">
            <p class="header-title">Gestão de Aulas</p>
            <p class="header-subtitle">Clarinha • Julia • Maite</p>
        </div>
    """, unsafe_allow_html=True)

# --- Conexão ---
SHEET_ID = "1K3ani89aUvWf98N010dDcHhr1sYaTIcVEqFAcfknmwU"
planilha = obter_planilha(SHEET_ID)

# --- Alunos ---
alunos = ler_aba_como_lista(planilha, "alunos")
df_alunos = lista_para_dataframe(alunos)
df_alunos = adicionar_frequencia(df_alunos)

precos = ler_aba_como_lista(planilha, "precos")
tabela_precos = montar_tabela_precos(precos)
df_alunos = adicionar_valor_esperado(df_alunos, tabela_precos)

# --- Pagamentos ---
pagamentos_brutos = ler_aba_como_lista(planilha, "Respostas ao formulário pagamentos")
pagamentos_limpos = processar_pagamentos_brutos(pagamentos_brutos)
df_pagamentos = lista_para_dataframe(pagamentos_limpos)

df_completo = cruzar_pagamentos_com_alunos(df_pagamentos, df_alunos)
df_completo = adicionar_status_pagamento(df_completo)

pendentes = identificar_pendentes(df_alunos, df_completo)

# --- Rateio ---
turmas_dados = ler_aba_como_lista(planilha, "turmas")
mapa_turmas = montar_mapa_turmas(turmas_dados)

df_explodido = explodir_pagamentos_por_turma(df_completo)
totais_por_turma = somar_pagamentos_por_turma(df_explodido)
rateio = calcular_rateio_professoras(totais_por_turma, mapa_turmas)

# --- Chamada / Presença ---
chamadas_matriz = ler_aba_como_matriz(planilha, "Respostas ao formulário chamada")
chamadas_processadas = processar_chamadas(chamadas_matriz)
df_chamadas = lista_para_dataframe(chamadas_processadas)

presencas_por_aluno = contar_presencas_por_aluno(df_chamadas)
aulas_por_turma = contar_aulas_por_turma(df_chamadas)
ultima_presenca = calcular_ultima_presenca(df_chamadas)

# --- Métricas principais ---
total_arrecadado = df_completo["Valor Recebido"].sum()
total_alunos_ativos = len(df_alunos[df_alunos["status"] == "ativo"])
total_pendentes = len(pendentes)

col1, col2, col3 = st.columns(3)
col1.metric("Total Arrecadado (mês)", f"R$ {total_arrecadado:.2f}")
col2.metric("Alunos Ativos", total_alunos_ativos)
col3.metric("Pendentes", total_pendentes)

st.write("")

# --- Pendentes + Pagamentos recebidos (lado a lado) ---
col_a, col_b = st.columns(2)

with col_a:
    with st.container(border=True):
        st.subheader("📋 Alunos Pendentes")
        st.dataframe(pendentes[["nome", "turmas", "valor_esperado"]], width='stretch')

with col_b:
    with st.container(border=True):
        st.subheader("✅ Pagamentos Recebidos")
        st.dataframe(
            df_completo[["nome", "Valor Recebido", "valor_esperado", "status_pagamento"]],
            width='stretch'
        )

st.write("")

# --- Rateio ---
with st.container(border=True):
    st.subheader("💰 Rateio entre Professoras")
    col1, col2, col3 = st.columns(3)
    col1.metric("Clarinha", f"R$ {rateio.get('Clarinha', 0):.2f}")
    col2.metric("Julia", f"R$ {rateio.get('Julia', 0):.2f}")
    col3.metric("Maite", f"R$ {rateio.get('Maite', 0):.2f}")

st.write("")

# --- Presença ---
with st.container(border=True):
    st.subheader("📅 Presença")
    st.dataframe(presencas_por_aluno, width='stretch')

st.write("")

# --- Pódio geral ---
with st.container(border=True):
    st.subheader("🏆 Ranking de Presença")

    ranking_presenca = calcular_percentual_presenca(df_alunos, presencas_por_aluno, aulas_por_turma)
    top3 = ranking_presenca.head(3).reset_index(drop=True)

    if len(top3) >= 3:
        col_2, col_1, col_3 = st.columns(3)
        with col_1:
            st.markdown("### 🥇 1º Lugar")
            st.metric(top3.loc[0, "nome"], f"{top3.loc[0, 'percentual_presenca']:.0f}%")
        with col_2:
            st.markdown("### 🥈 2º Lugar")
            st.metric(top3.loc[1, "nome"], f"{top3.loc[1, 'percentual_presenca']:.0f}%")
        with col_3:
            st.markdown("### 🥉 3º Lugar")
            st.metric(top3.loc[2, "nome"], f"{top3.loc[2, 'percentual_presenca']:.0f}%")
    else:
        st.info("Ainda não há dados suficientes para montar o pódio.")

st.write("")

# --- Ranking por turma ---
with st.container(border=True):
    st.subheader("🏅 Ranking de Presença por Turma")

    rankings_por_turma = calcular_ranking_por_turma(df_alunos, df_chamadas, aulas_por_turma)

    for turma, ranking_turma in rankings_por_turma.items():
        st.markdown(f"**{turma}**")
        top3_turma = ranking_turma.head(3).reset_index(drop=True)

        if len(top3_turma) >= 1:
            cols = st.columns(len(top3_turma))
            medalhas = ["🥇", "🥈", "🥉"]
            for i, col in enumerate(cols):
                with col:
                    st.metric(f"{medalhas[i]} {top3_turma.loc[i, 'nome']}", f"{top3_turma.loc[i, 'percentual_presenca']:.0f}%")
        else:
            st.info("Sem dados suficientes ainda.")

st.write("")

# --- Avisos ---
with st.container(border=True):
    st.subheader("⚠️ Avisos")

    nomes_em_pagamentos = df_pagamentos["Nome do Aluno"].tolist()
    nomes_em_chamadas = df_chamadas["nome"].tolist()
    todos_nomes_em_uso = nomes_em_pagamentos + nomes_em_chamadas
    nao_cadastrados = identificar_nomes_nao_cadastrados(df_alunos, todos_nomes_em_uso)

    if nao_cadastrados:
        st.warning(f"Nomes não cadastrados encontrados: {', '.join(nao_cadastrados)}")
    else:
        st.success("Todos os nomes usados em pagamentos e chamadas estão cadastrados.")

    em_risco = identificar_alunos_em_risco(ultima_presenca)

    if em_risco:
        st.warning(f"Alunos sem aparecer há 2+ semanas (risco de evasão): {', '.join(em_risco)}")
    else:
        st.success("Nenhum aluno em risco de evasão no momento.")

st.write("")

# --- Sequência de presença ---
with st.container(border=True):
    st.subheader("🔥 Sequência de Presença")

    sequencias = calcular_sequencia_presenca(df_alunos, df_chamadas, aulas_por_turma)
    df_sequencias = pd.DataFrame(list(sequencias.items()), columns=["nome", "sequencia"])
    df_sequencias = df_sequencias.sort_values("sequencia", ascending=False)

    st.dataframe(df_sequencias, width='stretch')

st.write("")

# --- Receita por mês ---
with st.container(border=True):
    st.subheader("📈 Receita por Mês")

    receita_por_mes = calcular_receita_por_mes(df_completo)
    st.bar_chart(receita_por_mes)

# --- Escrita de volta no Sheets ---
colunas_pagamentos = ["nome", "Valor Recebido", "Data do Pagamento", "Mês de Referencia", "valor_esperado", "status_pagamento"]
df_pagamentos_final = df_completo[colunas_pagamentos]
escrever_dataframe_na_aba(planilha, "pagamentos", df_pagamentos_final)

colunas_presenca = ["turma", "data_aula", "nome"]
df_presenca_final = df_chamadas[colunas_presenca]
escrever_dataframe_na_aba(planilha, "presencas", df_presenca_final)