########################
# Projeto IRC          #
# Grupo 5              #
########################
# Responsavel do Local #
# Servidor             #
########################
# 96742, Inês Gomes    #
########################

import socket
import threading
import sys
import os


#################
# Message Codes #
#################

INFO_MISS = "ERRO: Numero de parametros incorreto"
NO_INFO = "ERRO: Falta informacao"
# registo local
REG_OK = "Local registado com sucesso"
REG_DUP = "ERRO: Local com mesmo nome ja registado"
# consulta saldo
SAL_OK = "O saldo atual é"
SAL_NOT_OK = "ERRO: O local fornecido não existe"
# cancelamento registo local
CANC_OK = "Registo de local cancelado"
CANC_NOT_OK = "ERRO: Nao existe local com o id fornecido"
CANC_ON_GOING = "Os utentes foram avisados que o local vai fechar"
# criacao atividade
CR_ATIV_OK = "Atividade criada com sucesso"
CR_ATIV_DUP = "ERRO: Atividade do mesmo tipo ja existente"
CR_ATIV_MAX = "ERRO: Numero maximo de atividades atingido"
CR_ATIV_NO_LOC = "ERRO: Local inexistente"
# modificacao da atividade
MOD_ATIV_OK = "Atividade modificada com sucesso"
MOD_ATIV_INFO_MISS = "ERRO: Falta de informacao"
MOD_ATIV_NO_ATIV = "ERRO: Nao existe atividade com o id fornecido"
MOD_ATIV_ON_GOING = "ERRO: Atividade a decorrer"
# remocao atividade
REM_ATIV_OK = "Atividade removida com sucesso"
REM_ATIV_NO_ATIV = "ERRO: Nao existe atividade com o id fornecido"
REM_ATIV_ON_GOING = "ERRO: Atividade a decorrer"
# invalid message
INV = "ERRO: Tipo de mensagem incorreto"


########################
# Constant Defenitions #
########################

# estrutura local: tem as suas caracacteristicas + uma lista de atividades
class Local:
    def __init__(self, name, capacity, max_time, balance):
        self.id = local_id
        self.name = name
        self.capacity = capacity
        self.max_time = max_time
        self.balance = balance
        self.activities = []
    def __str__(self):              # override a print(local)
        loc = str(self.id) + " " + self.name + " " + str(self.capacity) + " " + str(self.max_time) + " " + str(self.balance) + "\n"
        return loc

# estrutura atividade: tem as suas caracacteristicas
class Activity:
    def __init__(self, local, type, destination, capacity, duration, score, cost):
        self.id = activity_id
        self.local = local
        self.type = type
        self.destination = destination
        self.capacity = capacity
        self.duration = duration
        self.score = score
        self.cost = cost
        self.participants = 0
    def __str__(self):
        return str(self.id) + " " + self.local + " " + self.type + " " + self.destination + " " + str(self.capacity) + " " + str(self.duration) + " " + str(self.score)  + " " + str(self.cost) + " " + str(self.participants) + "\n"


 # lista de locais e ids
local_id = 1
activity_id = 1
active_locals = {}

# max num de atividades
MAX_ATIV = 10

# requests
TYPE = 0

# files
file_locals = "registered_locals.txt"
file_activities = "registered_activities.txt"
file_clients = "registered_clients.txt"

# connection 
bind_ip = '127.0.0.1'
bind_port = 9994

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print ('Listening on {}:{}'.format(bind_ip, bind_port))


#######################
# Auxiliary Functions #
#######################

# dado o nome do local retorna o id do local caso exista
def find_local_name(name):
    for key, val in list(active_locals.items()):
        if val.name == name:
            return key
    return 0

# dado o id do local retorna esse id caso exista
def find_local_id(id_local):
    for key, val in list(active_locals.items()):
        if key == int(id_local):
            return key
    return 0

# dado o nome do local e tipo de atividade retorna o id da atividade caso exista
def find_activity_type(name_local, type):
    for key, val in list(active_locals.items()):
        if val.name == name_local:
            for i in val.activities:
                if i.type == type:
                    return i.id
    return 0

