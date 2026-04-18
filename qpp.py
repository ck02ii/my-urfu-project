import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from deep_translator import GoogleTranslator
import re
import sys

if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(
    page_title="OCR Translator | UrFU",
    page_icon="",
    layout="wide"
)

SUPPORTED_LANGS = {
    'eng': 'English',
    'jpn': 'Japanese',
    'jpn_vert': 'Japanese (Vertical)'
}

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

def rotate_image_for_japanese(image):
    img = preprocess_image(image)
    return img

def recognize_text(image):
    processed_img = preprocess_image(image)
    
    results = []
    
    for lang_code, lang_name in SUPPORTED_LANGS.items():
        try:
            text = pytesseract.image_to_string(processed_img, lang=lang_code).strip()
            text_len = len(text)
            if text_len > 0:
                results.append((text_len, text, lang_code, lang_name))
        except Exception as e:
            continue
    
    if not results:
        return None, None
    
    results.sort(reverse=True)
    best_text = results[0][1]
    best_lang_name = results[0][3]
    
    if best_lang_name == 'Japanese (Vertical)':
        lines = best_text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        best_text = ' '.join(cleaned_lines)
    
    clean_text = re.sub(r'[^\w\s.,!?;:\-\'"]', '', best_text).strip()
    
    return clean_text, best_lang_name

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
    
    Supported languages for recognition:
    - English (horizontal)
    - Japanese (horizontal)
    - Japanese (vertical)
    
    Translation to any language is available.
    """
)

st.title("OCR Translator")
st.markdown("Upload an image with text in **English** or **Japanese** (horizontal or vertical)")

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
        st.image(processed, caption="Processed for OCR", width="stretch")
    
    with st.spinner("Recognizing text..."):
        recognized_text, detected_lang = recognize_text(image)
        
        if recognized_text and len(recognized_text) > 5:
            with st.spinner("Translating..."):
                translated_text = translate_text(recognized_text, target_lang_code)
            
            chars, words, sentences = count_stats(recognized_text)
            
            st.success(f"Recognized! Language: {detected_lang}")
            
            st.subheader("Original text (Japanese)")
            st.text(recognized_text)
            
            st.subheader(f"Translation ({TRANSLATION_LANGS[target_lang_code]})")
            if translated_text:
                st.text(translated_text)
            else:
                st.error("Translation error. Check internet connection.")
            
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Characters", chars)
            col_s2.metric("Words", words)
            col_s3.metric("Sentences", sentences)
            
        else:
            st.error("Text not found. Supported languages: English, Japanese (horizontal and vertical)")
            st.markdown("""
            - Make sure the text is clear and contrast
            - For Japanese vertical text, make sure letters are aligned
            - Try another image
            """)
