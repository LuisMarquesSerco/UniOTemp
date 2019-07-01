import os
import logging
import time, requests, json
import multiprocessing as mp
import argparse, sys


class AbstractConsumer():
    def __init__(self):
        LOG_FILE = "consumer.log"
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            filename=LOG_FILE,
                            filemode='a')
        self.logger = logging.getLogger('consumer'.format(os.getpid()))
        self.parser = argparse.ArgumentParser()

    def get_task(self, address, port):
        host = 'http://{}:{}'.format(address, port)
        try:
            r = requests.get(host)
            if r.status_code == 200:
                prod = r.json()
                return prod
        except:
            return None

    def task_consumer(self, address,port):
        pass
        #for i in range(10):
        #    print(self.get_task(address,port))

    # abstract
    def add_argument_parser(self):
        pass
        # self.parser.add_argument("-r", "--report", help="The file where to write the report")

    # abstract
    def process_extra_args(self, args):
        pass

    def parseArguments(self):
        self.add_argument_parser()

        self.parser.add_argument("-p", "--port", help="The port that answers do HTTP Requests", type=int)
        self.parser.add_argument("-a", "--address", help="The IP that answers do HTTP Requests")
        self.parser.add_argument("-c", "--consumers", help="Number of parallel consumers", type=int)
        args = self.parser.parse_args()

        if not args.address or args.address=='' or not args.port:
            print("Address and Port arguments are mandatory")
            self.logger.error("Address and Port arguments are mandatory")
            sys.exit(1)

        if not args.consumers or args.consumers<1:
            print("#Consumers argument is mandatory")
            self.logger.error("#Consumers argument is mandatory")
            sys.exit(1)

        error_args = self.process_extra_args(args)
        if error_args is not None:
            print(error_args)
            self.logger.error(error_args)
            sys.exit(1)

        return args.address, args.port, args.consumers

    def execute(self):

        address, port, num_consumers = self.parseArguments()
        # with open('../version.txt') as f:
        #     version = f.readline()
        # logger.info("Version " + version)

        consumers=[]
        for t in range(num_consumers):
            cons = mp.Process(target=self.task_consumer, args=(address,port,))
            consumers.append(cons)
            cons.start()

        for consumer in consumers:
            consumer.join()