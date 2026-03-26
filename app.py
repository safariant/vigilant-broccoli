# ─────────────────────────────────────────────────────────────────────────────
# Vihiga Landslide Susceptibility Dashboard
# Directorate of Disaster Management · 2026 Q1
#
# Run:  streamlit run app.py
# Env:  NGROK_TOKEN=<your_token>  (optional, for tunnelling)
#       EE_PROJECT=ee-evanomondi   (optional override)
# ─────────────────────────────────────────────────────────────────────────────

import os
import ee
import geemap.foliumap as geemap
import streamlit as st
import pandas as pd
import plotly.express as px

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Vihiga Landslide Dashboard",
    page_icon="⚠️",
    layout="wide",
)

# ─────────────────────────────────────────────
# EARTH ENGINE INITIALISATION
# ─────────────────────────────────────────────
@st.cache_resource
def init_ee():
    credentials = ee.ServiceAccountCredentials(
        email=st.secrets["geospatial-service-account@ee-evanomondi.iam.gserviceaccount.com"],
        key_data=st.secrets["-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCxaUfCqhn8a+/9\nZbIq2wYFOELdzNTcuF11P1cmt4nFZ/UuIb8oMPlrY40THgNi16UaPcVw941M6sVa\ntxcLeoCVFWYWDYUok+jqeoV3x+/PdrV8+xTrZ/cQijpmh3/baCpjtt3AR6ENCFOu\nHW2AJenhNPwLVx1R40Q/M1S2wBIu3vH6eJwIbYWvk/ba+TYued144B3khz9sQG+1\nyT88oys+Du8Cb8TNcIEifICv+y89J+pbS2jShiN42MMsYzmTSIu+2ySQPc+sCMS2\njEbhmw1uFHehnEgUyN1WSSmWiqnCNDPDAwQvGFOzWQJ6frC4aZYYrGSbG3dYBxCM\n4USpmwU9AgMBAAECggEADofrf0Jpx3bbHMZQGK+A0jugn8RvqOEW5+FiFNiSmbnL\n51U58COhbON7V2tYEVKirMAOJGm6R+hbdXR/7YpBRDS7pvxrgX5/5M4CkY7YPFti\nPmmIS0cO1urOIWi2wbSfSDSJptPsboIAl0caGWrBjxcaZR65AY8w9KY9KYzDeyrX\nmI304vHPAFN7aMcwkatvo6w+5BGNloJErbiklsHYPriessNKSKxsFGgdcCxfyOVX\nILx4l4PXfnjR81n2UPDqxOuLcduE59DBEoASqLeXLcBB0A1WpT/a9HS1FpntQEX3\nOMpV6Kyot++4wHqWVAZ+wZfUC8nXWteINBTzqCXNcQKBgQDiXa7+ejMoDQZ5Tovc\nFxnGnMqaHkYI7X7fk5hnTLCEFe/UdT3X7ha+1t9xSsvtAcbPLP2lqUCG9P0OPBov\nGg4NVpyLVl4oRn+NwSIBAUlhZGuRvirJdLJhMDmS/vVTlycUypWF3gdWHz8U7+Ml\n6Q6z9eDj4fsmk/L9EX35eHQiWQKBgQDIovQCD+pr53nER00zAcNN/mthV5LKJytp\nzlV0rh7xPgjDm4ryelqjGveDs3igSmFZ+JUf/k4Xk3JBsygsaSEivnSt34orlNy4\nSzaRWaBYF6T13cLGfgMg3DoKHjUwi8Jfa9SXypjSLsJ8CLgyt+pFMeSpUaYlmrYh\nMBdrytb1hQKBgHgiWgXqGo4t43qrqeQjSmWyvn9ug6KnUEcdkKt58tAWyFJL6odX\nbzDW3nzEwldFMxqueOrbWUiGamqMkSTgQgboKWp1asEbMQStM/uukCAk6EXP0+tY\niHa13khaER7MwEvze8kw3VnieVsGONncxxXQ7wph2yVNLY8LIn0sZQ35AoGAcSmX\nvuIDMkEoqNAedrpz0bXCEvE11dcp4U+DW4Ap6581ij5crE7eeEhpelrrmlzZc8mF\nMrpYiWuccfn+mq3hBputa7Q9Vj9sDnY9nNWUXptXa2Vcyl+gnBQamEJZdbweMXu8\nOLEIaOP+xb6VReX9uHFfqzBmKaeNOkLJsv6BJ5ECgYBRM9KC0J8UDQznIqLWk1O7\nUrHxCydsoWFog7puYAS0T8/8IA0EM9ExGVpPonHhPgXXx96/X6O1XIBTrLTb07i8\n7Qy6oifWrSTgx2TRfQpyukts6G7vg3uK4+gHAm3o0+Cq0kwDUGq+yb4HvyXp4VB9\nY2njx4kVvLTIaZOjPuHHrg==\n-----END PRIVATE KEY-----\n"]
    )
    ee.Initialize(credentials)

