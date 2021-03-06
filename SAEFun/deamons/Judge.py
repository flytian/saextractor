__author__ = 'LeoDong'

import socket

import sys

from util import config
from judge.SAEJudge import SAEJudge
from util.logger import log

#TODO unique id in queue, store to file and reload.
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
log.info('start listening on %s' % str(config.socket_addr_judge))
sock.bind(config.socket_addr_judge)
# Listen for incoming connections
sock.listen(10)
judge = SAEJudge(config.path_judge_dtree,config.dtree_param)
try:
    while True:
        # Wait for a connection
        connection, client_address = sock.accept()
        judge.process(connection, client_address)
finally:
    log.info("Saving")
    judge.save()
