import pandas as pd
import streamlit as st
import sqlite3
import io, datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.express as px

DB_PATH = "ocean_data.sqlite"

# Load data
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM profiles", conn)

st.set_page_config(page_title="ARGO Dashboard", layout="wide", page_icon="🌊")
st.title("🌊 ARGO Ocean Data Dashboard")

# --- Sidebar Filters ---
st.sidebar.header("Filters")
depth_filter = st.sidebar.slider("Max Depth (m)", 0, int(df["depth_m"].max()), 500)
lat_min, lat_max = st.sidebar.slider("Latitude Range", -60, 60, (-30, 30))
lon_min, lon_max = st.sidebar.slider("Longitude Range", -180, 180, (-60, 60))

filtered = df[
    (df["depth_m"] <= depth_filter) &
    (df["latitude"].between(lat_min, lat_max)) &
    (df["longitude"].between(lon_min, lon_max))
]

st.subheader("Filtered Data")
st.dataframe(filtered)

# --- Geospatial Visualization ---
st.subheader("🗺️ Float Locations Map")

if not filtered.empty:
    fig = px.scatter_geo(
        filtered,
        lat="latitude",
        lon="longitude",
        color="temperature_C",
        size="current_speed_m_s",
        hover_name="sample_id",
        hover_data={
            "temperature_C": True,
            "salinity_psu": True,
            "density_kg_m3": True,
            "depth_m": True,
        },
        projection="natural earth",
        title="ARGO Float Positions (colored by Temperature, sized by Currents)"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data matches filter criteria.")

# --- Annotations ---
st.subheader("✍️ Collaboration: Annotate Profiles")
sid_anno = st.number_input("Enter sample_id to annotate", min_value=int(df["sample_id"].min()), max_value=int(df["sample_id"].max()))
user = st.text_input("Your name")
note = st.text_area("Your annotation")

if st.button("Save Annotation"):
    if user and note:
        cur = conn.cursor()
        cur.execute("INSERT INTO annotations (sample_id, user, note) VALUES (?, ?, ?)", (int(sid_anno), user, note))
        conn.commit()
        st.success("Annotation saved!")
    else:
        st.warning("Please enter both user and note.")

if st.button("View Annotations for Sample"):
    df_ann = pd.read_sql("SELECT * FROM annotations WHERE sample_id = ?", conn, params=(int(sid_anno),))
    if df_ann.empty:
        st.info("No annotations yet.")
    else:
        st.dataframe(df_ann)

# --- Export Section ---
st.subheader("📤 Export Data")

col1, col2 = st.columns(2)

with col1:
    towrite = io.BytesIO()
    filtered.to_excel(towrite, index=False, engine="openpyxl")
    st.download_button(
        "Download Excel",
        data=towrite.getvalue(),
        file_name="ocean_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col2:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 10)
    text.textLine("Ocean Data Export")
    text.textLine(str(datetime.datetime.now()))
    text.textLine("")
    for i, row in filtered.head(20).iterrows():
        text.textLine(str(row.to_dict()))
    c.drawText(text)
    c.save()
    st.download_button(
        "Download PDF",
        data=buf.getvalue(),
        file_name="ocean_filtered.pdf",
        mime="application/pdf"
    )
