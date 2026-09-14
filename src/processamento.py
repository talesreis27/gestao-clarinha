import pandas as pd
import datetime


def lista_para_dataframe(dados):
    """
    Convert a list of dictionaries into a Pandas DataFrame.

    Args:
        dados (list[dict]): Rows of data, typically from ler_aba_como_lista.

    Returns:
        pandas.DataFrame: Tabular representation of the input data.
    """
    df = pd.DataFrame(dados)
    return df


def calcular_frequencia_semanal(turmas_texto):
    """
    Calculate how many classes per week a student attends.

    Args:
        turmas_texto (str): Comma-separated class names, e.g. 
            "Terça 16h, Quarta 15h".

    Returns:
        int: The number of classes (frequency) per week.
    """
    listas_turmas = turmas_texto.split(",")
    quantidade = len(listas_turmas)
    return quantidade


def adicionar_frequencia(df):
    """
    Add a 'frequencia_semanal' column to the students DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame containing a 'turmas' column.

    Returns:
        pandas.DataFrame: The same DataFrame with an added 
            'frequencia_semanal' column.
    """
    df["frequencia_semanal"] = df["turmas"].apply(calcular_frequencia_semanal)
    return df


def montar_tabela_precos(dados_precos):
    """
    Build a price lookup dictionary from spreadsheet data.

    Args:
        dados_precos (list[dict]): Rows from the 'tabela_precos' worksheet,
            each with 'frequencia_semanal' and 'valor_mensal' keys.

    Returns:
        dict: Mapping of frequencia_semanal (int) to valor_mensal (int).
    """
    tabela = {}
    for linha in dados_precos:
        frequencia = int(linha["frequencia_semanal"])
        valor = int(linha["valor_mensal"])
        tabela[frequencia] = valor
    return tabela


def calcular_valor_esperado(frequencia, tabela_precos):
    """
    Determine the expected monthly payment based on weekly frequency.

    Args:
        frequencia (int): Number of classes per week.
        tabela_precos (dict): Mapping of frequency to expected price.

    Returns:
        int: Expected monthly payment in reais.
    """
    valor = tabela_precos.get(frequencia)
    return valor


def adicionar_valor_esperado(df, tabela_precos):
    """
    Add a 'valor_esperado' column to the students DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame containing a 'frequencia_semanal' column.
        tabela_precos (dict): Mapping of frequency to expected price.

    Returns:
        pandas.DataFrame: The same DataFrame with an added 
            'valor_esperado' column.
    """
    df["valor_esperado"] = df["frequencia_semanal"].apply(
        lambda freq: calcular_valor_esperado(freq, tabela_precos)
    )
    return df


def limpar_nomes_colunas(dados):
    """
    Strip leading/trailing whitespace from all dictionary keys.

    Args:
        dados (list[dict]): Rows of data with potentially messy column names.

    Returns:
        list[dict]: Same rows, with cleaned (stripped) column names.
    """
    dados_limpos = []
    for linha in dados:
        linha_limpa = {chave.strip(): valor for chave, valor in linha.items()}
        dados_limpos.append(linha_limpa)
    return dados_limpos


def limpar_valor_monetario(valor_texto):
    """
    Convert a Brazilian-formatted currency string into a float.

    Args:
        valor_texto (str): Currency string, e.g. "R$ 120,00".

    Returns:
        float: The numeric value, e.g. 120.0.
    """
    texto_limpo = valor_texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
    valor_numerico = float(texto_limpo)
    return valor_numerico


def processar_pagamentos_brutos(dados_brutos):
    """
    Clean raw payment data: strip column names and convert currency values.

    Args:
        dados_brutos (list[dict]): Raw rows from the payments form response sheet.

    Returns:
        list[dict]: Cleaned rows, ready to be converted into a DataFrame.
    """
    dados_limpos = limpar_nomes_colunas(dados_brutos)
    for linha in dados_limpos:
        linha["Valor Recebido"] = limpar_valor_monetario(linha["Valor Recebido"])
    return dados_limpos


