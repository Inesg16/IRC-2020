import socket, sys
import threading
import pathlib
import os
import random


bind_ip = '127.0.0.1'
bind_port = 9993

# shutdown = 1 -> kills server
shutdown = 0

#return codes
OK          = 'OK: '
NOT_OK      = 'ERRO: '

#message info
TYPE = 0
CLIENT_NAME = 1

#return sub-codes

REG_OK       = 'utilizdor registado com sucesso'
REG_UPDATED  = 'registo do utilizador atualizado'
REG_NOT_OK   = 'utilizador nao registado com sucesso'
REG_DUP      = 'user already registered'
LOCAL_FULL   = 'lotacao maxima do local atingida'
INV_CLIENT   = 'utilizador nao registado' # invalid user
INV_SESSION  = 'utilizador nao tem sessao ativa'  #no active session for the user"
INV_MSG      = 'tipo de mensagem invalido'
DEL_OK       = 'utilizador removido com sucesso'
MISS_INFO    = 'falta de informacao/parametros'
USER_IN_LOC  = 'utilizador ja se encontra no local'
MAX_CAP      = 'lotacao maxima atingida'
USER_IN_ACT  = 'utilizador enontra-se numa atividade'
INV_ACT      = 'atividade invalida'
INV_LOC      = 'local inexistente'
COMPLAINT_OK = 'reclamacao criada com sucesso'
CLIENT_ID    =  1
COMPLAINT_ID =  1
SHUTDOWN_MSG = 'the server will now shutdown'

# file names
CLIENT_FILE     = 'registered_clients.txt'
LOCAL_FILE      = 'registered_locals.txt'
ACTIVITIES_FILE = 'registered_activities.txt'
COMPLAINTS_FILE = 'registered_complaints.txt'


class Client:
    def __init__(self, name, local, job, score, budget, time):
    	self.name = name
    	self.local = local
    	self.job = job
    	self.score = score
    	self.budget = budget
    	self.time = time
    	global CLIENT_ID
    	self.id = CLIENT_ID
    	self.activity_id = 0
    	CLIENT_ID += 1

    def change_activity_id(self, new_activity_id):
    	self.activity_id = new_activity_id

    # create methods to change artibutes

    def __str__(self):
        return str(self.id) + " " + self.name + " " + self.local + " " + self.job + " " + str(self.score) + " " + str(self.budget) + " " + str(self.time) + " " + str(self.activity_id) +"\n"

class Complaint:
	def __init__(self, local, complaint_type, description):
		self.local = local
		self.type = complaint_type
		self.description = description
		global COMPLAINT_ID
		self.id = COMPLAINT_ID
		COMPLAINT_ID += 1
	def __str__(self):
		return str(self.id) + " " + self.local + " " + self.type + " " + self.description + "\n"


#global vector with all users
registered_users = {} #dict: key: client_ID; val: Client class: example:'maria'= ('127.0.0.1',17234)


#generic functions


#message creators
def shutdown_msg_maker():
	shtdwn_msg = SHUTDOWN_MSG
	return shtdwn_msg.encode()

def invalid_msg_maker():
	inv_msg = MISS_INFO
	return inv_msg.encode()



#finders and searchers
def find_client (client_name):
	global registered_users
	for key, val in list(registered_users.items()):
		if val.name == client_name:
			return key
	return 0

def search_id(client_ID):
    global registered_users
    for key, val in list(registered_users.items()):
        if val.id == int(client_ID):
            return key
    return 0 



#booleans

def local_exists(local):
	f = open(LOCAL_FILE, 'r')
	for line in f:
		words = line.split()
		if(words[0] == local):
			return True
	return False

def find_local_id(local_name):
	f = open(LOCAL_FILE, 'r')
	for line in f:
		words = line.split()
		if(words[1] == local_name):
			return words[0]
	return 0

def local_full(local):
	f = open(LOCAL_FILE, 'r')
	capacity = 0
	for line in f:
		words = line.split()
		if(words[0] == local):
			capacity = words[2]
	f.close()

	try:
		f = open(CLIENT_FILE, 'r')
		counter = 0

		for line in f:
			words = line.split()
			if(words[1] == local):
				counter += 1

		f.close()

		if counter == capacity:
			return True
		return False
	except FileNotFoundError:
		return False


def user_in_act(client_id):
	return registered_users[int(client_id)].activity_id != 0


def is_activity_full(activity_id):
	f = open(ACTIVITIES_FILE)
	for line in f:
		words = line.split()
		if (words[0] == activity_id):

			if (words[3]==0):
				return False

			elif (words[3]==words[7]):
				f.close()
				return True
			f.close()
			return False


def is_in_local(client_name, local):
	try:
		f = open(CLIENT_FILE, 'r')

		for line in f:
			words = line.split()
			if(words[2] == local and words[1] == client_name):
				return True
		return False
	except FileNotFoundError:
		return False


