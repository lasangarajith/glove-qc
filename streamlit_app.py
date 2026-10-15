import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration

st.set_page_config(page_title="Live Glove QC System", page_icon="🛡️", layout="centered")

st.title("🛡️ Live Glove Print QC Inspector")
st.write("ਕැමරාව ලයිව් ඔන් කර තබා, ග්ලවුස් එක පෙන්වූ සැනින් Real-time Pass/Reject බලන්න.")

# Initialize session state for master reference
if 'master_np' not in st.session_state:
    st.session_state.master_np = None

# --- STEP 1: MASTER REFERENCE UPLOAD ---
st.subheader("1️⃣ Master Reference Setup")
master_file = st.file_uploader("ප්‍රධාන (Master) Glove Print එකේ ෆොටෝ එකක් Upload කරන්න", type=["jpg", "png", "jpeg"])

if master_file is not None:
    master_img = Image.open(master_file).convert("RGB").resize((150, 150))
    st.session_state.master_np = np.array(master_img.convert("L"))
    st.success("✅ Master Reference සාර්ථකව සකස් විය!")
    st.image(master_img, caption="Master Print", width=150)

# --- STEP 2: LIVE VIDEO STREAM QC ---
if st.session_state.master_np is not None:
    st.markdown("---")
    st.subheader("2️⃣ Live Camera Feed (Real-time QC)")
    st.info("💡 පහත 'START' බොත්තම ඔබා කැමරාව ලයිව් ආරම්භ කරන්න.")
    
    master_arr = st.session_state.master_np

    class GloveTransformer(VideoTransformerBase):
        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")
            
            # Get video dimensions and crop center region
            h, w, _ = img.shape
            crop_w, crop_h = int(w * 0.4), int(h * 0.3)
            x, y = int((w - crop_w) / 2), int((h - crop_h) / 2)
            
            # Crop region of interest
            roi = img[y:y+crop_h, x:x+crop_w]
            
            # Convert to grayscale and resize for comparison
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            roi_resized = cv2.resize(roi_gray, (150, 150))
            
            # Compare with master image
            diff = np.mean(np.abs(master_arr.astype(float) - roi_resized.astype(float)))
            score = max(0, int(100 - (diff / 255 * 100 * 1.5)))
            
            # Determine Pass or Reject
            if score >= 65:
                status_text = f"PASS: {score}%"
                box_color = (0, 255, 0) # Green
            else:
                status_text = f"REJECT: {score}%"
                box_color = (0, 0, 255) # Red
            
            # Draw bounding box and text on the live video frame
            cv2.rectangle(img, (x, y), (x + crop_w, y + crop_h), box_color, 3)
            cv2.putText(img, status_text, (x, max(30, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, box_color, 2, cv2.LINE_AA)
            
            return img

    webrtc_streamer(
        key="glove-qc-live",
        video_processor_factory=GloveTransformer,
        rtc_configuration=RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}),
        media_stream_constraints={"video": {"facingMode": "environment"}, "audio": False}
    )
else:
    st.warning("⚠️ කරුණාකර මුලින්ම ඉහතින් Master Glove Print එකක් Upload කරන්න.")
