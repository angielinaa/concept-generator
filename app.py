import streamlit as st
import requests
import urllib.parse
from groq import Groq

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

st.set_page_config(page_title="Concept Generator", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 1. Sembunyikan Elemen Default Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Alignment Kiri Total */
    .left-align-title {
        text-align: left !important;
        font-weight: 700 !important;
        color: #222222;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .left-align-subtitle {
        text-align: left !important;
        font-weight: 400 !important;
        color: #777777;
        font-size: 15px;
        margin-top: 4px;
        margin-bottom: 32px;
    }

    /* 2 & 4. Standarisasi Komponen (8px Radius & Shadow Halus Pengganti Border) */
    .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        border-radius: 8px !important;
        border: 1px solid #E5E5E5 !important;
        background-color: #ffffff !important;
        font-size: 14px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
        transition: all 0.2s ease;
    }

    /* Hapus Focus State Terang */
    .stTextArea>div>div>textarea:focus, .stSelectbox>div>div>div:focus-within {
        border-color: #B0B0B0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
        outline: none !important;
    }

    .stTextArea textarea::placeholder {
        color: #cccccc !important;
    }

    .stTextArea>div>div>textarea { resize: none; }

    /* 3. Tipografi Label Parameter */
    label {
        font-weight: 600 !important;
        font-size: 13px !important;
        color: #444444 !important;
    }

    /* Tombol CTA Full-Width & Konsisten 8px */
    .stButton>button, .stDownloadButton>button {
        width: 100% !important;
        background-color: #111111 !important;
        color: #ffffff !important;
        border-radius: 8px !important; 
        padding: 10px 16px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #333333 !important;
    }

    /* Latar Belakang Placeholder (Empty State) */
    .empty-state {
        border: 1px dashed #D0D0D0;
        border-radius: 8px;
        background-color: #F8F9FA;
        height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #A0A0A0;
        font-size: 14px;
        font-weight: 400;
        margin-top: 28px;
    }

    /* Tampilan Code Block (Prompt) */
    div[data-testid="stCodeBlock"] {
        border-radius: 8px;
        background-color: #F8F9FA;
        border: 1px solid #E5E5E5;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 class='left-align-title'>Concept Generator</h2>", unsafe_allow_html=True)
st.markdown("<p class='left-align-subtitle'>AI-Powered Pre-production Tool</p>", unsafe_allow_html=True)


def generate_image(prompt, width, height):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

    try:
        response = requests.get(url, timeout=25)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return requests.get(f"https://via.placeholder.com/{width}x{height}.png?text=Generation+Failed").content


col_input, col_spacing, col_output = st.columns([1, 0.1, 1.2])

with col_input:
    scene_desc = st.text_area(
        "Scene Description",
        placeholder="e.g., A cinematic night scene with neon lights...",
        height=140
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        style = st.selectbox("Style", ["Cinematic", "Anime", "Realistic", "Watercolor"])
    with col_p2:
        mood = st.selectbox("Mood", ["Melancholic", "Hopeful", "Intense", "Mysterious"])

    aspect_ratio = st.selectbox("Ratio", ["16:9", "1:1", "9:16"])

    ratio_map = {"16:9": (1024, 576), "1:1": (768, 768), "9:16": (576, 1024)}
    width, height = ratio_map[aspect_ratio]

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    generate_btn = st.button("GENERATE CONCEPT")

with col_output:
    if generate_btn and scene_desc:
        with st.spinner("Processing visual concepts..."):
            try:
                client = Groq(api_key=GROQ_API_KEY)
                system_instruction = """
                You are an expert AI prompt engineer for Stable Diffusion. 
                CRITICAL RULES:
                1. PRESERVE THE CORE SUBJECT EXACTLY. If the user writes 'bunga bermekaran', they MUST be blooming/alive.
                2. Apply the 'Mood' ONLY to the environment/lighting.
                3. Translate Indonesian to English accurately.
                4. Output ONLY a comma-separated prompt string.
                """
                user_instruction = f"Subject: '{scene_desc}'. Style: {style}. Mood: {mood}."

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": system_instruction},
                              {"role": "user", "content": user_instruction}],
                    model="llama-3.1-8b-instant",
                    temperature=0.3
                )
                enhanced_prompt = chat_completion.choices[0].message.content.strip()

                image_bytes = generate_image(enhanced_prompt, width, height)

                # Render Gambar & Tombol Download Full-Width
                st.image(image_bytes, use_container_width=True)

                st.download_button(
                    label="Download Concept Image",
                    data=image_bytes,
                    file_name=f"concept_{style.lower()}_{mood.lower()}.png",
                    mime="image/png"
                )

                # Instruksi Hover Pudar
                st.markdown(
                    "<div style='margin-top: 16px;'><span style='font-size:13px; font-weight:600; color:#444;'>Engineered Prompt</span> &nbsp;<span style='font-size:11px; color:#AAAAAA; font-weight:400;'>(Hover over the box to copy)</span></div>",
                    unsafe_allow_html=True)
                st.code(enhanced_prompt, language="text")

            except Exception as e:
                st.error(f"Generation Error: {e}")
    else:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 24px; margin-bottom: 8px; color: #D0D0D0;">🖼️</div>
            <div>Image Preview Area</div>
        </div>
        """, unsafe_allow_html=True)