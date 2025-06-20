
import os
import pandas as pd
from datetime import datetime
from models.informacao_trimestral import Informacao_trimestral
import re

# Mapeamento entre siglas de arquivos e comportamentos da tabela planos_contas
SIGLA_COMPORTAMENTO_MAP = {
    "BPA": "BPA",
    "BPP": "BPP",
    "DRE": "DRE",
    "DVA": "DVA",
}


def carregar_grupos_demonstrativo(cursor):
    cursor.execute("SELECT codigo_grupo_dfp, grupo_dfp FROM grupo_demonstrativo_financeiro")
    rows = cursor.fetchall()
    return {codigo.upper(): descricao for codigo, descricao in rows}


def carregar_planos_contas(cursor):
    cursor.execute("SELECT comportamento, codigo_conta FROM planos_contas")
    rows = cursor.fetchall()

    planos = {}
    for comportamento, codigo in rows:
        if comportamento not in planos:
            planos[comportamento] = []
        planos[comportamento].append(str(codigo).strip().lower())
    return planos


def identificar_comportamento(arquivo_nome):
    arquivo_nome = arquivo_nome.upper()
    for sigla, comportamento in SIGLA_COMPORTAMENTO_MAP.items():
        if sigla in arquivo_nome:
            return comportamento
    return None


def parse_date(date_str):
    if pd.isnull(date_str) or not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def carregar_mapas_auxiliares(conexao):
    cursor = conexao.connection.cursor()

    def carregar_tabela(nome_tabela, nome_id_coluna):
        cursor.execute(f"SELECT {nome_id_coluna}, descricao FROM {nome_tabela}")
        return {desc.lower().strip(): id_ for id_, desc in cursor.fetchall()}

    return {
        "escala_monetaria": carregar_tabela("escala_monetaria", "id_escala"),
        "moeda": carregar_tabela("moeda", "id_moeda"),
        "ordem_exercicio": carregar_tabela("ordem_exercicio", "id_ordem"),
    }


def process_itr_files(base_path, conexao):
    informacao_tri_list = []
    cursor = conexao.connection.cursor()
    mapas = carregar_mapas_auxiliares(conexao)
    grupo_demostrativo = carregar_grupos_demonstrativo(cursor)
    planos_contas = carregar_planos_contas(cursor)

    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if not os.path.isdir(year_path):
            continue

        for file in os.listdir(year_path):
            if not file.endswith(".csv"):
                continue

            comportamento = identificar_comportamento(file)
            print(f"Arquivo: {file} → comportamento identificado: {comportamento}")

            if comportamento is None or comportamento not in planos_contas:
                continue

            contas_desejadas = planos_contas[comportamento]
            file_path = os.path.join(year_path, file)

            try:
                df = pd.read_csv(
                    file_path, encoding="latin1", delimiter=";", on_bad_lines="skip"
                )
            except (pd.errors.ParserError, UnicodeDecodeError) as e:
                print(f"[ERRO] {file_path}: {e}")
                continue

            # Normaliza colunas de comparação
            df["CD_CONTA"] = df["CD_CONTA"].astype(str).str.strip().str.lower()
            df["DS_CONTA"] = df["DS_CONTA"].astype(str).str.strip().str.lower()

            df_filtrado = df[
                df["CD_CONTA"].isin(contas_desejadas)
                | df["DS_CONTA"].isin(contas_desejadas)
            ]

            for _, row in df_filtrado.iterrows():
                informacao_tri = Informacao_trimestral(
                    _id_plano_conta=row.get("CD_CONTA"),
                    _cnpj_companhia=re.sub(r"\D", "", row.get("CNPJ_CIA") or ""),
                    _id_escala=mapas["escala_monetaria"].get(
                        str(row.get("ESCALA_MOEDA")).lower().strip()
                    ),
                    _id_moeda=mapas["moeda"].get(str(row.get("MOEDA")).lower().strip()),
                    _id_ordem=mapas["ordem_exercicio"].get(
                        str(row.get("ORDEM_EXERC")).lower().strip()
                    ),
                    _codigo_grupo_dfp=row.get("GRUPO_DFP"),
                    _conta_fixa=row.get("ST_CONTA_FIXA"),
                    _versao=row.get("VERSAO"),
                    _data_inicio_exercicio=parse_date(row.get("DT_INI_EXERC")),
                    _data_fim_exercicio=parse_date(row.get("DT_FIM_EXERC")),
                    _data_referencia_doc=parse_date(row.get("DT_REFER")),
                    _valor_conta=row.get("VL_CONTA"),
                    _mes=str(row.get("DT_REFER"))[5:7] if row.get("DT_REFER") else None,
                    _ano=str(row.get("DT_REFER"))[:4] if row.get("DT_REFER") else None,
                )

                informacao_tri_list.append(informacao_tri)

    return informacao_tri_list
