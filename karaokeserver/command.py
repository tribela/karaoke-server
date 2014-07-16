import argparse
from .crawler import crawl

def crawl_command(args):
    crawl(args.url)

parser = argparse.ArgumentParser(prog='karaokeserver')
subparsers = parser.add_subparsers(dest='command')

crawl_parser = subparsers.add_parser('crawl', help='Crawl karaoke database')
crawl_parser.set_defaults(function=crawl_command)
crawl_parser.add_argument('url', help='Database url for store karaoke datas')


def main():
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        exit(1)

    args.function(args)


if __name__ == '__main__':
    main()
