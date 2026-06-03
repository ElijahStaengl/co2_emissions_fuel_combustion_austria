
import matplotlib.pyplot as plt
import pandas as pd
import locale
from pathlib import Path

locale.setlocale(locale.LC_TIME, "en_US.UTF-8")


# ==================================================
# General functions
# ==================================================

def monthly_to_yearly(df_monthly):
    count = pd.DataFrame()
    count["value"] = df_monthly.iloc[:,0:1].resample("YS").count()
    full_years = count[count["value"] == 12].index 
    df_yearly = df_monthly.resample("YS").sum()
    df_yearly = df_yearly.loc[full_years]
    return df_yearly

OUTPUT_DIR = Path("figures")

def save_plot (filename, ax=None, fig=None, dpi=300):
    
    filepath = OUTPUT_DIR / filename

    plt.savefig(filepath, dpi=dpi, bbox_inches="tight")

    if ax is None:
        plt.close(fig)
    else:
        plt.close(ax.figure)

def get_latest_month(dataframe):
    date = dataframe.iloc[-1].name
    month = date.strftime("%B")
    year = date.year
    return f"Latest month: {month} {year}"

def text_source(sources="E-Control, Eurostat and Austria's NID/CRT 2026", latest_month_from=None):
    if latest_month_from is None:
        plt.figtext(
        0.5,
        0.02,
        f"Source: Calculations with data from {sources}",
        ha="center",
        fontsize=8,
        color="gray")
    else:
        plt.figtext(
        0.5,
        0.02,
        f"Source: Calculations with data from {sources}\n{get_latest_month(latest_month_from)}",
        ha="center",
        fontsize=8,
        color="gray")

# --- Color pallet
COLOR4 = "#fec44f"
COLOR3 = "#fe9929"
COLOR2 = "#d95f0e"
COLOR1 = "#993404"


# ==================================================
# Creating plots comparing CRT and calculations
# ==================================================

def style_comparison(ax):
    ax.lines[0].set_color("tab:blue")   
    ax.lines[1].set_color("tab:red")
    plt.legend(["Common Reporting Table (CRT)", "Calculation"])
    plt.xlabel("")
    plt.ylabel("CO₂ emissions in kt")
    plt.ylim(bottom=0)
    for line in ax.lines:
        line.set(marker="o", linestyle="-")
    plt.subplots_adjust(bottom=0.11)

def style_difference(ax):
    ax.lines[0].set_color("tab:red")
    plt.xlabel("")
    plt.ylabel("Difference from CRT in percent")
    for line in ax.lines:
        line.set(marker="o", linestyle="")
    ymax = max(abs(ax.get_ylim()[0]), abs(ax.get_ylim()[1]))
    ax.set_ylim(-ymax, ymax)

def creating_combination_crt_and_calculations_yearly(calculated_co2_total, crt_co2):
    calculated_yearly = monthly_to_yearly(calculated_co2_total)
    return crt_co2.join(calculated_yearly, how="inner")

def creating_difference_crt_and_calculations_yearly(calculated_co2_total, crt_co2):
    combination = creating_combination_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    difference_percent = ((combination.iloc[:, 1] - combination.iloc[:, 0]) / combination.iloc[:, 0]) * 100
    return difference_percent

def plotting_comparison_gas(calculated_co2_total, crt_co2):
    combination = creating_combination_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    ax = combination.plot(title=f"Comparison of CO₂ Emissions from Natural Gas")
    style_comparison(ax)
    text_source("E-Control and Austria's NID/CRT 2026")
    save_plot("comparison_gas_lines.png", ax)

def plotting_comparison_oil(calculated_co2_total, crt_co2):
    combination = creating_combination_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    ax = combination.plot(title=f"Comparison of CO₂ Emissions from Oil Products")
    style_comparison(ax)
    text_source("Eurostat and Austria's NID/CRT 2026")
    save_plot("comparison_oil_lines.png", ax)

def plotting_comparison_int_aviation(calculated_co2_total, crt_co2):
    combination = creating_combination_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    ax = combination.plot(title=f"Comparison of CO₂ Emissions from International Aviation")
    style_comparison(ax)
    text_source("Eurostat and Austria's NID/CRT 2026")
    save_plot("comparison_int_aviation_lines.png", ax)

def plotting_difference_gas(calculated_co2_total, crt_co2):
    difference = creating_difference_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    ax = difference.plot(title="Calculated CO₂ from Natural Gas: Difference from CRT in Percent")
    style_difference(ax)
    text_source("E-Control and Austria's NID/CRT 2026")
    save_plot("difference_gas_percent.png", ax)

