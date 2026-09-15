import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

CREDENTIALS_PATH = "credentials/google-credentials.json"

def conectar_planilha(sheet_id):
    """
    Authenticate with Google Sheets API and open a spreadsheet by its ID.
    Reads credentials from Streamlit Secrets when available (cloud deploy),
    falling back to a local JSON file for local development.

    Args:
        sheet_id (str): The unique ID of the Google Sheets spreadsheet,
            found in the spreadsheet's URL between '/d/' and '/edit'.

    Returns:
        gspread.Spreadsheet: An authorized spreadsheet object, ready
            for reading or writing data.
    """
    try:
        import streamlit as st
        info_credenciais = dict(st.secrets["gcp_service_account"])
        credenciais = Credentials.from_service_account_info(
            info_credenciais, scopes=SCOPES
        )
    except (ImportError, KeyError, FileNotFoundError):
        credenciais = Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=SCOPES
        )

    cliente = gspread.authorize(credenciais)
    planilha = cliente.open_by_key(sheet_id)
    return planilha

def ler_aba_como_lista(planilha, nome_aba):
    """
    Read all records from a specific worksheet as a list of dictionaries.

    Args:
        planilha (gspread.Spreadsheet): An already-authenticated spreadsheet object.
        nome_aba (str): The exact name of the worksheet/tab to read.

    Returns:
        list[dict]: Each row as a dictionary, using the header row as keys.
    """
    aba = planilha.worksheet(nome_aba)
    dados = aba.get_all_records()
    return dados
    
def ler_aba_como_matriz(planilha, nome_aba):
    """
    Read all raw values from a worksheet as a list of lists (rows), 
    useful when the header row contains duplicate column names.

    Args:
        planilha (gspread.Spreadsheet): An already-authenticated spreadsheet object.
        nome_aba (str): The exact name of the worksheet/tab to read.

    Returns:
        list[list[str]]: All rows including the header, as raw string values.
    """
    aba = planilha.worksheet(nome_aba)
    valores = aba.get_all_values()
    return valores

def escrever_dataframe_na_aba(planilha, nome_aba, df):
    """
    Overwrite a worksheet with the contents of a DataFrame, including headers.

    Args:
        planilha (gspread.Spreadsheet): An already-authenticated spreadsheet object.
        nome_aba (str): The exact name of the worksheet/tab to write to.
        df (pandas.DataFrame): Data to write, including column names as header.

    Returns:
        None
    """
    aba = planilha.worksheet(nome_aba)
    aba.clear()
    cabecalho = df.columns.tolist()
    linhas = df.values.tolist()
    aba.update([cabecalho] + linhas)