# dado o id de atividade retorna esse id caso exista
def find_activity_id(id_activity):
    for key, val in list(active_locals.items()):
        for i in val.activities:
            if i.id == int(id_activity):
                return i.id
    return 0

# dado um id de atividade retorna o id do local caso exista
def find_activity_local(id_activity):
    for key, val in list(active_locals.items()):
        for i in val.activities:
            if i.id == int(id_activity):
                return val.id
    return 0


# dado um ficheiro e algo para la escrever, escreve no ficheiro (append)
def process_into_file(text, file_name):
    f = open(file_name, 'a')
    f.write(str(text))
    f.close()


# no ficheiro dado troca a linha da atividade dada, e substitui pelos valores de to_replace
def replace_activity_file(id_activity, to_replace, file_name):
    file = open(file_name, "r")
    replaced_content = ""

    for line in file:
        words = line.split()
        if(words and words[0] == id_activity):
            line = line.strip()
            new_line = line.replace(words[2], to_replace[0])
            new_line = line.replace(words[3], to_replace[1])
            new_line = line.replace(words[4], to_replace[2])
            replaced_content = replaced_content + new_line + "\n"
        else:
            replaced_content += line

    file.close()
    write_file = open(file_name, "w")
    write_file.write(replaced_content)
    write_file.close()


# apanha a linha correspondente a atividade dada do ficheiro
def delete_activity_file(id_activity, file_name):
    file = open(file_name, "r")
    replaced_content = ""

    for line in file:
        words = line.split()
        if(words and words[0] == id_activity):
            pass
        else:
            replaced_content += line

    file.close()
    write_file = open(file_name, "w")
    write_file.write(replaced_content)
    write_file.close()


# apaga a linha correspondente ao local dado e apaga do ficheiro
def delete_local_file(id_local, file_name):
    file = open(file_name, "r")
    replaced_content = ""

    for line in file:
        words = line.split()
        if(words and words[0] == id_local):
            pass
        else:
            replaced_content += line

    file.close()
    write_file = open(file_name, "w")
    write_file.write(replaced_content)
    write_file.close()


# devolve o numero de clientes num dado local
def read_clients_file(id_local, file_name):
    #id name local job score budget time id_ativ

    file = open(file_name, "r")
    num_clients_in_local = 0

    for line in file:
        words = line.split()
        if(words and words[2] == id_local):
            num_clients_in_local += 1

    return num_clients_in_local


# apaga a linha correspondente ao utente dado do ficheiro
def delete_client_file(id_client, file_name):
    file = open(file_name, "r")
    replaced_content = ""

    for line in file:
        words = line.split()
        if(words and words[0] == id_client):
            pass
        else:
            replaced_content += line

    file.close()
    write_file = open(file_name, "w")
    write_file.write(replaced_content)
    write_file.close()

# se o utente estiver no local dado, devolve o id desse utente
def is_client_in_local(id_local, file_name):
    #id name local job score budget time id_ativ

    file = open(file_name, "r")

    for line in file:
        words = line.split()
        if(words and words[2] == id_local):
            return words[0]
    return 0

# se o utente estiver a participar numa atividade, devolve o id da mesma
def is_client_in_activity(id_activ, file_name):
    #id name local job score budget time id_ativ

    file = open(file_name, "r")

    for line in file:
        words = line.split()
        if(words and words[7] == id_activ):
            return words[7]
    return 0


##############################
# Message Handling Functions #
##############################

# REGISTAR nome_local lotacao tempo_permanencia saldo
def register_local(msg_request):
    if (len(msg_request) == 1):
        msg_reply = NO_INFO + "\n" + "id do local: " + "0" + "\n"
        server_msg = msg_reply.encode()
        return server_msg
    elif (len(msg_request) != 5):
        msg_reply = INFO_MISS + "\n" + "id do local: " + "0" + "\n"
        server_msg = msg_reply.encode()
        return server_msg

    global local_id
    id_loc = local_id
    name = msg_request[1]
    capacity = msg_request[2]
    max_time = msg_request[3]
    balance = msg_request[4]

    # limpar o ficheiro caso tenha algo la escrito
    if(id_loc == 1):
        try:
            os.remove(file_locals)
        except OSError:
            pass

    if (find_local_name(name) != 0):
        msg_reply = REG_DUP + "\n" + "id do local: " + "0" + "\n"
    else:
        msg_reply = REG_OK + "\n" + "id do local: " + str(id_loc) + "\n"
        new_local = Local(name, capacity, max_time, balance)
        active_locals[local_id] = new_local
        local_id += 1
        process_into_file(new_local, file_locals)

    server_msg = msg_reply.encode()
    return server_msg


