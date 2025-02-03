import os
import sys
import time
import argparse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Default settings
DEFAULT_MODEL = "gpt-4o"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

def translate_text(content, target_lang="zh-cn"):
    """Uses the gpt-4o model to translate Markdown while preserving formatting."""
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"Translate this Markdown document to {'Simplified Chinese' if target_lang == 'zh-cn' else 'English'}, preserving all Markdown formatting exactly."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )
    return response.choices[0].message.content

def verify_translation(original, translated, target_lang="zh-cn"):
    """Verifies the translation quality and returns a score and feedback."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    direction = "Chinese to English" if target_lang == "en" else "English to Chinese"
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"You are a translation quality expert. Compare the original and translated Markdown documents and provide: \n"
                          f"1. A score from 0-100\n"
                          f"2. Brief feedback on accuracy and preservation of formatting\n"
                          f"3. Specific issues found (if any)"
            },
            {
                "role": "user",
                "content": f"Direction: {direction}\n\nOriginal:\n{original}\n\nTranslation:\n{translated}"
            }
        ]
    )
    return response.choices[0].message.content

def process_file(filename, to_cn=True):
    """Reads a single Markdown file, translates it, and writes the output to a new file."""
    target_lang = "zh-cn" if to_cn else "en"
    suffix = "_cn.md" if to_cn else "_en.md"
    
    file_path = Path(filename)
    translated_filename = file_path.stem + suffix

    try:
        with open(filename, "r", encoding="utf-8") as f:
            original_content = f.read()

        translated_content = translate_text(original_content, target_lang)

        with open(translated_filename, "w", encoding="utf-8") as f:
            f.write(translated_content)

        print(f"Translated {filename} -> {translated_filename}")
        
        # Verify translation quality
        print("\nVerifying translation quality...")
        verification_result = verify_translation(original_content, translated_content, target_lang)
        print(f"\nQuality Assessment:\n{verification_result}")
        
    except Exception as e:
        print(f"Error processing {filename}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files using o3-mini model")
    parser.add_argument("file", help="Markdown file to translate")
    parser.add_argument("--to-cn", action="store_true", help="Translate to Chinese (default)")
    parser.add_argument("--to-en", action="store_true", help="Translate to English")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)

    process_file(args.file, to_cn=not args.to_en)

if __name__ == "__main__":
    main() 