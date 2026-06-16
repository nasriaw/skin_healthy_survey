import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
from streamlit.components.v1 import html

# Konfigurasi halaman
st.set_page_config(page_title="Survey Data Kesehatan Kulit", layout="wide")

# JavaScript untuk mengambil lokasi GPS dari browser
def get_location_js():
    return """
    <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        window.parent.postMessage({type: 'location', lat: lat, lon: lon}, '*');
                    },
                    (error) => {
                        window.parent.postMessage({type: 'location', error: error.message}, '*');
                    }
                );
            }
        }
        getLocation();
    </script>
    """

st.title("📋 Aplikasi Penginputan Data Survei Kulit")

# Tombol untuk trigger lokasi
if st.button("📍 Dapatkan Lokasi Otomatis"):
    html(get_location_js(), height=0)
    st.info("Sedang mencari lokasi... Pastikan Anda mengizinkan akses lokasi di browser.")

st.write("Silakan isi data surveyor dan klasifikasi kondisi kulit.")

# --- Sidebar: Data Surveyor ---
st.sidebar.header("Data Surveyor")
surveyor_name = st.sidebar.text_input("Nama Surveyor")
surveyor_id = st.sidebar.text_input("ID Surveyor")

location = st.text_input("Lokasi (GPS/Alamat)", help="Klik tombol Dapatkan Lokasi di atas atau isi manual")

# --- Form Utama ---
# Memisahkan input kamera agar tidak terbungkus form yang menghambat akses perangkat
img_source = st.radio("Pilih sumber gambar:", ("Unggah File", "Kamera"))

uploaded_file = None
if img_source == "Unggah File":
    uploaded_file = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])
else:
    st.info("Pastikan Anda telah memberikan izin akses kamera pada browser HP Anda.")
    uploaded_file = st.camera_input("Ambil foto kulit")

with st.form("survey_form"):
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        age = st.number_input("Usia", min_value=20, max_value=50, step=1)
    with col2:
        skin_type = st.selectbox("Tipe Kulit Dasar", ["Berminyak", "Kering", "Normal", "Kombinasi"])

    st.subheader("Klasifikasi Kondisi Kulit (Labeling)")
    col3, col4 = st.columns(2)
    with col3:
        status_kesehatan = st.selectbox("Status Kesehatan", ["Kulit Sehat", "Berjerawat", "Beruntusan/Tekstur Kasar", "Kemerahan/Iritasi"])
        tingkat_jerawat = st.select_slider("Tingkat Keparahan Jerawat", options=["Tidak Ada", "Ringan", "Sedang", "Parah"])
    with col4:
        tingkat_sebum = st.selectbox("Tingkat Sebum", ["Normal", "Berminyak", "Sangat Berminyak"])
        tekstur_kulit = st.selectbox("Tekstur Kulit", ["Halus", "Kasar", "Tidak Rata"])

    submitted = st.form_submit_button("Simpan Data")

if submitted:
    if not surveyor_name or not uploaded_file:
        st.error("Mohon isi Nama Surveyor dan pastikan foto sudah diambil/diunggah!")
    else:
        save_dir = "data_survey"
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{surveyor_id}_{timestamp}.jpg"
        file_path = os.path.join(save_dir, file_name)
        
        Image.open(uploaded_file).save(file_path)
        
        data = {
            "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Surveyor": [surveyor_name],
            "ID_Surveyor": [surveyor_id],
            "Location": [location],
            "Gender": [gender],
            "Age": [age],
            "Skin_Type": [skin_type],
            "Status_Kesehatan": [status_kesehatan],
            "Tingkat_Jerawat": [tingkat_jerawat],
            "Tingkat_Sebum": [tingkat_sebum],
            "Tekstur_Kulit": [tekstur_kulit],
            "Image_Path": [file_path]
        }
        
        df = pd.DataFrame(data)
        csv_file = "survey_log.csv"
        if not os.path.exists(csv_file): df.to_csv(csv_file, index=False)
        else: df.to_csv(csv_file, mode='a', header=False, index=False)
            
        st.success("Data berhasil disimpan!")
