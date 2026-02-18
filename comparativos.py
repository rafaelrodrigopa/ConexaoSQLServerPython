import pandas as pd
from db import engine
from conn_ftp import conect_ftp_e_leitura

def comparativo_captacao():
    query_captacao = """ 
        SELECT 
            *
        FROM [ComercialDB].[dbo].[TB_CAPTAÇAO_PEDIDOS]
        where [data_doc] >= '2026-02-01' and [data_doc] <= '2026-02-13'
    """

    #df_faturamento = pd.read_sql(query_faturamento,engine)
    df_captacao = pd.read_sql(query_captacao,engine)

    # Agrupado por doc_vendas -> Valor liquido
    df_captacao_agrupado = df_captacao.groupby('doc_vendas')['valor_liquido'].sum()
    df_captacao_agrupado = df_captacao_agrupado.to_frame()
    df_captacao_agrupado = df_captacao_agrupado.reset_index()


    bases = conect_ftp_e_leitura()

    df = bases['captacao_pedidos_202602.xlsx']

    # Agrupado por doc_venda -> Valor liquido
    df_agrupado = df.groupby('doc_vendas')['valor_liquido'].sum()
    df_agrupado = df_agrupado.to_frame()
    df_agrupado = df_agrupado.reset_index()


    # Juntar colunas e remover duplicatas
    docs_unicos = (
        pd.concat([
            # transformando no tipo string
            df_agrupado["doc_vendas"].astype(str),
            df_captacao_agrupado["doc_vendas"].astype(str)
        ])
        # Remove duplicatas
        .drop_duplicates()
        .sort_values()
        # Reseta o index
        .reset_index(drop=True)
    )
    # Ao juntar e remover duplicatas transformou e Series, por isso é preciso converter para dataframe
    docs_unicos = docs_unicos.to_frame(name="doc_vendas")

    #print(docs_unicos)


    #LEFT JOIN: base -> SQL -> FTP

    # padroniza tipo
    docs_unicos["doc_vendas"] = docs_unicos["doc_vendas"].astype(str).str.strip()
    df_agrupado["doc_vendas"] = df_agrupado["doc_vendas"].astype(str).str.strip()
    df_captacao_agrupado["doc_vendas"] = df_captacao_agrupado["doc_vendas"].astype(str).str.strip()

    # Realiza o merge do arquivo FTP com os dados da Tabela do SQL
    df_merge = docs_unicos.merge(
        df_agrupado,
        on="doc_vendas",
        how="left",
        suffixes=("", "_ftp")
    ).merge(
        df_captacao_agrupado,
        on="doc_vendas",
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

    return filtro_docs_divergentes
    #print(filtro_docs_divergentes)