#creators
def create_user (name, local, job, score, budget, time):
    New_client = Client(name, local, job, score, budget, time)
    global registered_users
    registered_users[New_client.id] = New_client
    f = open(CLIENT_FILE, 'a')
    f.write(str(New_client))
    f.close()
    return New_client



# socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print ('Listening on {}:{}'.format(bind_ip, bind_port))




#message handling functions

#registers a client in a local
#errors:  - local is full
#         - user exists in local

def register_client(msg_request):
    if(CLIENT_ID == 1):
        try:
            os.remove(CLIENT_FILE)
        except OSError:
            pass

    name = msg_request[2]
    msg_reply = OK + REG_OK + "\n" + 'id do cliente: ' + str(CLIENT_ID) + "\n"
    dst_name = find_client(name)

    if (not local_exists(msg_request[1])):
    	msg_reply = NOT_OK + INV_LOC + '\n' + 'id do cliente: 0\n'
    	server_msg = msg_reply.encode()
    	return(server_msg)

    elif (is_in_local(name, msg_request[1])):
    	msg_reply = NOT_OK + REG_DUP + "\n" + 'id do cliente: 0\n'
    	server_msg = msg_reply.encode()
    	return(server_msg)

    elif (local_full(msg_request[1])):
    	msg_reply = NOT_OK + LOCAL_FULL + "\n" + 'id do cliente: 0\n'
    	server_msg = msg_reply.encode()
    	return(server_msg)
    # register the user
    else:
    	create_user(msg_request[2], msg_request[1], msg_request[3], msg_request[4], msg_request[5], msg_request[6])
    	#create_user(client_name, local, job, score, budget, time)
    server_msg = msg_reply.encode()
    return(server_msg)




#alters a client's registration
#can change job and time
#errors:  - user doesnt exist
#         - user in activity

def alter_client(msg_request):
    global registered_users
    client_id = msg_request[1]
    dst_name = search_id(client_id)

    msg_reply = OK + REG_UPDATED + '\n1\n'

    if(dst_name == 0):
        msg_reply = NOT_OK + INV_CLIENT
        server_msg = msg_reply.encode()
        return (server_msg)

    elif(user_in_act(client_id)):
        msg_reply = NOT_OK + USER_IN_ACT + '\n0\n'
        server_msg = msg_reply.encode()
        return (server_msg)

    elif (len(msg_request) == 3):
        # modifies time
        if(isinstance(msg_request, int)):
            registered_users[dst_name].time = msg_request[2]
        # modifies job
        else:
            registered_users[dst_name].job = msg_request[2]
    # modiies both job and time
    else:
        registered_users[dst_name].time = msg_request[3]
        registered_users[dst_name].job = msg_request[2]       

    alter_client_aux(client_id, registered_users[dst_name].job, registered_users[dst_name].time)
    server_msg = msg_reply.encode()
    return(server_msg)


# alters client in client file
def alter_client_aux(clientID, newJob, newTime):

	file = open(CLIENT_FILE, "r")
	replaced_content = ""

	for line in file:
		words = line.split()
		if(words and words[0] == clientID):
		    line = line.strip()
		    new_line = line.replace(words[3], newJob)
		    new_line = new_line.replace(words[6], newTime)
		    replaced_content = replaced_content + new_line + "\n"
		else:
		    replaced_content += line

	file.close()
	write_file = open(CLIENT_FILE, "w")
	write_file.write(replaced_content)
	write_file.close()


#removes a client's registration
#errors:  - client doesnt exist
#         - client in activity
def remove_client(msg_request):
    global registered_users
    client_id = msg_request[1]
    dst_name = search_id(client_id)
    msg_reply = OK + DEL_OK + '\n1\n'
    
    if(dst_name == 0):
        msg_reply = NOT_OK + INV_CLIENT + '\n0\n'

    print(registered_users[int(client_id)].activity_id)
    if(user_in_act(client_id)):
        msg_reply = NOT_OK + USER_IN_ACT + '\n0\n'

    else:
        registered_users.pop(dst_name)
        remove_client_aux(client_id)

    server_msg = msg_reply.encode()
    return(server_msg)


def remove_client_aux(clientID):
	file = open(CLIENT_FILE, "r")
	replaced_content = ""

	for line in file:
		words = line.split()
		if (words and words[0] == clientID):
			pass
		else:
		    replaced_content += line

	file.close()
	write_file = open(CLIENT_FILE, "w")
	write_file.write(replaced_content)
	write_file.close()


#lists all available activities
#errors  - none
def list_activities(msg_request):
    msg_reply = ''
    f = open(ACTIVITIES_FILE)
    for line in f:
        msg_reply += line
    server_msg = msg_reply.encode()
    return server_msg


