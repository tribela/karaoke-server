import argparse
from .app import app
from .crawler import crawl
from .database import DbManager

def crawl_command(args):
    crawl(args.url)

def server_command(args):
    app.config['dbm'] = DbManager(args.url)
    app.debug = args.debug
    app.run(host=args.host, port=args.port)

parser = argparse.ArgumentParser(prog='karaokeserver')
subparsers = parser.add_subparsers(dest='command')

crawl_parser = subparsers.add_parser('crawl', help='Crawl karaoke database')
crawl_parser.set_defaults(function=crawl_command)
crawl_parser.add_argument('url', help='Database url for store karaoke datas')

server_parser = subparsers.add_parser('server', help='query server')
server_parser.set_defaults(function=server_command)
server_parser.add_argument('url', help='Database url for store karaoke datas')
server_parser.add_argument('-H', '--host', default='0.0.0.0',
    help='Host to bind.')
server_parser.add_argument('-p', '--port', type=int, default='8080',
    help='Port to bind.')
server_parser.add_argument('-d', '--debug', action='store_true', default=False,
    help='debug mode')


def main():
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        exit(1)

    args.function(args)


if __name__ == '__main__':
    main()
