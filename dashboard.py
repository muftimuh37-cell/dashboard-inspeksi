import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Inspeksi K3", layout="wide")

st.title("📊 Dashboard Inspeksi K3")

# ============== Upload Data ==============
uploaded_file = st.file_uploader("📂 Upload File Excel", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Pastikan kolom ada
    expected_cols = ["Tenant", "Tahun", "Bulan", "Objek", "Temuan"]
    if not all(col in df.columns for col in expected_cols):
        st.error(f"File harus mengandung kolom: {expected_cols}")
    else:
        # ============== Filter Sidebar ==============
        st.sidebar.header("🔍 Filter Data")

        tenants = st.sidebar.multiselect("Pilih Tenant", df["Tenant"].unique())
        years = st.sidebar.multiselect("Pilih Tahun", df["Tahun"].unique())
        months = st.sidebar.multiselect("Pilih Bulan", df["Bulan"].unique())
        objek = st.sidebar.multiselect("Pilih Objek", df["Objek"].unique())

        df_filtered = df.copy()

        if tenants:
            df_filtered = df_filtered[df_filtered["Tenant"].isin(tenants)]
        if years:
            df_filtered = df_filtered[df_filtered["Tahun"].isin(years)]
        if months:
            df_filtered = df_filtered[df_filtered["Bulan"].isin(months)]
        if objek:
            df_filtered = df_filtered[df_filtered["Objek"].isin(objek)]

        # ============== Summary Card ==============
        st.subheader("📌 Ringkasan Data")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Temuan", int(df_filtered["Temuan"].sum()))
        col2.metric("Jumlah Tenant", df_filtered["Tenant"].nunique())
        col3.metric("Jumlah Objek", df_filtered["Objek"].nunique())

        # ============== Grafik ==============
        st.subheader("📈 Grafik Interaktif")

        tab1, tab2, tab3 = st.tabs(["Per Tenant", "Per Objek", "Per Bulan"])

        with tab1:
            if not df_filtered.empty:
                fig1 = px.bar(df_filtered.groupby("Tenant")["Temuan"].sum().reset_index(),
                              x="Tenant", y="Temuan", color="Tenant",
                              title="Jumlah Temuan per Tenant")
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan.")

        with tab2:
            if not df_filtered.empty:
                fig2 = px.bar(df_filtered.groupby("Objek")["Temuan"].sum().reset_index(),
                              x="Objek", y="Temuan", color="Objek",
                              title="Jumlah Temuan per Objek")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan.")

        with tab3:
            if not df_filtered.empty:
                fig3 = px.line(df_filtered.groupby("Bulan")["Temuan"].sum().reset_index(),
                               x="Bulan", y="Temuan", markers=True,
                               title="Tren Temuan per Bulan")
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.warning("Tidak ada data untuk ditampilkan.")

        # ============== Download Data ==============
        st.subheader("📥 Download Data Hasil Filter")

        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="💾 Download CSV",
            data=convert_df_to_csv(df_filtered),
            file_name="data_temuan.csv",
            mime="text/csv",
        )

else:
    st.info("⬆️ Silakan upload file Excel untuk memulai.")
