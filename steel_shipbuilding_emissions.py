import streamlit as st
import pandas as pd
import altair as alt

# === Emission Factors ===

# Steel production phase (per kg steel)
production_factors = {
    "CO2": 996,
    "CO": 31.83,
    "CH4": 0.16317,
    "NOx": 5.84,
    "PM": 0.92896,
    "SOx": 5.58372,
    "VOC": 0.01257,
    "NMVOC": 0.01084
}

# Welding methods and electrode-specific PM EF (gr/kg)
grouped_welding_dict = {
    "FCAW": {
        "E110": 20.8, "E11018": 57.0, "E308LT": 9.1, "E316LT": 8.5,
        "E70T": 15.1, "E71T": 12.2
    },
    "GMAW": {
        "E308L": 5.4, "E70S": 5.2, "ER1260": 20.5, "ER5154": 24.1,
        "ER316": 3.2, "ERNiCrMo": 3.9, "ERNiCu": 2.0
    },
    "SAW": {
        "ER316, ER316L": 7.95, "ER309, ER309L": 17.62, "EM12K": 0.05
    },
    "SMAW": {
        "14Mn-4Cr": 81.6, "E11018": 16.4, "E308": 10.8, "E310": 15.1,
        "E316": 10.0, "E410": 13.2, "E6010": 25.6, "E6011": 38.4,
        "E6012": 8.0, "E6013": 19.7, "E7018": 18.4, "E7024": 9.2,
        "E7028": 18.0, "E8018": 17.1, "E9015": 17.0, "E9018": 16.9,
        "ECoCr": 27.9, "ENi-Cl": 18.2, "ENiCrMo": 11.7, "ENi-Cu": 10.1
    }
}

# Plasma cutting emission factors based on Plasma Gas type, Cutting Method, and Steel Thickness
emission_factors = {
    'Air': {
        'Dry': {
            'Mild steel, 8mm': {'PM': 23, 'NOx': 6.6},
            'Stainless, 8mm': {'PM': 35, 'NOx': 6.3},
            'Stainless, 35mm': {'PM': 2.6, 'NOx': 9.8}
        },
        'Semi-dry': {
            'Mild steel, 8mm': {'PM': 3, 'NOx': 3.7},
            'Stainless, 8mm': {'PM': 4.1, 'NOx': 3.3},
            'Stainless, 35mm': {'PM': 0.2, 'NOx': 5.2}
        },
        'Wet': {
            'Mild steel, 8mm': {'PM': 0.25, 'NOx': 1.4},
            'Stainless, 8mm': {'PM': 0.35, 'NOx': 1.5},
            'Stainless, 35mm': {'PM': 0.02, 'NOx': 2.6}
        }
    },
    'Oxygen': {
        'Dry': {
            'Mild steel, 8mm': {'PM': 17.25, 'NOx': 6.6},
            'Stainless, 8mm': {'PM': 26.25, 'NOx': 6.3},
            'Stainless, 35mm': {'PM': 1.95, 'NOx': 9.8}
        },
        'Semi-dry': {
            'Mild steel, 8mm': {'PM': 2.25, 'NOx': 3.7},
            'Stainless, 8mm': {'PM': 3.075, 'NOx': 3.3},
            'Stainless, 35mm': {'PM': 0.15, 'NOx': 5.2}
        },
        'Wet': {
            'Mild steel, 8mm': {'PM': 0.1875, 'NOx': 1.4},
            'Stainless, 8mm': {'PM': 0.2625, 'NOx': 1.5},
            'Stainless, 35mm': {'PM': 0.015, 'NOx': 2.6}
        }
    },
    'Nitrogen': {
        'Dry': {
            'Mild steel, 8mm': {'PM': 23, 'NOx': 5.28},
            'Stainless, 8mm': {'PM': 35, 'NOx': 5.04},
            'Stainless, 35mm': {'PM': 2.6, 'NOx': 7.84}
        },
        'Semi-dry': {
            'Mild steel, 8mm': {'PM': 3, 'NOx': 2.96},
            'Stainless, 8mm': {'PM': 4.1, 'NOx': 2.64},
            'Stainless, 35mm': {'PM': 0.2, 'NOx': 4.16}
        },
        'Wet': {
            'Mild steel, 8mm': {'PM': 0.25, 'NOx': 1.12},
            'Stainless, 8mm': {'PM': 0.35, 'NOx': 1.2},
            'Stainless, 35mm': {'PM': 0.02, 'NOx': 2.08}
        }
    }
}

# === Sandblasting Emission Factors ===

