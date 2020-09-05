import unittest
from ofertascx import filter_offers, gen_key
from ofertascx.settings import PagoIntervals


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

    def test_gen_key(self):
        self.assertEquals(gen_key(cripto='BTC'), 'cripto(BTC)')
        self.assertEqual(gen_key(valor=PagoIntervals.MIN), 'valor(MIN)')
        self.assertEqual(gen_key(cripto='BTC', valor=PagoIntervals.MIN), 'cripto(BTC)-valor(MIN)')
        self.assertEqual(gen_key(valor=PagoIntervals.MID, cripto='BTC'), 'cripto(BTC)-valor(MID)')
        self.assertEqual(gen_key(pago='EnZona', cripto='BTC'), 'cripto(BTC)-pago(EnZona)')


if __name__ == '__main__':
    unittest.main()
