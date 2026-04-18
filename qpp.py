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
    page_title="Universal OCR Translator | УрФУ",
    page_icon="🌍",
    layout="wide"
)

LANGUAGES = {
    'rus': '🇷🇺 Русский',
    'eng': '🇬🇧 English',
    'fra': '🇫🇷 Français',
    'deu': '🇩🇪 Deutsch',
    'spa': '🇪🇸 Español',
    'ita': '🇮🇹 Italiano',
    'ukr': '🇺🇦 Українська',
    'kaz': '🇰🇿 Қазақша',
    'por': '🇵🇹 Português',
    'nld': '🇳🇱 Nederlands',
    'pol': '🇵🇱 Polski',
    'tur': '🇹🇷 Türkçe',
    'ara': '🇸🇦 العربية',
    'hin': '🇮🇳 हिन्दी',
    'chi_sim': '🇨🇳 中文(简体)',
    'chi_tra': '🇹🇼 中文(繁體)',
    'jpn': '🇯🇵 日本語',
    'kor': '🇰🇷 한국어'
}

TRANSLATION_TARGETS = {
    'ru': 'Русский',
    'en': 'English',
    'fr': 'Français',
    'de': 'Deutsch',
    'es': 'Español',
    'it': 'Italiano',
    'uk': 'Українська',
    'kk': 'Қазақша',
    'pt': 'Português',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'tr': 'Türkçe',
    'ar': 'العربية',
    'hi': 'हिन्दी',
    'zh-cn': '中文(简体)',
    'zh-tw': '中文(繁體)',
    'ja': '日本語',
    'ko': '한국어'
}

def preprocess_image(image):
    if image.mode != 'L':
        image = image.convert('L')
    
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(2.0)
    
    return image

def recognize_text_all_languages(image):
    """Пробует распознать текст на всех доступных языках"""
    processed_img = preprocess_image(image)
    
    best_text = ""
    best_lang = None
    
    for lang_code in LANGUAGES.keys():
        try:
            text = pytesseract.image_to_string(processed_img, lang=lang_code).strip()
            if len(text) > len(best_text):
                best_text = text
                best_lang = lang_code
        except Exception as e:
            continue
    
    if best_text and len(best_text) > 3:
        clean_text = re.sub(r'[^\w\s.,!?;:\-]', '', best_text).strip()
        return clean_text, best_lang
    
    return None, None

def detect_language_from_text(text):
    if not text:
        return None, "не определён"
    try:
        lang_code = detect(text)
        return lang_code, TRANSLATION_TARGETS.get(lang_code, lang_code)
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
    chars = len(text)
    words = len(text.split())
    sentences = text.count('.') + text.count('!') + text.count('?') + text.count('。') + text.count('！') + text.count('？')
    return chars, words, sentences

st.sidebar.title("🌍 О проекте")
st.sidebar.info(
    """
    **Учебная программа:**  
    [Профессиональная переподготовка "Решение прикладных и фундаментальных задач в гуманитаристике с использованием языка программирования Python" УрФУ](https://dpo.urfu.ru/programs/92)

    **Команда проекта:**  
    - Руководитель: [ФИО]
    
    **Поддерживаемые языки:**  
    Русский, English, Français, Deutsch, Español, Italiano,  
    Українська, Қазақша, 中文, 日本語, 한국어, العربية, हिन्दी
    """
)

st.title("🌍 Universal OCR Translator")
st.markdown("Загрузите изображение с текстом на **любом языке** — приложение автоматически определит язык и переведёт")

uploaded_file = st.file_uploader(
    "Выберите изображение",
    type=["png", "jpg", "jpeg", "bmp", "tiff"]
)

target_lang_name = st.selectbox("Перевести на:", list(TRANSLATION_TARGETS.keys()), format_func=lambda x: TRANSLATION_TARGETS[x], index=0)
target_lang_code = target_lang_name

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="Оригинал", width="stretch")

    processed = preprocess_image(image)
    with col2:
        st.image(processed, caption="После обработки", width="stretch")

    with st.spinner("🔍 Распознавание текста на всех языках..."):
        recognized_text, detected_tesseract_lang = recognize_text_all_languages(image)

        if recognized_text:
            lang_code, lang_name = detect_language_from_text(recognized_text)
            
            if lang_name == "не определён" and detected_tesseract_lang:
                lang_name = LANGUAGES.get(detected_tesseract_lang, detected_tesseract_lang)

            with st.spinner("🌐 Перевод..."):
                translated_text = translate_text(recognized_text, target_lang_code)

            chars, words, sentences = count_stats(recognized_text)

            st.success(f"✅ Распознано! Язык оригинала: {lang_name}")

            col_res1, col_res2 = st.columns(2)

            with col_res1:
                st.subheader("📝 Оригинал")
                st.text_area("", recognized_text, height=200, key="orig", label_visibility="collapsed")

            with col_res2:
                st.subheader(f"🌍 Перевод ({TRANSLATION_TARGETS.get(target_lang_code, target_lang_code)})")
                if translated_text:
                    st.text_area("", translated_text, height=200, key="trans", label_visibility="collapsed")
                else:
                    st.error("❌ Ошибка перевода. Проверьте подключение к интернету.")

            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("📝 Символов", chars)
            col_s2.metric("📖 Слов", words)
            col_s3.metric("📄 Предложений", sentences)

        else:
            st.error("❌ Текст не найден. Попробуйте:")
            st.markdown("""
            - Использовать изображение с более чётким текстом
            - Убедиться, что текст контрастный
            - Для китайского/японского использовать крупный шрифт
            """)
