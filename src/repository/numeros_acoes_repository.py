import sqlite3
import os
from datetime import datetime
# from zoneinfo import ZoneInfo
import logging
from utils.logger import escrever_linha_em_branco, escrever_linha_separador


class ConexaoBanco:
    """Classe para gerenciar a conexão com o banco de dados SQLite."""


    def __init__(self, db_path, nivel=logging.WARNING):
        self.db_path = db_path
        self.connection = None
        self.log_sucesso, self.log_erro = self._setup_logger(nivel=nivel)


    def _setup_logger(self, log_dir="logs/logs_insercao", nivel=logging.WARNING):
        hoje = datetime.now().strftime("%Y-%m-%d")
        log_sucesso_dir = os.path.join(log_dir, hoje)
        log_erro_dir = os.path.join(log_dir, hoje)

        os.makedirs(log_sucesso_dir, exist_ok=True)
        os.makedirs(log_erro_dir, exist_ok=True)

        sucesso_logger = logging.getLogger(f"sucesso_{id(self)}")
        sucesso_logger.setLevel(nivel)
        sucesso_handler = logging.FileHandler(
            os.path.join(log_sucesso_dir, "sucesso.log"), encoding="utf-8"
        )
        sucesso_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        sucesso_logger.addHandler(sucesso_handler)

        erro_logger = logging.getLogger(f"erro_{id(self)}")
        erro_logger.setLevel(nivel)
        erro_handler = logging.FileHandler(
            os.path.join(log_erro_dir, "erro.log"), encoding="utf-8"
        )
        erro_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        erro_logger.addHandler(erro_handler)

        # return sucesso_logger, erro_logger


        # os.makedirs(log_sucesso_dir, exist_ok=True)
        # os.makedirs(log_erro_dir, exist_ok=True)

        # sucesso_logger = logging.getLogger("sucesso")
        # sucesso_logger.setLevel(logging.INFO)
        # sucesso_handler = logging.FileHandler(
        #     os.path.join(log_sucesso_dir, "sucesso.log"), encoding="utf-8"
        # )
        # sucesso_handler.setFormatter(
        #     logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # )
        # if not sucesso_logger.handlers:
        #     sucesso_logger.addHandler(sucesso_handler)

        # erro_logger = logging.getLogger("erro")
        # erro_logger.setLevel(logging.WARNING)
        # erro_handler = logging.FileHandler(
        #     os.path.join(log_erro_dir, "erro.log"), encoding="utf-8"
        # )
        # erro_handler.setFormatter(
        #     logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        # )
        # if not erro_logger.handlers:
        #     erro_logger.addHandler(erro_handler)


        return sucesso_logger, erro_logger

    def conectar(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            print("Conexão com o banco de dados SQLite estabelecida com sucesso.")
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")

    def desconectar(self):
        if self.connection:
            self.connection.close()
            print("Conexão com o banco de dados encerrada.")

    def inserir_numeros_acoes(self, numeros_acoes):
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO numeros_acoes (
                    fonte_dados,
                    cnpj_companhia,
                    qtd_acoes_ordinarias_capital_integralizado,
                    qtd_acoes_preferenciais_capital_integralizado,
                    qtd_total_acoes_capital_integralizado,
                    qtd_acoes_ordinarias_tesouro,
                    qtd_acoes_preferenciais_tesouro,
                    qtd_total_acoes_tesouro,
                    versao,
                    data_referencia,
                    mes,
                    ano
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(fonte_dados, cnpj_companhia, data_referencia) DO UPDATE SET
                    qtd_acoes_ordinarias_capital_integralizado = excluded.qtd_acoes_ordinarias_capital_integralizado,
                    qtd_acoes_preferenciais_capital_integralizado = excluded.qtd_acoes_preferenciais_capital_integralizado,
                    qtd_total_acoes_capital_integralizado = excluded.qtd_total_acoes_capital_integralizado,
                    qtd_acoes_ordinarias_tesouro = excluded.qtd_acoes_ordinarias_tesouro,
                    qtd_acoes_preferenciais_tesouro = excluded.qtd_acoes_preferenciais_tesouro,
                    qtd_total_acoes_tesouro = excluded.qtd_total_acoes_tesouro,
                    versao = excluded.versao
            """

            # Construir valores garantindo que não haja extras e substituindo 'nan' por None
            # Construir valores garantindo validação dos campos
            values = (
                    tratar_valor(numeros_acoes._fonte_dados),
                    tratar_valor(numeros_acoes._cnpj_companhia),
                    tratar_valor(numeros_acoes._qtd_acoes_ordinarias_capital_integralizado, tipo="int"),
                    tratar_valor(numeros_acoes._qtd_acoes_preferenciais_capital_integralizado, tipo="int"),
                    tratar_valor(numeros_acoes._qtd_total_acoes_capital_integralizado, tipo="int"),
                    tratar_valor(numeros_acoes._qtd_acoes_ordinarias_tesouro, tipo="int"),
                    tratar_valor(numeros_acoes._qtd_acoes_preferenciais_tesouro, tipo="int"),
                    tratar_valor(numeros_acoes._qtd_total_acoes_tesouro, tipo="int"),
                    tratar_valor(numeros_acoes._versao, tipo="int"),
                    tratar_valor(numeros_acoes._data_referencia,tipo="date"),
                    tratar_valor(numeros_acoes._mes,tipo="int"),
                    tratar_valor(numeros_acoes._ano,tipo="int"),
            )
            # print("\n\n")
            # # Gerar query SQL formatada para depuração
            # formatted_query = query.replace("%s", "{}").format(
            #     *[f"'{v}'" if v is not None else "NULL" for v in values]
            # )
            # print("SQL gerado para execução:\n", formatted_query)

            cursor.execute(query, values)
            # self.connection.commit()
            # escrever_linha_em_branco()
            # escrever_linha_separador()
            # escrever_linha_em_branco()
            # self.logger.info(f"Empresa {empresa._nome_empresa} do ano {empresa._ano} inserida com sucesso.")
            # escrever_linha_em_branco()
            self.log_sucesso.info(f"Numero de Ações do CNPJ: {numeros_acoes._cnpj_companhia} e do ano {numeros_acoes._ano} e da Fonte de dados: {numeros_acoes._fonte_dados} inserida com sucesso.")
            print(
                f"Numero de Ações  inserida com sucesso."
            )
            escrever_linha_em_branco(self.log_sucesso)
        except sqlite3.Error as e:
            escrever_linha_em_branco(self.log_erro)
            escrever_linha_separador(self.log_erro)
            escrever_linha_em_branco(self.log_erro)

            self.log_erro.error(
                f"Erro ao inserir Numero de Ações do CNPJ: {numeros_acoes._cnpj_companhia} e do ano {numeros_acoes._ano} e da Fonte de dados: {numeros_acoes._fonte_dados}, erro: {e}."
            )
            escrever_linha_em_branco(self.log_erro)
            print(
                f"Erro ao inserir Numero de Ações do CNPJ: {numeros_acoes._cnpj_companhia} e do ano {numeros_acoes._ano} e da Fonte de dados: {numeros_acoes._fonte_dados}, erro: {e}."
            )



def tratar_valor(valor, tipo=None):
    if str(valor).lower() == "nan" or valor is None:
        return None
    if tipo == "int":
        try:
            return int(valor)
        except (ValueError, TypeError):
            return None
    elif tipo == "date":
        try:
            return str(valor) if str(valor) != "" else None
        except (ValueError, TypeError):
            return None
    else:
        return valor









