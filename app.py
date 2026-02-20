from comparativos import comparativo_captacao, comparativo_open, comparativo_faturamento
import numpy as np
from datetime import datetime


#filtrado = comparativo_captacao("data_doc")[0]
#merge = comparativo_captacao("data_doc")[1]

#resultado = merge[merge['data_doc']=='2026-02-01']

#print(resultado)
data_atual = datetime.now()#.strftime("%d/%m/%Y")
dia_D_Menos_1 = int(data_atual.day)-1

dia_especifico = datetime(2026, 2, 2)

df_fat_ftp, df_fat_sql = comparativo_faturamento()

# Soma Acumulado
df_soma_acumulado_ftp = df_fat_ftp['valor_fat_liquido'].fillna(0).sum()
df_soma_acumulado_sql = df_fat_sql['valor_fat_liquido'].fillna(0).sum()

# Soma dia Anterior
df_soma_dia_anterior_ftp = df_fat_ftp.loc[
    df_fat_ftp['data_faturamento'].dt.date == dia_especifico.date(),
    'valor_fat_liquido'
].fillna(0).sum()
df_soma_dia_anterior_sql = df_fat_sql.loc[
    df_fat_ftp['data_faturamento'].dt.date == dia_especifico.date(),
    'valor_fat_liquido'
].fillna(0).sum()

# Calculo das diferenças
diferenca_entre_valores_acumulado = (df_soma_acumulado_sql-df_soma_acumulado_sql)
diferenca_entre_valores_dia_anterior = (df_soma_dia_anterior_sql-df_soma_dia_anterior_ftp)

#Verifica se há diferença no acumulado
if diferenca_entre_valores_acumulado > 0:
    print(f'Valor a mais no sql: {diferenca_entre_valores_acumulado:,.2f}')
elif diferenca_entre_valores_acumulado < 0:
    print(f'Valor a mais no ftp: {diferenca_entre_valores_acumulado:,.2f}')
else:
    print(f'Sem divergência: {diferenca_entre_valores_acumulado:,.2f}')

#Verifica se há diferença no dia anterior
if diferenca_entre_valores_dia_anterior > 0:
    print(f'Valor a mais no sql: {diferenca_entre_valores_dia_anterior:,.2f}')
elif diferenca_entre_valores_dia_anterior < 0:
    print(f'Valor a mais no ftp: {diferenca_entre_valores_dia_anterior:,.2f}')
else:
    print(f'Sem divergência: {diferenca_entre_valores_dia_anterior:,.2f}')