# SALDO id_local
def get_balance(msg_request):

    if (len(msg_request) == 1):
        msg_reply = NO_INFO + "\n"
        server_msg = msg_reply.encode()
        return server_msg
    elif (len(msg_request) != 2):
        msg_reply = INFO_MISS + "\n"
        server_msg = msg_reply.encode()
        return server_msg

    id_local = msg_request[1]

    if (find_local_id(id_local) == 0):
        msg_reply = SAL_NOT_OK + "\n"
    else:
        msg_reply = SAL_OK + ": " + active_locals[find_local_id(id_local)].balance + "\n"

    server_msg = msg_reply.encode()
    return server_msg


# CANCELAR id_local
def cancel_registration(msg_request):
    if (len(msg_request) == 1):
        msg_reply = NO_INFO + "\n"
        server_msg = msg_reply.encode()
        return server_msg
    elif (len(msg_request) != 2):
        msg_reply = INFO_MISS + "\n"
        server_msg = msg_reply.encode()
        return server_msg

    id_loc = msg_request[1]

    if (find_local_id(id_loc) == 0):
        msg_reply = CANC_NOT_OK + "\n"

    # se o local não tem utentes
    elif (read_clients_file(id_loc, file_clients) == 0):
        # local fecha -> apagado do ficheiro e dos active_locals
        active_locals.pop(int(id_loc))
        delete_local_file(id_loc, file_locals)
        msg_reply = CANC_OK + "\n"

    # se o local tem utentes
    elif (read_clients_file(id_loc, file_clients) != 0):
        # local avisa utentes, depois fecha
        # remover utentes e local dos ficheiros respetivos
        active_locals.pop(int(id_loc))
        delete_local_file(id_loc, file_locals)
        delete_client_file(is_client_in_local(id_loc, file_clients), file_clients)

        # avisar responsavel do local (client) que os utentes sairam e o local fechou
        msg_reply = CANC_ON_GOING + "\n" + CANC_OK + "\n"

    server_msg = msg_reply.encode()
    return server_msg


# CRIAR_ATIV nome_local tipo destinatarios lotacao duracao pontuacao custo
def create_activity(msg_request):

    if (len(msg_request) == 1):
        msg_reply = NO_INFO + "\n" + "id da atividade: " + "0" + "\n"
        server_msg = msg_reply.encode()
        return server_msg
    elif (len(msg_request) != 8):
        msg_reply = INFO_MISS + "\n" + "id da atividade: " + "0" + "\n"
        server_msg = msg_reply.encode()
        return server_msg

    global activity_id
    id_activ = activity_id
    local = msg_request[1]
    type = msg_request[2]
    destination = msg_request[3]
    capacity = msg_request[4]
    duration = msg_request[5]
    score = msg_request[6]
    cost = msg_request[7]

    # limpar o ficheiro caso tenha algo la escrito
    if(id_activ == 1):
        try:
            os.remove(file_activities)
        except OSError:
            pass

    if (find_local_name(local) == 0):
        msg_reply = CR_ATIV_NO_LOC + "\n" + "id da atividade: " + "0" + "\n"

    elif (find_activity_type(local, type) != 0):
        msg_reply = CR_ATIV_DUP + "\n" + "id da atividade: " + "0" + "\n"

    # se o local atingiu o numero maximo de atividades
    elif (len(active_locals[find_local_name(local)].activities) >= MAX_ATIV):
        msg_reply = CR_ATIV_MAX + "\n" + "id da atividade: " + "0" + "\n"

    else:
        msg_reply = CR_ATIV_OK + "\n" + "id da atividade: " + str(id_activ) + "\n"
        new_activity = Activity(local, type, destination, capacity, duration, score, cost)
        active_locals[find_local_name(local)].activities.append(new_activity)
        activity_id += 1
        process_into_file(new_activity, file_activities)

    server_msg = msg_reply.encode()
    return server_msg


