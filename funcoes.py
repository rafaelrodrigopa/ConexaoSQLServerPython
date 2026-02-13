from pathlib import Path
import os
import logging
from ftplib import FTP, error_perm
from fnmatch import fnmatch
from io import BytesIO
import pandas as pd
import openpyxl


logger = logging.getLogger(__name__)

def conectar_e_entrar_no_diretorio(
    host: str,
    port: int,
    user: str,
    password: str,
    remote_dir: str,
    timeout: int = 30,
    passive: bool = True,
    criar_diretorio: bool = True,
) -> FTP:
    """
    Conecta no FTP, faz login e entra no diretório remoto.
    Se criar_diretorio=True, cria o diretório caso não exista.

    Retorna o objeto FTP pronto para uso (lembre de fechar com ftp.quit()).
    """
    #logger.info(f"Conectando ao FTP {host}:{port}...")
    print(f"Conectando ao FTP {host}:{port}...")

    ftp = FTP()
    ftp.set_pasv(passive)
    ftp.connect(host, port, timeout=timeout)
    ftp.login(user, password)

    #logger.info("Conectado ao FTP com sucesso")
    print("Conectado ao FTP com sucesso")

    # Garantir modo binário (boa prática: evita conversões ASCII)
    ftp.voidcmd("TYPE I")

    # Ir para diretório (criar se precisar)
    if remote_dir:
        try:
            ftp.cwd(remote_dir)
            #logger.info(f"Diretório atual no FTP: {remote_dir}")
            print(f"Diretório atual no FTP: {remote_dir}")
        except Exception as e:
            if not criar_diretorio:
                #logger.error(f"Não foi possível acessar diretório {remote_dir}: {e}")
                print(f"Não foi possível acessar diretório {remote_dir}: {e}")
                raise

            #logger.info(f"Diretório {remote_dir} não existe, tentando criar...")
            print(f"Diretório {remote_dir} não existe, tentando criar...")
            ftp.mkd(remote_dir)
            ftp.cwd(remote_dir)
            #logger.info(f"Diretório {remote_dir} criado e acessado com sucesso")
            print(f"Diretório {remote_dir} criado e acessado com sucesso")

    
    #fechar_ftp(ftp)
    return ftp


def fechar_ftp(ftp: FTP) -> None:
    """Fecha conexão FTP com fallback."""
    if not ftp:
        print("Conexão fechada")
        return
    try:
        ftp.quit()
        print("Conexão fechada")
    except Exception:
        try:
            ftp.close()
            print("Conexão fechada")
        except Exception:
            pass


def listar_arquivos_ftp(ftp: FTP, padrao: str = "*") -> list[str]:
    """
    Lista arquivos no diretório atual do FTP filtrando por padrão.
    Tenta MLSD (mais confiável). Se não suportar, usa NLST com fallback.
    """
    arquivos: list[str] = []

    # 1) Tenta MLSD (servidores modernos)
    try:
        for nome, facts in ftp.mlsd():
            tipo = (facts.get("type") or "").lower()
            if tipo == "file" and fnmatch(nome, padrao):
                arquivos.append(nome)
        return arquivos
    except Exception:
        pass

    # 2) Fallback NLST (mais “cru”)
    nomes = ftp.nlst()
    for nome in nomes:
        if not fnmatch(nome, padrao):
            continue

        # Tenta validar se é arquivo sem depender de SIZE (alguns FTP bloqueiam)
        # - se conseguir CWD, é diretório => ignora
        # - se não conseguir CWD, assumimos arquivo
        pwd = ftp.pwd()
        try:
            ftp.cwd(nome)          # se entrar, é diretório
            ftp.cwd(pwd)           # volta
            continue
        except Exception:
            arquivos.append(nome)

    return arquivos



def ler_xlsx_da_pasta_ftp(
    ftp: FTP,
    padrao: str = "*.xlsx",
    sheet_name=0,
    **read_excel_kwargs
) -> dict[str, pd.DataFrame]:
    """
    Lê todos os XLSX do diretório atual do FTP.
    Retorna dict: {nome_arquivo: DataFrame}
    """
    bases: dict[str, pd.DataFrame] = {}

    arquivos = listar_arquivos_ftp(ftp, padrao=padrao)
    print(f"Encontrados {len(arquivos)} arquivo(s) no FTP com padrão {padrao}")

    for nome in arquivos:
        try:
            buffer = BytesIO()
            ftp.retrbinary(f"RETR {nome}", buffer.write)
            buffer.seek(0)

            df = pd.read_excel(buffer, sheet_name=sheet_name, **read_excel_kwargs)
            bases[nome] = df

            print(f"Lido: {nome} -> {df.shape[0]} linhas, {df.shape[1]} colunas")
        except Exception as e:
            print(f"Erro ao ler {nome}: {type(e).__name__} - {e}")

    return bases