sandblasting_factors = pd.DataFrame({
    "Wind Speed": ["5 mph", "5 mph", "5 mph", "10 mph", "10 mph", "10 mph", "15 mph", "15 mph", "15 mph"],
    "Surface Type": ["Precleaned", "Painted", "Oxidized", "Precleaned", "Painted", "Oxidized", "Precleaned", "Painted", "Oxidized"],
    "Emission Factor (kg/kg sand)": [29, 27, 25, 68, 70, 26, 92, 91, 89]
})

# === Coating Emission Factors ===
coating_emission_factors = {
    "Conveyor Single Flow": 0.00694,
    "Conveyor Dip": 0.00694,
    "Conveyor Single Spray": 0.0125,
    "Conveyor Two-Coat, Flow and Spray": 0.01944,
    "Conveyor Two-Coat, Dip and Spray": 0.01944,
    "Conveyor Two-Coat, Spray": 0.025,
    "Manual Two-Coat, Spray and Air Dry": 0.02494
}

# === Engine Construction Emission Factors ===
engine_emission_factors = {
    "CO2": 84827,
    "CO": 183,
    "CH4": 104,
    "NOx": 270,
    "PM": 29,
    "SOx": 557,
    "NMVOC": 18
}

# === Combined Emissions Initialization ===
combined_emissions = {
    "CO2": 0,
    "CO": 0,
    "CH4": 0,
    "NOx": 0,
    "PM": 0,
    "SOx": 0,
    "VOC": 0,
    "NMVOC": 0
}

# === UI ===

st.title("Steel Shipbuilding Emissions Calculator")

# --- Steel Production Phase ---
st.header("Production Phase")
steel_weight = st.number_input("Enter steel weight of the ship (kg):", min_value=0, step=1000)

# Production emissions
production_emissions = {
    gas: round(ef * steel_weight, 2)
    for gas, ef in production_factors.items()
}
# Add Steel Production emissions to the combined totals
for gas, value in production_emissions.items():
    combined_emissions[gas] += value  # Add Steel Production emissions to combined emissions

production_df = pd.DataFrame.from_dict(production_emissions, orient='index', columns=["Production Emissions (g)"])
production_df.index.name = "Emission Type"

# Display Production Results and Chart
st.subheader("Production Emissions")
st.dataframe(production_df)

production_chart = alt.Chart(production_df.reset_index()).mark_bar(size=40).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Production Emissions (g)", title="Emissions (g)"),
    tooltip=["Emission Type", "Production Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="Production Emissions by Gas"
)

st.altair_chart(production_chart, use_container_width=True)

# --- Welding Phase ---
st.header("Welding Phase")
method = st.selectbox("Select Welding Method", list(grouped_welding_dict.keys()))
electrodes = list(grouped_welding_dict[method].keys())
selected_electrode = st.selectbox("Select Electrode Type", electrodes)
electrode_kg = st.number_input("Enter electrode mass consumed (kg):", min_value=0.0, step=1.0)

# Welding emissions (PM only)
pm_from_welding = round(grouped_welding_dict[method][selected_electrode] * electrode_kg, 2)
welding_df = pd.DataFrame({
    "Emission Type": [f"PM ({method})"],
    "Welding Emissions (g)": [pm_from_welding]
}).set_index("Emission Type")

# Add PM from Welding to combined emissions
combined_emissions["PM"] += pm_from_welding

# Display Welding Results and Chart
st.subheader("Welding Emissions")
st.dataframe(welding_df)

welding_chart = alt.Chart(welding_df.reset_index()).mark_bar(size=60).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Welding Emissions (g)", title="PM Emissions (g)"),
    tooltip=["Emission Type", "Welding Emissions (g)"]
).properties(
    width=400,
    height=300,
    title="Welding PM Emissions"
)

st.altair_chart(welding_chart, use_container_width=True)

# --- Plasma Cutting Phase ---
st.header("Plasma Cutting Phase")

# Plasma Gas Selection
plasma_gas = st.selectbox("Select Plasma Gas", ['Air', 'Oxygen', 'Nitrogen'])

# Cutting Method Selection
cutting_method = st.selectbox("Select Cutting Method", ['Dry', 'Semi-dry', 'Wet'])

# Steel Thickness Selection
steel_thickness = st.selectbox("Select Steel Thickness", ['Mild steel, 8mm', 'Stainless, 8mm', 'Stainless, 35mm'])

# Cutting Duration Input
cutting_duration = st.number_input("Enter Cutting Duration (minutes):", min_value=0, step=1)

# === Emissions Calculation for Plasma Cutting ===
# Get the emission factors based on selections
pm_factor = emission_factors[plasma_gas][cutting_method][steel_thickness]['PM']
nox_factor = emission_factors[plasma_gas][cutting_method][steel_thickness]['NOx']

