from googletrans import Translator, LANGUAGES

def translate_text(text, src_lang='en', dest_lang='zh-cn'):
    translator = Translator()
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return None


translated_program_intro = translate_text("The Child and Young Persons Psychological Wellbeing Practice PG Dip programme, a Department of Health initiative, aims to train a new workforce for CAMHS: Children’s Wellbeing Practitioners.")
print(translated_program_intro)
