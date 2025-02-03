# Markdown Translation CLI

A flexible CLI tool that translates Markdown documents between English and Chinese while preserving formatting. It works with any OpenAI-compatible API (including GPT-4, GPT-4o, Azure OpenAI, and self-hosted APIs like Ollama or LocalAI).

## Features

- Preserves all Markdown formatting (headings, code blocks, tables, etc.)
- Translates between English and Simplified Chinese
- Verifies translation quality with automated scoring
- Supports any OpenAI-compatible API endpoint

## Installation

1. Clone this repository:

```bash
git clone https://github.com/loftwah/eng-cn-translate
cd eng-cn-translate
```

2. Install dependencies:

```bash
uv pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Translation

Translate English to Chinese:

```bash
uv run mdtranslate.py file.md
```

Translate Chinese to English:

```bash
uv run mdtranslate.py file.md --to-en
```

### Testing

Run the test suite:

```bash
./test_translation.sh
```

This will:

1. Test English to Chinese translation
2. Test Chinese to English translation
3. Verify translation quality for both directions
4. Generate translated files with quality scores

## Output Files

- English to Chinese: `{filename}_cn.md`
- Chinese to English: `{filename}_en.md`

Each translation includes a quality assessment with:

- Score (0-100)
- Feedback on accuracy
- Format preservation verification
- Specific issues (if any)

## Advanced Usage

### API Configuration

You can configure different API endpoints by setting these environment variables:

```bash
OPENAI_API_BASE=https://your-api-endpoint
OPENAI_API_MODEL=gpt-4  # or your preferred model
```

### Quality Control

Each translation is automatically evaluated for:
- Semantic accuracy
- Format preservation
- Cultural appropriateness
- Technical terminology accuracy

Quality scores below 80 will generate warnings in the output.

## Requirements

- Python 3.7+
- OpenAI API key
- `openai` Python package
- `python-dotenv`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
