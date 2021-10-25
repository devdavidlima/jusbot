import os
import re
from datetime import datetime, time
import pdfplumber
from db_functions import mycursor, register_log, insert_in_processo_retornos
from setup_extrator import path_pdf_downloads, path_text_extracted, path_log, keywords_list, insert_processos_retornos_activated, data_deposito_default, sql_processos_retorno


def create_text_backup():
    pass


def clear_text_path():
    pass


pdfdir = path_pdf_downloads
text_dir = path_text_extracted
log_path = path_log
pdf_path = "pdf/1.pdf"

pdfs = os.listdir(pdfdir)
dir_empty = os.stat(pdfdir).st_size == 0

log_time = datetime.now().strftime("%H:%M:%S")

# Dis is empty?;
# PDF List.
pdflist_to_read = []
for pdf in pdfs:
    if dir_empty:
        log = f"[ERROR] - Nao ha PDFS para ser lido em: {pdfdir}"
        # register_log(log_path, "pdf_download", log, "")
        register_log(csv_path=log_path, log=log, logtime=log_time)
    else:
        pdflist_to_read.append(pdf)
        # register_log("extrator/logs/extrator_log.csv", "pdf_download", log, "")

size_of_pdflist = len(pdflist_to_read)
print("*************")
print(
    f"SETUP_EXTRATOR: \npath_lista_pdfs= {path_pdf_downloads}, path_lista_pdfs_convertido_em_txt= {text_dir}, path_log_extrator= {log_path}")
print(f"LISTA DE PDFS: {pdflist_to_read}; TAMANHO DA LISTA: {size_of_pdflist}")
print("*************\n")

# PDF to TXT
# Txt list


def pdf2txt(pdflist_to_read, pdfdir, text_dir, log_time):
    print("*************")
    text = ""
    text_list_extracted = []
    for _pdf_path in pdflist_to_read:
        pdf_path = pdfdir + "/" + _pdf_path
        PDF = pdfplumber.open(pdf_path)
        pg = len(PDF.pages)
        pdf_name = _pdf_path.replace(".pdf", "")
        # pdf_name_list.append(pdf_name)

        # read all pages for each pdf.
        for page in range(pg):
            l = int(PDF.pages[page].rotation)
            pdf_status = "None"
            if(l):
                pdf_status = 'Orientation <{}>'.format(l)
            else:
                pdf_status = 'Orientation <Default>'
            print(f"--> {pdf_path} - quantidade de pag {page} - {pdf_status}")

            # pdf to text;
            text_path = text_dir + "/" + pdf_name + ".txt"
            try:
                data = PDF.pages[page].extract_text()
                text = text + "\n" + data

                text_list_extracted.append(text_path)

                create_text = open(text_path, "w")
                create_text.write(pdf_path + " " + str(pg) + " [Page " + str(
                    page) + " : " + str(pdf_status) + " status=ok " + "]" + "\n")
                create_text.write(text)

                print(":::::::::")
                print(
                    f"Convertendo o PDF <{pdf_path}> para TXT <{text_path}>\n")
                # print(f"{text}\n")

                create_text.close()

            except:
                # check if all pdfs were sucessfull
                print(
                    f"Falha na conversao do PDF <{pdf_path}> para TXT <{text_path}>\n")

    size_of_textlist = int(len(text_list_extracted))
    desvio = size_of_pdflist - size_of_textlist

    if not desvio == 0:
        a = f"[ERRO] nem todos pdfs foram convertidos para texto. Desvio: {desvio}"
        b = f"pdflist: {pdflist_to_read}; textlist: {text_list_extracted}\n"
        log = a + b
        # print(log)
    else:
        log = f"Conversao com Sucesso!! {pdflist_to_read} -> {text_list_extracted}\n"

    print(log)
    register_log(csv_path=log_path, log=log, logtime=log_time)
    print(":::::::::")
    PDF.close()

    return text_list_extracted


# get data from text

