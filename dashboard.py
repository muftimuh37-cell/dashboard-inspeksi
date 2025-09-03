import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO
import plotly.express as px

st.set_page_config(page_title="Dashboard Inspeksi K3", layout="wide")

# ----------------------------
# Struktur kolom master data
# ----------------------------
columns = [
    "No","Date","Month","Area","Objek","Komponen","Kode Alat","Temuan atau Potensi Bahaya",
    "Kategori","Rekomendasi Perbaikan","Due Date","Status","Penanggung Jawab/PIC",
    "Perusahaan/Dept","Inspektor","KET"
]

# Inisialisasi data
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=columns)

st.title("📊 Dashboard & Input Data Inspeksi K3")

# ============================
# Tab Menu
# ============================
tab1, tab2 = st.tabs(["📝 Input Data", "📈 Dashboard"])

# ----------------------------
# TAB 1: Input Data
# ----------------------------
with tab1:
    st.header("📝 Form Input Data Inspeksi")

    tenant = st.text_input("Perusahaan / Dept (Tenant)")
    area = st.text_input("Area / Lokasi")
    inspektor = st.text_input("Nama Inspektor")

    kategori_tabs = st.tabs(["PTP", "LISTRIK", "PUBT", "PAA"])

    def input_form(kategori, objek_list):
        with st.form(f"form_{kategori}"):
            today = date.today()
            tanggal = st.date_input("Tanggal Inspeksi", today)
            month = tanggal.month
            objek = st.selectbox(f"Objek {kategori}", objek_list)
            komponen = st.text_input("Komponen")
            kode_alat = st.text_input("Kode Alat")
            temuan = st.text_area("Temuan atau Potensi Bahaya")
            level = st.radio("Kategori Temuan", ["High","Medium","Low"])
            rekom = st.text_area("Rekomendasi Perbaikan")
            due_date = st.date_input("Due Date")
            status = st.radio("Status", ["Open","Close"])
            pic = st.text_input("Penanggung Jawab / PIC")
            ket = st.text_area("Keterangan tambahan")

            submitted = st.form_submit_button("💾 Simpan Data")
            if submitted:
                no = len(st.session_state["data"]) + 1
                new_row = pd.DataFrame([[
                    no, tanggal, month, area, objek, komponen, kode_alat, temuan,
                    level, rekom, due_date, status, pic, tenant, inspektor, ket
                ]], columns=columns)
                st.session_state["data"] = pd.concat([st.session_state["data"], new_row], ignore_index=True)
                st.success("✅ Data berhasil disimpan!")

    with kategori_tabs[0]:
        input_form("PTP", ["Furnace","Rotary Kiln","Rotary Dryer","Diesel Genset",
                           "Grinding Mill","Turbin","Pulverizer","CNC"])
    with kategori_tabs[1]:
        input_form("LISTRIK", ["LVMDP (Low Voltage Main Distribution Panel)",
                               "Instalasi Penyalur Petir","Transformer"])
    with kategori_tabs[2]:
        input_form("PUBT", ["Boiler","Pressure Vessel","Bejana Tekan"])
    with kategori_tabs[3]:
        input_form("PAA", [
            "Conveyor 输送机检查表","Overhead Crane桥式起重机检查表","Tower Crane","Crawler Crane",
            "Scissor Lift","Mixer Truck","Concrete Pump","Fuel Truck","Water Truck","Trailer",
            "Reach Stacker","Borepile","Telescopic Handler","Aerial Boomlift","Bulker Trailer",
            "Chain Block","Telehandler","Passenger Hoist","Stacker & Reclaimer","Excavator Breaker"
        ])

    # Preview tabel
    st.subheader("📋 Rekap Data Inspeksi (Finding Log)")
    st.dataframe(st.session_state["data"])

    # Export Excel
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Finding Log")
        return output.getvalue()

    if not st.session_state["data"].empty:
        excel_data = convert_df_to_excel(st.session_state["data"])
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="Finding_Log_Master.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ----------------------------
# TAB 2: Dashboard Grafik
# ----------------------------
with tab2:
    st.header("📈 Dashboard Analisis Temuan Inspeksi")

    if st.session_state["data"].empty:
        st.warning("⚠️ Belum ada data! Silakan isi data terlebih dahulu di tab Input Data.")
    else:
        df = st.session_state["data"].copy()

        # Agregasi untuk grafik
        df_summary = df.groupby(["Perusahaan/Dept","Month","Objek"]).size().reset_index(name="Jumlah Temuan")

        # Filter
        tenant_filter = st.multiselect("Pilih Tenant", df_summary["Perusahaan/Dept"].unique(), default=list(df_summary["Perusahaan/Dept"].unique()))
        bulan_filter = st.multiselect("Pilih Bulan", sorted(df_summary["Month"].unique()), default=sorted(df_summary["Month"].unique()))

        df_filtered = df_summary[
            (df_summary["Perusahaan/Dept"].isin(tenant_filter)) &
            (df_summary["Month"].isin(bulan_filter))
        ]

        # Grafik Temuan per Tenant
        st.subheader("📊 Jumlah Temuan per Tenant")
        fig1 = px.bar(df_filtered, x="Perusahaan/Dept", y="Jumlah Temuan", color="Objek", barmode="stack")
        st.plotly_chart(fig1, use_container_width=True)

        # Grafik Tren per Bulan
        st.subheader("📈 Tren Temuan per Bulan")
        fig2 = px.line(df_filtered, x="Month", y="Jumlah Temuan", color="Perusahaan/Dept", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Grafik Pie per Objek
        st.subheader("🥧 Distribusi Temuan per Objek")
        fig3 = px.pie(df_filtered, names="Objek", values="Jumlah Temuan")
        st.plotly_chart(fig3, use_container_width=True)
