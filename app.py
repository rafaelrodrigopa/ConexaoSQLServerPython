import pandas as pd
from db import engine

query = """ SELECT TOP (1000) *
  FROM [ComercialDB].[dbo].[TB_FATURAMENTO]
"""

df = pd.read_sql(query,engine)

print(df['segmento'])
