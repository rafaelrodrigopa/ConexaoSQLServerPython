import os
from funcoes import conectar_e_entrar_no_diretorio, fechar_ftp, ler_xlsx_da_pasta_ftp

# Configurações FTP (podem ser sobrescritas por variáveis de ambiente)
FTP_HOST = os.environ.get("FTP_HOST", "10.101.14.119")
FTP_PORT = int(os.environ.get("FTP_PORT", "21"))
FTP_USER = os.environ.get("FTP_USER", "ftpuser")
FTP_PASS = os.environ.get("FTP_PASS", "ftppass")
#FTP_DIR = os.environ.get("FTP_DIR", "Relatorios_inteligencia&Dados")
FTP_DIR = os.environ.get("FTP_DIR", "Dados&BI")

ftp = conectar_e_entrar_no_diretorio(FTP_HOST, FTP_PORT, FTP_USER, FTP_PASS, FTP_DIR)
bases = ler_xlsx_da_pasta_ftp(ftp, padrao="*.xlsx", sheet_name=0)
print(bases['captacao_pedidos_202602.xlsx'].groupby('data_doc')['valor_liquido'].sum())