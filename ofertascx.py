from ofertascx import get_page
from ofertascx.parser import process_table


def main():
    page = get_page()
    for i in process_table('ventas', page):
        print(i)


if __name__ == '__main__':
    main()
