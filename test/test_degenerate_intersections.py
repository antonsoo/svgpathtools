import unittest

from svgpathtools import Arc, CubicBezier, Path, QuadraticBezier
from svgpathtools.bezier import boxes_intersect


class TestDegenerateIntersections(unittest.TestCase):
    def test_closed_bounding_boxes(self):
        cases = [
            ((0, 6, 0, 0), (2, 2, -4, 2), True),
            ((0, 6, 0, 0), (7, 7, -4, 2), False),
            ((0, 6, 0, 0), (2, 4, 0, 0), True),
            ((0, 6, 0, 0), (2, 4, 1, 1), False),
            ((0, 0, 0, 0), (-1, 1, -1, 1), True),
            ((0, 1, 0, 1), (1, 2, 1, 2), True),
            ((0, 1, 0, 1), (2, 3, 0, 1), False),
        ]
        for first, second, expected in cases:
            with self.subTest(first=first, second=second):
                self.assertEqual(boxes_intersect(first, second), expected)
                self.assertEqual(boxes_intersect(second, first), expected)

    def test_axis_aligned_beziers(self):
        horizontal = [QuadraticBezier(0, 3, 6), CubicBezier(0, 2, 4, 6),
                      QuadraticBezier(0, 0, 6), CubicBezier(0, 0, 0, 6)]
        vertical = [QuadraticBezier(2 - 4j, 2 - 1j, 2 + 2j),
                    CubicBezier(2 - 4j, 2 - 2j, 2, 2 + 2j),
                    CubicBezier(2 - 4j, 2 - 4j, 2 - 4j, 2 + 2j)]
        for first in horizontal:
            for second in vertical:
                for a, b in [(first, second), (second, first)]:
                    with self.subTest(a=a, b=b):
                        result = Path(a).intersect(Path(b))
                        self.assertEqual(len(result), 1)
                        (ta, _, _), (tb, _, _) = result[0]
                        self.assertAlmostEqual(a.point(ta), 2, delta=1e-10)
                        self.assertAlmostEqual(b.point(tb), 2, delta=1e-10)

    def test_flat_curve_against_curved_bezier(self):
        horizontal = CubicBezier(0, 2, 4, 6)
        # y(t) = 16*t**2 - 16*t + 3 has roots at 1/4 and 3/4.
        curved = CubicBezier(3j, 2 - 7j / 3, 4 - 7j / 3, 6 + 3j)
        result = sorted(horizontal.intersect(curved))
        self.assertEqual(len(result), 2)
        for (ta, tb), expected in zip(result, [1.5, 4.5]):
            self.assertAlmostEqual(horizontal.point(ta), expected, delta=1e-10)
            self.assertAlmostEqual(curved.point(tb), expected, delta=1e-10)

    def test_separated_flat_curves(self):
        horizontal = CubicBezier(0, 2, 4, 6)
        for other in [horizontal.translated(1j),
                      QuadraticBezier(7 - 4j, 7 - 1j, 7 + 2j)]:
            with self.subTest(other=other):
                self.assertEqual(horizontal.intersect(other), [])

    def test_endpoint_of_flat_curve(self):
        horizontal = CubicBezier(0, 2, 4, 6)
        vertical = CubicBezier(6 - 4j, 6 - 2j, 6, 6 + 2j)
        result = horizontal.intersect(vertical)
        self.assertEqual(len(result), 1)
        ta, tb = result[0]
        self.assertAlmostEqual(horizontal.point(ta), 6, delta=1e-10)
        self.assertAlmostEqual(vertical.point(tb), 6, delta=1e-10)

    def test_flat_bezier_against_arc(self):
        vertical = CubicBezier(-2j, -1j, 1j, 2j)
        arc = Arc(-1, 1 + 1j, 0, False, True, 1)
        for a, b in [(vertical, arc), (arc, vertical)]:
            with self.subTest(a=a, b=b):
                result = a.intersect(b)
                self.assertEqual(len(result), 1)
                ta, tb = result[0]
                self.assertAlmostEqual(a.point(ta), -1j, delta=1e-10)
                self.assertAlmostEqual(b.point(tb), -1j, delta=1e-10)


if __name__ == '__main__':
    unittest.main()
