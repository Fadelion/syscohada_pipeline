import unittest
from syscohada_pipeline.core.accounting_rules import validate_bilan, compute_net

class TestAccountingRules(unittest.TestCase):
    
    def test_validate_bilan_balanced(self):
        actif = {"BZ": {"net": 1000.50}}
        passif = {"DZ": {"net": 1000.50}}
        self.assertTrue(validate_bilan(actif, passif))
        
    def test_validate_bilan_unbalanced(self):
        actif = {"BZ": {"net": 1000.00}}
        passif = {"DZ": {"net": 2000.00}}
        self.assertFalse(validate_bilan(actif, passif))

    def test_compute_net(self):
        self.assertEqual(compute_net(100.0, 20.0), 80.0)
        self.assertEqual(compute_net(None, 20.0), -20.0)
        self.assertEqual(compute_net(100.0, None), 100.0)

if __name__ == '__main__':
    unittest.main()
