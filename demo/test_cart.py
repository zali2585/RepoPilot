import unittest
from demo.cart import subtotal

class CartTests(unittest.TestCase):
    def test_subtotal_with_two_items(self):
        self.assertEqual(subtotal([125, 275]), 400)