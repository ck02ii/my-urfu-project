import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from deep_translator import GoogleTranslator
import re
import pandas as pd
from datetime import datetime
from langdetect import detect
import sys

if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(
    page_title="Universal OCR Translator | UrFU",
    page_icon="",
    layout="wide"
)

ALL_OCR_LANGS = {
    'rus': 'Russian',
    'eng': 'English',
    'fra': 'French',
    'deu': 'German',
    'spa': 'Spanish',
    'ita': 'Italian',
    'ukr': 'Ukrainian',
    'kaz': 'Kazakh',
    'chi_sim': 'Chinese Simplified',
    'chi_tra': 'Chinese Traditional',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'ara': 'Arabic',
    'hin': 'Hindi'
}

TRANSLATION_LANGS = {
    'ru': 'Russian',
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'uk': 'Ukrainian',
    'kk': 'Kazakh',
    'zh-cn': 'Chinese Simplified',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi'
}

def preprocess_image(image):
    if image.mode != 'L':
        image = image.convert('L')
    
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image

def smart_recognize(image):
    processed_img = preprocess_image(image)
    
    best_text = ""
    best_lang = None
    best_lang_name = None
    
    results = []
    
    for lang_code, lang_name in ALL_OCR_LANGS.items():
        try:
            text = pytesseract.image_to_string(processed_img, lang=lang_code).strip()
            text_len = len(text)
            if text_len > 0:
                results.append((text_len, text, lang_code, lang_name))
        except Exception as e:
            continue
    
    if not results:
        return None, None, None
    
    results.sort(reverse=True)
    best_text = results[0][1]
    best_lang_code = results[0][2]
    best_lang_name = results[0][3]
    
    clean_text = re.sub(r'[^\w\s.,!?;:\-]', '', best_text).strip()
    
    try:
        detected_lang = detect(clean_text)
        lang_map = {
            'ru': 'Russian', 'en': 'English', 'fr': 'French',
            'de': 'German', 'es': 'Spanish', 'it': 'Italian',
            'zh-cn': 'Chinese', 'ja': 'Japanese', 'ko': 'Korean',
            'ar': 'Arabic', 'hi': 'Hindi', 'uk': 'Ukrainian'
        }
        final_lang_name = lang_map.get(detected_lang, best_lang_name)
    except:
        final_lang_name = best_lang_name
    
    return clean_text, final_lang_name, best_lang_code

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

st.sidebar.title("About Project")
st.sidebar.info(
    """
    Educational program:
    Professional retraining "Solving applied and fundamental problems in humanities using Python programming language" UrFU
    
    Project team:
    - Leader: [Full Name]
    
    How it works:
    1. Tries to recognize text in 14 languages
    2. Selects the best result
    3. Automatically detects language
    4. Translates to selected language
    """
)

st.title("Universal OCR Translator")
st.markdown("Upload an image with text in any language - AI will detect the language and translate")

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

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Original", width="stretch")
    
    processed = preprocess_image(image)
    with col2:
        st.image(processed, caption="Processed", width="stretch")
    
    with st.spinner("Analyzing image (trying all languages)..."):
        recognized_text, detected_lang, used_lang_code = smart_recognize(image)
        
        if recognized_text and len(recognized_text) > 5:
            with st.spinner("Translating..."):
                translated_text = translate_text(recognized_text, target_lang_code)
            
            chars, words, sentences = count_stats(recognized_text)
            
            st.success(f"Recognized! Detected language: {detected_lang}")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.subheader("Original text")
                st.text_area("", recognized_text, height=250, key="orig", label_visibility="collapsed")
            
            with col_res2:
                st.subheader(f"Translation ({TRANSLATION_LANGS[target_lang_code]})")
                if translated_text:
                    st.text_area("", translated_text, height=250, key="trans", label_visibility="collapsed")
                else:
                    st.error("Translation error. Check internet connection.")
            
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Characters", chars)
            col_s2.metric("Words", words)
            col_s3.metric("Sentences", sentences)
            
        else:
            st.error("Text not found. Try:")
            st.markdown("""
            - Use image with clearer text
            - Make sure text is contrast
            - For Chinese/Japanese use larger font
            - Try another image
            """)
