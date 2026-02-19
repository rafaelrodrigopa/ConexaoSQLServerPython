from comparativos import comparativo_captacao, comparativo_open, comparativo_faturamento
import numpy as np
from datetime import datetime


#filtrado = comparativo_captacao("data_doc")[0]
#merge = comparativo_captacao("data_doc")[1]

#resultado = merge[merge['data_doc']=='2026-02-01']

#print(resultado)
df = comparativo_faturamento()
print(df['doc_fat'].head())