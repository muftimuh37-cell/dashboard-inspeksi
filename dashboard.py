# dashboard_k3.py
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard K3", layout="wide")

DATA_FILE = "data_k3.csv"

# Load data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    st.warning("Belum ada data. Silakan input terlebih dahulu di form.")
    st.stop()

st.title("Dashboard Temuan K3 - Manajemen")

# Filter berdasarkan bulan atau perusahaan
with st.sidebar:
    st.subheader("Filter")
    bulan_list = sorted(df["Month"].unique())
    bulan_filter = st.multiselect("Bulan", bulan_list, default=bulan_list)
    perusahaan_list = df["Perusahaan/Dept"].unique()
    perusahaan_filter = st.multiselect("Perusahaan/Dept", perusahaan_list, default=perusahaan_list)
    
df_filtered = df[(df["Month"].isin(bulan_filter)) & (df["Perusahaan/Dept"].isin(perusahaan_filter))]

# Grafik Jumlah Temuan per Objek
st.subheader("Jumlah Temuan per Objek")
objek_count = df_filtered.groupby("Objek")["No"].count().reset_index().rename(columns={"No":"Jumlah Temuan"})
st.bar_chart(objek_count.set_index("Objek"))

# Grafik Jumlah Temuan per Kategori
st.subheader("Jumlah Temuan per Kategori")
kategori_count = df_filtered.groupby("KATEGORI")["No"].count().reset_index().rename(columns={"No":"Jumlah Temuan"})
st.bar_chart(kategori_count.set_index("KATEGORI"))

# Grafik Jumlah Temuan per Perusahaan
st.subheader("Jumlah Temuan per Perusahaan / Dept")
perusahaan_count = df_filtered.groupby("Perusahaan/Dept")["No"].count().reset_index().rename(columns={"No":"Jumlah Temuan"})
st.bar_chart(perusahaan_count.set_index("Perusahaan/Dept"))
