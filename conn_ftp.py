import os
from funcoes import conectar_e_entrar_no_diretorio, fechar_ftp, ler_xlsx_da_pasta_ftp
from dotenv import load_dotenv

def conect_ftp_e_leitura() -> dict[str, pd.DataFrame]:
    load_dotenv()

    # Configurações FTP (podem ser sobrescritas por variáveis de ambiente)
    FTP_HOST = os.getenv("FTP_HOST")
    FTP_PORT = int(os.getenv("FTP_PORT"))
    FTP_USER = os.getenv("FTP_USER")
    FTP_PASS = os.getenv("FTP_PASS")
    FTP_DIR = os.getenv("FTP_DIR")

    ftp = conectar_e_entrar_no_diretorio(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASS, FTP_DIR)
    bases = ler_xlsx_da_pasta_ftp(ftp, padrao="open_ordens_202602.xlsx", sheet_name=0)
    return bases

"""
df = bases['captacao_pedidos_202602.xlsx']

# Filtrar apenas registros da data desejada
df_filtrado = df[df['data_doc'] == '2026-02-02']

# Verificar se existe algo nessa data
if not df_filtrado.empty:
    print(
        df_filtrado.groupby('data_doc')['valor_liquido'].sum()
    )
else:
    print("Nenhum registro encontrado para essa data.")
"""