# ─────────────────────────────────────────────
# SIDEBAR CONTROLS
# ─────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")

time_start = st.sidebar.date_input("Start Date", pd.to_datetime("2025-01-01"))
time_end   = st.sidebar.date_input("End Date",   pd.to_datetime("2026-03-20"))

st.sidebar.markdown("---")
st.sidebar.subheader("Layer Visibility")
show_layers = {
    "Risk":     st.sidebar.checkbox("Landslide Risk",  True),
    "Slope":    st.sidebar.checkbox("Slope",           False),
    "NDVI":     st.sidebar.checkbox("NDVI",            False),
    "Rainfall": st.sidebar.checkbox("Precipitation",   False),
    "Soil":     st.sidebar.checkbox("Soil Moisture",   False),
}

st.sidebar.markdown("---")
st.sidebar.subheader("Model Weights")
w_slope = st.sidebar.slider("Slope weight",          0.0, 1.0, 0.40, 0.05)
w_ndvi  = st.sidebar.slider("NDVI weight",           0.0, 1.0, 0.20, 0.05)
w_soil  = st.sidebar.slider("Soil Moisture weight",  0.0, 1.0, 0.20, 0.05)
w_prec  = st.sidebar.slider("Precipitation weight",  0.0, 1.0, 0.20, 0.05)
total_w = round(w_slope + w_ndvi + w_soil + w_prec, 2)
if total_w != 1.0:
    st.sidebar.warning(f"Weights sum to {total_w} (should be 1.0)")

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.title("⚠️ Vihiga Landslide Susceptibility Dashboard")
st.markdown("**Directorate of Disaster Management · 2026 Q1**")

