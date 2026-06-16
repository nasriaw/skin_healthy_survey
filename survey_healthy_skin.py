import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# Konfigurasi halaman
st.set_page_config(page_title="Survey Data Kesehatan Kulit", layout="wide")

st.title("📋 Aplikasi Penginputan Data Survei Kulit")
st.write("Silakan isi data surveyor dan klasifikasi kondisi kulit untuk kebutuhan riset.")

# --- Sidebar: Data Surveyor ---
st.sidebar.header("Data Surveyor")
surveyor_name = st.sidebar.text_input("Nama Surveyor")
surveyor_id = st.sidebar.text_input("ID Surveyor")

# --- Form Utama: Data Label ---
with st.form("survey_form"):
    st.subheader("Informasi Demografis")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        age = st.number_input("Usia", min_value=20, max_value=50, step=1)
    with col2:
        location = st.text_input("Lokasi (Kota/Provinsi)")
        skin_type = st.selectbox("Tipe Kulit Dasar", ["Berminyak", "Kering", "Normal", "Kombinasi"])

    st.subheader("Klasifikasi Kondisi Kulit (Labeling)")
    col3, col4 = st.columns(2)
    with col3:
        status_kesehatan = st.selectbox("Status Kesehatan", ["Kulit Sehat", "Berjerawat", "Beruntusan/Tekstur Kasar", "Kemerahan/Iritasi"])
        tingkat_jerawat = st.select_slider("Tingkat Keparahan Jerawat", options=["Tidak Ada", "Ringan", "Sedang", "Parah"])
    with col4:
        tingkat_sebum = st.selectbox("Tingkat Sebum", ["Normal", "Berminyak", "Sangat Berminyak"])
        tekstur_kulit = st.selectbox("Tekstur Kulit", ["Halus", "Kasar", "Tidak Rata"])

    # Input Gambar
    st.subheader("Unggah Foto Kulit")
    img_source = st.radio("Pilih sumber gambar:", ("Unggah File", "Kamera"))
    
    if img_source == "Unggah File":
        uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])
    else:
        uploaded_file = st.camera_input("Ambil foto kulit")

    submitted = st.form_submit_button("Simpan Data")

# --- Logika Penyimpanan ---
if submitted:
    if not surveyor_name or not uploaded_file:
        st.error("Mohon isi Nama Surveyor dan unggah/ambil foto!")
    else:
        # Buat direktori penyimpanan
        save_dir = "data_survey"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Simpan file gambar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_ext = os.path.splitext(uploaded_file.name)[1] if hasattr(uploaded_file, 'name') else ".jpg"
        file_name = f"{surveyor_id}_{timestamp}{file_ext}"
        file_path = os.path.join(save_dir, file_name)
        
        image = Image.open(uploaded_file)
        image.save(file_path)
        
        # Simpan metadata ke CSV
        data = {
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Surveyor": [surveyor_name],
            "ID_Surveyor": [surveyor_id],
            "Gender": [gender],
            "Age": [age],
            "Location": [location],
            "Skin_Type": [skin_type],
            "Status_Kesehatan": [status_kesehatan],
            "Tingkat_Jerawat": [tingkat_jerawat],
            "Tingkat_Sebum": [tingkat_sebum],
            "Tekstur_Kulit": [tekstur_kulit],
            "Image_Path": [file_path]
        }
        
        df = pd.DataFrame(data)
        csv_file = "survey_log.csv"
        
        # Append ke CSV
        if not os.path.exists(csv_file):
            df.to_csv(csv_file, index=False)
        else:
            df.to_csv(csv_file, mode='a', header=False, index=False)
            
        st.success(f"Data berhasil disimpan ke {file_path}!")
        st.balloons()

# Menampilkan riwayat (opsional)
if st.checkbox("Lihat Riwayat Survei"):
    if os.path.exists("survey_log.csv"):
        log_df = pd.read_csv("survey_log.csv")
        st.dataframe(log_df)
    else:
        st.info("Belum ada data survei.")