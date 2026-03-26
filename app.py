# ─────────────────────────────────────────────────────────────────────────────
# Vihiga Landslide Susceptibility Dashboard
# Directorate of Disaster Management · 2026 Q1
# ─────────────────────────────────────────────────────────────────────────────

import os
import ee
import folium                          # ← plain folium, no python-box dependency
import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium

# ─────────────────────────────────────────────
# PAGE CONFIG
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
        key_data=st.secrets["-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDATLBrAM+pzPSF\n2G7wg1yaKWQPNQEqEyOl2p31bdDTlks+fHES01YAoZAgDmfj9zeVt+vn8EuDL2Nl\nG3Bt41904M6b11blGEqhhY066GjvVf3xPjusEoHxNVSJCygorVbJzjYgMhkC0F+i\n5GnEVoPxu5aeJyAkttOvi1mSAleXMw9VNpLEqaSZcIjiFCj8mi28nDFwFlMcLFTa\nA4WcH6V3Jy28CRPZj93GhwJgLpbwQqRgO5Uy4LXk7iKygT8N1jxgN/ZUaDsrZ9Pc\nmO8KDfLXRl8Um1TdlgsIQ9X4EW+SLjcrIfpKKMJ+opGr5o8/q5wpbDjJQpjsMPSi\n6dUENPwpAgMBAAECggEAA5ytJ6VhQTA/W5BALTZac+7ZGUwGlJK9da0QkH6akI7f\nJPJTcWYU1Hg0a9W5b9fB7IcC4F1sHa+zLz//saC2t0xNtTGrSSxWoogOqg+ZgP1d\ngr2Hg2jple1JhDV4cKMo4SuFar9mJt5hHX8q2WxCmDTM1HWprebdPQviB9MRcB6W\nCnsSKeyfIHfZjk14AGZzYLi5YYQ5e0ZkGbNID3PwvflO6VRCDMr/2dv7NL2v6h36\n7geXAhVZdzJxO3BEulIaDDHHrlftDKK/s4DxL8HqQ5YRujF0WgFBT2CiZKMq6vvd\n4XbORkHPO9dO8ddBuZZ0uk/uRcyhIZz0O/nJMC3VfQKBgQDxvCRKr1SdjRkyceBq\nzYR4zL/d31RC4QuDW7bAfIcZnF4FbQ6NIjdMt49y9rBo7NahH8UcdDx2u2W1Dvnp\nBUT6kuu27wBP24N411alXb2B86JSIfc5dYTdhhrCZ6BrLyaYoUTE9NdIX5+LXttm\nnj34LbADVQYbmO+6Le5f8TaykwKBgQDLpbvX/ksI5rR/ynO7TLqqgMnL7MJFkrTO\n+pTGN+1alfCxo2Aj7JLeqEToeiboYxsbKk+TOUOjfmZw/a37cqm4RzLm/Kzha8z+\nbOXPPx0R9GqWkDzYWPe9s6qvEANOY7LMoxezIvloTyVh+xCn72BD9ByUwZ4+4vAn\nwUy8aYAf0wKBgQCspwvkq8VrodNVTDBVF+R9wv9moJO2ELYAZAjrAgYcLKqahYHX\nG5EToic6nSbySfYhrmdCI2LsCnxiDQhBfhn+PeFNDvbSEp6cOHESOxmXL0PIFapV\nx7HV5mpGX20cINkYOla7tYPtlR6GlIFvkaYBE+CbAKcUHu9ZsmSG8el3MQKBgE4r\nO8NY9Oxhwf8bcvj+JtizvsHsC1YxTf306Y58gTs4Or+0+n5PnMCiznB+Etk40XrH\n7uuQG4pyRlgwx8uw47y8d6l6a9HLU1CF9GBs1XfC3fcVPoW9ALtsb6Pq/ZnlYwhx\nwfMdBacoWi0V9frAQ69R0Ha5K0jwS0a3SAE6bdfJAoGBAIWTonXlHtc1RN0dUI+B\nIX+uxG18Er3R9FttkcmzA+oDbh5JGaK0pASLwKpNBaTJZ+hzzUx8IZX4qs8KOEdt\nSUjhjTpSFAMC8EOk2Fyv0j1lNrLt0LTQuDhXz3DtsOanOq8U4dy9M9GSi6sCGLMo\nxYZ1afQMbZQnaZDOZrIsmIjs\n-----END PRIVATE KEY-----\n"]
    )
    ee.Initialize(credentials)

init_ee()

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
w_slope = st.sidebar.slider("Slope weight",         0.0, 1.0, 0.40, 0.05)
w_ndvi  = st.sidebar.slider("NDVI weight",          0.0, 1.0, 0.20, 0.05)
w_soil  = st.sidebar.slider("Soil Moisture weight", 0.0, 1.0, 0.20, 0.05)
w_prec  = st.sidebar.slider("Precipitation weight", 0.0, 1.0, 0.20, 0.05)
total_w = round(w_slope + w_ndvi + w_soil + w_prec, 2)
if total_w != 1.0:
    st.sidebar.warning(f"Weights sum to {total_w} (should be 1.0)")