# ─────────────────────────────────────────────
# DATA & MODEL  (cached – only recomputes when
# date inputs or weights change)
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Computing risk model…")
def build_model(start: str, end: str, w_slope, w_ndvi, w_soil, w_prec):
    """
    Returns EE image objects and a DataFrame of subcounty risk scores.
    All heavy EE work is done here so Streamlit re-runs don't recompute.
    """
    Vihiga      = ee.FeatureCollection("projects/ee-evanomondi/assets/Vihiga")
    subCounties = ee.FeatureCollection("projects/ee-evanomondi/assets/Sub_Counties")
    AOI         = Vihiga.geometry()

    # ── DEM & Slope ──────────────────────────────────────────────────────────
    dem   = ee.Image("USGS/SRTMGL1_003").clip(AOI)
    slope = ee.Terrain.slope(dem).rename('Slope')

    # ── Sentinel-2 NDVI ───────────────────────────────────────────────────────
    s2_col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(AOI)
              .filterDate(start, end)
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
              .select(['B8', 'B4']))

    # Fallback: if no scenes pass filters, use a zero NDVI image
    s2 = ee.Algorithms.If(
        s2_col.size().gt(0),
        s2_col.median().clip(AOI),
        ee.Image.constant(0).rename('B8')
                .addBands(ee.Image.constant(0).rename('B4'))
    )
    s2   = ee.Image(s2)
    ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # ── Sentinel-1 Soil Moisture ─────────────────────────────────────────────
    # FIX: convert dB → linear power before computing the ratio
    s1_col = (ee.ImageCollection("COPERNICUS/S1_GRD")
              .filterBounds(AOI)
              .filterDate(start, end)
              .filter(ee.Filter.eq('instrumentMode', 'IW'))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
              .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
              .select(['VV', 'VH']))

    s1_present = s1_col.size().gt(0)

    def compute_soil_moisture():
        s1_med   = s1_col.median().clip(AOI)
        # dB → linear power: P = 10^(dB/10)
        vh_lin   = ee.Image(10).pow(s1_med.select('VH').divide(10))
        vv_lin   = ee.Image(10).pow(s1_med.select('VV').divide(10))
        # Cross-pol ratio (higher = wetter)
        return vh_lin.divide(vv_lin).rename('SoilMoisture')

    soilMoisture = ee.Image(
        ee.Algorithms.If(s1_present, compute_soil_moisture(),
                         ee.Image.constant(0).rename('SoilMoisture'))
    )

    # ── CHIRPS Precipitation ─────────────────────────────────────────────────
    precipitation = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
                     .filterBounds(AOI)
                     .filterDate(start, end)
                     .sum()
                     .rename('Precipitation')
                     .clip(AOI))

    # ── Normalisation ────────────────────────────────────────────────────────
    # FIX: precipitation cap lowered to 800 mm (realistic for Jan–Mar in Vihiga)
    normSlope         = slope.divide(60).clamp(0, 1)
    normNDVI          = ndvi.multiply(-1).add(1).clamp(0, 1)   # low veg → high risk
    # Cross-pol ratio typically 0–0.5; clamp and rescale to [0,1]
    normSoilMoisture  = soilMoisture.clamp(0, 0.5).divide(0.5)
    normPrecipitation = precipitation.divide(800).clamp(0, 1)

    # ── Weighted Risk Index ───────────────────────────────────────────────────
    landslideRisk = (normSlope.multiply(w_slope)
                    .add(normNDVI.multiply(w_ndvi))
                    .add(normSoilMoisture.multiply(w_soil))
                    .add(normPrecipitation.multiply(w_prec))
                    .rename('LandslideRisk'))

    # ── Subcounty Statistics ─────────────────────────────────────────────────
    subcountyRisk = landslideRisk.reduceRegions(
        collection=subCounties,
        reducer=ee.Reducer.mean(),
        scale=100
    )

    features = subcountyRisk.getInfo()['features']

    # Discover the actual subcounty name field from the first feature
    if features:
        props = features[0]['properties']
        # Common field name variations
        name_field = next(
            (k for k in props if k.lower() in ('subcounty', 'sub_county', 'name', 'adm3_en')),
            list(props.keys())[0]
        )
    else:
        name_field = 'name'

    rows = [
        {
            "Subcounty": f['properties'].get(name_field, 'Unknown'),
            "Risk":      round(f['properties'].get('mean', 0) or 0, 4),
        }
        for f in features
    ]
    df = pd.DataFrame(rows).sort_values("Risk", ascending=False)

    # Mean risk over AOI
    mean_risk = landslideRisk.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=AOI,
        scale=100
    ).getInfo().get('LandslideRisk', 0) or 0

    return {
        "slope":         slope,
        "ndvi":          ndvi,
        "soilMoisture":  soilMoisture,
        "precipitation": precipitation,
        "landslideRisk": landslideRisk,
        "subCounties":   subCounties,
        "df":            df,
        "mean_risk":     mean_risk,
        "AOI":           AOI,
    }


# ── Run model ────────────────────────────────────────────────────────────────
try:
    ctx = build_model(
        str(time_start), str(time_end),
        w_slope, w_ndvi, w_soil, w_prec
    )
