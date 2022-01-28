###########################
# Projeto IRC             #
# Grupo 5                 #
###########################
# Francisca Nunes, 96736  #
# Gestor Municipal        #
###########################


import socket
import sys
import select

server_ip = '127.0.0.1'
server_port = 9995

#hostname, sld, tld, port = 'www', 'integralist', 'co.uk', 80
hostname, sld, tld, port = 'www', 'tecnico', 'ulisboa.pt', 80
target = '{}.{}.{}'.format(hostname, sld, tld)
print ('target', target)

while True:

	# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# connect the client
	# client.connect((target, port))
	client.connect((server_ip, server_port))

	print('Input message to server: ')
	msg = sys.stdin.readline()
	msg_to_send = msg.encode()

	# send some data (in this case a HTTP GET request)
	client.send(msg_to_send)

	# receive the response data (4096 is recommended buffer size)
	response = client.recv(4096)

	msg_from_client = response.decode()
	print(msg_from_client)
	if(msg_from_client == 'The server will shutdown'):
		msg = 'Ok, shutdown'
		msg_to_send = msg.encode()
		break
