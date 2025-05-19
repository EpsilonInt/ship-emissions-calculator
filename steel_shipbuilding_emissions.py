
import streamlit as st
import pandas as pd
import altair as alt

# === Emission Factors ===
production_factors = {"CO2": 996, "CO": 31.83, "CH4": 0.16317, "NOx": 5.84,
                      "PM": 0.92896, "SOx": 5.58372, "VOC": 0.01257, "NMVOC": 0.01084}
grouped_welding_dict = {
    "FCAW": {"E110": 20.8, "E11018": 57.0, "E308LT": 9.1, "E316LT": 8.5, "E70T": 15.1, "E71T": 12.2},
    "GMAW": {"E308L": 5.4, "E70S": 5.2, "ER1260": 20.5, "ER5154": 24.1, "ER316": 3.2, "ERNiCrMo": 3.9, "ERNiCu": 2.0},
    "SAW": {"ER316, ER316L": 7.95, "ER309, ER309L": 17.62, "EM12K": 0.05},
    "SMAW": {"14Mn-4Cr": 81.6, "E11018": 16.4, "E308": 10.8, "E310": 15.1, "E316": 10.0,
             "E410": 13.2, "E6010": 25.6, "E6011": 38.4, "E6012": 8.0, "E6013": 19.7,
             "E7018": 18.4, "E7024": 9.2, "E7028": 18.0, "E8018": 17.1,
             "E9015": 17.0, "E9018": 16.9, "ECoCr": 27.9, "ENi-Cl": 18.2,
             "ENiCrMo": 11.7, "ENi-Cu": 10.1}
}
emission_factors = {
    'Air': {
        'Dry': {'Mild steel, 8mm': {'PM': 23, 'NOx': 6.6}, 'Stainless, 8mm': {'PM': 35, 'NOx': 6.3},
                'Stainless, 35mm': {'PM': 2.6, 'NOx': 9.8}},
        'Semi-dry': {'Mild steel, 8mm': {'PM': 3, 'NOx': 3.7}, 'Stainless, 8mm': {'PM': 4.1, 'NOx': 3.3},
                     'Stainless, 35mm': {'PM': 0.2, 'NOx': 5.2}},
        'Wet': {'Mild steel, 8mm': {'PM': 0.25, 'NOx': 1.4}, 'Stainless, 8mm': {'PM': 0.35, 'NOx': 1.5},
                'Stainless, 35mm': {'PM': 0.02, 'NOx': 2.6}}
    },
    'Oxygen': {
        'Dry': {'Mild steel, 8mm': {'PM': 17.25, 'NOx': 6.6}, 'Stainless, 8mm': {'PM': 26.25, 'NOx': 6.3},
                'Stainless, 35mm': {'PM': 1.95, 'NOx': 9.8}},
        'Semi-dry': {'Mild steel, 8mm': {'PM': 2.25, 'NOx': 3.7}, 'Stainless, 8mm': {'PM': 3.075, 'NOx': 3.3},
                     'Stainless, 35mm': {'PM': 0.15, 'NOx': 5.2}},
        'Wet': {'Mild steel, 8mm': {'PM': 0.1875, 'NOx': 1.4}, 'Stainless, 8mm': {'PM': 0.2625, 'NOx': 1.5},
                'Stainless, 35mm': {'PM': 0.015, 'NOx': 2.6}}
    },
    'Nitrogen': {
        'Dry': {'Mild steel, 8mm': {'PM': 23, 'NOx': 5.28}, 'Stainless, 8mm': {'PM': 35, 'NOx': 5.04},
                'Stainless, 35mm': {'PM': 2.6, 'NOx': 7.84}},
        'Semi-dry': {'Mild steel, 8mm': {'PM': 3, 'NOx': 2.96}, 'Stainless, 8mm': {'PM': 4.1, 'NOx': 2.64},
                     'Stainless, 35mm': {'PM': 0.2, 'NOx': 4.16}},
        'Wet': {'Mild steel, 8mm': {'PM': 0.25, 'NOx': 1.12}, 'Stainless, 8mm': {'PM': 0.35, 'NOx': 1.2},
                'Stainless, 35mm': {'PM': 0.02, 'NOx': 2.08}}
    }
}
# === Sandblasting Emission Factors ===
sandblasting_factors = pd.DataFrame({
    "Wind Speed": ["5 mph"]*3 + ["10 mph"]*3 + ["15 mph"]*3,
    "Surface Type": ["Precleaned", "Painted", "Oxidized"]*3,
    "Emission Factor (kg/kg sand)": [29, 27, 25, 68, 70, 26, 92, 91, 89]
})
coating_emission_factors = {"Conveyor Single Flow": 6.94, "Conveyor Dip": 6.94,
    "Conveyor Single Spray": 12.5, "Conveyor Two-Coat, Flow and Spray": 19.44,
    "Conveyor Two-Coat, Dip and Spray": 19.44, "Conveyor Two-Coat, Spray": 25,
    "Manual Two-Coat, Spray and Air Dry": 24.94}
