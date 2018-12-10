import multiprocessing as mp
import requests
import pprint, argparse, time, random, base64, sys
from termcolor import colored 

pp = pprint.PrettyPrinter(indent=4).pprint

class PyParamMiner(object):
    headers = []
    args = None

    def __init__(self):
        self.parse_cli_args()
        self.read_headers()

        if self.args.header:
            self.headers = [self.args.header]

        pool = mp.Pool(processes=10)
        results = pool.map(self.probe, self.headers)
        print("")

        founds = []
        for result in results:
            if result['status']:
                founds.append(result)
            if result['error']:
                print('Error: ' + result['header'])

        if len(founds) > 0:
            print("\nFound Reflected: ")
            for f in founds:
                print("- %s" % f['header'])
        else:
            print("* Found Nothing")

    def probe(self, header):
        url = self.args.url + "?ts=" + str(time.time()) + str(random.random())
        header_payload = base64.b64encode(( str(time.time()) + str(random.random())  ).encode('utf-8')).decode('utf-8')
        reflected = False
        error = False

        # do request
        try:
            headers = {}
            headers[header] = header_payload
            resp = requests.get(url, headers=headers)
            reflected = header_payload in resp.text
        except:
            resp = None
            error = True
            pass

        if resp:
            s = "%s (%d) [%s] %s" % (header, len(resp.text), resp.status_code, self.print_reflected(reflected))
        else:
            error = True
            s = "%s [error]" % (header)
        print(s)
        return {'status': reflected, 'header': header, 'resp': resp, 'error': error}

    def print_reflected(self, reflected):
        if reflected:
            return "[" + colored("Reflected!", "green") + "]"
        else:
            return ""

    def read_headers(self):
        f = open('headers.txt', 'r')
        self.headers = [line.rstrip("\n\r") for line in f.readlines()]
        f.close()

    def parse_cli_args(self):
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('url', help='Target URL to be scrapped')
        parser.add_argument('--worker', action='store', help='Specify number for workers (default: 5)')
        parser.add_argument('--header', action='store', help='Custom header')
        self.args = parser.parse_args()


if __name__ == '__main__':
    PyParamMiner()
