import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Inspeksi K3", layout="wide")

st.title("Dashboard Inspeksi K3")

uploaded_file = st.file_uploader("Upload file Excel Finding Log", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Data 2", header=2)
        df = df.dropna(how="all")

        # tampilkan semua kolom asli
        st.write("Kolom yang ditemukan di file:", df.columns.tolist())

        # rename agar seragam
        df = df.rename(columns={
            "Perusahaan": "Tenant",
            "Objek K3": "Objek",
            "Bulan": "Bulan",
            "Jumlah Temuan": "Temuan"
        })

        st.success("Data berhasil dimuat!")

        tenant = st.sidebar.multiselect(
            "Pilih Tenant",
            df["Tenant"].dropna().unique(),
            default=df["Tenant"].dropna().unique()
        )
        bulan = st.sidebar.multiselect(
            "Pilih Bulan",
            df["Bulan"].dropna().unique(),
            default=df["Bulan"].dropna().unique()
        )

        df_filtered = df[(df["Tenant"].isin(Smelter)) & (df["Bulan"].isin(bulan))]

        if not df_filtered.empty:
            fig = px.bar(df_filtered, x="Objek", y="Temuan", color="Tenant",
                         barmode="group", title="Jumlah Temuan per Objek")
            st.plotly_chart(fig, use_container_width=True)

            pivot_table = df_filtered.pivot_table(index="Objek", columns="Tenant",
                                                  values="Temuan", aggfunc="sum", fill_value=0)
            st.write("Heatmap Tenant vs Objek")
            fig2 = px.imshow(pivot_table, text_auto=True, aspect="auto", color_continuous_scale="Reds")
            st.plotly_chart(fig2, use_container_width=True)

        st.write("Data Temuan Detail")
        st.dataframe(df_filtered, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal membaca file: {e}")

else:
    st.info("Silakan upload file Excel untuk melihat dashboard.")
