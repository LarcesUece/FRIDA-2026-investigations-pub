import time
import tracemalloc
import gc
import os
import warnings

# Silencia o aviso de transição de motor do Dask
warnings.filterwarnings("ignore", message="Computing mixed collections*")
warnings.filterwarnings("ignore", category=UserWarning, module="dask")

import numpy as np
import pandas as pd
import polars as pl
import duckdb
import pyarrow as pa
import pyarrow.csv as pv
import pyarrow.compute as pc
import dask
import dask.dataframe as dd


def aquecer_cache_do_so(arquivo):
    print(f"\n🔥 Aquecendo o Cache do SO para: {arquivo} ...")
    with open(arquivo, "r", encoding="utf-8") as f:
        _ = f.read()


# ==========================================
# MAPEADOR DINÂMICO DE COLUNAS
# ==========================================
def mapear_colunas(colunas):
    """Descobre quais colunas devem sofrer quais operações, independente dos sufixos."""
    return {
        "drop": [
            c for c in colunas if c.split("_")[0] in ["nome", "estado", "email", "sexo"]
        ],
        "cpf": [c for c in colunas if c.startswith("cpf")],
        "k_anon": [c for c in colunas if c.startswith("peso")],
        "diff_priv": [c for c in colunas if c.startswith("valor_precisao")],
    }


# ==========================================
# MONITOR DE PERFORMANCE
# ==========================================
class Monitor:
    def __init__(self, resultados, biblioteca, etapa):
        self.resultados = resultados
        self.biblioteca = biblioteca
        self.etapa = etapa

    def __enter__(self):
        gc.collect()
        time.sleep(1)
        tracemalloc.start()
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        t1 = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tempo = t1 - self.t0
        mem_mb = peak / (1024 * 1024)

        chave_tempo = f"{self.etapa} - Tempo (s)"
        chave_mem = f"{self.etapa} - RAM (MB)"

        if self.biblioteca not in self.resultados:
            self.resultados[self.biblioteca] = {}

        self.resultados[self.biblioteca][chave_tempo] = round(tempo, 4)
        self.resultados[self.biblioteca][chave_mem] = round(mem_mb, 4)
        print(f"  [{self.biblioteca}] {self.etapa}: {tempo:.3f}s | {mem_mb:.2f} MB")


# ==========================================
# FUNÇÕES DE TESTE (SALVANDO NO TRASH)
# ==========================================


