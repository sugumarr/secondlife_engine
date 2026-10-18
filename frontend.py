import streamlit as st
import requests
import base64
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="SecondLife Engine", page_icon="♻️", layout="wide")

st.title("♻️ SecondLife Engine")
st.markdown("### Give Discarded Things a New Job — Powered by Gemini Flash Multi-Agent AI")

BACKEND_URL = "http://127.0.0.1:8000/analyze"

with st.sidebar:
    st.header("Upload & Demo Control")
    uploaded_file = st.file_uploader("Upload waste batch photo", type=["jpg", "jpeg", "png"])
    
    st.markdown("---")
    st.markdown("### Quick Test Samples")
    sample_choice = st.selectbox("Load Sample Batch:", ["Select...", "Plastic Bottles Batch", "E-Waste Scrap", "Cardboard & Cans"])
    
    target_file_bytes = None
    if uploaded_file is not None:
        target_file_bytes = uploaded_file.getvalue()
    elif sample_choice != "Select...":
        sample_map = {
            "Plastic Bottles Batch": "images/test_plastic_bottles.jpg",
            "E-Waste Scrap": "images/test_ewaste.jpg",
            "Cardboard & Cans": "images/test_cardboard_cans.jpg"
        }
        path = sample_map[sample_choice]
        if os.path.exists(path):
            with open(path, "rb") as f:
                target_file_bytes = f.read()
            st.image(path, caption=sample_choice, width="stretch")

    analyze_btn = st.button("Run Multi-Agent Engine", type="primary")

if target_file_bytes and analyze_btn:
    with st.spinner("🤖 Multi-Agents (Vision, Safety, Valuation, Creative) analyzing components..."):
        try:
            files = {"file": ("image.jpg", target_file_bytes, "image/jpeg")}
            response = requests.post(BACKEND_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state['data'] = data
                st.session_state['image_bytes'] = target_file_bytes
            else:
                st.error(f"Backend Error: {response.text}")
        except Exception as e:
            st.error(f"Connection Error: Is the FastAPI backend running? Details: {e}")

if 'data' in st.session_state:
    data = st.session_state['data']
    orig_image = Image.open(io.BytesIO(st.session_state['image_bytes'])).convert("RGB")
    w, h = orig_image.size

    # Metric Dashboard Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Materials Identified", len(data.get("detected_materials", [])))
    col2.metric("Est. Value / Savings", f"${data.get('valuation_summary', {}).get('total_estimated_value_usd', 0):.2f}")
    col3.metric("Waste Diverted", f"{data.get('valuation_summary', {}).get('estimated_waste_diverted_kg', 0)} kg")

    st.markdown("---")
    
    # Task 3: Bounding boxes visualization on original image
    st.subheader("📍 Agent 1: Vision Bounding Boxes & Crop Breakdown")
    draw_img = orig_image.copy()
    draw = ImageDraw.Draw(draw_img)
    
    for mat in data.get("detected_materials", []):
        ymin, xmin, ymax, xmax = mat.get("box_2d", [0, 0, 1000, 1000])
        abs_ymin = int((ymin / 1000.0) * h)
        abs_xmin = int((xmin / 1000.0) * w)
        abs_ymax = int((ymax / 1000.0) * h)
        abs_xmax = int((xmax / 1000.0) * w)
        
        draw.rectangle([abs_xmin, abs_ymin, abs_xmax, abs_ymax], outline="lime", width=4)
        draw.text((abs_xmin + 5, abs_ymin + 5), mat.get("item_name", "Item"), fill="yellow")

    col_img, col_list = st.columns([1, 1])
    with col_img:
        st.image(draw_img, caption="Detected Objects with Bounding Boxes", use_column_width=True)
    
    with col_list:
        st.markdown("#### Detailed Material List & Cropped Assets (Task 1 & 4)")
        for idx, mat in enumerate(data.get("detected_materials", [])):
            with st.expander(f"📦 {mat.get('item_name')} (Qty: {mat.get('quantity')})"):
                if "cropped_image_base64" in mat:
                    img_bytes = base64.b64decode(mat["cropped_image_base64"])
                    st.image(io.BytesIO(img_bytes), width=150)
                st.write(f"**Category:** {mat.get('category')}")
                st.write(f"**Estimated Value (Task 5):** ${mat.get('estimated_value_usd', 0):.2f}")
                st.write(f"**Safety Precautions:** {mat.get('safety_notes')}")

    st.markdown("---")
    
    # Task 6: Reusable creative artistic ideas
    st.subheader("🎨 Agent 3: Creative Artistic & Functional Reuse Blueprints")
    proposals = data.get("creative_proposals", [])
    
    tabs = st.tabs([p.get("project_name", f"Proposal {i+1}") for i, p in enumerate(proposals)])
    for i, tab in enumerate(tabs):
        if i < len(proposals):
            prop = proposals[i]
            with tab:
                st.markdown(f"### Theme: {prop.get('artistic_theme')}")
                st.markdown("#### 🛠️ Bill of Materials")
                for bom in prop.get("bill_of_materials", []):
                    st.markdown(f"- {bom}")
                st.markdown("#### 📝 Step-by-Step Assembly Plan")
                for step in prop.get("step_by_step_plan", []):
                    st.markdown(f"1. {step}")
else:
    st.info("👈 Generate or upload test images, then click **Run Multi-Agent Engine** in the sidebar to start.")