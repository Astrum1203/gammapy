# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import astropy.units as u
from numpy.testing import assert_allclose
from gammapy.estimators.utils import find_peaks, find_roots
from gammapy.maps import Map, MapAxis
import pytest


class TestFindPeaks:
    def test_simple(self):
        """Test a simple example"""
        image = Map.create(npix=(10, 5), unit="s")
        image.data[3, 3] = 11
        image.data[3, 4] = 10
        image.data[3, 5] = 12
        image.data[3, 6] = np.nan
        image.data[0, 9] = 1e20

        table = find_peaks(image, threshold=3)

        assert len(table) == 3
        assert table["value"].unit == "s"
        assert table["ra"].unit == "deg"
        assert table["dec"].unit == "deg"

        row = table[0]
        assert tuple((row["x"], row["y"])) == (9, 0)
        assert_allclose(row["value"], 1e20)
        assert_allclose(row["ra"], 359.55)
        assert_allclose(row["dec"], -0.2)

        row = table[1]
        assert tuple((row["x"], row["y"])) == (5, 3)
        assert_allclose(row["value"], 12)

    def test_no_peak(self):
        image = Map.create(npix=(10, 5))
        image.data[3, 5] = 12

        table = find_peaks(image, threshold=12.1)
        assert len(table) == 0

    def test_constant(self):
        image = Map.create(npix=(10, 5))

        table = find_peaks(image, threshold=3)
        assert len(table) == 0

    def test_flat_map(self):
        """Test a simple example"""
        axis1 = MapAxis.from_edges([1, 2], name="axis1")
        axis2 = MapAxis.from_edges([9, 10], name="axis2")
        image = Map.create(npix=(10, 5), unit="s", axes=[axis1, axis2])
        image.data[..., 3, 3] = 11
        image.data[..., 3, 4] = 10
        image.data[..., 3, 5] = 12
        image.data[..., 3, 6] = np.nan
        image.data[..., 0, 9] = 1e20

        table = find_peaks(image, threshold=3)
        row = table[0]

        assert len(table) == 3
        assert_allclose(row["value"], 1e20)
        assert_allclose(row["ra"], 359.55)
        assert_allclose(row["dec"], -0.2)


class TestFindRoots:
    lower_bound = -3 * np.pi * u.rad
    upper_bound = 0 * u.rad

    def f(self, x):
        return np.cos(x)

    def h(self, x):
        return x ** 3 - 1

    def test_methods(self):

        methods = ["brentq", "secant"]
        for method in methods:
            roots, res = find_roots(
                self.f,
                lower_bound=self.lower_bound,
                upper_bound=self.upper_bound,
                method=method,
            )
            assert roots.unit == u.rad
            assert_allclose(2 * roots.value / np.pi, np.array([-5.0, -3.0, -1.0]))
            assert np.all([sol.converged for sol in res])

            roots, res = find_roots(
                self.h,
                lower_bound=self.lower_bound,
                upper_bound=self.upper_bound,
                method=method,
            )
            assert np.isnan(roots[0])
            assert res[0].iterations == 0

    def test_invalid_method(self):
        with pytest.raises(ValueError, match='Unknown solver "xfail"'):
            find_roots(
                self.f,
                lower_bound=self.lower_bound,
                upper_bound=self.upper_bound,
                method="xfail",
            )