# ─────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────
st.title("⚠️ Vihiga Landslide Susceptibility Dashboard")
st.markdown("**Directorate of Disaster Management · 2026 Q1**")

# ─────────────────────────────────────────────
# DATA & MODEL
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner="Computing risk model…")
def build_model(start, end, w_slope, w_ndvi, w_soil, w_prec):
    Vihiga      = ee.FeatureCollection("projects/ee-evanomondi/assets/Vihiga")
    subCounties = ee.FeatureCollection("projects/ee-evanomondi/assets/Sub_Counties")
    AOI         = Vihiga.geometry()

    # DEM & Slope
    dem   = ee.Image("USGS/SRTMGL1_003").clip(AOI)
    slope = ee.Terrain.slope(dem).rename('Slope')

    # Sentinel-2 NDVI
    s2_col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(AOI).filterDate(start, end)
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
              .select(['B8', 'B4']))
    s2 = ee.Image(ee.Algorithms.If(
        s2_col.size().gt(0),
        s2_col.median().clip(AOI),
        ee.Image.constant(0).rename('B8').addBands(ee.Image.constant(0).rename('B4'))
    ))
    ndvi = s2.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # Sentinel-1 Soil Moisture (dB → linear)
    s1_col = (ee.ImageCollection("COPERNICUS/S1_GRD")
              .filterBounds(AOI).filterDate(start, end)
              .filter(ee.Filter.eq('instrumentMode', 'IW'))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
              .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
              .filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
              .select(['VV', 'VH']))

    def compute_sm():
        med    = s1_col.median().clip(AOI)
        vh_lin = ee.Image(10).pow(med.select('VH').divide(10))
        vv_lin = ee.Image(10).pow(med.select('VV').divide(10))
        return vh_lin.divide(vv_lin).rename('SoilMoisture')

    soilMoisture = ee.Image(ee.Algorithms.If(
        s1_col.size().gt(0), compute_sm(),
        ee.Image.constant(0).rename('SoilMoisture')
    ))

    # CHIRPS Precipitation
    precipitation = (ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
                     .filterBounds(AOI).filterDate(start, end)
                     .sum().rename('Precipitation').clip(AOI))

    # Normalise
    normSlope        = slope.divide(60).clamp(0, 1)
    normNDVI         = ndvi.multiply(-1).add(1).clamp(0, 1)
    normSoilMoisture = soilMoisture.clamp(0, 0.5).divide(0.5)
    normPrecip       = precipitation.divide(800).clamp(0, 1)

    # Weighted index
    landslideRisk = (normSlope.multiply(w_slope)
                    .add(normNDVI.multiply(w_ndvi))
                    .add(normSoilMoisture.multiply(w_soil))
                    .add(normPrecip.multiply(w_prec))
                    .rename('LandslideRisk'))

    # Subcounty stats
    features = landslideRisk.reduceRegions(
        collection=subCounties, reducer=ee.Reducer.mean(), scale=100
    ).getInfo()['features']

    if features:
        props      = features[0]['properties']
        name_field = next(
            (k for k in props if k.lower() in ('subcounty','sub_county','name','adm3_en')),
            list(props.keys())[0]
        )
    else:
        name_field = 'name'

    df = pd.DataFrame([{
        "Subcounty": f['properties'].get(name_field, 'Unknown'),
        "Risk":      round(f['properties'].get('mean', 0) or 0, 4),
    } for f in features]).sort_values("Risk", ascending=False)

    mean_risk = (landslideRisk.reduceRegion(
        reducer=ee.Reducer.mean(), geometry=AOI, scale=100
    ).getInfo().get('LandslideRisk', 0) or 0)

    # Pre-fetch EE tile URLs (avoids geemap dependency entirely)
    def tile_url(image, vis):
        token = image.getMapId(vis)
        return f"https://earthengine.googleapis.com/v1/{token['mapid']}/tiles/{{z}}/{{x}}/{{y}}"

    tiles = {
        "Risk":     tile_url(landslideRisk, {'min':0,'max':1,'palette':['1a9641','ffffbf','d7191c']}),
        "Slope":    tile_url(slope,         {'min':0,'max':60,'palette':['f7fcf0','41ab5d','00441b']}),
        "NDVI":     tile_url(ndvi,          {'min':-0.2,'max':0.8,'palette':['d73027','ffffbf','1a9850']}),
        "Rainfall": tile_url(precipitation, {'min':0,'max':800,'palette':['f7fbff','2171b5','08306b']}),
        "Soil":     tile_url(soilMoisture,  {'min':0,'max':0.5,'palette':['fff9c4','4fc3f7','0d47a1']}),
    }

    return {
        "slope": slope, "ndvi": ndvi, "soilMoisture": soilMoisture,
        "precipitation": precipitation, "landslideRisk": landslideRisk,
        "subCounties": subCounties, "df": df,
        "mean_risk": mean_risk, "AOI": AOI, "tiles": tiles,
    }