def testar_pandas(arquivo, res):
    print("\n🐼 Iniciando PANDAS...")
    with Monitor(res, "Pandas", "1_Load"):
        df = pd.read_csv(arquivo)
        cols = mapear_colunas(df.columns)

    with Monitor(res, "Pandas", "2_Drop (Supressão)"):
        df = df.drop(columns=cols["drop"])

    with Monitor(res, "Pandas", "3_Mask (Pseudonimização)"):
        for c in cols["cpf"]:
            df[c] = "***.***.***-" + df[c].astype(str).str[-2:]

    with Monitor(res, "Pandas", "4_K-Anonymity (Peso)"):
        for c in cols["k_anon"]:
            df[c] = (df[c] // 10) * 10

    with Monitor(res, "Pandas", "5_Diff Privacy (Valor Precisão)"):
        ruido = np.random.laplace(0.0, 50.0, len(df))
        for c in cols["diff_priv"]:
            df[c] = df[c] + ruido

    with Monitor(res, "Pandas", "6_Stats (Descritivas)"):
        estatisticas = df[cols["diff_priv"]].describe()

    with Monitor(res, "Pandas", "7_Write"):
        # Substitui DATA/ por DATA/trash/ para manter a pasta raiz limpa
        caminho_saida = arquivo.replace("DATA/", "DATA/trash/").replace(
            ".csv", "_pd.csv"
        )
        df.to_csv(caminho_saida, index=False)
    del df
    gc.collect()


def testar_polars(arquivo, res):
    print("\n🐻‍❄️ Iniciando POLARS...")
    with Monitor(res, "Polars", "1_Load"):
        df = pl.read_csv(arquivo)
        cols = mapear_colunas(df.columns)

    with Monitor(res, "Polars", "2_Drop (Supressão)"):
        df = df.drop(cols["drop"])

    with Monitor(res, "Polars", "3_Mask (Pseudonimização)"):
        expr_cpf = [
            (pl.lit("***.***.***-") + pl.col(c).cast(pl.Utf8).str.slice(-2)).alias(c)
            for c in cols["cpf"]
        ]
        df = df.with_columns(expr_cpf)

    with Monitor(res, "Polars", "4_K-Anonymity (Peso)"):
        expr_kanon = [((pl.col(c) // 10) * 10).alias(c) for c in cols["k_anon"]]
        df = df.with_columns(expr_kanon)

    with Monitor(res, "Polars", "5_Diff Privacy (Valor Precisão)"):
        ruido = pl.Series(np.random.laplace(0.0, 50.0, df.height))
        expr_diff = [(pl.col(c) + ruido).alias(c) for c in cols["diff_priv"]]
        df = df.with_columns(expr_diff)

    with Monitor(res, "Polars", "6_Stats (Descritivas)"):
        estatisticas = df.select(cols["diff_priv"]).describe()

    with Monitor(res, "Polars", "7_Write"):
        caminho_saida = arquivo.replace("DATA/", "DATA/trash/").replace(
            ".csv", "_pl.csv"
        )
        df.write_csv(caminho_saida)
    del df
    gc.collect()


def testar_duckdb(arquivo, res):
    print("\n🦆 Iniciando DUCKDB...")
    conn = duckdb.connect()
    with Monitor(res, "DuckDB", "1_Load"):
        conn.sql(f"CREATE TABLE t AS SELECT * FROM read_csv_auto('{arquivo}')")
        colunas_db = [x[0] for x in conn.sql("DESCRIBE t").fetchall()]
        cols = mapear_colunas(colunas_db)

    with Monitor(res, "DuckDB", "2_Drop (Supressão)"):
        for c in cols["drop"]:
            conn.sql(f"ALTER TABLE t DROP {c}")

    with Monitor(res, "DuckDB", "3_Mask (Pseudonimização)"):
        for c in cols["cpf"]:
            conn.sql(
                f"UPDATE t SET {c} = '***.***.***-' || substr(CAST({c} AS VARCHAR), -2)"
            )

    with Monitor(res, "DuckDB", "4_K-Anonymity (Peso)"):
        for c in cols["k_anon"]:
            conn.sql(f"UPDATE t SET {c} = cast(floor({c}/10)*10 as double)")

    with Monitor(res, "DuckDB", "5_Diff Privacy (Valor Precisão)"):
        for c in cols["diff_priv"]:
            conn.sql(f"UPDATE t SET {c} = {c} + (random() * 100 - 50)")

    with Monitor(res, "DuckDB", "6_Stats (Descritivas)"):
        for c in cols["diff_priv"]:
            conn.sql(
                f"SELECT avg({c}), stddev({c}), quantile_cont({c}, 0.5) FROM t"
            ).fetchall()

    with Monitor(res, "DuckDB", "7_Write"):
        caminho_saida = arquivo.replace("DATA/", "DATA/trash/").replace(
            ".csv", "_duck.csv"
        )
        conn.sql(f"COPY t TO '{caminho_saida}' (HEADER, DELIMITER ',')")
    conn.close()
    del conn
    gc.collect()


def testar_pyarrow(arquivo, res):
    print("\n🏹 Iniciando PYARROW...")
    with Monitor(res, "PyArrow", "1_Load"):
        tabela = pv.read_csv(arquivo)
        cols = mapear_colunas(tabela.column_names)

    with Monitor(res, "PyArrow", "2_Drop (Supressão)"):
        tabela = tabela.drop(cols["drop"])

    with Monitor(res, "PyArrow", "3_Mask (Pseudonimização)"):
        for c in cols["cpf"]:
            str_col = pc.cast(tabela[c], pa.string())
            cpf_masc = pc.replace_substring_regex(
                str_col, pattern=r"^.{12}", replacement="***.***.***-"
            )
            tabela = tabela.set_column(
                tabela.schema.get_field_index(c), pa.field(c, pa.string()), cpf_masc
            )

    with Monitor(res, "PyArrow", "4_K-Anonymity (Peso)"):
        for c in cols["k_anon"]:
            k_anon = pc.multiply(pc.floor(pc.divide(tabela[c], 10)), 10)
            tabela = tabela.set_column(
                tabela.schema.get_field_index(c),
                pa.field(c, pa.float64()),
                pc.cast(k_anon, pa.float64()),
            )

    with Monitor(res, "PyArrow", "5_Diff Privacy (Valor Precisão)"):
        ruido = pa.array(np.random.laplace(0.0, 50.0, tabela.num_rows))
        for c in cols["diff_priv"]:
            val = pc.add(tabela[c], ruido)
            tabela = tabela.set_column(
                tabela.schema.get_field_index(c), pa.field(c, pa.float64()), val
            )

    with Monitor(res, "PyArrow", "6_Stats (Descritivas)"):
        for c in cols["diff_priv"]:
            pc.mean(tabela[c])
            pc.stddev(tabela[c])
            pc.quantile(tabela[c], q=[0.25, 0.5, 0.75])

    with Monitor(res, "PyArrow", "7_Write"):
        caminho_saida = arquivo.replace("DATA/", "DATA/trash/").replace(
            ".csv", "_arrow.csv"
        )
        pv.write_csv(tabela, caminho_saida)
    del tabela
    gc.collect()


def testar_dask_free(arquivo, res):
    print("\n🌪️ Iniciando DASK FREE (Preguiçoso)...")
    with Monitor(res, "Dask_Free", "1_Load"):
        df = dd.read_csv(arquivo)
        cols = mapear_colunas(df.columns)

    with Monitor(res, "Dask_Free", "2_Drop (Supressão)"):
        df = df.drop(columns=cols["drop"])

    with Monitor(res, "Dask_Free", "3_Mask (Pseudonimização)"):
        for c in cols["cpf"]:
            df[c] = "***.***.***-" + df[c].astype(str).str[-2:]

    with Monitor(res, "Dask_Free", "4_K-Anonymity (Peso)"):
        for c in cols["k_anon"]:
            df[c] = (df[c] // 10) * 10

    with Monitor(res, "Dask_Free", "5_Diff Privacy (Valor Precisão)"):

        def aplicar_ruido(s):
            return s + np.random.laplace(0.0, 50.0, len(s))

        for c in cols["diff_priv"]:
            df[c] = df[c].map_partitions(aplicar_ruido, meta=(c, "f8"))

    with Monitor(res, "Dask_Free", "6_Stats (Descritivas)"):
        estatisticas = [df[c].describe() for c in cols["diff_priv"]]

    with Monitor(res, "Dask_Free", "7_Write (Execução Total)"):
        caminho_saida = arquivo.replace("DATA/", "DATA/trash/").replace(
            ".csv", "_dask_free_out_*.csv"
        )
        tarefa_salvar = df.to_csv(caminho_saida, index=False, compute=False)
        dask.compute(*estatisticas, tarefa_salvar)
    del df
    gc.collect()


# ==========================================
# MOTOR DE EXECUÇÃO
# ==========================================
def rodar_pipeline_completo(arquivo_teste):
    if not os.path.exists(arquivo_teste):
        print(f"\n❌ A pular {arquivo_teste} (Ficheiro não encontrado)")
        return

    resultados_finais = {}
    print(f"\n" + "=" * 70)
    print(f"📊 INICIANDO BENCHMARK: {arquivo_teste}")
    print("=" * 70)

    # 🔥 Cria a pasta "trash" antes de rodar qualquer coisa
    os.makedirs("DATA/trash", exist_ok=True)

    aquecer_cache_do_so(arquivo_teste)

    testar_pandas(arquivo_teste, resultados_finais)
    testar_polars(arquivo_teste, resultados_finais)
    testar_duckdb(arquivo_teste, resultados_finais)
    testar_pyarrow(arquivo_teste, resultados_finais)
    testar_dask_free(arquivo_teste, resultados_finais)

    print("\n💾 Exportando resultados...")
    df_resultados = pd.DataFrame(resultados_finais)
    df_resultados.index.name = "Operacao_Metrica"
    df_resultados.reset_index(inplace=True)

    # Substitui DATA/ por DATA/relatorio/ para manter a pasta raiz limpa
    nome_csv = arquivo_teste.replace("DATA/", "DATA/relatorio/").replace(
        ".csv", "_RELATORIO.csv"
    )
    os.makedirs("DATA/relatorio", exist_ok=True)
    df_resultados.to_csv(nome_csv, index=False)
    print(f"🎉 Relatório guardado em: {nome_csv}")


if __name__ == "__main__":
    # Testa os 3 ficheiros que o gerador criou!
    arquivos_para_testar = [
        "DATA/dataset_1M_padrao.csv",
        "DATA/dataset_100k_largo.csv",
        "DATA/dataset_500k_25cols.csv",
    ]

    for arquivo in arquivos_para_testar:
        rodar_pipeline_completo(arquivo)

    print("\n🏁 TODOS OS BENCHMARKS FORAM CONCLUÍDOS!")
