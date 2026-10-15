import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="Glove QC System", page_icon="🛡️", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    h1 { color: #38bdf8; text-align: center; font-size: 1.5rem; }
    .stMetric { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Glove Print QC System")

# Initialize Session State
if 'pass_count' not in st.session_state:
    st.session_state.pass_count = 0
if 'fail_count' not in st.session_state:
    st.session_state.fail_count = 0
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'master_image' not in st.session_state:
    st.session_state.master_image = None

# --- STEP 1: MASTER SETUP ---
st.subheader("1️⃣ Master Print Setup")
master_file = st.camera_input("ප්‍රධාන (Master) Glove Print එකේ ෆොටෝ එකක් ගන්න")

if master_file is not None:
    st.session_state.master_image = Image.open(master_file).convert("RGB")
    st.success("✅ Master Print සාර්ථකව Save විය!")
    st.image(st.session_state.master_image, caption="Master Reference", width=200)

# --- STEP 2: LIVE QC INSPECTION ---
if st.session_state.master_image is not None:
    st.markdown("---")
    st.subheader("2️⃣ Live Inspection Check")
    
    test_file = st.camera_input("පරීක්ෂා කළ යුතු Glove එකේ ෆොටෝ එකක් ගන්න (Live Check)")
    
    if test_file is not None:
        test_image = Image.open(test_file).convert("RGB")
        
        # Image Comparison
        master_arr = np.array(st.session_state.master_image.resize((150, 150)).convert("L"))
        test_arr = np.array(test_image.resize((150, 150)).convert("L"))
        
        diff = np.mean(np.abs(master_arr.astype(float) - test_arr.astype(float)))
        score = max(0, int(100 - (diff / 255 * 100 * 1.5)))
        
        st.metric(label="Match Score", value=f"{score}%")
        
        # Threshold: 65%
        if score >= 65:
            st.success(f"🟢 PASS / OK ({score}%)")
            st.session_state.pass_count += 1
        else:
            st.error(f"🔴 REJECT / FAIL ({score}%)")
            st.session_state.fail_count += 1
            
        st.session_state.total_count = st.session_state.pass_count + st.session_state.fail_count

    # --- SUMMARY DASHBOARD ---
    st.markdown("---")
    st.subheader("📊 QC Counters")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", st.session_state.total_count)
    col2.metric("Pass", st.session_state.pass_count)
    col3.metric("Reject", st.session_state.fail_count)

    if st.button("🔄 Reset Counters"):
        st.session_state.pass_count = 0
        st.session_state.fail_count = 0
        st.session_state.total_count = 0
        st.rerun()