def plotting_gas_accuracy(calculated_co2_total, crt_co2):
    plotting_comparison_gas(calculated_co2_total, crt_co2)
    plotting_difference_gas(calculated_co2_total, crt_co2)

def plotting_difference_oil(calculated_co2_total, crt_co2):
    difference = creating_difference_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    ax = difference.plot(title="Calculated CO₂ from Oil Products: Difference from CRT in Percent")
    style_difference(ax)
    text_source("Eurostat and Austria's NID/CRT 2026")
    save_plot("difference_oil_percent.png", ax)

def plotting_oil_accuracy(calculated_co2_total, crt_co2):
    plotting_comparison_oil(calculated_co2_total, crt_co2)
    plotting_difference_oil(calculated_co2_total, crt_co2)

def plotting_difference_int_aviation(calculated_co2_total, crt_co2):
    difference = creating_difference_crt_and_calculations_yearly(calculated_co2_total, crt_co2)
    ax = difference.plot(title="Calculated CO₂ from International Aviation: Difference from CRT in Percent")
    style_difference(ax)
    text_source("Eurostat and Austria's NID/CRT 2026")
    save_plot("difference_int_aviation_percent.png", ax)

def plotting_int_aviation_accuracy(calculated_co2_total, crt_co2):
    plotting_comparison_int_aviation(calculated_co2_total, crt_co2)
    plotting_difference_int_aviation(calculated_co2_total, crt_co2)

def plotting_difference_oil_uncorrected(difference_uncorrected):
    ax = difference_uncorrected.plot(title="Uncorrected Calculated CO₂ from Oil Products: Difference from CRT")
    ax.lines[0].set_color("tab:red")
    plt.xlabel("")
    plt.ylabel("Difference from CRT in kt CO₂")
    for line in ax.lines:
        line.set(marker="o", linestyle="")
    plt.ylim(top=0)
    text_source("Eurostat and Austria's NID/CRT 2026")
    save_plot("uncorrected_difference_oil_kt_co2.png", ax)
    

# ==================================================    
# Creating short-time plots
# ==================================================

def monthly_to_plot(df):
    df_plot = df.copy()
    df_plot["values"] = df_plot.iloc[:,:]
    df_plot["year"] = df.index.year
    df_plot["month"] = df.index.month
    df_plot = df_plot.pivot(index="month", columns="year", values="values")
    return df_plot

def monthly_to_plot_cumulative(df_for_plot):
    df_cumulative = df_for_plot.cumsum()
    df_cumulative.loc[0] = 0
    df_cumulative = df_cumulative.sort_index()
    return df_cumulative

labels_years = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
years_to_plot = [-4, -3, -2, -1]

def style_months_of_year(ax):
    ax.lines[-1].set_linewidth(2.5)
    ax.lines[-1].set_markersize(7)
    ax.lines[-1].set_color(COLOR1)
    ax.lines[-2].set_color(COLOR2)
    ax.lines[-3].set_color(COLOR3)
    ax.lines[-4].set_color(COLOR4)
    for line in ax.lines:
        line.set(marker="o", linestyle="-")
    plt.xticks(
        ticks=range(1, 13),
        labels=labels_years)
    plt.xlabel("")
    plt.ylabel("CO₂ emissions in kt")
    plt.legend(title="", loc=4)
    ax.margins(y=0.1)
    ax.set_ylim(bottom=0)
    plt.subplots_adjust(bottom=0.13)


def plot_months_of_year_monthly(df_to_plot, fuel_for_title, sources,  df_original, fuel_for_name):
    ax = df_to_plot.iloc[:, years_to_plot].plot(title=f"CO₂ Emissions from {fuel_for_title} in Recent Years")
    ax.set_xlim(left=0.6, right=12.4)
    style_months_of_year(ax)
    text_source(sources, df_original)
    save_plot(f"emissions_short_time_{fuel_for_name}_monthly.png", ax)

def plot_months_of_year_cumulative(df_to_plot_cumulative, fuel_for_title, sources,  df_original, fuel_for_name):
    ax = df_to_plot_cumulative.iloc[:, years_to_plot].plot(title=f"Cumulative CO₂ Emissions from {fuel_for_title} in Recent Years")
    ax.set_xlim(left=0, right=12.4)
    style_months_of_year(ax)
    text_source(sources, df_original)
    save_plot(f"emissions_short_time_{fuel_for_name}_cumulative.png", ax)

