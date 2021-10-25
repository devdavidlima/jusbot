import csv
import mysql.connector
from setup_extrator import host, user, password, database, sql_processos_retorno


mydb = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

mycursor = mydb.cursor()

# pegar numero de processo para o bot Trj:


def insert_in_processo_retornos(sql_processos_retornos, numero_processo, docprocesso, favorecido_nome, conta, datadeposito, valor, log_time, status=0, data_resgate=""):
    numero_processos = []
    sql = sql_processos_retornos
    #sql = "INSERT INTO processos_retornos (numero_processo, documento_processo, nome_processo, conta_guia, data_deposito, nome_favorecido, favorecido_documento, numero_precatorio_judicial, valor_precatorio, data_resgate, created, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    # numero_processo, nome_processo, ano_processo, valor_precatorio, status
    # documentoProcesso =
    value = (numero_processo, docprocesso, favorecido_nome, conta, datadeposito,
             favorecido_nome, docprocesso, numero_processo, valor, data_resgate, log_time, status)

    try:
        mycursor.execute(sql, value)
        mydb.commit()

        log = f">>>[Sucesso] insert_in_processo_retornos -> {value}"

    except:
        log = ">>[erro] insert_in_processo_retornos "

    print(log)

    return numero_processos


#insert_in_processo_devolvido(mycursor, sql_processos_retorno)

def register_log(csv_path, log, logtime):
    with open(csv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([log, logtime])
