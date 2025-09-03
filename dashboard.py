# k3_dashboard_allinone.py
import streamlit as st
import pandas as pd
import numpy as np
import os
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="K3 Dashboard All-in-One", layout="wide")

DATA_FILE = "data_k3.csv"
PASSWORD_INSPEKTOR = "inspektor123"  # password untuk form input

# Load atau buat DataFrame
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["No","Date","Month","Year","Area","Objek","Komponen","Kode Alat",
                               "Temuan/Potensi Bahaya","KATEGORI","Rekomendasi Perbaikan",
                               "Due Date","Status","PIC","Perusahaan/Dept","Inspektor","KET",
                               "High","Medium","Low","Open","Close"])

# ========================
# Sidebar Menu
# ========================
st.sidebar.title("Menu")
page = st.sidebar.selectbox("Pilih Halaman", ["Dashboard","Form Input Inspektor"])

# ========================
# Form Input Inspektor (Password Protected)
# ========================
if page == "Form Input Inspektor":
    st.title("Form Input Temuan K3 - Inspektor")
    pwd = st.text_input("Masukkan Password Inspektor", type="password")
    if pwd != PASSWORD_INSPEKTOR:
        st.warning("Password salah! Form input hanya untuk inspektor.")
        st.stop()
    
    # Daftar Objek & Sub-Objek
    objects = {
        "PTP": ["Furnace","Rotary Kiln","Rotary Dryer","Diesel Genset","Grinding Mill","Turbin","Pulverizer","CNC"],
        "Listrik": ["LVMDP","Instalasi Penyalur Petir","Transformer"],
        "PUBT": ["Boiler","Pressure Vessel","Bejana Tekan"],
        "PAA": ["Conveyor","Overhead Crane","Tower Crane","Crawler Crane","Scissor Lift","Mixer Truck",
                "Concrete Pump","Fuel Truck","Water Truck","Trailer","Reach Stacker","Borepile",
                "Telescopic Handler","Aerial Boomlift","Bulker Trailer","Chain Block","Telehandler",
                "Passenger Hoist","Stacker & Reclaimer","Excavator Breaker"]
    }
    kategori_list = ["High","Medium","Low"]
    status_list = ["Open","Close"]

    with st.form("input_form"):
        objek_k3 = st.selectbox("Pilih Objek K3", list(objects.keys()))
        komponen = st.selectbox("Pilih Komponen", objects[objek_k3])
        date = st.date_input("Tanggal")
        month = date.month
        year = date.year
        area = st.text_input("Area")
        kode_alat = st.text_input("Kode Alat")
        temuan = st.text_area("Temuan / Potensi Bahaya")
        kategori = st.selectbox("Kategori", kategori_list)
        rekomendasi = st.text_area("Rekomendasi Perbaikan")
        due_date = st.date_input("Due Date")
        status = st.selectbox("Status", status_list)
        pic = st.text_input("Penanggung Jawab / PIC")
        perusahaan = st.text_input("Perusahaan / Dept")
        inspektor = st.text_input("Inspektor")
        ket = st.text_input("Keterangan")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            new_data = pd.DataFrame([{
                "No": len(df)+1,
                "Date": date,
                "Month": month,
                "Year": year,
                "Area": area,
                "Objek": objek_k3,
                "Komponen": komponen,
                "Kode Alat": kode_alat,
                "Temuan/Potensi Bahaya": temuan,
                "KATEGORI": kategori,
                "Rekomendasi Perbaikan": rekomendasi,
                "Due Date": due_date,
                "Status": status,
                "PIC": pic,
                "Perusahaan/Dept": perusahaan,
                "Inspektor": inspektor,
                "KET": ket,
                "High": 1 if kategori=="High" else 0,
                "Medium": 1 if kategori=="Medium" else 0,
                "Low": 1 if kategori=="Low" else 0,
                "Open": 1 if status=="Open" else 0,
                "Close": 1 if status=="Close" else 0
            }])
            df = pd.concat([df,new_data], ignore_index=True)
            df.to_csv(DATA_FILE,index=False)
            st.success("Data berhasil disimpan!")