def cruzar_pagamentos_com_alunos(df_pagamentos, df_alunos):
    """
    Merge payment records with student data to compare expected vs paid values.

    Args:
        df_pagamentos (pandas.DataFrame): Cleaned payments DataFrame, 
            containing a 'Nome do Aluno' column.
        df_alunos (pandas.DataFrame): Students DataFrame, containing 
            'nome' and 'valor_esperado' columns.

    Returns:
        pandas.DataFrame: Merged DataFrame with both payment and student data.
    """
    df_pagamentos = df_pagamentos.rename(columns={"Nome do Aluno": "nome"})
    df_completo = df_pagamentos.merge(df_alunos, on="nome", how="left")
    return df_completo


def classificar_pagamento(valor_recebido, valor_esperado):
    """
    Classify a payment as correct, underpaid, or overpaid.

    Args:
        valor_recebido (float): The amount actually received.
        valor_esperado (float): The amount expected based on pricing rules.

    Returns:
        str: One of "correto", "a_menor", or "a_maior".
    """
    if valor_recebido == valor_esperado:
        status = "correto"
    elif valor_recebido < valor_esperado:
        status = "a_menor"
    else:
        status = "a_maior"
    return status


def adicionar_status_pagamento(df):
    """
    Add a 'status_pagamento' column comparing received vs expected values.

    Args:
        df (pandas.DataFrame): Merged DataFrame with 'Valor Recebido' 
            and 'valor_esperado' columns.

    Returns:
        pandas.DataFrame: The same DataFrame with an added 
            'status_pagamento' column.
    """
    df["status_pagamento"] = df.apply(
        lambda linha: classificar_pagamento(linha["Valor Recebido"], linha["valor_esperado"]),
        axis=1
    )
    return df


def identificar_pendentes(df_alunos, df_pagamentos):
    """
    Identify active students who have no payment record for the period.

    Args:
        df_alunos (pandas.DataFrame): Students DataFrame with 'nome' and 
            'status' columns.
        df_pagamentos (pandas.DataFrame): Cleaned payments DataFrame with 
            a 'nome' column (already renamed from 'Nome do Aluno').

    Returns:
        pandas.DataFrame: Subset of df_alunos containing only students 
            with no matching payment record.
    """
    alunos_ativos = df_alunos[df_alunos["status"] == "ativo"]
    nomes_que_pagaram = df_pagamentos["nome"].tolist()
    pendentes = alunos_ativos[~alunos_ativos["nome"].isin(nomes_que_pagaram)]
    return pendentes


def montar_mapa_turmas(dados_turmas):
    """
    Build a lookup mapping each turma to its list of teachers.

    Args:
        dados_turmas (list[dict]): Rows from the 'turmas' worksheet, each 
            with 'turma' and 'professores' keys (the latter comma-separated).

    Returns:
        dict: Mapping of turma name (str) to a list of teacher names (list[str]).
    """
    mapa = {}
    for linha in dados_turmas:
        nome_turma = linha["turma"]
        lista_professores = [p.strip() for p in linha["professores"].split(",")]
        mapa[nome_turma] = lista_professores
    return mapa


def somar_pagamentos_por_turma(df_pagamentos_validos):
    """
    Sum payment amounts grouped by turma.

    Args:
        df_pagamentos_validos (pandas.DataFrame): Payments merged with 
            student data, containing 'turmas' and 'Valor Recebido' columns.

    Returns:
        pandas.Series: Total amount received, indexed by turma name.
    """
    totais = df_pagamentos_validos.groupby("turmas")["Valor Recebido"].sum()
    return totais


