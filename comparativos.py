import pandas as pd
from db import engine
from conn_ftp import conect_ftp_e_leitura

def comparativo_captacao(coluna_comparativa="doc_vendas"):
    query_captacao = """ 
        SELECT 
            *
        FROM [ComercialDB].[dbo].[TB_CAPTAÇAO_PEDIDOS]
        where [data_doc] >= '2026-02-01' and [data_doc] <= '2026-02-13'
    """

    df_captacao = pd.read_sql(query_captacao,engine)

    # Agrupado por doc_vendas -> Valor liquido
    df_captacao_agrupado = df_captacao.groupby(coluna_comparativa)['valor_liquido'].sum()
    df_captacao_agrupado = df_captacao_agrupado.to_frame()
    df_captacao_agrupado = df_captacao_agrupado.reset_index()


    bases = conect_ftp_e_leitura()

    df = bases['captacao_pedidos_202602.xlsx']

    # Agrupado por doc_venda -> Valor liquido
    df_agrupado = df.groupby(coluna_comparativa)['valor_liquido'].sum()
    df_agrupado = df_agrupado.to_frame()
    df_agrupado = df_agrupado.reset_index()


    # Juntar colunas e remover duplicatas
    docs_unicos = (
        pd.concat([
            # transformando no tipo string
            df_agrupado[coluna_comparativa].astype(str),
            df_captacao_agrupado[coluna_comparativa].astype(str)
        ])
        # Remove duplicatas
        .drop_duplicates()
        .sort_values()
        # Reseta o index
        .reset_index(drop=True)
    )
    # Ao juntar e remover duplicatas transformou e Series, por isso é preciso converter para dataframe
    docs_unicos = docs_unicos.to_frame(name=coluna_comparativa)

    #print(docs_unicos)


    #LEFT JOIN: base -> SQL -> FTP

    # padroniza tipo
    docs_unicos[coluna_comparativa] = docs_unicos[coluna_comparativa].astype(str).str.strip()
    df_agrupado[coluna_comparativa] = df_agrupado[coluna_comparativa].astype(str).str.strip()
    df_captacao_agrupado[coluna_comparativa] = df_captacao_agrupado[coluna_comparativa].astype(str).str.strip()

    # Realiza o merge do arquivo FTP com os dados da Tabela do SQL
    df_merge = docs_unicos.merge(
        df_agrupado,
        on=coluna_comparativa,
        how="left",
        suffixes=("", "_ftp")
    ).merge(
        df_captacao_agrupado,
        on=coluna_comparativa,
        how="left",
        suffixes=("", "_sql")
    )

    # Por que usar fillna(0)? Porque se algum doc existir só em um lado, o valor vem como NaN, fillna transforma NaN em 0
    df_merge["diferenca"] = (
        df_merge["valor_liquido_sql"].fillna(0)
        - df_merge["valor_liquido"].fillna(0)
    )

    df_merge["status"] = df_merge["diferenca"].apply(
        lambda x: "OK" if x == 0 else "DIVERGENTE"
    )

    filtro_docs_divergentes = df_merge[df_merge['status']=='DIVERGENTE']

    return filtro_docs_divergentes, df_merge
    #print(filtro_docs_divergentes)


def comparativo_open():
    query_open = """ 
        SELECT 
            *
        FROM [ComercialDB].[dbo].[TB_OPEN_ORDENS]
        WHERE [calendar_day] >= '2026-02-01' AND [calendar_day] <= '2026-02-13'
    """

    df_open = pd.read_sql(query_open,engine)
    df_agrupado_por_data_sql = df_open.groupby('calendar_day')['open_order_net'].sum().reset_index()
    df_agrupado_por_data_sql = df_agrupado_por_data_sql#.to_frame()
    #df_agrupado_por_data_sql = df_agrupado_por_data_sql.reset_index()
    print(df_agrupado_por_data_sql.head())

    bases = conect_ftp_e_leitura()

    df = bases['open_ordens_202602.xlsx']
    df_agrupado_por_data_ftp = df.groupby('created_on')['open_order_net'].sum().reset_index()
    df_agrupado_por_data_ftp = df_agrupado_por_data_ftp#.to_frame()
    #df_agrupado_por_data_ftp = df_agrupado_por_data_ftp.reset_index()
    print(df_agrupado_por_data_ftp.head())

    # Juntar colunas e remover duplicatas
    df_sem_duplicatas = (
        pd.concat([
            # transformando no tipo string
            df_agrupado_por_data_sql['calendar_day'].astype(str),
            df_agrupado_por_data_ftp['created_on'].astype(str)
        ])
        # Remove duplicatas
        .drop_duplicates()
        .sort_values()
        # Reseta o index
        .reset_index(drop=True)
    ).to_frame()

    # Realiza o merge do arquivo FTP com os dados da Tabela do SQL
    """
    df_merge = df_sem_duplicatas.merge(
        df_agrupado_por_data_sql,
        on='calendar_day',
        how="left",
        suffixes=("", "_sql")
    ).merge(
        df_agrupado_por_data_ftp,
        on='created_on',
        how="left",
        suffixes=("", "_ftp")
    )
    """
    
    print(df_sem_duplicatas.head())


def comparativo_faturamento():
    query_faturamento = """
        SELECT 
            *
        FROM [ComercialDB].[dbo].[TB_FATURAMENTO]
        WHERE [data_faturamento] >= '2026-02-01' AND [data_faturamento] <= GETDATE()-1 AND [tipo_doc_vendas] NOT IN ('ZIV')
    """

    # Leitura na tabela
    df_fat = pd.read_sql(query_faturamento,engine)

    # Preenche NaN com 0
    df_fat['valor_fat_liquido'] = df_fat['valor_fat_liquido'].fillna(0)

    # Agrupamento pelo doc_fat com soma do valor_fat_liquido
    df_agrupado_por_doc = df_fat.groupby('doc_fat')['valor_fat_liquido'].sum().reset_index()

    #Leitura do arquivo de faturamento
    bases = conect_ftp_e_leitura()
    df = bases['faturamento_202602.xlsx']
    print(df)


    