import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ===============================
# ✅ Autentikasi API Key
# ===============================
st.sidebar.title("🔐 Autentikasi")
api_key_input = st.sidebar.text_input("Masukkan API Key:", type="password")
API_KEY = "RahasiaBanget"  # Ganti sesuai kebutuhan

if api_key_input != API_KEY:
    st.warning("Masukkan API Key yang benar untuk mengakses aplikasi ini.")
    st.stop()

# ===============================
# ✅ Upload File
# ===============================
st.title("📊 Join dan Filter Multi-Data")
st.markdown("Unggah hingga 4 data tambahan dan 1 data acuan untuk proses join.")

col1, col2 = st.columns(2)
with col1:
    file1 = st.file_uploader("Data 1", type=["xlsx", "csv"], key="data1")
    file2 = st.file_uploader("Data 2", type=["xlsx", "csv"], key="data2")
with col2:
    file3 = st.file_uploader("Data 3", type=["xlsx", "csv"], key="data3")
    file4 = st.file_uploader("Data 4", type=["xlsx", "csv"], key="data4")

data_acuan = st.file_uploader("Data Acuan (Utama)", type=["xlsx", "csv"], key="acuan")

# ===============================
# ✅ Load Data
# ===============================
def load_data(file):
    if file is not None:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    return None

df_list = []
for f in [file1, file2, file3, file4]:
    df = load_data(f)
    if df is not None:
        df_list.append(df)

df_acuan = load_data(data_acuan)

# ===============================
# ✅ Join dan Filter Data
# ===============================
if df_acuan is not None:
    try:
        result = df_acuan.copy()
        for df in df_list:
            common_cols = list(set(result.columns).intersection(set(df.columns)))
            if common_cols:
                result = pd.merge(result, df, how="left", on=common_cols)

        st.subheader("🔍 Preview Data Join (Sebelum Filter)")
        st.dataframe(result, use_container_width=True)

        # Format tanggal
        result['Check-In Date'] = pd.to_datetime(result['Check-In Date'], errors='coerce')
        result['Check-Out Date'] = pd.to_datetime(result['Check-Out Date'], errors='coerce')

        # ===============================
        # ✅ Sidebar Filter
        # ===============================
        st.sidebar.title("📅 Filter Periode")

        min_date = result['Check-In Date'].min()
        max_date = result['Check-Out Date'].max()

        check_in_filter = st.sidebar.date_input("Dari Tanggal", value=min_date)
        check_out_filter = st.sidebar.date_input("Sampai Tanggal", value=max_date)

        filtered_data = result[
            (result['Check-In Date'] >= pd.to_datetime(check_in_filter)) &
            (result['Check-Out Date'] <= pd.to_datetime(check_out_filter))
        ]

        # Filter Booking ID
        if 'Booking ID' in filtered_data.columns:
            st.sidebar.markdown("### 🔎 Filter Booking ID")
            options = ['(Semua)'] + sorted(filtered_data['Booking ID'].dropna().unique().tolist())
            selected_id = st.sidebar.selectbox("Pilih Booking ID", options=options)
            if selected_id != '(Semua)':
                filtered_data = filtered_data[filtered_data['Booking ID'] == selected_id]

        # ===============================
        # ✅ Preview Hasil Filter
        # ===============================
        st.subheader("📋 Data Setelah Difilter")
        st.dataframe(filtered_data, use_container_width=True)

        # ===============================
        # ✅ Optional Download
        # ===============================
        if st.checkbox("📥 Simpan hasil ke Excel"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered_data.to_excel(writer, index=False, sheet_name='Hasil')
            st.download_button(
                label="⬇️ Download Excel",
                data=output.getvalue(),
                file_name="hasil_join_filtered.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ Error saat proses join/filter: {e}")
else:
    st.info("📥 Silakan unggah Data Acuan terlebih dahulu.")
