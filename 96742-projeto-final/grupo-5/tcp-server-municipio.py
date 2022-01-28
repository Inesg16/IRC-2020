###########################
# Projeto IRC             #
# Grupo 5                 #
###########################
# Francisca Nunes, 96736  #
# Gestor Municipal        #
###########################


import socket, sys
import threading
import os

bind_ip = '127.0.0.1'
bind_port = 9995

#################
# Message Codes #
#################

OK          = 'OK: '
NOT_OK      = 'ERRO: '

#message info
TYPE = 0
LOCAL_NAME = 1
SERVICE_NAME = 1

INFO_MISS = "ERRO: Numero de parametros incorreto"
NO_INFO = "ERRO: Falta informacao"

#registo servico
LOCAL_NOT_OK   = 'Local nao existe'
LOCAL_OK       = 'Local existe'
SERVICE_OK     = 'Servico registado com sucess'
SERVICE_NOT_OK = 'Servico nao existe'
SERVICE_DUP    = 'Servico duplicado'
#cobranca
NOT_SALDO      = 'Nao tem saldo suficiente'
#apagar servico
DEL_SERV_OK    = 'Servico removido com sucesso'
#mensagem invalida
INV_MSG        = 'Tipo de mensagem invalido'
SERVICE_ID     =  1
SHUTDOWN_MSG   = 'The server will shutdown'

SERVICE_FILE   = 'registered_services.txt'
LOCAL_FILE     = 'registered_locals.txt'
COMPLAINT_FILE = 'registered_complaints.txt'
CLIENT_FILE    = 'registered_clients.txt'
registered_services = {}

class Service:
    def __init__(self, name, local, tipo, price):
        self.name = name
        self.local = local
        self.tipo = tipo
        self.price = price
        global SERVICE_ID
        self.id = SERVICE_ID
        SERVICE_ID += 1

    def __str__(self):
        return str(self.id) + " " + self.name + " " + self.local  + " " + self.tipo + " " + self.price + "\n"


#######################
# Funcoes Auxiliares #
#######################

#mensagem devolida caso mensagem nao seja valida
def invalid_msg_maker():
    inv_msg = INV_MSG
    return inv_msg.encode()

#mensagem devolida caso o numero de parametros nao seja valido
def invalid_parametros():
    inv_param = INFO_MISS
    return inv_param.encode()

#mensagem devolida caso o numero de parametros nao seja valido
def no_info():
    noinfo = NO_INFO
    return noinfo.encode()

#procura um servico dado o nome
def find_service(service_name):
    global registered_services
    for key, val in list(registered_services.items()):
        if val.name == service_name:
            return key
    return 0 #retorna 0 caso nao exista

#confirma que existe o id dado
def find_service_id(service_id):
    global registered_services
    for key, val in list(registered_services.items()):
        if val.id == int(service_id):
            return key
    return 0

#procura o id do local de um servico
def find_service_local(local_name):
    global registered_services
    for key, val in list(registered_services.items()):
        if val.local == local_name:
            return key
    return 0

#procura o preco dado o id do servico
def find_preco(service_id):
    global registered_services
    for key, val in list(registered_services.items()):
        if val.id == service_id:
            return val.price
    return 0

#cria um servico no dicionario e no ficheiro
def create_service(name, local, tipo, price):
    #cria no dicionario
    New_service = Service(name, local, tipo, price)
    global registered_services
    registered_services[New_service.id] = New_service

    #cria no ficheiro, caso a ligacao seja fechada os valores nunca sao perdidos
    f = open(SERVICE_FILE, 'a')
    f.write(str(New_service))
    f.close()
    return New_service.id

#procura no ficheiro dos locais, um local com o id dado
def find_local_id(local_id):
    f = open(LOCAL_FILE, 'r')
    for line in f:
        words = line.split()
        if int(words[0]) == int(local_id):
            return int(local_id)
    return 0

#conta o numero de reclamacoes dado um local_id
def complaint_number(local_id):
    count_complaint = 0
    complaint_file = open(COMPLAINT_FILE, 'r')
    for line in complaint_file:
        words = line.split()
        if (int(words[1]) == local_id):
            count_complaint += 1
    return count_complaint

