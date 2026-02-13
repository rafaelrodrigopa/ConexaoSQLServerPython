from funcoes import listar_arquivos
import pandas as pd

arquivos = listar_arquivos(r"C:\Users\rafael.almeida\Videos\Bases.xlsx","*.xlsx")
print(arquivos)