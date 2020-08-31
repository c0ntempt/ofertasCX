import unittest
from ofertascx import filter_offers


class OfertascxTestCase(unittest.TestCase):

    # TODO Improve and add more tests
    def test_filter_offers(self):
        ofertas = [
            dict(cripto='BTC', valor='15', pago=['EnZona MLC']),
            dict(cripto='LTC', valor='15', pago=['EnZona MLC']),
            dict(cripto='BTC', valor='15', pago=['EnZona CUC']),
            dict(cripto='USD', valor='15', pago=['EnZona MLC']),
        ]
        a = filter_offers(ofertas, cripto='BTC')
        self.assertIsNotNone(a, 'Debe retornar algo')
        self.assertTrue(len(a) == 2)


if __name__ == '__main__':
    unittest.main()
