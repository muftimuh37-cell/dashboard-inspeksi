import streamlit as st
import pandas as pd
from datetime import date
from io import BytesIO

st.set_page_config(page_title="Input Data Inspeksi K3", layout="wide")

# --- Struktur Kolom Master ---
columns = [
    "No","Date","Month","Area","Objek","Komponen","Kode Alat","Temuan atau Potensi Bahaya",
    "Kategori","Rekomendasi Perbaikan","Due Date","Status","Penanggung Jawab/PIC",
    "Perusahaan/Dept","Inspektor","KET"
]

# --- Inisialisasi Dataframe ---
if "data" not in st.session_state:
    st.session_state["data"] = pd.DataFrame(columns=columns)

st.title("📝 Form Input Data Inspeksi K3")

tenant = st.text_input("Perusahaan / Dept (Tenant)")
area = st.text_input("Area / Lokasi")
inspektor = st.text_input("Nama Inspektor")

tab1, tab2, tab3, tab4 = st.tabs(["PTP", "LISTRIK", "PUBT", "PAA"])

# --- Template form umum ---
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

# --- Tab Input ---
with tab1:
    input_form("PTP", ["Furnace","Rotary Kiln","Rotary Dryer","Diesel Genset",
                       "Grinding Mill","Turbin","Pulverizer","CNC"])

with tab2:
    input_form("LISTRIK", ["LVMDP (Low Voltage Main Distribution Panel)",
                           "Instalasi Penyalur Petir","Transformer"])

with tab3:
    input_form("PUBT", ["Boiler","Pressure Vessel","Bejana Tekan"])

with tab4:
    input_form("PAA", [
        "Conveyor 输送机检查表","Overhead Crane桥式起重机检查表","Tower Crane","Crawler Crane",
        "Scissor Lift","Mixer Truck","Concrete Pump","Fuel Truck","Water Truck","Trailer",
        "Reach Stacker","Borepile","Telescopic Handler","Aerial Boomlift","Bulker Trailer",
        "Chain Block","Telehandler","Passenger Hoist","Stacker & Reclaimer","Excavator Breaker"
    ])

# --- Preview Tabel ---
st.subheader("📋 Rekap Data Inspeksi (Master Sheet)")
st.dataframe(st.session_state["data"])

# --- Export ke Excel ---
def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Finding Log")
    processed_data = output.getvalue()
    return processed_data

if not st.session_state["data"].empty:
    excel_data = convert_df_to_excel(st.session_state["data"])
    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="Finding_Log_Master.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
