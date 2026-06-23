
import pandas as pd

# general functions

def mwh_to_twh(data_mwh):
    return data_mwh / 1000000

def gas_gcv_to_ncv(data_gcv):
    return data_gcv * 0.9

def tj_to_twh(data_tj):
    return data_tj / 3600


def validate_data(df):
    df_values_everywhere = df[~(df == 0.0).any(axis=1)]

    df_cleaned = df_values_everywhere.sort_index()

    m = df_cleaned.index.to_period("M")

    cutoff = pd.period_range(m.min(), m.max(), freq="M").difference(m).min()

    if pd.notna(cutoff):
        df_cleaned = df_cleaned[m < cutoff]
    return df_cleaned


# ==================================================
# Preparing gas consumption
# ==================================================

def extracting_inlandgasconsumption_twh_ncv(raw_gas_consumption_mwh_gcv):
    raw_gas_consumption_twh_ncv = gas_gcv_to_ncv(mwh_to_twh(raw_gas_consumption_mwh_gcv))
    inlandgasconsumption = raw_gas_consumption_twh_ncv[["#99002_Inlandgasverbrauch"]]
    return inlandgasconsumption

def preparing_gas_non_energy_twh_ncv(gas_for_ammonia_yearly_tj_ncv):
    gas_for_ammonia_yearly_twh_ncv = tj_to_twh(gas_for_ammonia_yearly_tj_ncv)
    average_non_energy_monthly_twh_ncv = gas_for_ammonia_yearly_twh_ncv["gas_used_ammonia"].mean() / 12
    return average_non_energy_monthly_twh_ncv

def calculating_gas_for_combustion(raw_gas, raw_ammonia):
    """Returns gas calculated gas consumption used for combustion in twh and ncv"""
    relevant_gas_consumption = extracting_inlandgasconsumption_twh_ncv(raw_gas)
    relevant_gas_consumption_cleaned = validate_data(relevant_gas_consumption)
    monthly_non_energy = preparing_gas_non_energy_twh_ncv(raw_ammonia)
    gas_combustion_twh_ncv = relevant_gas_consumption_cleaned - monthly_non_energy
    gas_combustion_twh_ncv = gas_combustion_twh_ncv.rename(columns={"#99002_Inlandgasverbrauch": "gas_for_combustion"})
    return gas_combustion_twh_ncv


# ==================================================
# Preparing oil consumption
# ==================================================

def converting_oil_to_wide(raw_oil_kt):
    oil_wide = raw_oil_kt.pivot(
        columns= ["Standardisierte internationale Klassifikation der Energieprodukte (SIEC)", "siec"],
        values="OBS_VALUE")
    oil_wide.columns = [f"{name}_{code}" for name, code in oil_wide.columns]
    return oil_wide

def selecting_relevant_fuel_types(oil_wide):
    selected_oil = oil_wide[
    ["Flüssiggas_O4630", "Motorenbenzin (ohne Biokraftstoffanteil)_O4652XR5210B", "Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B", "Gasöl und Dieselöl (ohne Biokraftstoffanteil)_O4671XR5220B", 
     "Heizöl_O4680"]].copy()
    selected_oil = selected_oil.loc['2013':]
    return selected_oil


# All faktors in TJ/kt from NID 2026, Annex 3, Table A 67, Country specific conversion factor 2024
TJ_PER_KT_GAS_AND_DIESEL_OIL = 42.5
TJ_PER_KT_FUEL_OIL = 41.47
TJ_PER_KT_LPG = 46.12
TJ_PER_KT_GASOLINE = 41.63
TJ_PER_KT_KEROSENE = 43.40

tj_per_kt_selected_fuels_oil = {
    "Gasöl und Dieselöl (ohne Biokraftstoffanteil)_O4671XR5220B": TJ_PER_KT_GAS_AND_DIESEL_OIL,
    "Heizöl_O4680": TJ_PER_KT_FUEL_OIL,
    "Flüssiggas_O4630": TJ_PER_KT_LPG,
    "Motorenbenzin (ohne Biokraftstoffanteil)_O4652XR5210B": TJ_PER_KT_GASOLINE,
    "Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B": TJ_PER_KT_KEROSENE}