def calcular_rateio_professoras(totais_por_turma, mapa_turmas):
    """
    Calculate how much each teacher should receive, based on per-turma totals.

    Args:
        totais_por_turma (pandas.Series): Total amount received, indexed 
            by turma name (from somar_pagamentos_por_turma).
        mapa_turmas (dict): Mapping of turma name to list of teacher names 
            (from montar_mapa_turmas).

    Returns:
        dict: Mapping of teacher name (str) to total amount to receive (float).
    """
    rateio = {}
    for turma, total_arrecadado in totais_por_turma.items():
        professoras_da_turma = mapa_turmas[turma]
        valor_por_professora = total_arrecadado / len(professoras_da_turma)
        for professora in professoras_da_turma:
            if professora not in rateio:
                rateio[professora] = 0
            rateio[professora] += valor_por_professora
    return rateio


def explodir_pagamentos_por_turma(df_pagamentos_validos):
    """
    Split payments across multiple turmas when a student attends more than one,
    dividing the paid amount equally among their turmas.

    Args:
        df_pagamentos_validos (pandas.DataFrame): Payments merged with student 
            data, containing 'turmas' (comma-separated) and 'Valor Recebido'.

    Returns:
        pandas.DataFrame: One row per (aluno, turma) combination, with 
            'Valor Recebido' already divided among the student's turmas.
    """
    linhas_explodidas = []
    for _, linha in df_pagamentos_validos.iterrows():
        lista_turmas = [t.strip() for t in linha["turmas"].split(",")]
        valor_por_turma = linha["Valor Recebido"] / len(lista_turmas)
        for turma in lista_turmas:
            nova_linha = linha.copy()
            nova_linha["turmas"] = turma
            nova_linha["Valor Recebido"] = valor_por_turma
            linhas_explodidas.append(nova_linha)
    df_explodido = pd.DataFrame(linhas_explodidas)
    return df_explodido


def processar_chamadas(matriz_chamada):
    """
    Transform raw attendance form data into one row per (student, date) pair.
    Skips any header rows that may appear duplicated within the data.

    Args:
        matriz_chamada (list[list[str]]): Raw rows from the attendance form 
            response sheet, including header row(s), with repeated 
            'Data da Aula' / 'Quem Esteve Presente?' column pairs.

    Returns:
        list[dict]: Each dict has 'turma', 'data_aula', and 'nome' keys, 
            one row per student marked present.
    """
    linhas_processadas = []

    for linha in matriz_chamada:
        turma = linha[1]

        if turma == "Qual Turma?":
            continue

        pares_data_presenca = [(linha[2], linha[3]), (linha[4], linha[5]), (linha[6], linha[7])]

        for data_aula, presentes_texto in pares_data_presenca:
            if data_aula == "":
                continue
            nomes_presentes = [n.strip() for n in presentes_texto.split(",")]
            for nome in nomes_presentes:
                linhas_processadas.append({
                    "turma": turma,
                    "data_aula": data_aula,
                    "nome": nome,
                })
    return linhas_processadas


def contar_presencas_por_aluno(df_chamadas):
    """
    Count how many times each student was marked present.

    Args:
        df_chamadas (pandas.DataFrame): Processed attendance records, 
            containing a 'nome' column (one row per student per class).

    Returns:
        pandas.Series: Number of times present, indexed by student name.
    """
    contagem = df_chamadas.groupby("nome").size()
    return contagem


def calcular_ultima_presenca(df_chamadas):
    """
    Find the most recent attendance date for each student.

    Args:
        df_chamadas (pandas.DataFrame): Processed attendance records, 
            containing 'nome' and 'data_aula' columns (date as string, 
            format DD/MM/YYYY).

    Returns:
        pandas.Series: Most recent attendance date (as Timestamp), 
            indexed by student name.
    """
    df_chamadas = df_chamadas.copy()
    df_chamadas["data_aula"] = pd.to_datetime(df_chamadas["data_aula"], format="%d/%m/%Y")
    ultima_presenca = df_chamadas.groupby("nome")["data_aula"].max()
    return ultima_presenca


