
import pandas as pd

# Importing for gas

def load_gas_consumption():
    """Returns current monthly gas consumption in multiple categories in mwh and gcv in a dataframe.
        Data from https://www.e-control.at/statistik/g-statistik/data, "Zeitreihen mit monatlichen Daten"""
    data = pd.read_csv("https://www.e-control.at/documents/1785851/10140531/gas_dataset_mn.csv",
                                   sep=";", encoding="cp1252", index_col = 0, parse_dates=True, skiprows=[0,1,3,4,6,7,8,9,10,11], header=[0,1], decimal=",")
    data.columns = [f"{a}_{b}" for a, b in data.columns]
    return data

def load_gas_for_ammonia():
    """Returns gas consumption for ammonia production in tj and ncv for 2010-2024.
    Data from NID 2026 page 336, Table 138, Natural gas input [TJ]"""
    data = pd.DataFrame(
        data={"gas_used_ammonia": [15996, 16108, 15744, 14274, 16677, 16195, 16885, 15716, 12651, 16932, 16073, 16360, 14132, 14967, 11821]},
        index=pd.to_datetime([2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024], format="%Y"))
    return data

# Importing for oil

def load_oil_consumption():
    """Returns current monthly consumption of different oil products in kt in a dataframe.
    Data from Eurostat"""
    data = pd.read_csv("https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/dataflow/ESTAT/nrg_cb_oilm/1.0/*.*.*.*.*?c[freq]=M&c[nrg_bal]=GID_OBS&c[siec]=O4100_TOT_4200-4500,O4100_TOT,O4200,O4300,O4400,O4410,O4500,O4600,O4610,O4620,O4630,O4640,O4651,O4652,O4652XR5210B,O4653,O4661,O4661XR5230B,O4669,O4671,O4671XR5220B,O46711,O46712,O4680,O4681,O46811,O4682,O4690XO4694,O4694,R5210B,R5220B,R5230,R5230B&c[unit]=THS_T&c[geo]=AT&c[TIME_PERIOD]=ge:2008-01&compress=true&format=csvdata&formatVersion=2.0&lang=de&labels=name",
                   compression="gzip", index_col = 13, parse_dates=True)
    return data

def load_aviation_percent():
    """Returs percent of kerosene used for international and domestic aviation in dataframe for the years 1990 to 2024.
    Automatically created CSVs from "Austria. 2026 Common Reporting Table (CRT)" (Publication date: 16 Apr 2026)"""
    data = pd.read_csv(f'data/input_data/aviation_percent.csv', sep=";", index_col = 0, parse_dates=True, decimal=",")
    return data

# Importing for verification

def load_crt_1a_combustion():
    """Returns consumption and emissions data for liquid and gaseous fuels in a dataframe.
    Automatically created CSVs from "Austria. 2026 Common Reporting Table (CRT)" (Publication date: 16 Apr 2026)"""
    data = pd.read_csv(f'data/input_data/nid_2026_1a_fuel_combustion_gas_oil.csv', sep=";", index_col = 0, parse_dates=True, decimal=",")
    return data

def load_crt_1d_international_aviation():
    """Returns consumption and emissions data for international aviation in a dataframe.
    Automatically created CSVs from "Austria. 2026 Common Reporting Table (CRT)" (Publication date: 16 Apr 2026)"""
    data = pd.read_csv(f'data/input_data/international_bunker_aviation.csv', sep=";", index_col = 0, parse_dates=True, decimal=",")
    return data

