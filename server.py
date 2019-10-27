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


#

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render('index.html', schedule=timeSchedule)
    
    def post(self):
        action = self.get_argument('action')
        if action == 'reload':
            print('Restarting')
            logging.info('Restarting server...')
            subprocess.run('')

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
        self.write_message("connected to websocket")

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
        while True:
            try:
                data = await stream.read_until(b'\n')
                #print(dir(stream))
                if data:
                    output_queue.put(data)
                # await stream.write(data + b'REPLY FROM ECHO SERVER!')
            except StreamClosedError:
                break
            


if __name__ == '__main__':

    def checkQueue():
        # print('inside check queue')
        if not output_queue.empty():
            message = output_queue.get()
            print ("tornado received from raspberry: ", message)
            for c in clients:
                c.write_message(message)
        if not input_queue.empty():
            message = input_queue.get()
            print('processing output queue')
            for d in devices:
                d.write(message.encode())


                
    server = TcpListener()
    server.listen(options.listener_port)
    data = {'status': 'initialized'}
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
    print(f'Web Application listening on port {options.port}...')
    mainLoop.start()