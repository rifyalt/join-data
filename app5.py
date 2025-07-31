import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Dashboard Join & Filter", layout="wide")

st.title("📊 Dashboard Join & Filter - 4 Source + 1 Acuan")

# Sidebar Filter
st.sidebar.header("🔍 Filter Periode Berdasarkan Check-In & Check-Out")
start_date = st.sidebar.date_input("Tanggal Mulai", None)
end_date = st.sidebar.date_input("Tanggal Selesai", None)

# Upload data sumber (opsional)
st.header("📁 Upload Data Sumber (Opsional, Maks. 4)")
data1 = st.file_uploader("Upload Data Sumber 1", type=["csv", "xlsx"])
data2 = st.file_uploader("Upload Data Sumber 2", type=["csv", "xlsx"])
data3 = st.file_uploader("Upload Data Sumber 3", type=["csv", "xlsx"])
data4 = st.file_uploader("Upload Data Sumber 4", type=["csv", "xlsx"])

st.markdown("---")

# Upload data acuan (wajib)
st.header("📌 Upload Data Acuan (WAJIB)")
data_ref = st.file_uploader("Upload Data Acuan untuk Join", type=["csv", "xlsx"])

primer_key = st.text_input("🔑 Masukkan nama kolom Primer Key (harus sama di semua data):")

# Fungsi untuk membaca file
def read_file(file):
    if file is None:
        return None
    if file.name.endswith(".csv"):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

# Fungsi untuk ekspor ke Excel (tanpa writer.save())
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Proses utama
if data_ref and primer_key:
    df_ref = read_file(data_ref)
    list_data = [read_file(f) for f in [data1, data2, data3, data4] if f is not None]

    if not list_data:
        st.warning("⚠️ Tidak ada file sumber yang diunggah.")
    else:
        try:
            # Join semua data sumber
            df_joined = list_data[0]
            for df in list_data[1:]:
                df_joined = pd.merge(df_joined, df, on=primer_key, how='inner')

            # Join dengan data acuan
            df_final = pd.merge(df_joined, df_ref, on=primer_key, how='left')

            st.success("✅ Data berhasil digabungkan.")

            # Preview hasil join sebelum filter
            st.subheader("👁️ Preview Hasil Join (sebelum filter)")
            st.dataframe(df_final.head(50))

            # Filter berdasarkan Check-In Date dan Check-Out Date
            checkin_col = 'Check-In Date'
            checkout_col = 'Check-Out Date'

            if checkin_col in df_final.columns and checkout_col in df_final.columns:
                df_final[checkin_col] = pd.to_datetime(df_final[checkin_col], errors='coerce')
                df_final[checkout_col] = pd.to_datetime(df_final[checkout_col], errors='coerce')

                # Filter hanya jika tanggal dipilih
                if start_date and end_date:
                    mask = (df_final[checkout_col] >= pd.to_datetime(start_date)) & \
                           (df_final[checkin_col] <= pd.to_datetime(end_date))
                    df_filtered = df_final[mask]
                else:
                    df_filtered = df_final.copy()

                st.subheader("📋 Data Setelah Filter")
                st.write(f"📂 Menampilkan {len(df_filtered)} baris data.")
                st.dataframe(df_filtered)

                # Download CSV
                csv = df_filtered.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Download Data (CSV)", csv, "filtered_data.csv", "text/csv")

                # Download Excel
                excel_data = to_excel(df_filtered)
                st.download_button("⬇️ Download Data (Excel)", excel_data,
                                   file_name="filtered_data.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            else:
                st.warning("⚠️ Kolom 'Check-In Date' dan/atau 'Check-Out Date' tidak ditemukan di data acuan.")

        except Exception as e:
            st.error(f"❌ Error saat proses join/filter: {e}")
else:
    if not data_ref:
        st.info("🟡 Harap upload file Data Acuan.")
    elif not primer_key:
        st.info("🟡 Masukkan nama kolom Primer Key.")