engine_emission_factors = {"CO2": 84827, "CO": 183, "CH4": 104,
    "NOx": 270, "PM": 29, "SOx": 557, "NMVOC": 18}

# Initialize combined emissions
combined_emissions = {k: 0 for k in set(production_factors) | set(engine_emission_factors)}

# Sensitivity helper
def run_sensitivity(name, base_value, compute_fn, pct=(-50,50)):
    with st.expander(f"📊 Sensitivity: {name}"):
        if base_value <= 0:
            st.info(f"Enter a {name.lower()} above before using sensitivity analysis.")
            return
        delta = st.slider(f"Change in {name} (%)", pct[0], pct[1], 0)
        adj = base_value * (1 + delta/100)
        base_em = compute_fn(base_value)
        adj_em = compute_fn(adj)
        df = pd.DataFrame({"Baseline (g)": base_em, "Adjusted (g)": adj_em})
        df["Δ (g)"] = df["Adjusted (g)"] - df["Baseline (g)"]
        st.dataframe(df.style.format({"Baseline (g)":"{:.2f}",
                                      "Adjusted (g)":"{:.2f}",
                                      "Δ (g)":"{:+.2f}"}))
        m = df.reset_index().melt(
            id_vars="index", value_vars=["Baseline (g)","Adjusted (g)"],
            var_name="Scenario", value_name="Emissions")
        chart = alt.Chart(m).mark_bar(size=40).encode(
            x=alt.X("index:N", title="Emission Type"),
            y=alt.Y("Emissions:Q", title="Emissions (g)"),
            color=alt.Color("Scenario:N", title="Scenario"),
            xOffset="Scenario:N",
            tooltip=[alt.Tooltip("index:N", title="Emission Type"),
                     alt.Tooltip("Scenario:N"),
                     alt.Tooltip("Emissions:Q")]
        ).properties(width=600, height=300,
                     title=f"{name} Sensitivity")
        st.altair_chart(chart, use_container_width=True)

# UI
st.title("Steel Shipbuilding Emissions Calculator")

# Production
st.header("Production Phase")
steel_weight = st.number_input("Enter steel weight (kg):", 0, step=1000)
prod_em = {g: production_factors[g]*steel_weight for g in production_factors}
for g,v in prod_em.items(): combined_emissions[g]+=v
df_prod = pd.DataFrame.from_dict(prod_em, orient='index', columns=["Production Emissions (g)"])
df_prod.index.name="Emission Type"
st.dataframe(df_prod)
st.altair_chart(alt.Chart(df_prod.reset_index()).mark_bar(size=40).encode(
    x="Emission Type", y="Production Emissions (g)", tooltip=["Emission Type","Production Emissions (g)"]
).properties(width=600,height=300,title="Production Emissions"), use_container_width=True)