#asks for an activity
#if sucessefull the client starts the activity
#0 -> random activity
#errors  - activity at capacity
#        - local is closing
#        - inadequate profile

def ask_activity(msg_request):
	global registered_users
	client_id = msg_request[1]
	activity_id = msg_request[2]
	msg_reply = ''
	if (not search_id(client_id)):
		msg_reply = INV_CLIENT
		server_msg = msg_reply.encode()
		return server_msg

	if (user_in_act(int(client_id))):
		msg_reply = USER_IN_ACT
		server_msg = msg_reply.encode()
		return server_msg

	if (int(activity_id) == 0):
		activity_id = random_activity(client_id)

	f = open(ACTIVITIES_FILE, 'r')
	for line in f:
		words = line.split()
		if (words and words[0] == str(activity_id)):
			if(is_in_local(registered_users[int(client_id)].name, find_local_id(words[1]))):
				if(not is_activity_full(activity_id)):
					client_on_activity(client_id, activity_id)				
					msg_reply = str(activity_id) + ' ' + str(words[5])
					server_msg = msg_reply.encode()
					return server_msg
			else:
				break

	msg_reply = INV_ACT
	server_msg = msg_reply.encode()
	return server_msg

def find_local_name(local_id):
	f = open(LOCAL_FILE, 'r')
	for line in f:
		words = line.split()
		if (words[0] == local_id):
			return words[1]
	return 0

def random_activity(client_id):
	local_id = registered_users[int(client_id)].local
	local_name = find_local_name(local_id)
	f = open(ACTIVITIES_FILE, 'r')
	possible_activ = []

	for line in f:
		words = line.split()
		if (words[1] == str(local_name)):
			possible_activ.append(words[0])

	if (len(possible_activ) == 0):
		return 0
	random_activity_id = random.choice(possible_activ)
	return random_activity_id


def client_on_activity(client_id, activity_id):
	global registered_users
	f = open(CLIENT_FILE, 'r')
	file_contents = ''
	for line in f:
		words = line.split()
		if(words[0] == client_id):
		    line = line.strip()
		    new_line = line.replace(words[7], activity_id)
		    file_contents = file_contents + new_line + "\n"	
		else:
			file_contents = file_contents + line
	f.close()
	write_file = open(CLIENT_FILE, 'w')
	write_file.write(file_contents)
	write_file.close
	registered_users[int(client_id)].change_activity_id(activity_id)


#files a complaint
#errors  - local doesnt exist
def file_complaint(msg_request):
	local = msg_request[1]
	complaintType = msg_request[2]
	description = msg_request[3]
	msg_reply = COMPLAINT_OK + '\n'

	if(not local_exists(local)):
		msg_reply = INV_LOC + '\n'

	newComplaint = create_complaint(local, complaintType, description)
	server_msg = msg_reply.encode()
	return server_msg




def create_complaint(local, complaintType, description):
	newComplaint = Complaint(local, complaintType, description)
	f = open(COMPLAINTS_FILE, 'a')
	f.write(str(newComplaint))
	f.close()

	return newComplaint



def handle_client_connection(client_socket):
    msg_from_client = client_socket.recv(1024)
    request = msg_from_client.decode().split()
    msg_send = ''
    print ('Received {}'.format(request))

    if(request[TYPE] == 'REGISTAR_UT'):
        if(len(request) != 7):
            msg_send = invalid_msg_maker()
        else:
            msg_send = register_client(request)

    elif(request[TYPE] == 'ALTERAR_UT'):
        if(3 > len(request) or len(request) > 4):
            msg_send = invalid_msg_maker()
        else:
            msg_send = alter_client(request)
    
    elif(request[TYPE] == 'REMOVER_UT'):
        if(len(request) != 2):
            msg_send = invalid_msg_maker()
        else:
            msg_send = remove_client(request)
    
    elif(request[TYPE] == 'CONSULTAR_ATIV'):
        if(len(request) != 1):
            msg_send = invalid_msg_maker()
        else:
            msg_send = list_activities(request)

    elif(request[TYPE] == 'REALIZAR_ATIV'):
        if(len(request) != 3):
            msg_send = invalid_msg_maker()
        else:
            msg_send = ask_activity(request)

    elif(request[TYPE] == 'RECLAMAR'):
        if(len(request) != 4):
            msg_send = invalid_msg_maker()
        else:
            msg_send = file_complaint(request)

    elif(request[TYPE] == 'KILLSERVER'):
    	global shutdown
    	shutdown = 1
    	msg_send = shutdown_msg_maker()
    	client_socket.send(msg_send)
    	client_socket.close()
    	os._exit(1)

    else:
    	msg_send = INV_MSG + '\n'
    	msg_send =msg_send.encode()


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