def identificar_alunos_para_inativar(ultima_presenca, semanas_limite=4):
    """
    Identify students whose last attendance is older than the allowed limit.

    Args:
        ultima_presenca (pandas.Series): Most recent attendance date, 
            indexed by student name (from calcular_ultima_presenca).
        semanas_limite (int): Number of weeks of absence before flagging 
            a student as inactive. Defaults to 4.

    Returns:
        list[str]: Names of students who should be marked as inactive.
    """
    hoje = pd.Timestamp(datetime.date.today())
    dias_limite = semanas_limite * 7
    dias_ausente = (hoje - ultima_presenca).dt.days
    alunos_inativar = dias_ausente[dias_ausente > dias_limite].index.tolist()
    return alunos_inativar


def contar_aulas_por_turma(df_chamadas):
    """
    Count how many distinct class dates occurred per turma.

    Args:
        df_chamadas (pandas.DataFrame): Processed attendance records, 
            containing 'turma' and 'data_aula' columns.

    Returns:
        pandas.Series: Number of distinct class dates, indexed by turma name.
    """
    aulas_por_turma = df_chamadas.groupby("turma")["data_aula"].nunique()
    return aulas_por_turma


def calcular_percentual_presenca(df_alunos, presencas_por_aluno, aulas_por_turma):
    """
    Calculate each student's attendance percentage, based only on classes 
    that occurred on their enrolled days.

    Args:
        df_alunos (pandas.DataFrame): Students DataFrame with 'nome' and 
            'turmas' (comma-separated) columns.
        presencas_por_aluno (pandas.Series): Count of times present, 
            indexed by student name.
        aulas_por_turma (pandas.Series): Count of distinct class dates, 
            indexed by turma name.

    Returns:
        pandas.DataFrame: Columns 'nome' and 'percentual_presenca', 
            sorted descending by percentage.
    """
    resultados = []
    for _, aluno in df_alunos.iterrows():
        nome = aluno["nome"]
        turmas_do_aluno = [t.strip() for t in aluno["turmas"].split(",")]

        aulas_esperadas = sum(aulas_por_turma.get(turma, 0) for turma in turmas_do_aluno)
        presencas = presencas_por_aluno.get(nome, 0)

        if aulas_esperadas > 0:
            percentual = (presencas / aulas_esperadas) * 100
        else:
            percentual = 0

        resultados.append({"nome": nome, "percentual_presenca": percentual})

    df_ranking = pd.DataFrame(resultados)
    df_ranking = df_ranking.sort_values("percentual_presenca", ascending=False)
    return df_ranking


def calcular_ranking_por_turma(df_alunos, df_chamadas, aulas_por_turma):
    """
    Calculate attendance percentage rankings separately for each turma,
    counting only presences that occurred within that specific turma.

    Args:
        df_alunos (pandas.DataFrame): Students DataFrame with 'nome' and 
            'turmas' (comma-separated) columns.
        df_chamadas (pandas.DataFrame): Processed attendance records, 
            containing 'turma' and 'nome' columns.
        aulas_por_turma (pandas.Series): Count of distinct class dates, 
            indexed by turma name.

    Returns:
        dict: Mapping of turma name (str) to a DataFrame with 'nome' and 
            'percentual_presenca' columns, sorted descending by percentage.
    """
    rankings = {}
    for turma in aulas_por_turma.index:
        chamadas_da_turma = df_chamadas[df_chamadas["turma"] == turma]
        presencas_na_turma = chamadas_da_turma.groupby("nome").size()

        resultados = []
        for _, aluno in df_alunos.iterrows():
            nome = aluno["nome"]
            turmas_do_aluno = [t.strip() for t in aluno["turmas"].split(",")]

            if turma not in turmas_do_aluno:
                continue

            aulas_esperadas = aulas_por_turma.get(turma, 0)
            presencas = presencas_na_turma.get(nome, 0)

            if aulas_esperadas > 0:
                percentual = (presencas / aulas_esperadas) * 100
            else:
                percentual = 0

            resultados.append({"nome": nome, "percentual_presenca": percentual})

        df_turma = pd.DataFrame(resultados)
        df_turma = df_turma.sort_values("percentual_presenca", ascending=False)
        rankings[turma] = df_turma

    return rankings


