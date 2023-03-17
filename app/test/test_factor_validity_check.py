from quantization.factor_validity_check.factor_validity_check import FactorValidityCheck

def test_cal_factors_ic():
    fvc = FactorValidityCheck(factors=['pe_ttm', 'pb', 'ps'],sample_periods=0)
    fvc.cal_factors_ic()


