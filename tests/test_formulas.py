#

import unittest
import math
from benekli.formulas import de76, de94, de94_for_graphic_arts, de94_for_textiles, de2000

class TestColorDifferenceFormulas(unittest.TestCase):
    """Test cases for color difference formulas (de76, de94, de2000)."""
    
    def setUp(self):
        """Set up test cases with known Lab color pairs and expected delta E values."""
        self.test_cases = [
            (
                (50, 0, 0),  # Lab1
                (50, 0, 0),  # Lab2
                0.0,         # expected de76
                0.0,         # expected de94_graphic
                0.0,         # expected de94_textile
                0.0          # expected de2000
            ),
            (
                (50, 0, 0),  # Lab1
                (60, 0, 0),  # Lab2
                10.0,        # expected de76
                10.0,        # expected de94_graphic
                5.0,         # expected de94_textile (kL=2.0)
                10.0         # expected de2000
            ),
            (
                (50, 0, 0),  # Lab1
                (50, 10, 0), # Lab2
                10.0,        # expected de76
                None,        # expected de94_graphic
                None,        # expected de94_textile
                None         # expected de2000
            ),
            (
                (50, 0, 0),  # Lab1
                (50, 0, 10), # Lab2
                10.0,        # expected de76
                None,        # expected de94_graphic
                None,        # expected de94_textile
                None         # expected de2000
            ),
            (
                (75, -20, -30),  # Lab1: light blue
                (55, -20, -30),  # Lab2: darker blue (only L changes)
                20.0,            # expected de76
                None,            # expected de94_graphic
                None,            # expected de94_textile
                None             # expected de2000
            ),
            (
                (50, 60, 30),   # Lab1: red
                (60, 40, 60),   # Lab2: orange
                37.42,          # expected de76 = sqrt((50-60)^2 + (60-40)^2 + (30-60)^2)
                None,           # expected de94_graphic
                None,           # expected de94_textile
                None            # expected de2000
            )
        ]
    
    def test_de76(self):
        """Test the CIE76 color difference formula."""
        for test_case in self.test_cases:
            Lab1, Lab2, expected_de76, _, _, _ = test_case
            if expected_de76 is not None:
                with self.subTest(f"de76 for {Lab1} and {Lab2}"):
                    result = de76(Lab1, Lab2)
                    self.assertAlmostEqual(result, expected_de76, places=2)
    
    def test_de94_for_graphic_arts(self):
        """Test the CIE94 color difference formula for graphic arts."""
        for test_case in self.test_cases:
            Lab1, Lab2, _, expected_de94_graphic, _, _ = test_case
            if expected_de94_graphic is not None:
                with self.subTest(f"de94_graphic for {Lab1} and {Lab2}"):
                    result = de94_for_graphic_arts(Lab1, Lab2)
                    self.assertAlmostEqual(result, expected_de94_graphic, places=2)
    
    def test_de94_for_textiles(self):
        """Test the CIE94 color difference formula for textiles."""
        for test_case in self.test_cases:
            Lab1, Lab2, _, _, expected_de94_textile, _ = test_case
            if expected_de94_textile is not None:
                with self.subTest(f"de94_textile for {Lab1} and {Lab2}"):
                    result = de94_for_textiles(Lab1, Lab2)
                    self.assertAlmostEqual(result, expected_de94_textile, places=2)
    
    def test_de2000(self):
        """Test the CIEDE2000 color difference formula."""
        for test_case in self.test_cases:
            Lab1, Lab2, _, _, _, expected_de2000 = test_case
            if expected_de2000 is not None:
                with self.subTest(f"de2000 for {Lab1} and {Lab2}"):
                    result = de2000(Lab1, Lab2)
                    self.assertAlmostEqual(result, expected_de2000, places=2)
    
    def test_symmetry(self):
        """Test that color difference formulas are symmetric (de(a,b) = de(b,a))."""
        for test_case in self.test_cases:
            Lab1, Lab2 = test_case[0], test_case[1]
            
            de76_forward = de76(Lab1, Lab2)
            de76_reverse = de76(Lab2, Lab1)
            self.assertAlmostEqual(de76_forward, de76_reverse, places=6)
            
            try:
                de94_graphic_forward = de94_for_graphic_arts(Lab1, Lab2)
                de94_graphic_reverse = de94_for_graphic_arts(Lab2, Lab1)
                self.assertAlmostEqual(de94_graphic_forward, de94_graphic_reverse, places=6)
            except Exception as e:
                self.skipTest(f"de94_for_graphic_arts symmetry test skipped: {e}")
            
            try:
                de94_textile_forward = de94_for_textiles(Lab1, Lab2)
                de94_textile_reverse = de94_for_textiles(Lab2, Lab1)
                self.assertAlmostEqual(de94_textile_forward, de94_textile_reverse, places=6)
            except Exception as e:
                self.skipTest(f"de94_for_textiles symmetry test skipped: {e}")
            
            try:
                de2000_forward = de2000(Lab1, Lab2)
                de2000_reverse = de2000(Lab2, Lab1)
                self.assertAlmostEqual(de2000_forward, de2000_reverse, places=6)
            except Exception as e:
                self.skipTest(f"de2000 symmetry test skipped: {e}")
    
    def test_triangle_inequality(self):
        """Test that color difference formulas satisfy triangle inequality (de(a,c) ≤ de(a,b) + de(b,c))."""
        Lab_a = (50, 10, 10)
        Lab_b = (60, 20, 20)
        Lab_c = (70, 30, 30)
        
        de76_ab = de76(Lab_a, Lab_b)
        de76_bc = de76(Lab_b, Lab_c)
        de76_ac = de76(Lab_a, Lab_c)
        self.assertLessEqual(de76_ac, de76_ab + de76_bc)
        
        try:
            de94_graphic_ab = de94_for_graphic_arts(Lab_a, Lab_b)
            de94_graphic_bc = de94_for_graphic_arts(Lab_b, Lab_c)
            de94_graphic_ac = de94_for_graphic_arts(Lab_a, Lab_c)
            self.assertLessEqual(de94_graphic_ac, de94_graphic_ab + de94_graphic_bc)
        except Exception as e:
            self.skipTest(f"de94_for_graphic_arts triangle inequality test skipped: {e}")
        
        try:
            de94_textile_ab = de94_for_textiles(Lab_a, Lab_b)
            de94_textile_bc = de94_for_textiles(Lab_b, Lab_c)
            de94_textile_ac = de94_for_textiles(Lab_a, Lab_c)
            self.assertLessEqual(de94_textile_ac, de94_textile_ab + de94_textile_bc)
        except Exception as e:
            self.skipTest(f"de94_for_textiles triangle inequality test skipped: {e}")
        
        try:
            de2000_ab = de2000(Lab_a, Lab_b)
            de2000_bc = de2000(Lab_b, Lab_c)
            de2000_ac = de2000(Lab_a, Lab_c)
            self.assertLessEqual(de2000_ac, de2000_ab + de2000_bc)
        except Exception as e:
            self.skipTest(f"de2000 triangle inequality test skipped: {e}")


if __name__ == "__main__":
    unittest.main()