def converting_selected_oil_fuels_to_tj(selected_fuels_kt):
    return selected_fuels_kt * tj_per_kt_selected_fuels_oil


def international_aviation_decimal_constant(aviation_percent):
    aviation_percent_constant = aviation_percent[-3:].mean().round(2)
    international_aviation_decimal_constant = aviation_percent_constant["international_aviation_percent"]/100
    return international_aviation_decimal_constant

def correcting_aviation_relevant_fuel_types(relevant_fuel_types, int_aviation_constant_decimal):
    corrected = relevant_fuel_types.copy()
    corrected["Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B"] = corrected["Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B"] * (1 - int_aviation_constant_decimal)
    return corrected

def international_aviation_combustion(relevant_fuel_types, int_aviation_constant_decimal):
    international_aviation_combustion = relevant_fuel_types[["Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B"]] * int_aviation_constant_decimal
    international_aviation_combustion = international_aviation_combustion.rename(columns={"Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B": "international_aviation_calculated"})
    return international_aviation_combustion


def preparing_oil_combustion_and_int_aviation(raw_oil_kt, aviation_percent):
    """Returns two dataframes with consumption of oil products in twh. The first one is for the selected oil products and the second one for international aviation"""
    oil_wide = converting_oil_to_wide(raw_oil_kt)
    relevant_fuel_types_kt = selecting_relevant_fuel_types(oil_wide)
    relevant_fuel_types_kt_cleaned = validate_data(relevant_fuel_types_kt)
    relevant_fuel_types_tj = converting_selected_oil_fuels_to_tj(relevant_fuel_types_kt_cleaned)
    relevant_fuel_types_twh = tj_to_twh(relevant_fuel_types_tj)

    int_aviation_decimal_constant = international_aviation_decimal_constant(aviation_percent)
    relevant_fuel_types_twh_corrected = correcting_aviation_relevant_fuel_types(relevant_fuel_types_twh, int_aviation_decimal_constant)
    international_aviation_twh = international_aviation_combustion(relevant_fuel_types_twh, int_aviation_decimal_constant)
    return relevant_fuel_types_twh_corrected, international_aviation_twh


# ==================================================
# Preparing emission from CRT
# ==================================================

def converting_1a_combustion_to_wide(raw_crt_1a_combustion):
    wide = raw_crt_1a_combustion.pivot(
        columns="fuel_type",
        values=["consumption_tj", "co2_kt"])
    wide.columns = [f"{name}_{code}" for name, code in wide.columns]
    wide = wide.rename(columns={
        "consumption_tj_Gaseous fuels (6) ": "nid_gaseous_consumption",	
        "consumption_tj_Liquid fuels": "nid_liquid_consumption",
        "co2_kt_Gaseous fuels (6) ": "nid_gaseous_co2",
        "co2_kt_Liquid fuels": "nid_liquid_co2"})
    return wide

def selecting_co2_gaseous_and_liquid_crt(raw_crt_1a_combustion):
    """Returns two dataframes containing yearly CO2 emissions from 1A fuel combustion from the CRT. The first one contains emissions from gaseous fuels and the second one from liquid."""
    combustion_1a_wide = converting_1a_combustion_to_wide(raw_crt_1a_combustion)
    co2_crt_gaseous = combustion_1a_wide[["nid_gaseous_co2"]]
    co2_crt_liquid = combustion_1a_wide[["nid_liquid_co2"]]
    return co2_crt_gaseous, co2_crt_liquid

def selecting_co2_int_aviation_crt(raw_int_aviation_crt):
    """Returns a dataframes containing yearly CO2 emissions from 1D international aviation from the CRT."""
    co2_int_aviation = raw_int_aviation_crt[["emissions_co2_kt"]]
    co2_int_aviation = co2_int_aviation.rename(columns={"emissions_co2_kt": "nid_international_aviation_co2"})
    return co2_int_aviation