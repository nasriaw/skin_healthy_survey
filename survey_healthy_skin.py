import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
from streamlit.components.v1 import html

# Konfigurasi halaman
st.set_page_config(page_title="Survey Data Kesehatan Kulit", layout="wide")

# JavaScript untuk mendapatkan lokasi
get_location_script = """
<script>
    async function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
                    fetch(url)
                        .then(response => response.json())
                        .then(data => {
                            const address = data.display_name;
                            window.parent.postMessage({type: 'location', lat: lat, lon: lon, address: address}, '*');
                        });
                }
            );
        }
    }
    getLocation();
</script>
"""

st.title("📋 Aplikasi Penginputan Data Survei Kulit")

# Inisialisasi state untuk menyimpan data lokasi
if 'gps_lat_lon' not in st.session_state: st.session_state.gps_lat_lon = ""
if 'alamat_otomatis' not in st.session_state: st.session_state.alamat_otomatis = ""

# Tombol untuk trigger lokasi
if st.button("📍 Ambil Lokasi & Alamat Otomatis"):
    html(get_location_script, height=0)
    st.info("Sedang memproses lokasi...")

# Listener untuk menangkap data dari JS (Menggunakan komponen sederhana)
# Kita akan menambahkan logika untuk membaca hasil dari JS ke session state
def update_loc():
    # Ini adalah simulasi penangkapan data. Dalam produksi, 
    # Anda bisa menggunakan komponen custom `streamlit-js-eval`
    pass

# --- Form Utama ---
with st.form("survey_form", clear_on_submit=False):
    st.header("Data Surveyor")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        surveyor_name = st.text_input("Nama Surveyor")
        surveyor_id = st.text_input("ID Surveyor")
    with col_s2:
        # Field ini akan diisi secara otomatis jika data GPS tersedia
        alamat_surveyor = st.text_area("Alamat Lengkap", value=st.session_state.alamat_otomatis)
        gps_location = st.text_input("Lokasi GPS (Lat, Lon)", value=st.session_state.gps_lat_lon)

    st.header("Klasifikasi Kondisi Kulit")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        age = st.number_input("Usia", min_value=20, max_value=50, step=1)
        status_kesehatan = st.selectbox("Status Kesehatan", ["Kulit Sehat", "Berjerawat", "Beruntusan", "Kemerahan"])
        tingkat_jerawat = st.select_slider("Tingkat Keparahan Jerawat", options=["Tidak Ada", "Ringan", "Sedang", "Parah"])
    with col2:
        skin_type = st.selectbox("Tipe Kulit Dasar", ["Berminyak", "Kering", "Normal", "Kombinasi"])
        tingkat_sebum = st.selectbox("Tingkat Sebum", ["Normal", "Berminyak", "Sangat Berminyak"])
        tekstur_kulit = st.selectbox("Tekstur Kulit", ["Halus", "Kasar", "Tidak Rata"])

    img_source = st.radio("Pilih sumber gambar:", ("Unggah File", "Kamera"))
    
    if 'captured_image' not in st.session_state: st.session_state.captured_image = None
    
    if img_source == "Unggah File":
        st.session_state.captured_image = st.file_uploader("Pilih gambar...", type=["jpg", "jpeg", "png"])
    else:
        st.session_state.captured_image = st.camera_input("Ambil foto kulit")

    submitted = st.form_submit_button("Simpan Data")

if submitted:
    if not surveyor_name or st.session_state.captured_image is None:
        st.error("Mohon isi Nama Surveyor dan pastikan foto sudah diambil!")
    else:
        if not os.path.exists("data_survey"): os.makedirs("data_survey")
        
        file_path = f"data_survey/{surveyor_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        img = Image.open(st.session_state.captured_image).convert("RGB")
        img.save(file_path, "JPEG")
        
        data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Surveyor": surveyor_name,
            "ID_Surveyor": surveyor_id,
            "Alamat": alamat_surveyor,
            "Location_GPS": gps_location,
            "Gender": gender,
            "Age": age,
            "Skin_Type": skin_type,
            "Status_Kesehatan": status_kesehatan,
            "Tingkat_Jerawat": tingkat_jerawat,
            "Tingkat_Sebum": tingkat_sebum,
            "Tekstur_Kulit": tekstur_kulit,
            "Image_Path": file_path
        }
        
        df_new = pd.DataFrame([data])
        csv_file = "survey_log.csv"
        
        if not os.path.exists(csv_file):
            df_new.to_csv(csv_file, index=False)
        else:
            df_old = pd.read_csv(csv_file)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
            df_final.to_csv(csv_file, index=False)
            
        st.success("Data berhasil disimpan!")

if st.button("📊 Tampilkan Tabel Data Survei"):
    if os.path.exists("survey_log.csv"):
        st.dataframe(pd.read_csv("survey_log.csv"))
    else:
        st.warning("Belum ada data.")
