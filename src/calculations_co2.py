
import pandas as pd

from src.plotting import monthly_to_yearly


def per_tj_to_per_twh(faktor_per_tj):
    return faktor_per_tj * 3600


# ==================================================
# Calculating natural gas
# ==================================================

# from NID 2026, page 164 and 172
GAS_CO2_KT_PER_TJ = 55.6 / 1000
GAS_CO2_KT_PER_TWH = per_tj_to_per_twh(GAS_CO2_KT_PER_TJ)

def calculating_co2_from_gas_kt(gas_consumption_twh):
    return gas_consumption_twh * GAS_CO2_KT_PER_TWH


# ==================================================
# Calculating oil products
# ==================================================

def carbon_t_per_tj_to_co2_kt_per_twh(factor):
    co2_t_per_tj = factor * (44/12)
    co2_kt_per_tj = co2_t_per_tj / 1000
    co2_kt_per_twh = per_tj_to_per_twh(co2_kt_per_tj)
    return co2_kt_per_twh

# All emission-factors are calculated from NID 2026, Annex 3, Table A67, Carbon emission factor
CARBON_T_PER_TJ_GAS_AND_DIESEL_OIL = 20.20
CO2_KT_PER_TWH_GAS_AND_DIESEL_OIL = carbon_t_per_tj_to_co2_kt_per_twh(CARBON_T_PER_TJ_GAS_AND_DIESEL_OIL)
CARBON_T_PER_TJ_FUEL_OIL = 21.10
CO2_KT_PER_TWH_FUEL_OIL = carbon_t_per_tj_to_co2_kt_per_twh(CARBON_T_PER_TJ_FUEL_OIL)
CARBON_T_PER_TJ_LPG = 17.20
CO2_KT_PER_TWH_LPG = carbon_t_per_tj_to_co2_kt_per_twh(CARBON_T_PER_TJ_LPG)
CARBON_T_PER_TJ_GASOLINE = 18.90
CO2_KT_PER_TWH_GASOLINE = carbon_t_per_tj_to_co2_kt_per_twh(CARBON_T_PER_TJ_GASOLINE)
CARBON_T_PER_TJ_KEROSENE = 19.50
CO2_KT_PER_TWH_KEROSENE = carbon_t_per_tj_to_co2_kt_per_twh(CARBON_T_PER_TJ_KEROSENE)

CO2_KT_PER_TJ_SELECTED_FUELS_OIL = {
    "Gasöl und Dieselöl (ohne Biokraftstoffanteil)_O4671XR5220B": CO2_KT_PER_TWH_GAS_AND_DIESEL_OIL,
    "Heizöl_O4680": CO2_KT_PER_TWH_FUEL_OIL,
    "Flüssiggas_O4630": CO2_KT_PER_TWH_LPG,
    "Motorenbenzin (ohne Biokraftstoffanteil)_O4652XR5210B": CO2_KT_PER_TWH_GASOLINE,
    "Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B": CO2_KT_PER_TWH_KEROSENE}


def calculating_co2_from_oil_kt_uncorrected(oil_consumption_twh):
    """Returns a dataframe with uncorrected monthly co2 from oil with one column named total_oil_products."""
    co2_oil_uncorrected = oil_consumption_twh * CO2_KT_PER_TJ_SELECTED_FUELS_OIL
    co2_oil_uncorrected["total_oil_products"] = co2_oil_uncorrected.sum(axis=1)
    return co2_oil_uncorrected

def calculating_difference_crt_to_co2_oil_uncorrected(oil_consumption_twh, co2_crt_liquid_yearly_kt):
    """Returns dataframe with the missing CO2 in kt in uncorrected oil"""
    co2_calculated_oil_uncorrected_kt = calculating_co2_from_oil_kt_uncorrected(oil_consumption_twh)
    calculated_oil_yearly = monthly_to_yearly(co2_calculated_oil_uncorrected_kt)
    combination = co2_crt_liquid_yearly_kt.join(calculated_oil_yearly["total_oil_products"], how="inner")
    difference = combination["total_oil_products"] - combination["nid_liquid_co2"]
    return difference

def calculating_rounded_missing_monthly_co2_oil(difference_crt_oil_uncorrected):
    return abs(difference_crt_oil_uncorrected.mean()/12).round(-1)

def explaining_missing_co2_oil(oil_consumption_twh, co2_crt_liquid_yearly_kt):
    """Returns as a first value the monthly not rounded missing co2 and as a second the rounded"""
    difference = calculating_difference_crt_to_co2_oil_uncorrected(oil_consumption_twh, co2_crt_liquid_yearly_kt)
    not_rounded = abs(difference.mean()/12)
    rounded = calculating_rounded_missing_monthly_co2_oil(difference)
    return not_rounded, rounded

def correcting_co2_from_oil_kt(calculated_oil_uncorrected, missing_monthly):
    corrected = calculated_oil_uncorrected.copy()
    corrected["missing_oil_combustion"] = missing_monthly
    corrected["total_oil_products"] = 0
    corrected["total_oil_products"] = corrected.sum(axis=1)
    return corrected

def calculating_co2_from_oil_kt_final(oil_consumption_twh, co2_crt_liquid_yearly_kt):
    """Returns a dataframe with final monthly co2 from oil with one column named total_oil_products."""
    uncorrected = calculating_co2_from_oil_kt_uncorrected(oil_consumption_twh)
    difference = calculating_difference_crt_to_co2_oil_uncorrected(oil_consumption_twh, co2_crt_liquid_yearly_kt)
    missing_monthly = calculating_rounded_missing_monthly_co2_oil(difference)
    corrected = correcting_co2_from_oil_kt(uncorrected, missing_monthly)
    return corrected 


# ==================================================
# Calculating international aviation
# ==================================================

def calculating_co2_from_int_aviation_kt(int_aviation_consumption_twh):
    return int_aviation_consumption_twh * CO2_KT_PER_TWH_KEROSENE
