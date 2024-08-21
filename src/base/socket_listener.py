import socket
import select

class SocketListener:
    def __init__(self, logger, port):
        self.logger = logger

        try:
            self.socket = socket.socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(socket.getaddrinfo('0.0.0.0', port)[0][-1])
            self.socket.listen(10)

            self.poller = select.poll()
            self.poller.register(self.socket, select.POLLIN)
        except Exception as e:
            self.logger.set_status("SocketListener.__init__()", "Exception " + str(e))

    def accept(self):
        try:
            res = self.poller.poll(1)

            if not res:
                return None

            cl, addr = self.socket.accept()
            return cl
        except Exception as e:
            self.logger.set_status("SocketListener.accept()", "Last exception " + str(e))
        