def plot_months_of_year_complete(df, fuel_for_title, sources, fuel_for_name):
    df_for_plot = monthly_to_plot(df)
    df_for_plot_cumulative = monthly_to_plot_cumulative(df_for_plot)

    plot_months_of_year_monthly(df_for_plot, fuel_for_title, sources,  df, fuel_for_name)
    plot_months_of_year_cumulative(df_for_plot_cumulative, fuel_for_title, sources,  df, fuel_for_name)

def plot_short_time_gas(co2_calculated_gas):
    plot_months_of_year_complete(co2_calculated_gas, "Natural Gas", "E-Control and Austria's NID/CRT 2026", "gas")

def plot_short_time_oil(co2_calculated_oil_total):
    plot_months_of_year_complete(co2_calculated_oil_total, "Oil Products", "Eurostat and Austria's NID/CRT 2026", "oil")

def plot_short_time_int_aviation(co2_calculated_int_aviation):
    plot_months_of_year_complete(co2_calculated_int_aviation, "International Aviation", "Eurostat and Austria's NID/CRT 2026", "int_aviation")


# ==================================================
# Creating long-time plots
# ==================================================

months_to_show = 12*12

def creating_rolling_12m_mean(df):
    return df.rolling(window=12).mean().dropna()

def adding_12m_mean(df):
    df_with_rolling_12m = creating_rolling_12m_mean(df)
    df_with_both = df.join(df_with_rolling_12m, how="inner", lsuffix="_12m")
    return(df_with_both)


# --- All Fuels Together ---

def merging_all_calculated_co2(co2_gas, co2_oil_all, co2_int_aviation):
    merged = co2_gas.join([co2_oil_all["total_oil_products"], co2_int_aviation], how="inner")
    merged["total_calculated"] = merged.sum(axis=1)
    return merged

def plot_all_longtime_together(df_normal_and_12m):
    ax = df_normal_and_12m.iloc[-months_to_show:, :].rename(
        columns={"gas_for_combustion": "Gas", "total_oil_products": "Oil", "international_aviation_calculated": "Int. Aviation", "total_calculated": "Total"}
        ).plot(ylim=(0,None))
    alpha_monthly = 0.65
    line_with_12m_mean = 2.5
    ax.lines[0].set_alpha(alpha_monthly)
    ax.lines[1].set_alpha(alpha_monthly)
    ax.lines[2].set_alpha(alpha_monthly)
    ax.lines[3].set_alpha(alpha_monthly)
    ax.lines[4].set_linewidth(line_with_12m_mean)
    ax.lines[5].set_linewidth(line_with_12m_mean)
    ax.lines[6].set_linewidth(line_with_12m_mean)
    ax.lines[7].set_linewidth(line_with_12m_mean)
    ax.lines[0].set_color("tab:green")
    ax.lines[4].set_color("tab:green")
    ax.lines[1].set_color("tab:orange")
    ax.lines[5].set_color("tab:orange")
    ax.lines[2].set_color("tab:blue")
    ax.lines[6].set_color("tab:blue")
    ax.lines[7].set_color("tab:red")
    ax.lines[3].set_color("tab:red")
    

    plt.ylabel("CO₂ emissions in kt")
    plt.title("CO₂ Emissions from Combustion (Monthly and Rolling 12 Months)")

    order = [7, 5, 4, 6]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend([handles[i] for i in order],
            [labels[i] for i in order])

    plt.subplots_adjust(bottom=0.13)

    text_source(latest_month_from=df_normal_and_12m)

    save_plot("emissions_long_time_together.png", ax)


