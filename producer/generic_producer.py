from simplewebservice import SimpleWebService
import os
import logging
import multiprocessing as mp
import time
import argparse, sys

class AbstractProducer():
    def __init__(self):
        LOG_FILE = "producer.log"
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=LOG_FILE,
                            filemode='a')
        self.logger = logging.getLogger('producer'.format(os.getpid()))
        self.parser = argparse.ArgumentParser()

    #abstract
    def task_generator(self, queue):
        pass
        # for i in range(10):
        #     queue.put(i+1)

    #abstract
    def add_argument_parser(self):
        pass
        # self.parser.add_argument("-r", "--report", help="The file where to write the report")

    # abstract
    def process_extra_args(self, args):
        pass

    # abstract, default is a SimpleWebService
    def set_web_service(self, address, port, queue, args):
        return SimpleWebService(address, port, queue)

    def parseArguments(self):
        self.add_argument_parser()

        self.parser.add_argument("-p", "--port", help="The port that answers do HTTP Requests", type=int)
        self.parser.add_argument("-a", "--address", help="The public IP from which this server answers")
        args = self.parser.parse_args()

        if not args.address or not args.port:
            print("Address and Port arguments are mandatory")
            self.logger.error("Address and Port arguments are mandatory")
            sys.exit(1)

        error_args = self.process_extra_args(args)
        if error_args is not None:
            print(error_args)
            self.logger.error(error_args)
            sys.exit(1)

        return args.address, args.port

    def execute(self):

        address, port = self.parseArguments()
        # with open('../version.txt') as f:
        #     version = f.readline()
        # logger.info("Version " + version)

        queue = mp.Queue()

        generator = mp.Process(target=self.task_generator, args=(queue,))
        generator.start()

        server = self.set_web_service(address, port, queue, None)
        server_process = mp.Process(target=server.run)
        server_process.daemon=True
        server_process.start()

        generator.join()
        while (not queue.empty()):  # queue not empty)
            time.sleep(2)