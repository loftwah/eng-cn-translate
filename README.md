# Markdown Translation CLI — Detailed Design Document

---

## Title

**Markdown Translation CLI: A Flexible, OpenAI-Compatible Translation Tool**

## Overview

### Purpose

This CLI tool automates **Markdown document translation** while preserving the original formatting. It leverages any model compatible with the OpenAI API format (including GPT-4, GPT-4o, Azure OpenAI, and self-hosted APIs like Ollama or LocalAI).

### Scope

- Reads Markdown files and translates them between **English** and **Simplified Chinese** by default.
- Preserves headings, code blocks, tables, and other Markdown elements.
- Provides both a **command-line interface** (CLI) and a **watch mode** to automatically translate files on save.

### Goals

- Offer a single, flexible **CLI** that can switch between OpenAI-compatible providers by simply changing the base URL and model.
- Keep the design simple and portable, requiring only the `openai` Python package (plus optional `watchdog` for watching directories).

### Non-Goals

- Does not perform advanced text post-processing or specialized domain translations.
- Does not manage concurrency or parallel batch operations beyond a straightforward loop.

---

## Requirements

- **Python 3.7+** environment.
- **`openai`** library for connecting to OpenAI-compatible endpoints.
- **`watchdog`** library (only required for the watch feature).
- Ability to override the model, API key, and base URL using CLI arguments or environment variables.

---

## Architecture

### High-Level Structure

- **CLI (mdtranslate)**: Entry point that parses user arguments (file to translate, watch mode, batch mode, etc.).
- **Translation Logic**: Reads Markdown, constructs requests to the model, and writes translated output.
- **OpenAI-Compatible Endpoint**: Could be official OpenAI, Azure OpenAI, or any self-hosted environment that supports the same REST API format.

```
[ CLI ] --> [ Translate Manager ] --> [ OpenAI-compatible endpoint ]
```

### Data Flow

1. **User invokes CLI** with desired flags (e.g., `--model`, `--watch`).
2. **CLI** reads the file(s) and **calls** the translation routine.
3. **Translation Routine** sets up a **system prompt** for Markdown translation and sends the content via `openai.ChatCompletion.create()`.
4. **Response** is captured, and the translated text is **written** to a new file (using `_cn.md` or `_en.md` suffixes).
5. **Watch Mode** (if enabled) automatically repeats this process whenever a `.md` file is modified.

---

## Detailed Design

### Core Components

- **`translate_text`**  
  Calls the OpenAI-compatible API to translate Markdown content.
- **`process_file`**  
  Orchestrates reading a file, translating it, and writing the output.
- **`MarkdownWatcher`**  
  Uses `watchdog` to monitor files and triggers translation on changes.
- **`watch_directory`**  
  Spawns the watcher in the current directory.
- **`batch_translate`**  
  Iterates over all `.md` files (excluding `_cn.md` or `_en.md` variations) and translates each one.
- **`main`**  
  Coordinates CLI arguments using `argparse` and invokes the appropriate functionality.

### Implementation Details

The code below illustrates a complete Python file named `mdtranslate.py`:

