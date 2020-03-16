import pytest
import numpy as np
from astropy import units as u
from astropy import modeling
from specutils.utils import QuantityModel, excise_regions, linear_exciser
from specutils import Spectrum1D, SpectralRegion
from ..utils.wcs_utils import refraction_index, vac_to_air, air_to_vac

wavelengths = [300, 500, 1000] * u.nm
data_index_refraction = {
   'Griesen2006': np.array([3.07393068, 2.9434858 , 2.8925797 ]),
   'Edlen1953': np.array([2.91557413, 2.78963801, 2.74148172]),
   'Edlen1966': np.array([2.91554272, 2.7895973 , 2.74156098]),
   'PeckReeder1972': np.array([2.91554211, 2.78960005, 2.74152561]),
   'Morton2000': np.array([2.91568573, 2.78973402, 2.74169531]),
   'Ciddor1996': np.array([2.91568633, 2.78973811, 2.74166131])
}

def test_quantity_model():
    c = modeling.models.Chebyshev1D(3)
    uc = QuantityModel(c, u.AA, u.km)

    assert uc(10*u.nm).to(u.m) == 0*u.m

def test_true_exciser():
    np.random.seed(84)
    spectral_axis = np.linspace(5000,5100,num=100)*u.AA
    flux = (np.random.randn(100) + 3) * u.Jy
    spec = Spectrum1D(flux=flux, spectral_axis = spectral_axis)
    region = SpectralRegion([(5005,5010), (5060,5065)]*u.AA)
    excised_spec = excise_regions(spec, region)

    assert len(excised_spec.spectral_axis) == len(spec.spectral_axis)-10
    assert len(excised_spec.flux) == len(spec.flux)-10
    assert np.isclose(excised_spec.flux.sum(), 274.54139*u.Jy, atol=0.001)

def test_linear_exciser():
    np.random.seed(84)
    spectral_axis = np.linspace(5000,5100,num=100)*u.AA
    flux = np.random.randn(100) * u.Jy
    uncertainty = np.random.
    spec = Spectrum1D(flux=flux)
    region = SpectralRegion([(5005,5010), (5060,5065)]*u.AA)
    excised_spec = excise_regions(spec, region, exciser = linear_exciser)

@pytest.mark.parametrize("method", data_index_refraction.keys())
def test_refraction_index(method):
    tmp = (refraction_index(wavelengths, method) - 1) * 1e4
    assert np.isclose(tmp, data_index_refraction[method], atol=1e-7).all()


@pytest.mark.parametrize("method", data_index_refraction.keys())
def test_air_to_vac(method):
    tmp = refraction_index(wavelengths, method)
    assert np.isclose(wavelengths.value * tmp,
                      air_to_vac(wavelengths, method=method, scheme='inversion').value,
                      rtol=1e-6).all()
    assert np.isclose(wavelengths.value,
                      air_to_vac(vac_to_air(wavelengths, method=method),
                                 method=method, scheme='iteration').value,
                      atol=1e-12).all()
