from tornado.tcpserver import TCPServer, IOLoop
from tornado.iostream import StreamClosedError
from tornado import gen, ioloop, web, httpserver, websocket
from tornado.options import define, options
import multiprocessing
import os, random, string, logging, time, subprocess 

define("port", default=8000, help="ვებსერვერის პორტი", type=int)
define("listener_port", default=8888, help="პორტი რომელსაც მოწყობილობა უკავშირდება", type=int)
input_queue = multiprocessing.Queue()
output_queue = multiprocessing.Queue()
clients = []
devices = []
addresses = []

#

class IndexHandler(web.RequestHandler):
    def get(self):
        print(devices)
        self.render('index.html', schedule=timeSchedule, device=addresses)
    
    def post(self):
        action = self.get_argument('action')
        if action == 'reload':
            logging.info('Restarting server...')
            subprocess.run(['supervisorctl',  'restart tornado_listener'], check=True)
            print('Restarting')
            exit()

class UploadFileHander(web.RequestHandler):
    def post(self):
        file1 = self.request.files['file'][0]
        fname = 'schedule'
        output_file = open(fname, 'w')
        output_file.write(file1['body'].decode())
        self.redirect('/')

class WebSocketHandler(websocket.WebSocketHandler):
    def open(self):
        print ('new http connection')
        clients.append(self)
        self.write_message(f"connected to websocket")

#    def check_origin(self, origin):
#        print(f'origin is: {origin}')
#        return True

    def on_close(self):
        print('socket closed')
        self.close()
        clients.pop()

    def on_message(self, message):
        print('tornado received from client: %s' % message)
        # self.write_message('got it!')
        input_queue.put(message)


class StaticFileHandler(web.RequestHandler):
    def get(self):
        self.render('main.js')

class TcpListener(TCPServer):
    async def handle_stream(self, stream, address):
        devices.append(stream)
        addresses.append(address)
        while True:
            try:
                data = await stream.read_until(b'\n')
                #print(dir(stream))
                if data:
                    output_queue.put(data)
                # await stream.write(data + b'REPLY FROM ECHO SERVER!')
            except StreamClosedError:
                print('closed stream')
                devices.pop() 
                break


if __name__ == '__main__':

    def checkQueue():
        # print('inside check queue')
        if not output_queue.empty():
            message = output_queue.get()
            print ("tornado received from device: ", message) #these are WEBSOCKETS
            for c in clients:                       # there are websockets clients
                c.write_message(message)
        if not input_queue.empty():                # messages received from web to send to devices
            message = input_queue.get()
            print('processing input queue')
            for d in devices:                       #there are TCPserver stream objects
                d.write(message.encode())


                
    server = TcpListener()
    server.listen(options.listener_port)
    app = web.Application(
        [
            (r'/', IndexHandler),
            (r'/static/(.*)', StaticFileHandler),
            (r'/ws', WebSocketHandler), 
            (r'/upload', UploadFileHander)
        ], 
        template_path=os.path.join(os.path.dirname(__file__),"templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    with open('schedule', 'r') as file:
        timeSchedule = file.readlines()
    mainLoop = ioloop.IOLoop.instance()
    scheduler_interval = 10
    scheduler = ioloop.PeriodicCallback(checkQueue, scheduler_interval)
    scheduler.start()
    webserver = httpserver.HTTPServer(app)
    webserver.listen(options.port)
    print(f'Web application listening on port {options.port}...')
    print(f'Socket application listening on port {options.listener_port}...')
    mainLoop.start()
