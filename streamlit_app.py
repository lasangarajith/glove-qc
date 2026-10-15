import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="Glove QC System", page_icon="🛡️", layout="centered")

st.title("🛡️ Glove Print QC System")
st.write("Phone එකෙන් Master Print එක සහ Inspection prints පහසුවෙන් පරීක්ෂා කරන්න.")

# Initialize Session State Counters
if 'pass_count' not in st.session_state:
    st.session_state.pass_count = 0
if 'fail_count' not in st.session_state:
    st.session_state.fail_count = 0
if 'total_count' not in st.session_state:
    st.session_state.total_count = 0
if 'master_image' not in st.session_state:
    st.session_state.master_image = None

# --- STEP 1: MASTER REFERENCE ---
st.header("1️⃣ Master Print Setup")
master_file = st.camera_input("Master Glove එකේ ෆොටෝ එකක් ගන්න")

if master_file is not None:
    st.session_state.master_image = Image.open(master_file).convert("RGB")
    st.success("✅ Master Reference සාර්ථකව Save විය!")
    st.image(st.session_state.master_image, caption="Master Print", width=250)

# --- STEP 2: INSPECTION ---
if st.session_state.master_image is not None:
    st.markdown("---")
    st.header("2️⃣ Live Glove QC Inspection")
    
    test_file = st.camera_input("පරීක්ෂා කළ යුතු Glove එකේ ෆොටෝ එකක් ගන්න")
    
    if test_file is not None:
        test_image = Image.open(test_file).convert("RGB")
        
        # Compare images (Resize and get mean absolute difference)
        master_arr = np.array(st.session_state.master_image.resize((150, 150)).convert("L"))
        test_arr = np.array(test_image.resize((150, 150)).convert("L"))
        
        diff = np.mean(np.abs(master_arr.astype(float) - test_arr.astype(float)))
        score = max(0, int(100 - (diff / 255 * 100 * 1.5)))
        
        st.metric(label="Match Score", value=f"{score}%")
        
        # Threshold: 65%
        if score >= 65:
            st.success(f"🟢 STATUS: PASS / OK ({score}%)")
            st.session_state.pass_count += 1
        else:
            st.error(f"🔴 STATUS: REJECT / FAIL ({score}%)")
            st.session_state.fail_count += 1
            
        st.session_state.total_count = st.session_state.pass_count + st.session_state.fail_count

    # --- RESULTS DASHBOARD ---
    st.markdown("---")
    st.subheader("📊 Inspection Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Checked", st.session_state.total_count)
    col2.metric("Pass (OK)", st.session_state.pass_count)
    col3.metric("Reject (Fail)", st.session_state.fail_count)

    if st.button("🔄 Reset All Counters"):
        st.session_state.pass_count = 0
        st.session_state.fail_count = 0
        st.session_state.total_count = 0
        st.rerun()