# Calculate emissions based on duration
pm_emissions = pm_factor * cutting_duration
nox_emissions = nox_factor * cutting_duration

# Add PM and NOx from Plasma Cutting to combined emissions
combined_emissions["PM"] += pm_emissions
combined_emissions["NOx"] += nox_emissions

# Display Plasma Cutting Results and Chart
st.subheader("Emissions from Plasma Cutting")
st.markdown(f"- **Metal Fumes (PM)**: {pm_emissions:.2f} grams")
st.markdown(f"- **NOₓ**: {nox_emissions:.2f} grams")

# Displaying the results as a dataframe
emissions_df = pd.DataFrame({
    "Emission Type": ["Metal Fumes (PM)", "NOₓ"],
    "Emissions (g)": [pm_emissions, nox_emissions]
})
st.dataframe(emissions_df)

# Altair chart for visualizing emissions
emissions_chart = alt.Chart(emissions_df).mark_bar(size=40).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Emissions (g)", title="Emissions (g)"),
    tooltip=["Emission Type", "Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="Plasma Cutting Emissions"
)

st.altair_chart(emissions_chart, use_container_width=True)

# --- Coating Process ---
st.header("Coating Process")

# Coating method selection
coating_method = st.selectbox("Select the Coating Method", list(coating_emission_factors.keys()))

# Surface area unit toggle
area_unit = st.radio("Surface area unit:", ("ft²", "m²"))
if area_unit == "ft²":
    surface_area_input = st.number_input("Enter the surface area covered by coating (ft²):", min_value=0.0, step=1.0)
    surface_area = surface_area_input
else:
    surface_area_input = st.number_input("Enter the surface area covered by coating (m²):", min_value=0.0, step=0.1)
    # convert m² to ft² for calculation
    surface_area = surface_area_input / 0.092903  

# Calculate VOC emissions (g)
if surface_area > 0:
    emission_factor = coating_emission_factors[coating_method]
    voc_emissions = emission_factor * surface_area
else:
    voc_emissions = 0

# Add VOC emissions from Coating to combined emissions
combined_emissions["VOC"] += voc_emissions

# Display the results
st.subheader("VOC Emissions from Coating")
st.markdown(f"- **VOC Emissions (g)**: {voc_emissions:.2f} grams")

# DataFrame and Chart for Coating
coating_df = pd.DataFrame({
    "Emission Type": ["VOC Emissions"],
    "Emissions (g)": [voc_emissions]
})
st.dataframe(coating_df)

coating_chart = alt.Chart(coating_df).mark_bar(size=40).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Emissions (g)", title="Emissions (g)"),
    tooltip=["Emission Type", "Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="VOC Emissions from Coating"
)

st.altair_chart(coating_chart, use_container_width=True)


# --- Sandblasting Phase ---
st.header("Sandblasting Phase")

# User Inputs: Wind Speed, Surface Type, and Sand Used
wind_speed = st.selectbox("Select Wind Speed", ["5 mph", "10 mph", "15 mph"])
surface_type = st.selectbox("Select Surface Type", ["Precleaned", "Painted", "Oxidized"])
sand_used = st.number_input("Enter amount of sand used (kg):", min_value=0.0, step=1.0)

# Get the emission factor based on the selected wind speed and surface type
selected_factor = sandblasting_factors[
    (sandblasting_factors["Wind Speed"] == wind_speed) & 
    (sandblasting_factors["Surface Type"] == surface_type)
]["Emission Factor (kg/kg sand)"].values[0]

# Calculate PM emissions from Sandblasting
pm_sandblasting = selected_factor * sand_used

# Add PM from Sandblasting to combined emissions
combined_emissions["PM"] += pm_sandblasting

# Display Sandblasting Results and Chart
st.subheader("Emissions from Sandblasting")
st.markdown(f"- **Metal Fumes (PM)**: {pm_sandblasting:.2f} grams")

# Displaying the results as a dataframe
sandblasting_df_result = pd.DataFrame({
    "Emission Type": ["Metal Fumes (PM)"],
    "Emissions (g)": [pm_sandblasting]
})
st.dataframe(sandblasting_df_result)

# Altair chart for visualizing emissions
sandblasting_chart = alt.Chart(sandblasting_df_result).mark_bar(size=40).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Emissions (g)", title="Emissions (g)"),
    tooltip=["Emission Type", "Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="Sandblasting Emissions"
)

st.altair_chart(sandblasting_chart, use_container_width=True)


# --- Shop Test Engine Phase ---
st.header("Shop Test Engine Phase")