# ========================
# Dashboard Manajemen
# ========================
elif page == "Dashboard":
    st.title("Dashboard Temuan K3 - Manajemen")

    # Filter Sidebar untuk Dashboard
    st.sidebar.subheader("Filter Dashboard")
    bulan_list = sorted(df["Month"].unique())
    bulan_filter = st.sidebar.multiselect("Bulan", bulan_list, default=bulan_list)

    tahun_list = sorted(df["Year"].unique())
    tahun_filter = st.sidebar.multiselect("Tahun", tahun_list, default=tahun_list)

    perusahaan_list = df["Perusahaan/Dept"].unique()
    perusahaan_filter = st.sidebar.multiselect("Perusahaan/Dept", perusahaan_list, default=perusahaan_list)

    objek_list = df["Objek"].unique()
    objek_filter = st.sidebar.multiselect("Objek K3", objek_list, default=objek_list)

    kategori_list = ["High","Medium","Low"]
    kategori_filter = st.sidebar.multiselect("Kategori", kategori_list, default=kategori_list)

    # Apply filter
    df_filtered = df[
        (df["Month"].isin(bulan_filter)) &
        (df["Year"].isin(tahun_filter)) &
        (df["Perusahaan/Dept"].isin(perusahaan_filter)) &
        (df["Objek"].isin(objek_filter)) &
        (df["KATEGORI"].isin(kategori_filter))
    ]

    # Grafik Jumlah Temuan per Objek
    st.subheader("Jumlah Temuan per Objek")
    if not df_filtered.empty:
        objek_count = df_filtered.groupby("Objek")["No"].count().reset_index().rename(columns={"No":"Jumlah Temuan"})
        chart_objek = alt.Chart(objek_count).mark_bar().encode(
            x="Objek",
            y="Jumlah Temuan",
            tooltip=["Objek","Jumlah Temuan"]
        )
        st.altair_chart(chart_objek, use_container_width=True)

    # Grafik Jumlah Temuan per Kategori
    st.subheader("Jumlah Temuan per Kategori")
    kategori_count = df_filtered.groupby("KATEGORI")["No"].count().reset_index().rename(columns={"No":"Jumlah Temuan"})
    chart_kategori = alt.Chart(kategori_count).mark_bar(color="orange").encode(
        x="KATEGORI",
        y="Jumlah Temuan",
        tooltip=["KATEGORI","Jumlah Temuan"]
    )
    st.altair_chart(chart_kategori, use_container_width=True)

    # Trend Temuan per Bulan
    st.subheader("Trend Temuan per Bulan")
    df_filtered["MonthYear"] = pd.to_datetime(df_filtered["Date"]).dt.to_period("M")
    trend = df_filtered.groupby("MonthYear")["No"].count().reset_index().rename(columns={"No":"Jumlah Temuan"})
    trend["MonthYear"] = trend["MonthYear"].astype(str)
    chart_trend = alt.Chart(trend).mark_line(point=True).encode(
        x="MonthYear",
        y="Jumlah Temuan",
        tooltip=["MonthYear","Jumlah Temuan"]
    )
    st.altair_chart(chart_trend, use_container_width=True)

    # Heatmap Tenant x Objek
    st.subheader("Heatmap Tenant × Objek")
    heatmap_data = df_filtered.pivot_table(index="Perusahaan/Dept", columns="Objek", values="No", aggfunc="count", fill_value=0)
    fig, ax = plt.subplots(figsize=(12,6))
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlOrRd", ax=ax)
    st.pyplot(fig)

    # Tabel Data & Download
    st.subheader("Data Temuan")
    st.dataframe(df_filtered)
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data CSV",
        data=csv,
        file_name='temuan_k3_filtered.csv',
        mime='text/csv',
    )
