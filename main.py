
from src import load_data as ld
from src import data_preparation as prep
from src import calculations_co2 as calc
from src import plotting as pl
from src import saving as save
import os

os.makedirs("figures", exist_ok=True)
os.makedirs("data/output_data", exist_ok=True)

# --- Information ---
# All calculated dataframes are with monthly values, if not stated otherwise
# -------------------

# ==================================================
# Loading data
# ==================================================

raw_gas_consumption_mwh_gcv = ld.load_gas_consumption()
save.save_input_df_to_csv(raw_gas_consumption_mwh_gcv, "input_gas")
raw_gas_for_ammonia_tj_ncv = ld.load_gas_for_ammonia()
raw_oil_consumption_kt = ld.load_oil_consumption()
save.save_input_df_to_csv(raw_oil_consumption_kt, "input_oil")
raw_aviation_percent = ld.load_aviation_percent()
raw_1a_combustion = ld.load_crt_1a_combustion()
raw_1d_international_aviation = ld.load_crt_1d_international_aviation()


# ==================================================
# Preparing data
# ==================================================

gas_consumption_twh = prep.calculating_gas_for_combustion(raw_gas_consumption_mwh_gcv, raw_gas_for_ammonia_tj_ncv)

oil_consumption_twh, int_aviation_twh = prep.preparing_oil_combustion_and_int_aviation(raw_oil_consumption_kt, raw_aviation_percent)

co2_gaseous_yearly_crt_kt, co2_liquid_yearly_crt_kt = prep.selecting_co2_gaseous_and_liquid_crt(raw_1a_combustion)

co2_int_aviation_yearly_crt_kt = prep.selecting_co2_int_aviation_crt(raw_1d_international_aviation)


# ==================================================
# Calculating emissions
# ==================================================

co2_calculated_gas_kt = calc.calculating_co2_from_gas_kt(gas_consumption_twh)

difference_uncorrected_oil_to_crt_co2_kt = calc.calculating_difference_crt_to_co2_oil_uncorrected(oil_consumption_twh, co2_liquid_yearly_crt_kt)

co2_calculated_oil_kt = calc.calculating_co2_from_oil_kt_final(oil_consumption_twh, co2_liquid_yearly_crt_kt)

co2_calculated_int_aviation_kt = calc.calculating_co2_from_int_aviation_kt(int_aviation_twh)

save.save_output_df_to_csv(co2_calculated_gas_kt, "co2_calculated_gas_kt")
save.save_output_df_to_csv(co2_calculated_oil_kt, "co2_calculated_oil_kt")
save.save_output_df_to_csv(co2_calculated_int_aviation_kt, "co2_calculated_int_aviation_kt")

# ==================================================
# Creating plots
# ==================================================

pl.plotting_difference_oil_uncorrected(difference_uncorrected_oil_to_crt_co2_kt)

pl.plotting_gas_accuracy(co2_calculated_gas_kt, co2_gaseous_yearly_crt_kt)
pl.plotting_oil_accuracy(co2_calculated_oil_kt[["total_oil_products"]], co2_liquid_yearly_crt_kt)
pl.plotting_int_aviation_accuracy(co2_calculated_int_aviation_kt, co2_int_aviation_yearly_crt_kt)
pl.plotting_total_accuracy(co2_calculated_oil_kt[["total_oil_products"]], co2_calculated_gas_kt, co2_liquid_yearly_crt_kt, co2_gaseous_yearly_crt_kt)

pl.plot_short_time_gas(co2_calculated_gas_kt)
pl.plot_short_time_oil(co2_calculated_oil_kt[["total_oil_products"]])
pl.plot_short_time_int_aviation(co2_calculated_int_aviation_kt)
pl.plot_short_time_together(co2_calculated_gas_kt, co2_calculated_oil_kt, co2_calculated_int_aviation_kt)

pl.plot_all_longtime(co2_calculated_gas_kt, co2_calculated_oil_kt, co2_calculated_int_aviation_kt)
pl.plot_different_oil_products(co2_calculated_oil_kt)


# ==================================================
# Values for bachelor thesis
# ==================================================

gas_non_energy_monthly_twh_ncv = prep.preparing_gas_non_energy_twh_ncv(raw_gas_for_ammonia_tj_ncv)
print(f"The constant used for gas consumption used for non-energy purpose is rounded {gas_non_energy_monthly_twh_ncv.round(4)} TWh per month and {(gas_non_energy_monthly_twh_ncv*12).round(4)} TWh per year (all NCV).")

int_aviation_decimal_constant = prep.international_aviation_decimal_constant(raw_aviation_percent)
print(f"{int_aviation_decimal_constant * 100}% of kerosene consumption is appointed towards international aviation and {(1 - int_aviation_decimal_constant).round(4) * 100}% towards domestic aviation (oil products).")

missing_monthly_co2_oil_uncorrected_not_rounded, missing_monthly_co2_oil_uncorrected_rounded = calc.explaining_missing_co2_oil(oil_consumption_twh, co2_liquid_yearly_crt_kt)
print(f'CO₂ missing per month is {missing_monthly_co2_oil_uncorrected_not_rounded} and per year {missing_monthly_co2_oil_uncorrected_not_rounded * 12}')
print(f'The added CO₂ per month is {missing_monthly_co2_oil_uncorrected_rounded} and per year {missing_monthly_co2_oil_uncorrected_rounded * 12}')

gas_difference = pl.creating_difference_crt_and_calculations_yearly(co2_calculated_gas_kt, co2_gaseous_yearly_crt_kt)
print(f"Natural Gas CO2 difference from CRT in percent:\n{abs(gas_difference).describe()}")
oil_difference = pl.creating_difference_crt_and_calculations_yearly(co2_calculated_oil_kt[["total_oil_products"]], co2_liquid_yearly_crt_kt)
print(f"Oil Products CO2 difference from CRT in percent:\n{abs(oil_difference).describe()}")
oil_and_gas_difference = pl.creating_difference_crt_and_calculations_yearly(pl.sum_of_two_df(co2_calculated_oil_kt[["total_oil_products"]], co2_calculated_gas_kt), pl.sum_of_two_df(co2_liquid_yearly_crt_kt, co2_gaseous_yearly_crt_kt))
print(f"Sum of Oil Products and Natural Gas CO2 difference from CRT in percent:\n{abs(oil_and_gas_difference).describe()}")
int_aviation_difference = pl.creating_difference_crt_and_calculations_yearly(co2_calculated_int_aviation_kt, co2_int_aviation_yearly_crt_kt)
print(f"International Aviation CO2 difference from CRT in percent:\n{abs(int_aviation_difference).describe()}")