# Emission factors per kg fuel (from Excel)
shop_test_factors_main = {
    "CO2": 3114,
    "CO": 2.77,
    "CH4": 0.06,
    "NOx": 90.3,
    "PM": 7.28,
    "SOx": 49.08,
    "NMVOC": 3.08
}

shop_test_factors_aux = {
    "CO2": 3206,
    "CO": 3.84,
    "CH4": 0.6,
    # NOx and SOx not provided in Excel for MGO
    "PM": 0.04,
    "NMVOC": 1.75
}

# --- Inputs for Main Engine ---
num_main_engines = st.number_input("Number of Main Engines:", min_value=0, step=1)
main_engine_power = st.number_input("Power per Main Engine (kW):", min_value=0.0, step=10.0)

# --- Inputs for Auxiliary Engine ---
num_aux_engines = st.number_input("Number of Auxiliary Engines:", min_value=0, step=1)
aux_engine_power = st.number_input("Power per Auxiliary Engine (kW):", min_value=0.0, step=10.0)

# Fuel use per kW (as given)
fuel_per_kw_main = 1.886
fuel_per_kw_aux = 0.35

# Calculate total fuel used
total_fuel_main = num_main_engines * main_engine_power * fuel_per_kw_main
total_fuel_aux = num_aux_engines * aux_engine_power * fuel_per_kw_aux

# Calculate emissions
total_shop_test_emissions = {}
for gas in set(shop_test_factors_main) | set(shop_test_factors_aux):
    main_emission = shop_test_factors_main.get(gas, 0) * total_fuel_main
    aux_emission = shop_test_factors_aux.get(gas, 0) * total_fuel_aux
    total_emission = main_emission + aux_emission
    total_shop_test_emissions[gas] = total_emission
    combined_emissions[gas] += total_emission

# Display results
st.subheader("Shop Test Engine Emissions")
shop_test_df = pd.DataFrame.from_dict(total_shop_test_emissions, orient='index', columns=["Emissions (g)"])
shop_test_df.index.name = "Emission Type"
st.dataframe(shop_test_df)

# Chart
shop_test_chart = alt.Chart(shop_test_df.reset_index()).mark_bar(size=40).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Emissions (g)", title="Emissions (g)"),
    tooltip=["Emission Type", "Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="Shop Test Engine Emissions"
)

st.altair_chart(shop_test_chart, use_container_width=True)

# === Engine Construction Phase ===
st.header("Engine Construction Phase")

# Power input for the engine (in kW)
power = st.number_input("Enter the engine power (kW):", min_value=0.0, step=1.0)

# Calculate emissions for Engine Construction based on Power (kW)
if power > 0:
    engine_emissions = {gas: engine_emission_factors[gas] * power for gas in engine_emission_factors}
else:
    engine_emissions = {gas: 0 for gas in engine_emission_factors}

# Add Engine Construction emissions to combined emissions
for gas, emission in engine_emissions.items():
    combined_emissions[gas] += emission

# Display the results for Engine Construction
st.subheader("Engine Construction Emissions")
engine_df = pd.DataFrame(list(engine_emissions.items()), columns=["Emission Type", "Emissions (g)"])
st.dataframe(engine_df)

# Create a bar chart for Engine Construction Emissions
engine_chart = alt.Chart(engine_df).mark_bar(size=40).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Emissions (g)", title="Emissions (g)"),
    tooltip=["Emission Type", "Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="Engine Construction Emissions"
)

st.altair_chart(engine_chart, use_container_width=True)

# === Update Combined Totals ===
# Display the updated combined totals
st.subheader("Updated Combined Totals")

# Convert combined emissions to DataFrame
total_df = pd.DataFrame.from_dict(combined_emissions, orient='index', columns=["Total Emissions (g)"])
total_df.index.name = "Emission Type"

st.dataframe(total_df)

# Altair chart for all gases
total_chart = alt.Chart(total_df.reset_index()).mark_bar(size=50).encode(
    x=alt.X("Emission Type", title="Emission Type"),
    y=alt.Y("Total Emissions (g)", title="Total Emissions (g)"),
    tooltip=["Emission Type", "Total Emissions (g)"]
).properties(
    width=600,
    height=300,
    title="Total Emissions by Gas Type"
)

st.altair_chart(total_chart, use_container_width=True)

# === Summary of All Emissions ===
st.markdown("### 🧮 Summary of All Emissions")

for gas, value in combined_emissions.items():
    if gas == "CO2":
        st.markdown(f"- **{gas}**: {value:,.0f} g ({value / 1e6:.2f} metric tons)")
    else:
        st.markdown(f"- **{gas}**: {value:,.0f} g")