# Welding
st.header("Welding Phase")
method = st.selectbox("Welding Method", list(grouped_welding_dict.keys()))
electrode_type = st.selectbox("Electrode Type", list(grouped_welding_dict[method].keys()))
electrode_kg = st.number_input("Enter electrode mass (kg):", 0.0, step=1.0)
pm_weld = grouped_welding_dict[method][electrode_type] * electrode_kg
combined_emissions["PM"] += pm_weld
df_weld = pd.DataFrame({"Emission Type":[f"PM ({method})"],"Welding Emissions (g)":[pm_weld]}).set_index("Emission Type")
st.dataframe(df_weld)
st.altair_chart(alt.Chart(df_weld.reset_index()).mark_bar(size=60).encode(
    x="Emission Type", y="Welding Emissions (g)", tooltip=["Emission Type","Welding Emissions (g)"]
).properties(width=400,height=300,title="Welding Emissions"), use_container_width=True)

# Plasma Cutting
st.header("Plasma Cutting Phase")
plasma_gas = st.selectbox("Plasma Gas", ['Air','Oxygen','Nitrogen'])
cut_method = st.selectbox("Cutting Method", ['Dry','Semi-dry','Wet'])
thickness = st.selectbox("Thickness", ['Mild steel, 8mm','Stainless, 8mm','Stainless, 35mm'])
duration = st.number_input("Enter cutting duration (min):", 0, step=1)
em_f = emission_factors[plasma_gas][cut_method][thickness]
pm_cut = em_f['PM']*duration; nox_cut = em_f['NOx']*duration
combined_emissions["PM"] += pm_cut; combined_emissions["NOx"] += nox_cut
df_cut = pd.DataFrame({"Emission Type":["Metal Fumes (PM)","NOₓ"],"Emissions (g)":[pm_cut,nox_cut]})
st.dataframe(df_cut)
st.altair_chart(alt.Chart(df_cut).mark_bar(size=40).
    encode(x="Emission Type",y="Emissions (g)",tooltip=["Emission Type","Emissions (g)"]).
    properties(width=600,height=300,title="Plasma Cutting Emissions"), use_container_width=True)

# Coating
st.header("Coating Process")
coat_method = st.selectbox("Coating Method", list(coating_emission_factors.keys()))
unit = st.radio("Surface area unit", ("ft²","m²"))
area = st.number_input("Enter surface area", 0.0, step=1.0)
if unit=="m²": area *= 1/0.092903
voc = coating_emission_factors[coat_method]*area
combined_emissions["VOC"] += voc
df_coat = pd.DataFrame({"Emission Type":["VOC Emissions"],"Emissions (g)":[voc]})
st.dataframe(df_coat)
st.altair_chart(alt.Chart(df_coat).mark_bar(size=40).encode(
    x="Emission Type", y="Emissions (g)", tooltip=["Emission Type","Emissions (g)"]
).properties(width=600,height=300,title="VOC Emissions from Coating"), use_container_width=True)

# Sandblasting
st.header("Sandblasting Phase")
wind = st.selectbox("Wind Speed", ["5 mph","10 mph","15 mph"])
surf = st.selectbox("Surface Type", ["Precleaned","Painted","Oxidized"])
sand_amt = st.number_input("Enter sand used (kg):", 0.0, step=1.0)
factor = sandblasting_factors[(sandblasting_factors["Wind Speed"]==wind)&(sandblasting_factors["Surface Type"]==surf)]["Emission Factor (kg/kg sand)"].values[0]
pm_sand = factor*sand_amt
combined_emissions["PM"] += pm_sand
df_sand = pd.DataFrame({"Emission Type":["Metal Fumes (PM)"],"Emissions (g)":[pm_sand]})
st.dataframe(df_sand)
st.altair_chart(alt.Chart(df_sand).mark_bar(size=40).encode(
    x="Emission Type", y="Emissions (g)", tooltip=["Emission Type","Emissions (g)"]
).properties(width=600,height=300,title="Sandblasting Emissions"), use_container_width=True)

# --- Shop Test Engine Phase ---
st.header("Shop Test Engine Phase")

# Emission factors per kg fuel
shop_test_factors_main = {
    "CO2": 3114, "CO": 2.77, "CH4": 0.06, "NOx": 90.3,
    "PM": 7.28, "SOx": 49.08, "NMVOC": 3.08
}
shop_test_factors_aux = {
    "CO2": 3206, "CO": 3.84, "CH4": 0.6,
    "PM": 0.04, "NMVOC": 1.75
}