except Exception as e:
    st.error(f"❌ Earth Engine error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
def classify_risk(val: float) -> str:
    if val < 0.33:   return "🟢 Low"
    elif val < 0.66: return "🟡 Moderate"
    else:            return "🔴 High"

mean_risk = ctx["mean_risk"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean Risk Score",   f"{mean_risk:.3f}")
col2.metric("Risk Class",        classify_risk(mean_risk))
col3.metric("Date Range",        f"{time_start} → {time_end}")
col4.metric("Weight Check",      f"Σ = {total_w:.2f}", delta=None if total_w == 1.0 else f"{1.0 - total_w:+.2f} off")

st.markdown("---")

# ─────────────────────────────────────────────
# MAP
# ─────────────────────────────────────────────
st.subheader("🗺️ Interactive Risk Map")

m = geemap.Map(center=[0.06, 34.72], zoom=11)

vis = {
    "Risk":     (ctx["landslideRisk"], {'min': 0, 'max': 1,    'palette': ['1a9641','ffffbf','d7191c']}, 'Landslide Risk'),
    "Slope":    (ctx["slope"],         {'min': 0, 'max': 60,   'palette': ['f7fcf0','41ab5d','00441b']}, 'Slope (°)'),
    "NDVI":     (ctx["ndvi"],          {'min':-0.2,'max': 0.8, 'palette': ['d73027','ffffbf','1a9850']}, 'NDVI'),
    "Rainfall": (ctx["precipitation"], {'min': 0, 'max': 800,  'palette': ['f7fbff','2171b5','08306b']}, 'Precipitation (mm)'),
    "Soil":     (ctx["soilMoisture"],  {'min': 0, 'max': 0.5,  'palette': ['fff9c4','4fc3f7','0d47a1']}, 'Soil Moisture'),
}

for key, (img, params, label) in vis.items():
    if show_layers.get(key):
        m.addLayer(img, params, label)

m.addLayer(ctx["subCounties"], {}, 'Subcounties')
m.to_streamlit(height=600)

st.markdown("---")

# ─────────────────────────────────────────────
# SUBCOUNTY BAR CHART
# ─────────────────────────────────────────────
st.subheader("📊 Subcounty Risk Scores")

df = ctx["df"].copy()
df["Class"] = df["Risk"].apply(lambda v: "High" if v >= 0.66 else ("Moderate" if v >= 0.33 else "Low"))

fig = px.bar(
    df,
    x="Subcounty",
    y="Risk",
    color="Risk",
    color_continuous_scale=["#1a9641", "#ffffbf", "#d7191c"],
    range_color=[0, 1],
    text=df["Risk"].apply(lambda v: f"{v:.3f}"),
    title="Mean Landslide Risk per Subcounty",
    labels={"Risk": "Risk Score (0–1)"},
)
fig.update_traces(textposition="outside")
fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)")
fig.add_hline(y=0.33, line_dash="dot", line_color="orange",  annotation_text="Moderate threshold")
fig.add_hline(y=0.66, line_dash="dot", line_color="red",     annotation_text="High threshold")

st.plotly_chart(fig, use_container_width=True)

# Sortable data table
with st.expander("📋 View data table"):
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# POINT INSPECTOR
# ─────────────────────────────────────────────
st.subheader("📍 Point Inspector")

pi_col1, pi_col2 = st.columns(2)
lon = pi_col1.number_input("Longitude", value=34.72, format="%.5f")
lat = pi_col2.number_input("Latitude",  value=0.06,  format="%.5f")

if st.button("🔍 Inspect Point"):
    with st.spinner("Sampling point…"):
        try:
            pt = ee.Geometry.Point([lon, lat])
            values = (ctx["landslideRisk"]
                      .addBands([ctx["slope"], ctx["ndvi"],
                                 ctx["precipitation"], ctx["soilMoisture"]])
                      .reduceRegion(
                          reducer=ee.Reducer.first(),
                          geometry=pt,
                          scale=30
                      ).getInfo())

            if not any(v is not None for v in values.values()):
                st.warning("No data at this location — the point may be outside the AOI.")
            else:
                r = values.get("LandslideRisk", 0) or 0
                m2, m3, m4 = st.columns(3)
                m2.metric("Risk Score",   f"{r:.3f}")
                m3.metric("Risk Class",   classify_risk(r))
                m4.metric("Slope (°)",    f"{values.get('Slope', 'N/A')}")

                with st.expander("All band values"):
                    st.json(values)
        except Exception as e:
            st.error(f"Inspection failed: {e}")

st.markdown("---")

# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────
st.subheader("📤 Export")

exp_col1, exp_col2 = st.columns([2, 1])
exp_desc = exp_col1.text_input("Export filename (no extension)",
                               value="Vihiga_LandslideRisk_2026Q1")
exp_scale = exp_col2.selectbox("Resolution (m/px)", [10, 30, 100], index=1)

if st.button("☁️ Export GeoTIFF to Google Drive"):
    with st.spinner("Starting Earth Engine export task…"):
        try:
            task = ee.batch.Export.image.toDrive(
                image=ctx["landslideRisk"],
                description=exp_desc,
                scale=exp_scale,
                region=ctx["AOI"],
                fileFormat='GeoTIFF',
                maxPixels=1e13
            )
            task.start()
            st.success("✅ Export started. Monitor progress in the "
                       "[Earth Engine Tasks panel](https://code.earthengine.google.com/tasks).")
        except Exception as e:
            st.error(f"Export failed: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Data sources: Sentinel-1/2 (ESA Copernicus) · SRTM DEM (USGS) · "
    "CHIRPS Daily (UCSB-CHG). Model: normalised weighted index. "
    "Not a substitute for field surveys."
)