def plot_all_longtime_separate(df_normal_and_12m):
    fig, axes = plt.subplots(2, 2, figsize=(7, 5))
    fig.suptitle("CO₂ Emissions from Combustion (Monthly and Rolling 12 Months)", fontsize=15)
    fig.supylabel("CO₂ emissions in kt", fontsize=12)


    df_normal_and_12m["gas_for_combustion_12m"].iloc[-months_to_show:].plot(ax=axes[1,0], ylim=(0, None), xlabel=(""), title="Gas", color="tab:green", alpha=(0.65))
    df_normal_and_12m["gas_for_combustion"].iloc[-months_to_show:].plot(ax=axes[1,0], xlabel=(""), color="tab:green", linewidth=(2.5))

    df_normal_and_12m["total_oil_products_12m"].iloc[-months_to_show:].plot(ax=axes[0,1], ylim=(0, None), xlabel=(""), title="Oil", color="tab:orange", alpha=(0.65))
    df_normal_and_12m["total_oil_products"].iloc[-months_to_show:].plot(ax=axes[0,1], xlabel=(""), color="tab:orange", linewidth=(2.5))

    df_normal_and_12m["total_calculated_12m"].iloc[-months_to_show:].plot(ax=axes[0,0], ylim=(0, None), xlabel=(""), title="Total", color="tab:red", alpha=(0.65))
    df_normal_and_12m["total_calculated"].iloc[-months_to_show:].plot(ax=axes[0,0], xlabel=(""), color="tab:red", linewidth=(2.5))

    df_normal_and_12m["international_aviation_calculated_12m"].iloc[-months_to_show:].plot(ax=axes[1,1], ylim=(0, None), xlabel=(""), title="Int. Aviation", color="tab:blue", alpha=(0.65))
    df_normal_and_12m["international_aviation_calculated"].iloc[-months_to_show:].plot(ax=axes[1,1], xlabel=(""), color="tab:blue", linewidth=(2.5))

    plt.tight_layout()

    plt.subplots_adjust(bottom=0.13)

    text_source(latest_month_from=df_normal_and_12m)

    save_plot("emissions_long_time_separate.png", fig=fig)

def plot_all_longtime(co2_gas, co2_oil_all, co2_int_aviation):
    merged = merging_all_calculated_co2(co2_gas, co2_oil_all, co2_int_aviation)
    normal_and_12m = adding_12m_mean(merged)
    plot_all_longtime_together(normal_and_12m)
    plot_all_longtime_separate(normal_and_12m)


# --- Different Oil Products ---

color_gasoil_dieseloil = COLOR4
color_gasoline = COLOR3
color_others = COLOR2
color_missing_combustion =COLOR1



def sorting_oil_in_4_catgories(co2_oil):
    sorted = pd.DataFrame()
    sorted = pd.DataFrame()
    sorted["Gasoil and Dieseloil"] = co2_oil[["Gasöl und Dieselöl (ohne Biokraftstoffanteil)_O4671XR5220B"]]
    sorted["Gasoline"] = co2_oil[["Motorenbenzin (ohne Biokraftstoffanteil)_O4652XR5210B"]]
    sorted["Others"] = co2_oil[["Flüssiggas_O4630"]]
    sorted["Others"] = sorted["Others"] + co2_oil["Flugturbinenkraftstoff auf Petroleumbasis (ohne Biokraftstoffanteil)_O4661XR5230B"] + co2_oil["Heizöl_O4680"]
    sorted["Missing Oil Combustion"] = co2_oil[["missing_oil_combustion"]]
    return sorted

def plot_area_graph_oil_products(oil_4_categories_12m):
    order_of_graphs = ["Missing Oil Combustion", "Others", "Gasoline", "Gasoil and Dieseloil"]
    ax = oil_4_categories_12m[order_of_graphs].iloc[-months_to_show:, :].plot.area(
        linewidth=0,
        alpha=1,
        color = {"Gasoil and Dieseloil":color_gasoil_dieseloil, "Gasoline": color_gasoline, "Others": color_others, "Missing Oil Combustion": color_missing_combustion})

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc=6)
    plt.xlabel("")
    plt.ylabel("CO₂ emissions in kt")
    plt.title("Monthly CO₂ Emissions from Different Liquid Fuels (Rolling 12 Months)")

    plt.subplots_adjust(bottom=0.13)

    text_source("Eurostat and Austria's NID/CRT 2026", oil_4_categories_12m)
    save_plot("emissions_long_time_oil_area_graph.png", ax)


def plot_oil_products_separate(oil_4_categories_monthly, oil_4_categories_12m):
    fig, axes = plt.subplots(2, 2, figsize=(7, 5))
    fig.suptitle("Monthly CO₂ Emissions from Different Liquid Fuels", fontsize=15)
    fig.supylabel("CO₂ emissions in kt", fontsize=12)

    oil_4_categories_monthly["Gasoline"].iloc[-months_to_show:].plot(ax=axes[0,1], ylim=(0, 500), xlabel=(""), title="Gasoline", color=color_gasoline, alpha=(0.65))
    oil_4_categories_12m["Gasoline"].iloc[-months_to_show:].plot(ax=axes[0,1], xlabel=(""), color=color_gasoline, linewidth=(2.5))

    oil_4_categories_monthly["Gasoil and Dieseloil"].iloc[-months_to_show:].plot(ax=axes[0,0], ylim=(0, 2500), xlabel=(""), title="Gasoil and Dieseloil", color=color_gasoil_dieseloil, alpha=(0.65))
    oil_4_categories_12m["Gasoil and Dieseloil"].iloc[-months_to_show:].plot(ax=axes[0,0], xlabel=(""), color=color_gasoil_dieseloil, linewidth=(2.5))

    oil_4_categories_monthly["Others"].iloc[-months_to_show:].plot(ax=axes[1,0], ylim=(0, 200), xlabel=(""), title="Others", color=color_others, alpha=(0.65))
    oil_4_categories_12m["Others"].iloc[-months_to_show:].plot(ax=axes[1,0], xlabel=(""), color=color_others, linewidth=(2.5))

    oil_4_categories_12m["Missing Oil Combustion"].iloc[-months_to_show:].plot(ax=axes[1,1], ylim=(0, 500), xlabel=(""), title="Missing Oil Combustion", color=color_missing_combustion, linewidth=(2.5))

    plt.tight_layout()

    plt.subplots_adjust(bottom=0.13)

    text_source("Eurostat and Austria's NID/CRT 2026", oil_4_categories_monthly)
    save_plot("emissions_long_time_oil_separate.png", fig=fig)