try:
    ctx = build_model(str(time_start), str(time_end), w_slope, w_ndvi, w_soil, w_prec)
except Exception as e:
    st.error(f"❌ Earth Engine error: {e}")
    st.stop()

# ─────────────────────────────────────────────
# KPI METRICS
# ─────────────────────────────────────────────
def classify_risk(val):
    if val < 0.33:   return "🟢 Low"
    elif val < 0.66: return "🟡 Moderate"
    else:            return "🔴 High"

mean_risk = ctx["mean_risk"]
col1, col2, col3, col4 = st.columns(4)
col1.metric("Mean Risk Score", f"{mean_risk:.3f}")
col2.metric("Risk Class",      classify_risk(mean_risk))
col3.metric("Date Range",      f"{time_start} → {time_end}")
col4.metric("Weight Check",    f"Σ = {total_w:.2f}",
            delta=None if total_w == 1.0 else f"{1.0-total_w:+.2f} off")

st.markdown("---")

# ─────────────────────────────────────────────
# MAP  (plain folium — no python-box dependency)
# ─────────────────────────────────────────────
st.subheader("🗺️ Interactive Risk Map")

m = folium.Map(location=[0.06, 34.72], zoom_start=11, tiles="CartoDB positron")

layer_labels = {
    "Risk": "Landslide Risk", "Slope": "Slope (°)", "NDVI": "NDVI",
    "Rainfall": "Precipitation (mm)", "Soil": "Soil Moisture",
}

for key, label in layer_labels.items():
    if show_layers.get(key):
        folium.TileLayer(
            tiles=ctx["tiles"][key],
            attr="Google Earth Engine",
            name=label,
            overlay=True,
            control=True,
            opacity=0.8,
        ).add_to(m)

folium.LayerControl().add_to(m)
st_folium(m, height=600, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SUBCOUNTY BAR CHART
# ─────────────────────────────────────────────
st.subheader("📊 Subcounty Risk Scores")

df = ctx["df"].copy()
df["Class"] = df["Risk"].apply(lambda v: "High" if v >= 0.66 else ("Moderate" if v >= 0.33 else "Low"))

fig = px.bar(
    df, x="Subcounty", y="Risk", color="Risk",
    color_continuous_scale=["#1a9641","#ffffbf","#d7191c"],
    range_color=[0,1],
    text=df["Risk"].apply(lambda v: f"{v:.3f}"),
    title="Mean Landslide Risk per Subcounty",
    labels={"Risk": "Risk Score (0–1)"},
)
fig.update_traces(textposition="outside")
fig.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)")
fig.add_hline(y=0.33, line_dash="dot", line_color="orange", annotation_text="Moderate threshold")
fig.add_hline(y=0.66, line_dash="dot", line_color="red",    annotation_text="High threshold")
st.plotly_chart(fig, use_container_width=True)

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
            pt     = ee.Geometry.Point([lon, lat])
            values = (ctx["landslideRisk"]
                      .addBands([ctx["slope"], ctx["ndvi"],
                                 ctx["precipitation"], ctx["soilMoisture"]])
                      .reduceRegion(reducer=ee.Reducer.first(), geometry=pt, scale=30)
                      .getInfo())
            if not any(v is not None for v in values.values()):
                st.warning("No data — point may be outside the AOI.")
            else:
                r = values.get("LandslideRisk", 0) or 0
                m2, m3, m4 = st.columns(3)
                m2.metric("Risk Score", f"{r:.3f}")
                m3.metric("Risk Class", classify_risk(r))
                m4.metric("Slope (°)",  f"{values.get('Slope','N/A')}")
                with st.expander("All band values"):
                    st.json(values)
        except Exception as e:
            st.error(f"Inspection failed: {e}")

st.markdown("---")

# ─────────────────────────────────────────────
# EXPORT
# ─────────────────────────────────────────────
st.subheader("📤 Export")

exp_col1, exp_col2 = st.columns([2,1])
exp_desc  = exp_col1.text_input("Export filename", value="Vihiga_LandslideRisk_2026Q1")
exp_scale = exp_col2.selectbox("Resolution (m/px)", [10, 30, 100], index=1)

if st.button("☁️ Export GeoTIFF to Google Drive"):
    with st.spinner("Starting export…"):
        try:
            task = ee.batch.Export.image.toDrive(
                image=ctx["landslideRisk"], description=exp_desc,
                scale=exp_scale, region=ctx["AOI"],
                fileFormat='GeoTIFF', maxPixels=1e13
            )
            task.start()
            st.success("✅ Export started. Check the "
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
