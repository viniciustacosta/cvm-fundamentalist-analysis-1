import os
import pandas as pd
from datetime import datetime
from models.parecer_trimestral import Parecer_trimestral

def process_csv_files(base_path):
    parecer_trimestral_list = []
    for year_folder in os.listdir(base_path):
        year_path = os.path.join(base_path, year_folder)
        if not os.path.isdir(year_path):
            continue

        for file in os.listdir(year_path):
            if file.endswith(".csv") and file.startswith("itr_cia_aberta_parecer"):
                file_path = os.path.join(year_path, file)

                try:
                    # Carregar o CSV com o delimitador correto
                    df = pd.read_csv(file_path, encoding='latin1', delimiter=';', on_bad_lines='skip')
                except pd.errors.ParserError as e:
                    print(f"Erro ao processar o arquivo {file_path}: {e}")
                    continue
                except UnicodeDecodeError as e:
                    print(f"Erro de codificação ao processar o arquivo {file_path}: {e}")
                    continue

                # Mapear cada linha para um objeto Periodicos e Eventuais
                for _, row in df.iterrows():
                    parecer_trimestral = Parecer_trimestral(
                        _cnpj_companhia= row.get('CNPJ_CIA'),
                        _num_linha_parecer_declaracao= row.get('NUM_ITEM_PARECER_DECL'),
                        _tipo_parecer_declaracao= row.get('TP_PARECER_DECL'),
                        _tipo_relatorio_especial= row.get('TP_RELAT_ESP'),
                        _texto_parecer_declaracao= row.get('TXT_PARECER_DECL'),
                        _versao= row.get('VERSAO'),
                        _data_referencia_doc= row.get('DT_REFER'),
                        _data_doc=datetime.now().date(),
                        _mes_doc=str(row.get('DT_REFER'))[5:7],
                        _ano_doc=str(row.get('DT_REFER'))[:4]
                    )
                    # print(parecer_demonstrativo.mostrarDados())
                    parecer_trimestral_list.append(parecer_trimestral)

    return parecer_trimestral_list

def parse_date(date_str):
    if pd.isnull(date_str) or not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None