def identificar_nomes_nao_cadastrados(df_alunos, nomes_em_uso):
    """
    Find names that appear in payments or attendance but are not registered 
    in the students sheet.

    Args:
        df_alunos (pandas.DataFrame): Students DataFrame with a 'nome' column.
        nomes_em_uso (list[str]): Names found in payments or attendance data.

    Returns:
        list[str]: Names that don't match any registered student.
    """
    nomes_cadastrados = set(df_alunos["nome"].tolist())
    nomes_desconhecidos = [nome for nome in set(nomes_em_uso) if nome not in nomes_cadastrados]
    return nomes_desconhecidos


def identificar_alunos_em_risco(ultima_presenca, semanas_aviso=2, semanas_limite=4):
    """
    Identify students who haven't attended recently but haven't yet 
    crossed the inactivity threshold — an early warning list.

    Args:
        ultima_presenca (pandas.Series): Most recent attendance date, 
            indexed by student name.
        semanas_aviso (int): Minimum weeks of absence to trigger a warning. 
            Defaults to 2.
        semanas_limite (int): Weeks of absence that would mark inactivity 
            (used as the upper bound for this warning range). Defaults to 4.

    Returns:
        list[str]: Names of students in the "at risk" window.
    """
    hoje = pd.Timestamp(datetime.date.today())
    dias_aviso = semanas_aviso * 7
    dias_limite = semanas_limite * 7
    dias_ausente = (hoje - ultima_presenca).dt.days
    em_risco = dias_ausente[(dias_ausente >= dias_aviso) & (dias_ausente <= dias_limite)].index.tolist()
    return em_risco


def calcular_sequencia_presenca(df_alunos, df_chamadas, aulas_por_turma):
    """
    Calculate each student's current attendance streak (consecutive 
    classes attended without missing, counting backward from the most 
    recent class in their turma).

    Args:
        df_alunos (pandas.DataFrame): Students DataFrame with 'nome' and 
            'turmas' columns.
        df_chamadas (pandas.DataFrame): Processed attendance records with 
            'turma', 'data_aula', and 'nome' columns.
        aulas_por_turma (pandas.Series): Count of distinct class dates, 
            indexed by turma name.

    Returns:
        dict: Mapping of student name (str) to current streak count (int).
    """
    sequencias = {}
    for _, aluno in df_alunos.iterrows():
        nome = aluno["nome"]
        turmas_do_aluno = [t.strip() for t in aluno["turmas"].split(",")]

        todas_datas = []
        for turma in turmas_do_aluno:
            datas_turma = df_chamadas[df_chamadas["turma"] == turma]["data_aula"].unique()
            todas_datas.extend(datas_turma)

        datas_ordenadas = sorted(todas_datas, reverse=True)

        streak = 0
        for data in datas_ordenadas:
            presente = ((df_chamadas["nome"] == nome) & (df_chamadas["data_aula"] == data)).any()
            if presente:
                streak += 1
            else:
                break

        sequencias[nome] = streak

    return sequencias

def calcular_receita_por_mes(df_pagamentos_completo):
    """
    Sum total revenue grouped by reference month.

    Args:
        df_pagamentos_completo (pandas.DataFrame): Payments data containing 
            'Mês de Referencia' and 'Valor Recebido' columns.

    Returns:
        pandas.Series: Total amount received, indexed by reference month.
    """
    receita_por_mes = df_pagamentos_completo.groupby("Mês de Referencia")["Valor Recebido"].sum()
    return receita_por_mes