# ALTERAR_ATIV id_atividade lotacao pontuacao custo
def modify_activity(msg_request):
    if (len(msg_request) == 1):
        msg_reply = NO_INFO + "\n"
        server_msg = msg_reply.encode()
        return server_msg
    elif (len(msg_request) != 5):
        msg_reply = INFO_MISS + "\n"
        server_msg = msg_reply.encode()
        return server_msg

    id_activ = msg_request[1]
    capacity = msg_request[2]
    score = msg_request[3]
    cost = msg_request[4]

    if (find_activity_id(id_activ) == 0):
        msg_reply = MOD_ATIV_NO_ATIV + "\n"

    # erro se a atividade estiver em curso
    elif (is_client_in_activity(id_activ, file_clients) != 0):
        msg_reply = MOD_ATIV_ON_GOING + "\n"

    else:
        for a in active_locals[find_activity_local(id_activ)].activities:
            if a.id == id_activ:
                a.capacity = capacity
                a.score = score
                a.cost = cost
        msg_reply = MOD_ATIV_OK + "\n"
        to_replace = [capacity, score, cost]
        replace_activity_file(id_activ, to_replace, file_activities)

    server_msg = msg_reply.encode()
    return server_msg


# APAGAR_ATIV id_atividade
def delete_activity(msg_request):
    if (len(msg_request) == 1):
        msg_reply = NO_INFO + "\n"
        server_msg = msg_reply.encode()
        return server_msg
    elif (len(msg_request) != 2):
        msg_reply = INFO_MISS + "\n"
        server_msg = msg_reply.encode()
        return server_msg

    id_activ = msg_request[1]

    if (find_activity_id(id_activ) == 0):
        msg_reply = REM_ATIV_NO_ATIV + "\n"

    # erro se a atividade estiver em curso
    elif (is_client_in_activity(id_activ, file_clients) != 0):
        msg_reply = REM_ATIV_ON_GOING + "\n"

    else:
        for a in active_locals[find_activity_local(id_activ)].activities:
            if a.id == id_activ:
                a.activities.remove(find_activity_id(id_activ))
        msg_reply = REM_ATIV_OK + "\n"
        delete_activity_file(id_activ, file_activities)

    server_msg = msg_reply.encode()
    return server_msg


# input invalido
def invalid_message():
    response = INV + "\n"
    server_msg = response.encode()
    return server_msg


#############
# Main Code #
#############

def handle_client_connection(client_socket):
    msg_from_client = client_socket.recv(1024)
    msg_request = msg_from_client.decode().split()
    print ('--> Received {}'.format(msg_request))

    request = msg_request[TYPE]
    
    if (request == "REGISTAR"):
        server_msg = register_local(msg_request)

    elif (request == "SALDO"):
        server_msg = get_balance(msg_request)

    elif (request == "CANCELAR"):
        server_msg = cancel_registration(msg_request)

    elif (request == "CRIAR_ATIV"):
        server_msg = create_activity(msg_request)

    elif (request == "ALTERAR_ATIV"):
        server_msg = modify_activity(msg_request)

    elif (request == "APAGAR_ATIV"):
        server_msg = delete_activity(msg_request)

    elif (request == "FIM"):
        msg_reply = "OK: Finalizando...\n"
        server_msg =  msg_reply.encode()
        print("<-- Sent: {}".format(server_msg))
        client_socket.send(server_msg)
        client_socket.close()
        os._exit(1)
        
    else:
        server_msg = invalid_message()

    print("<-- Sent: {}".format(server_msg))
    client_socket.send(server_msg)
    client_socket.close()


while True:
    client_sock, address = server.accept()
    print ('Accepted connection from {}:{}'.format(address[0], address[1]))
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,)  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
    )
    client_handler.start()