# Inputs
num_main = st.number_input("Number of Main Engines:", 0, step=1)
power_main = st.number_input("Maximum Continuous Rating of Main Engine (kW):", 0.0, step=10.0)
num_aux = st.number_input("Number of Auxiliary Engines:", 0, step=1)
power_aux = st.number_input("Maximum Continuous Rating of Auxiliary Engine (kW):", 0.0, step=10.0)

# Fuel rates per kW
fuel_per_kw_main = 1.886
fuel_per_kw_aux  = 0.35

# Total fuel used
fuel_main = num_main * power_main * fuel_per_kw_main
fuel_aux  = num_aux  * power_aux  * fuel_per_kw_aux

# Calculate emissions
shop_em = {}
for gas in set(shop_test_factors_main) | set(shop_test_factors_aux):
    e_main = shop_test_factors_main.get(gas, 0) * fuel_main
    e_aux  = shop_test_factors_aux .get(gas, 0) * fuel_aux
    shop_em[gas] = e_main + e_aux
    combined_emissions[gas] += shop_em[gas]

# Display
shop_df = pd.DataFrame.from_dict(shop_em, orient="index", columns=["Emissions (g)"])
shop_df.index.name = "Emission Type"
st.subheader("Shop Test Engine Emissions")
st.dataframe(shop_df)
st.altair_chart(
    alt.Chart(shop_df.reset_index()).mark_bar(size=40)
       .encode(x="Emission Type", y="Emissions (g)",
               tooltip=["Emission Type","Emissions (g)"])
       .properties(width=600, height=300, title="Shop Test Engine Emissions"),
    use_container_width=True
)


# Engine Construction
st.header("Engine Construction Phase")
eng_power = st.number_input("Enter engine power (kW):", 0.0, step=1.0)
eng_em = {g: engine_emission_factors[g]*eng_power for g in engine_emission_factors}
for g,v in eng_em.items(): combined_emissions[g]+=v
df_eng = pd.DataFrame(list(eng_em.items()),columns=["Emission Type","Emissions (g)"])
st.dataframe(df_eng)
st.altair_chart(alt.Chart(df_eng).mark_bar(size=40).encode(
    x="Emission Type", y="Emissions (g)", tooltip=["Emission Type","Emissions (g)"]
).properties(width=600,height=300,title="Engine Construction Emissions"), use_container_width=True)

# Totals & Summary
st.subheader("Updated Combined Totals")
df_tot = pd.DataFrame.from_dict(combined_emissions,orient='index',columns=["Total Emissions (g)"])
df_tot.index.name="Emission Type"
st.dataframe(df_tot)
st.altair_chart(alt.Chart(df_tot.reset_index()).mark_bar(size=50).encode(
    x="Emission Type", y="Total Emissions (g)", tooltip=["Emission Type","Total Emissions (g)"]
).properties(width=600,height=300,title="Total Emissions by Gas Type"), use_container_width=True)
st.markdown("### 🧮 Summary of All Emissions")
for gas,val in combined_emissions.items():
    if gas=="CO2":
        st.markdown(f"- **{gas}**: {val:,.0f} g ({val/1e6:.2f} metric tons)")
    else:
        st.markdown(f"- **{gas}**: {val:,.0f} g")

# Sensitivity analysis
st.header("Sensitivity Analysis")
run_sensitivity("Steel Weight", steel_weight,
                lambda w: {g: production_factors[g]*w for g in production_factors})
run_sensitivity("Electrode Mass", electrode_kg,
                lambda m: {"PM": grouped_welding_dict[method][electrode_type]*m})
run_sensitivity("Cutting Duration", duration,
                lambda d: {"Metal Fumes (PM)": emission_factors[plasma_gas][cut_method][thickness]['PM']*d,
                           "NOx": emission_factors[plasma_gas][cut_method][thickness]['NOx']*d})
run_sensitivity("Coating Area", area,
                lambda a: {"VOC": coating_emission_factors[coat_method]*a})
run_sensitivity("Sand Used", sand_amt,
                lambda s: {"Metal Fumes (PM)": s*factor})
run_sensitivity("Engine Power", eng_power,
                lambda p: {g: engine_emission_factors[g]*p for g in engine_emission_factors})