#mensagems de shutdown do sistema
def shutdown_msg():
	shtdwn_msg = SHUTDOWN_MSG
	return shtdwn_msg.encode()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print ('Listening on {}:{}'.format(bind_ip, bind_port))


##############################
# Message Handling Functions #
##############################

#1. Registar servico
#Dado o nome, id_local, tipo_servico e preco
#Erros:
#   - O servico ja existe
#   - O local nao existe
def register_service(msg_request):
    #apaga tudo do ficheiro quando uma nova ligacao e efetuada
    if(SERVICE_ID == 1):
        try:
            os.remove(SERVICE_FILE)
        except OSError:
            pass

    global registered_services
    name = msg_request[SERVICE_NAME]
    msg_reply = OK + SERVICE_OK + "\n"
    local_id = msg_request[2]
    local = find_local_id(local_id)
    msg_reply = ''

    #se o nome e local onde vai ser criado ja existe
    dst_name = find_service(str(name))
    print(dst_name)
    if (dst_name != 0):
        service_id = find_service_id(dst_name)
        if str(registered_services[service_id].local) == str(local_id):
            msg_reply = ' 0 ' + NOT_OK + SERVICE_DUP + "\n"
            msg_reply = msg_reply.encode()
            return(msg_reply)

    #caso o id fornecido seja 0, o servico esta disponivel para todos os locais
    if (int(local_id) == 0):
        lf = open(LOCAL_FILE, 'r')
        for line in lf:
            words = line.split()
            create_service(name, words[1], msg_request[3], msg_request[4])
            _id = find_service_local(words[1])
            msg_reply += OK + str(registered_services[_id].id) + "\n"


    else:
        if local == 0:
            msg_reply = ' 0 ' + NOT_OK + LOCAL_NOT_OK + "\n"

        else:
            _id = create_service(name, local_id, msg_request[3], msg_request[4])
            msg_reply = OK + str(registered_services[_id].id) + "\n"

    msg_reply = msg_reply.encode()
    return(msg_reply)

#2. Procurar local
#Dado id_local
#Erros:
#   - O local nao existe
def search_local(msg_request):
    local_id = msg_request[1]
    dst_name = find_local_id(int(local_id))
    msg_reply = OK + LOCAL_OK + "\n"
    count_complaint = 0
    ranking = 1
    lista = {}

    #cria lista com o id do local e o numero de reclamacoes de cada local
    #ordena a lista
    lf = open(LOCAL_FILE, 'r')
    for line in lf:
        words = line.split()
        cn = complaint_number(int(words[0]))
        lista[words[0]] = cn
        sort_list = sorted(lista.values())


    # se for dado o valor 0, imprime-se todos os locais por ordem do ranking
    if (int(local_id) == 0):
        f = open(LOCAL_FILE)
        keys = list(lista.keys())
        for line in f:
            words = line.split()
            ranking = keys.index(words[0])
            msg_reply += str(words[0]) + ' ' + str(words[1]) + ' ' + str(words[2]) + ' ' + str(ranking + 1) + "\n"
        server_msg = msg_reply.encode()
        return(server_msg)
    else:
        if (dst_name == 0):
            msg_reply = NOT_OK + LOCAL_NOT_OK + "\n"

        # imprime o local dado um id_local diferente de 0
        else:
            lf = open(LOCAL_FILE, 'r')
            keys = list(lista.keys())
            for line in lf:
                words = line.split()
                if (int(words[0]) == int(local_id)):
                    ranking = keys.index(words[0])
                    msg_reply = OK + ' ' + str(local_id) + ' ' + str(words[1]) + ' ' + str(words[2]) + ' ' + str(ranking + 1) + '\n'

        server_msg = msg_reply.encode()
        return(server_msg)


#3. Procura reclamacoes
#Dado id_local
#Erros:
#   - O local nao existe
def search_reclamacao(msg_request):
    local_id = msg_request[1]
    msg_reply = OK + LOCAL_OK + "\n"
    count_complaint = 0
    count_client = 0

    #o local nao existe
    dst_name = find_local_id(local_id)
    if (dst_name == 0):
        msg_reply = NOT_OK + LOCAL_NOT_OK + "\n"

    else:
        #conta o numero de reclamcoes dado um lugar
        count_complaint = complaint_number(int(local_id))

        #conta o numero de clientes num dado lugar
        f = open(CLIENT_FILE, 'r')
        for line in f:
            words = line.split()
            if (words and words[2] == local_id):
                count_client += 1

        msg_reply = OK + ' ' + str(count_complaint) + ' ' + str(count_client)

    server_msg = msg_reply.encode()
    return(server_msg)