```python
import os
import sys
import time
import argparse
import openai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Default OpenAI settings
DEFAULT_MODEL = "gpt-4o"
DEFAULT_BASE_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_api_key_here")

def translate_text(content, target_lang="zh-cn", model=DEFAULT_MODEL, base_url=DEFAULT_BASE_URL):
    """Uses an OpenAI-compatible API to translate Markdown while preserving formatting."""
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

    openai.api_key = OPENAI_API_KEY
    openai.api_base = base_url

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"Translate this Markdown document to {'Simplified Chinese' if target_lang == 'zh-cn' else 'English'}, preserving Markdown formatting."
            },
            {
                "role": "user",
                "content": content
            }
        ]
    )
    return response["choices"][0]["message"]["content"]

def process_file(filename, to_cn=True, model=DEFAULT_MODEL, base_url=DEFAULT_BASE_URL):
    """Reads a single Markdown file, translates it, and writes the output to a new file."""
    target_lang = "zh-cn" if to_cn else "en"
    suffix = "_cn.md" if to_cn else "_en.md"
    translated_filename = filename.replace(".md", suffix)

    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    translated_content = translate_text(content, target_lang, model, base_url)

    with open(translated_filename, "w", encoding="utf-8") as f:
        f.write(translated_content)

    print(f"Translated {filename} -> {translated_filename}")

class MarkdownWatcher(FileSystemEventHandler):
    """Watchdog event handler to translate Markdown files on modification."""
    def __init__(self, model, base_url):
        self.model = model
        self.base_url = base_url

    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".md") or event.src_path.endswith(("_cn.md", "_en.md")):
            return
        print(f"Detected change: {event.src_path}")
        process_file(event.src_path, to_cn=True, model=self.model, base_url=self.base_url)

def watch_directory(model=DEFAULT_MODEL, base_url=DEFAULT_BASE_URL):
    """Continuously watches the current directory for Markdown file changes."""
    observer = Observer()
    event_handler = MarkdownWatcher(model, base_url)
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    print("Watching for Markdown file changes... (Ctrl+C to exit)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def batch_translate(model=DEFAULT_MODEL, base_url=DEFAULT_BASE_URL):
    """Translates all Markdown files in the current directory (excluding already translated)."""
    for filename in os.listdir("."):
        if filename.endswith(".md") and not filename.endswith(("_cn.md", "_en.md")):
            process_file(filename, to_cn=True, model=model, base_url=base_url)

def main():
    parser = argparse.ArgumentParser(description="Translate Markdown files using OpenAI-compatible models.")
    parser.add_argument("file", nargs="?", help="Markdown file to translate")
    parser.add_argument("--to-cn", action="store_true", help="Translate to Chinese (_cn.md)")
    parser.add_argument("--to-en", action="store_true", help="Translate to English (_en.md)")
    parser.add_argument("--watch", action="store_true", help="Watch directory for Markdown changes")
    parser.add_argument("--batch", action="store_true", help="Translate all Markdown files in directory")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help="Specify OpenAI model (default: gpt-4o)")
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help="Specify OpenAI-compatible API base URL")

    args = parser.parse_args()

    if args.watch:
        watch_directory(args.model, args.base_url)
    elif args.batch:
        batch_translate(args.model, args.base_url)
    elif args.file:
        process_file(args.file, to_cn=not args.to_en, model=args.model, base_url=args.base_url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

## Usage

**Installation**

1. Clone the repository or download the script.
2. `pip install openai watchdog` (the second is only necessary for watch mode).
3. (Optional) Set `OPENAI_API_KEY` if not using a hard-coded key.

**Basic Commands**

- `mdtranslate file.md`  
  Translates `file.md` into simplified Chinese, producing `file_cn.md`.
- `mdtranslate file_cn.md --to-en`  
  Translates back to English, producing `file_cn_en.md` (or `file_en.md` if the source was `file.md`).
- `mdtranslate --batch`  
  Translates all Markdown files in the current directory to Chinese.
- `mdtranslate --watch`  
  Watches the current directory for changes and translates any modified `.md` file to Chinese.
- `mdtranslate file.md --model gpt-4`  
  Uses GPT-4 from OpenAI by changing the model parameter.
- `mdtranslate file.md --base-url http://localhost:8000`  
  Targets a local self-hosted OpenAI-compatible API.

---

## Extensions

- **GitHub Actions Integration**: Automate translation workflows on commit.
- **Multiple Languages**: Support additional language codes (`--lang es`, etc.).
- **Advanced Prompts**: Customizable system prompts for domain-specific translations.
- **Custom Output Paths**: Specify a different folder or suffix pattern for translated files.

---

## Security

- **API Keys** should be handled carefully (environment variables or secure key vault).
- **File Permissions**: Ensure sensitive files are excluded from watch or batch mode if confidentiality is required.

---

## Performance and Scalability

- The performance largely depends on the latency and capacity of the chosen model endpoint.
- For high-volume usage, batching or concurrency can be considered (though that’s not provided out of the box).
- Caching responses or partial translations could optimize repeated runs.

---

## Testing

- **Unit Tests**:  
  Use mocking for `openai.ChatCompletion.create` to verify correct request payloads and ensure the code handles success/fail scenarios.
- **Integration Tests**:  
  Run `mdtranslate` on sample files in a controlled environment to verify correct translations and file naming.
- **Watch Mode Tests**:  
  Use file modification triggers to ensure real-time translation is functioning properly.

---

## Future Improvements

- **Improved Error Handling**: Implement retry logic or backoff for API rate limits.
- **Multi-Language Watch**: Automatic detection of source language or user prompts to specify target language.
- **Front Matter Handling**: Skip or filter out front matter blocks (e.g., YAML or TOML) if required.

---

## Conclusion

This Markdown Translation CLI provides a **simple yet powerful** solution for translating Markdown documents using any **OpenAI-compatible** model. By requiring minimal dependencies and offering flexible configuration, it covers a wide range of use cases—from quick local translations to continuous integration within a repository.

Feel free to extend or integrate with more advanced workflows, and enjoy effortless switching between GPT-4, GPT-4o, Azure OpenAI, or self-hosted models—all under a unified Python CLI.