def plot_different_oil_products(co2_oil):
    sorted_monthly = sorting_oil_in_4_catgories(co2_oil)
    sorted_12m = creating_rolling_12m_mean(sorted_monthly)
    plot_area_graph_oil_products(sorted_12m)
    plot_oil_products_separate(sorted_monthly, sorted_12m)


# ==================================================
# Combining short-time plots
# ==================================================

labels_years_6 = ['Jan', '', 'Mar', '', 'May', '',
            'Jul', '', 'Sep', '', 'Nov', '']


def plot_months_of_year_for_subplots(df_to_plot, title="xxx", cumulative=False, ax="example: axes[0, 0]"):
    if cumulative == True:
        left = 0
    else:
        left = 0.6
    ax = df_to_plot.iloc[:, years_to_plot].plot(ax=ax, style="-o", title=title, legend="", xlabel="")
    ax.set_xlim(left=left, right=12.4)

    ax.lines[-1].set_linewidth(2.5)
    ax.lines[-1].set_markersize(7)
    ax.lines[-1].set_color(COLOR1)
    ax.lines[-2].set_color(COLOR2)
    ax.lines[-3].set_color(COLOR3)
    ax.lines[-4].set_color(COLOR4)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(labels_years_6)

    ax.margins(y=0.1)
    ax.set_ylim(bottom=0)


def plot_short_time_together(co2_gas, co2_oil, co2_int_aviation):
    common_years = (
        set(co2_gas.index.year)
        & set(co2_oil.index.year)
        & set(co2_int_aviation.index.year))

    co2_gas = co2_gas[co2_gas.index.year.isin(common_years)]
    co2_oil = co2_oil[co2_oil.index.year.isin(common_years)]
    co2_int_aviation = co2_int_aviation[co2_int_aviation.index.year.isin(common_years)]

    fig, axes = plt.subplots(3, 2, figsize=(8, 8))

    fig.supylabel("CO₂ emissions in kt", fontsize=12)

    plt.subplots_adjust(
        hspace=0.35, 
        wspace=0.23)

    fig.text(
        0.30,
        0.93,
        "Monthly Emissions",
        ha="center",
        fontsize=15)

    fig.text(
        0.73,
        0.93,
        "Cumulative Emissions",
        ha="center",
        fontsize=15)

    plot_months_of_year_for_subplots(monthly_to_plot(co2_gas), title="Natural Gas", ax=axes[0,0])
    plot_months_of_year_for_subplots(monthly_to_plot_cumulative(monthly_to_plot(co2_gas)), title="Natural Gas", ax=axes[0,1], cumulative=True)

    plot_months_of_year_for_subplots(monthly_to_plot(co2_oil[["total_oil_products"]]), title="Oil Products", ax=axes[1,0])
    plot_months_of_year_for_subplots(monthly_to_plot_cumulative(monthly_to_plot(co2_oil[["total_oil_products"]])), title="Oil Products", ax=axes[1,1], cumulative=True)

    plot_months_of_year_for_subplots(monthly_to_plot(co2_int_aviation), title="International Aviation", ax=axes[2,0])
    plot_months_of_year_for_subplots(monthly_to_plot_cumulative(monthly_to_plot(co2_int_aviation)), title="International Aviation", ax=axes[2,1], cumulative=True)

    plt.subplots_adjust(bottom=0.13)

    text_source(latest_month_from=co2_gas)

    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.046),
        ncol=4,
        frameon=False)
    save_plot("emissions_short_time_all.png", fig=fig)