import asyncio
import polib
import googletrans
from googletrans import Translator

async def translate_po_file(input_po_file, output_po_file, target_language):
    # Load the PO file
    po = polib.pofile(input_po_file)
    async with Translator() as translator:
        for entry in po:
            if not entry.translated():  # Only translate empty translations
                try:
                    translation = await translator.translate(entry.msgid, dest=target_language)
                    entry.msgstr = translation.text
                    print(f"Translated: {entry.msgid} -> {translation.text}")
                except Exception as e:
                    print(f"Error translating '{entry.msgid}': {e}")
    
    # Save the translated PO file
    po.save(output_po_file)
    print(f"Translation complete. Translated file saved as {output_po_file}")

async def main():
    target_lang = "nl"  # Target language (e.g., 'es' for Spanish, 'fr' for French)
    input_po = f"locale/{target_lang}/LC_MESSAGES/django.po"  # Input PO file path
    output_po = f"locale/{target_lang}/LC_MESSAGES/django_translated.po"  # Output translated PO file path
    await translate_po_file(input_po, output_po, target_lang)

if __name__ == "__main__":
    asyncio.run(main())
