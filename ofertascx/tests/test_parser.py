import unittest
from ofertascx.parser import process_table
from ofertascx import Offers


# ToDo Improve unittest and create more
@unittest.skip('Need fixs')
class ParserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with open(r'./ofertascx/tests/offers.html', 'r') as f:
            self.data = f.read()

    def test_process_table_venta(self):
        ventas = process_table(selector=Offers.VENTA, page=self.data)
        self.assertIsNotNone(ventas, 'Failed to create ventas data')


if __name__ == '__main__':
    unittest.main()