#4. Cobranca
#Dado id_servico e valor
#Erros:
#   - O servico nao existe
#   - Nao tem saldo suficiente
def cobranca(msg_request):
    global registered_services
    service_id = msg_request[1]
    service = find_service_id(service_id)
    valor = int(msg_request[2])
    msg_reply = OK + SERVICE_OK + "\n"
    replaced_content = ""

    lf = open(SERVICE_FILE, 'w')
    #nao existe servico dado
    if service == 0:
        msg_reply = '0 ' + NOT_OK + SERVICE_NOT_OK + "\n"
    else:
        price = registered_services[int(service_id)].price
        #caso tenho saldo suficiente:
        if(int(price) > valor):
            valor_final = int(price) - valor
            registered_services[int(service_id)].price = valor_final
            #altera o valor e reescrever o ficheiro com os servicos
            for key,val in list(registered_services.items()):
                New_service = str(val.id) + " " + str(val.name) + " " + str(val.local)  + " " + str(val.tipo) + " " + str(val.price) + "\n"
                lf.write(str(New_service))
            lf.close()
            msg_reply = '1 ' + OK + "\n"
        else:
            msg_reply = '0 ' + NOT_OK + NOT_SALDO + "\n"

    server_msg = msg_reply.encode()
    return(server_msg)


#5. Terminacao do servico
#Dado id_servico
#Erro:
#   - O servico nao existe
def remove_service(msg_request):
    global registered_services
    service_id = msg_request[1]
    dst_name = find_service_id(service_id)
    msg_reply = '1 ' + OK + DEL_SERV_OK + '\n'

    if (dst_name == 0):
        msg_reply = '0 ' + NOT_OK + SERVICE_NOT_OK + "\n"

    else:
        registered_services.pop(int(service_id))

        f = open(SERVICE_FILE, 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            words = line.split()
            if(words and words[0] == service_id):
                lines.remove(line)
        #reescrever tudo no ficheiro visto que tivemos de apagar uma linha
        nf = open(SERVICE_FILE, "w+")
        for line in lines:
            nf.write(line)
        nf.close()

    server_msg = msg_reply.encode()
    return(server_msg)


def handle_client_connection(client_socket):
    msg_from_client = client_socket.recv(1024)
    request = msg_from_client.decode().split()
    msg_send = ''
    print ('Received {}'.format(request))

    msg_to_client = 'ACK'.encode()

    if(request[TYPE] == 'REGISTAR_SERVICO'):
        if(len(request) == 1):
            msg_send = no_info()
        elif(len(request) != 5):
            msg_send = invalid_parametros()
        else:
            msg_send = register_service(request)

    elif (request[TYPE] == 'PROCURAR_LOCAL'):
        if(len(request) == 1):
            msg_send = no_info()
        elif(len(request) != 2):
            msg_send = invalid_parametros()
        else:
            msg_send = search_local(request)
    elif (request[TYPE] == 'COBRANCA'):
        if(len(request) == 1):
            msg_send = no_info()
        elif(len(request) != 3):
            msg_send = invalid_parametros()
        else:
            msg_send = cobranca(request)
    elif (request[TYPE] == 'APAGAR_SERVICO'):
        if(len(request) == 1):
            msg_send = no_info()
        elif(len(request) != 2):
            msg_send = invalid_parametros()
        else:
            msg_send = remove_service(request)

    elif (request[TYPE] == 'PROCURAR_RECLAMACAO'):
        if(len(request) == 1):
            msg_send = no_info()
        elif(len(request) != 2):
            msg_send = invalid_parametros()
        else:
            msg_send = search_reclamacao(request)
    elif(request[TYPE] == 'KILLSERVER'):
    	global shutdown
    	shutdown = 1
    	msg_send = shutdown_msg()
    	client_socket.send(msg_send)
    	client_socket.close()
    	os._exit(1)
    else:
        msg_send = invalid_msg_maker()
    client_socket.send(msg_send)
    client_socket.close()

while True:
    client_sock, address = server.accept()
    print ('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
    )
    client_handler.start()

