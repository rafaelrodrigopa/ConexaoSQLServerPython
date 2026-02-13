from pathlib import Path
import os
import logging
from ftplib import FTP
from fnmatch import fnmatch
from io import BytesIO
import pandas as pd

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
    """Lista arquivos no diretório atual do FTP filtrando por padrão (ex: *.csv)."""
    nomes = ftp.nlst()
    arquivos = []

    for nome in nomes:
        if not fnmatch(nome, padrao):
            continue
        # Ignorar diretórios (ftp.size geralmente falha para diretórios)
        try:
            ftp.size(nome)
            arquivos.append(nome)
        except Exception:
            continue

    return arquivos


def ler_csvs_da_pasta_ftp(
    ftp: FTP,
    padrao: str = "*.xlsx",
    **read_csv_kwargs
) -> dict[str, pd.DataFrame]:
    """
    Lê todos os xlsx do diretório atual do FTP.
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

            df = pd.read_csv(buffer, **read_csv_kwargs)
            bases[nome] = df

            print(f"Lido: {nome} -> {df.shape[0]} linhas, {df.shape[1]} colunas")
        except Exception as e:
            print(f"Erro ao ler {nome}: {type(e).__name__} - {e}")

    return bases
