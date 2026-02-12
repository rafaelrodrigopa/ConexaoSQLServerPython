from pathlib import Path

""" lista os arquivos na pasta """
def listar_arquivos(pasta,padrao="*"):
    pasta = Path(pasta)
    return [p for p in pasta.glob(padrao) if p.is_file()]
