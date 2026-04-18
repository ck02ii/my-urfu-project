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
    page_title="OCR Translator | УрФУ",
    page_icon="📖",
    layout="wide"
)

def preprocess_image(image):
    if image.mode != 'L':
        image = image.convert('L')
    
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image

def recognize_text_with_preprocessing(image, force_lang=None):
    try:
        processed_img = preprocess_image(image)

        if force_lang:
            text = pytesseract.image_to_string(processed_img, lang=force_lang)
        else:
            text = pytesseract.image_to_string(processed_img, lang='eng')

            if len(text.strip()) < 10:
                try:
                    text_rus = pytesseract.image_to_string(processed_img, lang='rus')
                    if len(text_rus.strip()) > len(text.strip()):
                        text = text_rus
                except:
                    pass

        clean_text = re.sub(r'[^\w\s.,!?;:\-]', '', text).strip()

        return clean_text if clean_text and len(clean_text) > 3 else None

    except Exception as e:
        st.error(f"Ошибка распознавания: {str(e)}")
        return None

def detect_language_from_text(text):
    if not text:
        return None, "не определён"
    try:
        lang_code = detect(text)
        lang_names = {
            'ru': '🇷🇺 Русский', 'en': '🇬🇧 English', 'fr': '🇫🇷 Français',
            'de': '🇩🇪 Deutsch', 'es': '🇪🇸 Español', 'it': '🇮🇹 Italiano',
            'uk': '🇺🇦 Українська', 'kk': '🇰🇿 Қазақша'
        }
        return lang_code, lang_names.get(lang_code, lang_code)
    except:
        return None, "не определён"

def translate_text(text, target_lang):
    if not text:
        return None
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        return None

def count_stats(text):
    return len(text), len(text.split()), text.count('.') + text.count('!') + text.count('?')

st.sidebar.title("О проекте")
st.sidebar.info(
    """
    **Учебная программа:**  
    [Профессиональная переподготовка "Решение прикладных и фундаментальных задач в гуманитаристике с использованием языка программирования Python" УрФУ](https://dpo.urfu.ru/programs/92)

    **Команда проекта:**  
    - Руководитель: [ФИО]
    """
)

st.title("Translator")
st.markdown("Загрузите изображение с текстом")

uploaded_file = st.file_uploader(
    "Выберите изображение",
    type=["png", "jpg", "jpeg", "bmp", "tiff"]
)

target_langs = {
    "Русский": "ru",
    "Английский": "en",
    "Французский": "fr",
    "Немецкий": "de",
    "Испанский": "es",
    "Итальянский": "it",
    "Китайский": "zh-cn",
    "Японский": "ja"
}
target_lang_name = st.selectbox("Перевести на:", list(target_langs.keys()), index=0)
target_lang_code = target_langs[target_lang_name]

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Оригинал", width="stretch")

    processed = preprocess_image(image)
    with col2:
        st.image(processed, caption="После обработки (для OCR)", width="stretch")

    with st.spinner("Распознавание текста..."):
        recognized_text = recognize_text_with_preprocessing(image)

        if recognized_text:
            lang_code, lang_name = detect_language_from_text(recognized_text)

            translated_text = translate_text(recognized_text, target_lang_code)

            chars, words, sentences = count_stats(recognized_text)

            st.success(f"Язык: {lang_name}")

            col_res1, col_res2 = st.columns(2)

            with col_res1:
                st.subheader("Оригинал")
                st.text_area("", recognized_text, height=200, key="orig", label_visibility="collapsed")

            with col_res2:
                st.subheader(f"Перевод ({target_lang_name})")
                if translated_text:
                    st.text_area("", translated_text, height=200, key="trans", label_visibility="collapsed")
                else:
                    st.error("Ошибка перевода")

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("Символов", chars)
            col_s2.metric("Слов", words)
            col_s3.metric("Предложений", sentences)

        else:
            st.error("Текст не найден. Попробуйте:")
            st.markdown("""
            - Использовать изображение с более чётким текстом
            - Убедиться, что текст контрастный (тёмный на светлом)
            - Увеличить изображение
            - Попробовать другое изображение
            """)
