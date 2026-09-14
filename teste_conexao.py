from src.sheets_client import (
    conectar_planilha,
    ler_aba_como_lista,
    ler_aba_como_matriz,
    escrever_dataframe_na_aba,
)
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
    calcular_ultima_presenca,
    identificar_alunos_para_inativar,
    calcular_ranking_por_turma,
    identificar_nomes_nao_cadastrados,
    identificar_alunos_em_risco,
    calcular_sequencia_presenca,
)

SHEET_ID = "1K3ani89aUvWf98N010dDcHhr1sYaTIcVEqFAcfknmwU"

planilha = conectar_planilha(SHEET_ID)

# --- Alunos ---
alunos = ler_aba_como_lista(planilha, "alunos")
df_alunos = lista_para_dataframe(alunos)
df_alunos = adicionar_frequencia(df_alunos)

precos = ler_aba_como_lista(planilha, "precos")
tabela_precos = montar_tabela_precos(precos)
df_alunos = adicionar_valor_esperado(df_alunos, tabela_precos)

print(df_alunos)

# --- Pagamentos ---
pagamentos_brutos = ler_aba_como_lista(planilha, "Respostas ao formulário pagamentos")
pagamentos_limpos = processar_pagamentos_brutos(pagamentos_brutos)
df_pagamentos = lista_para_dataframe(pagamentos_limpos)

df_completo = cruzar_pagamentos_com_alunos(df_pagamentos, df_alunos)
df_completo = adicionar_status_pagamento(df_completo)
print(df_completo[["nome", "Valor Recebido", "valor_esperado", "status_pagamento"]])

pendentes = identificar_pendentes(df_alunos, df_completo)
print("Alunos pendentes esse mês:")
print(pendentes[["nome", "turmas", "valor_esperado"]])

# --- Rateio (com explosão de turmas múltiplas) ---
turmas_dados = ler_aba_como_lista(planilha, "turmas")
mapa_turmas = montar_mapa_turmas(turmas_dados)
print("Mapa de turmas:", mapa_turmas)

df_explodido = explodir_pagamentos_por_turma(df_completo)
totais_por_turma = somar_pagamentos_por_turma(df_explodido)
print("Total arrecadado por turma:")
print(totais_por_turma)

rateio = calcular_rateio_professoras(totais_por_turma, mapa_turmas)
print("Rateio entre professoras:")
print(rateio)

# --- Chamada ---
chamadas_matriz = ler_aba_como_matriz(planilha, "Respostas ao formulário chamada")
print("Matriz de chamadas crua:")
for i, linha in enumerate(chamadas_matriz):
    print(i, linha)
chamadas_processadas = processar_chamadas(chamadas_matriz)

df_chamadas = lista_para_dataframe(chamadas_processadas)
presencas_por_aluno = contar_presencas_por_aluno(df_chamadas)
print("Presenças por aluno:")
print(presencas_por_aluno)

ultima_presenca = calcular_ultima_presenca(df_chamadas)
print("Última presença por aluno:")
print(ultima_presenca)

alunos_para_inativar = identificar_alunos_para_inativar(ultima_presenca)
print("Alunos que deveriam ficar inativos (4+ semanas sem aparecer):")
print(alunos_para_inativar)

# --- Escrita de volta no Sheets ---
colunas_pagamentos = ["nome", "Valor Recebido", "Data do Pagamento", "Mês de Referencia", "valor_esperado", "status_pagamento"]
df_pagamentos_final = df_completo[colunas_pagamentos]

escrever_dataframe_na_aba(planilha, "pagamentos", df_pagamentos_final)
print("Aba 'pagamentos' atualizada com sucesso!")

# --- Escrita da presença no Sheets ---
colunas_presenca = ["turma", "data_aula", "nome"]
df_presenca_final = df_chamadas[colunas_presenca]

escrever_dataframe_na_aba(planilha, "presencas", df_presenca_final)
print("Aba 'presencas' atualizada com sucesso!")

from src.processamento import contar_aulas_por_turma, calcular_percentual_presenca

# ... código existente

aulas_por_turma = contar_aulas_por_turma(df_chamadas)
print("Aulas por turma:", aulas_por_turma)

ranking_presenca = calcular_percentual_presenca(df_alunos, presencas_por_aluno, aulas_por_turma)
print("Ranking de presença:")
print(ranking_presenca)

print("Aulas por turma:", aulas_por_turma)
print(ranking_presenca)

rankings_por_turma = calcular_ranking_por_turma(df_alunos, df_chamadas, aulas_por_turma)
for turma, ranking in rankings_por_turma.items():
    print(f"\nRanking - {turma}")
    print(ranking)

print("Valores únicos em df_chamadas['turma']:", df_chamadas["turma"].unique())
print("Valores em aulas_por_turma.index:", list(aulas_por_turma.index))  

nomes_em_pagamentos = df_pagamentos["Nome do Aluno"].tolist()
nomes_em_chamadas = df_chamadas["nome"].tolist()
todos_nomes_em_uso = nomes_em_pagamentos + nomes_em_chamadas

nao_cadastrados = identificar_nomes_nao_cadastrados(df_alunos, todos_nomes_em_uso)
print("Nomes não cadastrados:", nao_cadastrados)

em_risco = identificar_alunos_em_risco(ultima_presenca)
print("Alunos em risco de evasão:", em_risco)

sequencias = calcular_sequencia_presenca(df_alunos, df_chamadas, aulas_por_turma)
print("Sequências de presença:", sequencias)

print(df_chamadas["data_aula"].unique())