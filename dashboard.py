import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Inspeksi K3", layout="wide")

st.title("📊 Dashboard Inspeksi K3")
st.write("Upload file Excel berisi log inspeksi K3 untuk dianalisis.")

# Upload file
uploaded_file = st.file_uploader("📂 Upload File Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)
        # Cari sheet yang kira-kira mengandung data
        sheet_names = list(df.keys())
        st.write(f"📑 Sheet ditemukan: {sheet_names}")

        # Ambil sheet pertama
        df = pd.read_excel(uploaded_file, sheet_name=sheet_names[0])

        # Normalisasi nama kolom
        df.columns = df.columns.str.strip().str.title()

        # Mapping nama kolom agar fleksibel
        rename_dict = {
            "Perusahaan": "Tenant",
            "Nama Tenant": "Tenant",
            "Company": "Tenant",
            "Tahun Inspeksi": "Tahun",
            "Year": "Tahun",
            "Bulan Inspeksi": "Bulan",
            "Month": "Bulan",
            "Objek K3": "Objek",
            "Object": "Objek",
            "Jumlah Temuan": "Temuan",
            "Finding": "Temuan"
        }
        df = df.rename(columns=rename_dict)

        required_columns = ["Tenant", "Tahun", "Bulan", "Objek", "Temuan"]

        if not all(col in df.columns for col in required_columns):
            st.error(f"File harus mengandung kolom: {required_columns}")
            st.stop()

        # Sidebar filter
        st.sidebar.header("🔎 Filter Data")
        tenant = st.sidebar.multiselect("Pilih Tenant", df["Tenant"].unique())
        tahun = st.sidebar.multiselect("Pilih Tahun", df["Tahun"].unique())
        bulan = st.sidebar.multiselect("Pilih Bulan", df["Bulan"].unique())

        df_filtered = df.copy()
        if tenant:
            df_filtered = df_filtered[df_filtered["Tenant"].isin(tenant)]
        if tahun:
            df_filtered = df_filtered[df_filtered["Tahun"].isin(tahun)]
        if bulan:
            df_filtered = df_filtered[df_filtered["Bulan"].isin(bulan)]

        # Statistik ringkas
        st.subheader("📌 Ringkasan Data")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tenant", df_filtered["Tenant"].nunique())
        col2.metric("Total Objek", df_filtered["Objek"].nunique())
        col3.metric("Total Temuan", int(df_filtered["Temuan"].sum()))

        # Grafik
        st.subheader("📈 Grafik Analisis")
        tab1, tab2, tab3 = st.tabs(["Temuan per Tenant", "Temuan per Objek", "Tren Bulanan"])

        with tab1:
            fig1 = px.bar(df_filtered.groupby("Tenant")["Temuan"].sum().reset_index(),
                          x="Tenant", y="Temuan", title="Temuan per Tenant",
                          text_auto=True, color="Tenant")
            st.plotly_chart(fig1, use_container_width=True)

        with tab2:
            fig2 = px.bar(df_filtered.groupby("Objek")["Temuan"].sum().reset_index(),
                          x="Objek", y="Temuan", title="Temuan per Objek",
                          text_auto=True, color="Objek")
            st.plotly_chart(fig2, use_container_width=True)

        with tab3:
            df_tren = df_filtered.groupby(["Tahun", "Bulan"])["Temuan"].sum().reset_index()
            fig3 = px.line(df_tren, x="Bulan", y="Temuan", color="Tahun", markers=True,
                           title="Tren Bulanan Temuan")
            st.plotly_chart(fig3, use_container_width=True)

        # Data table
        st.subheader("📋 Data Detail")
        st.dataframe(df_filtered)

    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
else:
    st.info("⬆️ Silakan upload file Excel untuk memulai analisis.")