def get_data(textlist_extracted, keywords_list):
    print("*****")
    print(f"Extraindo Dados do Arquivo: {textlist_extracted}:\n")

    # 2015.02742-9
    # 2015.01261-8
    # formatando o textpath para virar id da lista de dados extraidos
    processo_id = textlist_extracted.replace("extrator/txt/", "")
    processo_id = processo_id.replace(".txt", "")
    processo_id = re.sub('[^0-9]', '', processo_id)
    processo_id = processo_id[0:10]
    # print(processo_id)

    processo_id = "numero_processo:" + processo_id
    values_of_data = [processo_id]
    f = open(textlist_extracted, "r")
    for line in f:
        # 2) docprocesso = favorecido_docuemnto (ok)
        _cpf = keywords_list[1] or keywords_list[0]
        if _cpf in line:
            cpf_line = line
            cpf = re.sub('[^0-9]', '', cpf_line)
            # validador
            if len(cpf) == 11 or len(cpf) == 14:
                cpf = 'cpf:' + cpf
                values_of_data.append(cpf)
                print(f"\t** {keywords_list[1]} - {cpf}")
            else:
                cpf = "[ERRO] CPF/CNPJ {textlist_extracted}"

        _nome = keywords_list[2]
        if _nome in line:
            nome_line = line
            nome_line = line.lower()
            # print("nome", nome_line)
            nome = re.sub('[^a-z]', '', nome_line)

            # print("{}".format(nome_line))
            nome_line = nome_line.replace("favorecido:", "")
            nome = nome.replace("favorecido", "")
            # n = nome + " " + nome_line
            if int(len(nome_line)) < 30:
                nome = 'favorecido:' + nome
                values_of_data.append(nome)
                print(f"\t** {keywords_list[2]}- {nome}")

        # _data_deposito = 'Data do Depósito'
        # 4) data deposito
        _data_deposito = keywords_list[3]
        if _data_deposito in line:
            timestamp_line = line
            timestamp = re.sub('[^0-9]', '', timestamp_line)
            # print("----------------{}".format(timestamp_line))
            # print("--------------- data_deposito: {}".format(timestamp))

            #data_deposito_day = timestamp[0:2]
            #data_deposito_month = timestamp[3:5]
            #data_deposito_year = timestamp[6:10]

            # 0000-00-00
            #data_deposito_usa = "{}-{}-{}".format(data_deposito_year, data_deposito_month, data_deposito_day)

            if len(timestamp) > 8:
                timestamp = data_deposito_default
                timestamp = "[ERRO] Data Deposito {textlist_extracted} data default {timestamp}"
                timestamp = 'datadeposito:' + timestamp
                values_of_data.append(timestamp)
                print(f"\t** {keywords_list[3]} - {timestamp}")
                # print("----------------", data_deposito_usa)
                # data_deposito_formart_usa = datetime.strptime(botBB_createtime, "%Y-%m-%d").date()
                # print("-", data_deposito_year)

        _conta = keywords_list[4]
        # print(_conta)
        if _conta in line:
            conta_line = line
            conta = re.sub('[^0-9]', '', conta_line)
            # validador
            # 1900 1300 5086 6
            # 4500 1300 5072 7 = 13 digitos

            # if not int(len(conta)) == 13:
            # conta = f"[ERRO] Conta/Guia {textlist_extracted}"
            conta = 'conta:' + conta
            values_of_data.append(conta)
            print(f"\t** {keywords_list[4]}- {conta}")

        _precatorio = keywords_list[5]
        # 1) numero do processo = numero precatorio judicial (ok) -> processo_id = numero precatorio judicial
        if _precatorio in line:
            precatorio_line = line
            precatorio = re.sub('[^0-9]', '', precatorio_line)

            # validador
            # if int(len(precatorio)) < 10:
            precatorio = 'precatorio:' + precatorio
            values_of_data.append(precatorio)
            print(f"\t** {keywords_list[5]} - {precatorio}")

        _valor_precatorio = keywords_list[6]
        if _valor_precatorio in line:
            _valor_precatorio_line = line
            valor_precatorio = re.sub('[^0-9]', '', _valor_precatorio_line)

            if int(len(valor_precatorio)) > 3:
                valor_precatorio = 'valor:' + valor_precatorio
                values_of_data.append(valor_precatorio)
                print(f"\t** {keywords_list[6]} - {valor_precatorio}")

        # 3) nome processo = nome favorecido
        _author = keywords_list[7] or keywords_list[8]
        if _author in line:
            author_line = line
            author = author_line
            author = 'author' + author
            values_of_data.append(author)
            print(f"\t** {keywords_list[7]} - {author}")

        # n usado para db
        _nprocesso = keywords_list[9] or keywords_list[10]
        if _nprocesso in line:
            _nprocesso_line = line
            nprocesso = re.sub('[^0-9]', '', _nprocesso_line)
            # values_of_data.append(_nprocesso_line)
            nprocesso = 'nprocesso' + nprocesso
            # values_of_data.append(nprocesso)
            print(f"\t** {keywords_list[9]} - {_nprocesso}")

        # data = {processo_id: values_of_data}
        # print(f"\n*Data_extraido* -> \n{data}")

    print(f"\n*Data_extraido* -> \n{values_of_data}")
    f.close()

    print(f"\nExtracao Completa de Dados -> {textlist_extracted}")
    print("*****")

    # if insert_processos_retornos_activated:
    # print("insert_processos_retornos_activated {insert_processos_retornos_activated}")

    return values_of_data


# run pdf to text converter
text_list_extracted = pdf2txt(pdflist_to_read=pdflist_to_read, pdfdir=pdfdir,
                              text_dir=text_dir, log_time=log_time)

# 1) numero do processo = numero precatorio judicial (ok) -> processo_id = numero precatorio judicial
# 2) docprocesso = favorecido_docuemnto (ok) -> CPF
# 3) nome processo = nome favorecido
# 4) data deposito (ta meio zuada, se n conseguir vai startar desde 2009) (ok) -> exception default


# run extrator and insert
for each_text in text_list_extracted:
    values_of_get_data = get_data(each_text, keywords_list)

    if insert_processos_retornos_activated:
        print(f"DADOS A SER INSERIDOS NO <processos_retornos>")
        for values in values_of_get_data:
            if "numero_processo" in values:
                numero_processo = values.replace("numero_processo:", "")
                print(f"\t** Processo: {numero_processo}")

            if "cpf" in values:
                docprocesso = values.replace("cpf:", "")
                print(f"\t** DOC:{docprocesso}")

            if "favorecido" in values:
                favorecido_nome = values.replace("favorecido:", "")
                print(f"\t** Favorecido: {favorecido_nome}")

            if "conta" in values:
                conta = values.replace("conta:", "")
                print(f"\t** Conta: {conta}")

            if "datadeposito" in values:
                datadeposito = values.replace("datadeposito:", "")
                datadeposito = data_deposito_default
                print(f"\t** datadeposito: {datadeposito}")

            if "valor" in values:
                valor = values.replace("valor:", "")
                print(f"\t** valor: {valor}")

                # Insert_processos_retornos_mysql
                insert_in_processo_retornos(sql_processos_retorno, numero_processo,
                                            docprocesso, favorecido_nome, conta, data_deposito_default, valor, log_time)

        #insert_inf_processo_retornos(mycursor, values_of_get_data)
    else:
        print("insert_in_processos_retornos: {insert_in_processos_retornos}")
    register_log("extrator/logs/insert_in_processos_retornos.csv",
                 values_of_get_data, log_time)

