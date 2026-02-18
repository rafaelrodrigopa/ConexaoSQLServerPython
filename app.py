import pandas as pd
from db import engine

query = """ SELECT 
             *
            FROM [ComercialDB].[dbo].[TB_FATURAMENTO]
            WHERE [data_faturamento]='2026-02-02'
"""

df = pd.read_sql(query,engine)

print(df.groupby('doc_fat')['valor_fat_liquido'].sum())
