import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance
from deep_translator import GoogleTranslator
import re
import sys

if sys.platform == 'win32':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

st.set_page_config(
    page_title="OCR Перевод с изображений",
    page_icon="📖",
    layout="wide"
)

TRANSLATION_LANGS = {
    'ru': 'Русский',
    'en': 'Английский',
    'fr': 'Французский',
    'de': 'Немецкий',
    'es': 'Испанский',
    'it': 'Итальянский',
    'zh-cn': 'Китайский',
    'ko': 'Корейский'
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

st.title("📖 OCR Перевод с изображений")
st.markdown("Загрузите изображение с горизонтальным текстом на английском или японском языке")

# Кнопка загрузки с объединённым действием
uploaded_file = st.file_uploader(
    "Загрузить и распознать",
    type=["png", "jpg", "jpeg", "bmp", "tiff"],
    label_visibility="visible"
)

target_lang_name = st.selectbox(
    "Перевести на:", 
    list(TRANSLATION_LANGS.keys()),
    format_func=lambda x: TRANSLATION_LANGS[x],
    index=0
)
target_lang_code = target_lang_name

st.subheader("Настройки распознавания")
force_lang = st.radio(
    "Принудительный язык распознавания:",
    ["Автоопределение", "Только английский", "Только японский"],
    index=0
)

# Кнопка запуска обработки
if st.button("🔍 Распознать и перевести", type="primary", use_container_width=True):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="Оригинал", use_container_width=True)
        
        processed = preprocess_image(image)
        with col2:
            st.image(processed, caption="Обработано для OCR", use_container_width=True)
        
        with st.spinner("Распознавание текста..."):
            if force_lang == "Только английский":
                recognized_text = pytesseract.image_to_string(processed, lang='eng').strip()
                detected_lang = "Английский"
            elif force_lang == "Только японский":
                recognized_text = pytesseract.image_to_string(processed, lang='jpn').strip()
                detected_lang = "Японский"
            else:
                jpn_text = pytesseract.image_to_string(processed, lang='jpn').strip()
                eng_text = pytesseract.image_to_string(processed, lang='eng').strip()
                
                if len(jpn_text) > len(eng_text) and len(jpn_text) > 5:
                    recognized_text = jpn_text
                    detected_lang = "Японский"
                elif len(eng_text) > 5:
                    recognized_text = eng_text
                    detected_lang = "Английский"
                else:
                    recognized_text = None
                    detected_lang = None
            
            if recognized_text and len(recognized_text) > 3:
                with st.spinner("Перевод..."):
                    translated_text = translate_text(recognized_text, target_lang_code)
                
                chars, words, sentences = count_stats(recognized_text)
                
                st.success(f"✅ Распознано! Язык: {detected_lang}")
                
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.subheader("Оригинальный текст")
                    st.text_area("", recognized_text, height=200, key="orig", label_visibility="collapsed")
                
                with col_res2:
                    st.subheader(f"Перевод ({TRANSLATION_LANGS[target_lang_code]})")
                    if translated_text:
                        st.text_area("", translated_text, height=200, key="trans", label_visibility="collapsed")
                    else:
                        st.error("Ошибка перевода. Проверьте интернет-соединение.")
                
                col_s1, col_s2, col_s3 = st.columns(3)
                col_s1.metric("Символов", chars)
                col_s2.metric("Слов", words)
                col_s3.metric("Предложений", sentences)
                
            else:
                st.error("Текст не найден. Попробуйте:")
                st.markdown("""
                - Выберите принудительно «Только японский» в настройках распознавания
                - Убедитесь, что изображение не повёрнуто
                - Используйте чёткий печатный шрифт
                - Попробуйте другое изображение
                """)
    else:
        st.warning("⚠️ Сначала загрузите изображение")
