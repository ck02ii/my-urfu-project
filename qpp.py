import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance
from deep_translator import GoogleTranslator
import re
import sys

if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(
    page_title="OCR Translator",
    page_icon="",
    layout="wide"
)

TRANSLATION_LANGS = {
    'ru': 'Russian',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'zh-cn': 'Chinese',
    'ko': 'Korean'
}

def preprocess_image(image):
    if image.mode != 'L':
        image = image.convert('L')
    
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image

def translate_text(text, target_lang):
    if not text:
        return None
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        return None

def count_stats(text):
    chars = len(text)
    words = len(text.split())
    sentences = text.count('.') + text.count('!') + text.count('?') + text.count('。') + text.count('！') + text.count('？')
    return chars, words, sentences

st.title("OCR Translator")
st.markdown("Upload an image with horizontal text in English or Japanese")

uploaded_file = st.file_uploader(
    "Select image",
    type=["png", "jpg", "jpeg", "bmp", "tiff"]
)

target_lang_name = st.selectbox(
    "Translate to:", 
    list(TRANSLATION_LANGS.keys()),
    format_func=lambda x: TRANSLATION_LANGS[x],
    index=0
)
target_lang_code = target_lang_name

st.subheader("Recognition settings")
force_lang = st.radio(
    "Force recognition language:",
    ["Auto detect", "English only", "Japanese only"],
    index=0
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Original", width="stretch")
    
    processed = preprocess_image(image)
    with col2:
        st.image(processed, caption="Processed for OCR", width="stretch")
    
    with st.spinner("Recognizing text..."):
        if force_lang == "English only":
            recognized_text = pytesseract.image_to_string(processed, lang='eng').strip()
            detected_lang = "English"
        elif force_lang == "Japanese only":
            recognized_text = pytesseract.image_to_string(processed, lang='jpn').strip()
            detected_lang = "Japanese"
        else:
            jpn_text = pytesseract.image_to_string(processed, lang='jpn').strip()
            eng_text = pytesseract.image_to_string(processed, lang='eng').strip()
            
            if len(jpn_text) > len(eng_text) and len(jpn_text) > 5:
                recognized_text = jpn_text
                detected_lang = "Japanese"
            elif len(eng_text) > 5:
                recognized_text = eng_text
                detected_lang = "English"
            else:
                recognized_text = None
                detected_lang = None
        
        if recognized_text and len(recognized_text) > 3:
            with st.spinner("Translating..."):
                translated_text = translate_text(recognized_text, target_lang_code)
            
            chars, words, sentences = count_stats(recognized_text)
            
            st.success(f"Recognized! Language: {detected_lang}")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.subheader("Original text")
                st.text_area("", recognized_text, height=200, key="orig", label_visibility="collapsed")
            
            with col_res2:
                st.subheader(f"Translation ({TRANSLATION_LANGS[target_lang_code]})")
                if translated_text:
                    st.text_area("", translated_text, height=200, key="trans", label_visibility="collapsed")
                else:
                    st.error("Translation error. Check internet connection.")
            
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Characters", chars)
            col_s2.metric("Words", words)
            col_s3.metric("Sentences", sentences)
            
        else:
            st.error("Text not found. Try:")
            st.markdown("""
            - Select "Japanese only" in recognition settings
            - Make sure the image is not rotated
            - Use clear printed Japanese font
            - Try another image
            """)
