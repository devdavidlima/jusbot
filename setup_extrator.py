import json

jsonFile = "setup_extrator.json"


def read_configJson(arquivo):
    try:
        with open(arquivo) as f:
            config_json = json.load(f)
    except:
        print("[erro] setup.json Inlegível")

    return config_json


read_input_json = read_configJson(jsonFile)

path_pdf_downloads = read_input_json["path_pdf_downloads"]
path_text_extracted = read_input_json["path_text_extracted"]
path_log = read_input_json["path_logs"]
keywords_list = read_input_json["keywords_list"]
run_extrator_activate = read_input_json["run_extrator"]
insert_processos_retornos_activated = read_input_json["insert_processos_retornos_activated"]
data_deposito_default = read_input_json["data_deposito_default"]

host = read_input_json["host"]
user = read_input_json["user"]
password = read_input_json["password"]
database = read_input_json["database"]
delay = read_input_json["delay"]

sql_processos_retorno = read_input_json["sql_processos_retorno"]
path_logs_insert_in_processos_retornos = read_input_json["path_logs_insert_in_processos_retornos"]
