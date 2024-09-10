import os
import socket


tokens = {}
smsList = []
hName = socket.gethostname()
currentServer = socket.gethostbyname(hName)
currentPort = os.getenv('PORT')