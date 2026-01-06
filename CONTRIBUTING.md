# Contributing to Gemini Voice Bot

Thank you for your interest in contributing to the Gemini Voice Bot project! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- **Bug Reports:** Report issues you encounter
- **Feature Requests:** Suggest new features or improvements
- **Code Contributions:** Submit bug fixes or new features
- **Documentation:** Improve or expand documentation
- **Testing:** Help test new features and report results

## 🚀 Getting Started

### Setting Up Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/gemini-voice-bot.git
cd gemini-voice-bot
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up configuration**

```bash
cp .env.example .env
# Add your API key to .env
```

5. **Run setup verification**

```bash
python test_setup.py
```

## 📝 Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Add docstrings to all functions and classes
- Keep functions focused and under 50 lines when possible

**Example:**

```python
def process_query(self, query: str) -> str:
    """
    Process a text query and return response
    
    Args:
        query: User query text
        
    Returns:
        Response text in Tanglish
    """
    # Implementation
    pass
```

### Commit Messages

Use clear, descriptive commit messages:

- **Format:** `<type>: <subject>`
- **Types:** feat, fix, docs, style, refactor, test, chore

**Examples:**

```
feat: Add support for markdown SOP files
fix: Handle empty audio files gracefully
docs: Update installation instructions
refactor: Simplify RAG engine logic
test: Add tests for document parser
```

### Branch Naming

- **Features:** `feature/description`
- **Bug Fixes:** `bugfix/description`
- **Documentation:** `docs/description`

**Examples:**

```
feature/add-markdown-support
bugfix/fix-audio-transcription
docs/update-setup-guide
```

## 🔧 Adding New Features

### 1. Document Formats

To add support for new document formats:

**Location:** `src/sop_loader/document_parser.py`

```python
def _parse_markdown(self, file_path: Path) -> List[DocumentChunk]:
    """Parse Markdown document"""
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Your parsing logic here
        chunk = DocumentChunk(
            content=content,
            source=file_path.name,
            metadata={'format': 'markdown'}
        )
        chunks.append(chunk)
    except Exception as e:
        logger.error(f"Error parsing Markdown {file_path.name}: {e}")
        raise
    
    return chunks
```

Update `SUPPORTED_FORMATS`:

```python
SUPPORTED_FORMATS = {'.pdf', '.docx', '.txt', '.md'}
```

### 2. Voice Providers

To add alternative TTS/STT providers:

**Location:** `src/voice_handler/`

Create new file `custom_tts.py`:

```python
class CustomTTS:
    """Custom text-to-speech provider"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def synthesize_speech(self, text: str) -> bytes:
        """Synthesize speech from text"""
        # Implementation
        pass
```

### 3. Retrieval Strategies

To implement custom retrieval logic:

**Location:** `src/retrieval/rag_engine.py`

```python
def retrieve_context_with_reranking(self, query: str) -> Dict:
    """Retrieve context with additional reranking step"""
    # Initial retrieval
    results = self.vector_store.search(query, top_k=10)
    
    # Rerank results
    reranked = self._rerank_results(results, query)
    
    # Return top results
    return self._format_results(reranked[:self.top_k])
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_document_parser.py

# Run with coverage
python -m pytest --cov=src
```

### Writing Tests

Create test files in `tests/` directory:

```python
import pytest
from src.sop_loader import DocumentParser

def test_parse_txt_file():
    """Test parsing of TXT files"""
    parser = DocumentParser(Path("tests/fixtures/sops"))
    chunks = parser._parse_txt(Path("tests/fixtures/sample.txt"))
    
    assert len(chunks) > 0
    assert chunks[0].content
    assert chunks[0].source == "sample.txt"
```

### Test Coverage Guidelines

- Aim for >80% code coverage
- Test both success and error cases
- Mock external API calls
- Use fixtures for test data

## 📚 Documentation

### Adding Documentation

- Update README.md for user-facing features
- Update ARCHITECTURE.md for technical changes
- Add inline comments for complex logic
- Update SETUP_GUIDE.md for new setup steps

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up-to-date with code

## 🔍 Code Review Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No sensitive data in commits

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
Describe how you tested the changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.0]
- Package versions: [from pip list]

**Logs**
Relevant log output

**Screenshots**
If applicable
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How would you implement it?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Any other relevant information
```

## 🔐 Security

### Reporting Security Issues

**Do NOT** open public issues for security vulnerabilities.

Instead:
1. Email security concerns to the maintainers
2. Include detailed description
3. Wait for acknowledgment before disclosure

### Security Guidelines

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all user inputs
- Keep dependencies updated

## 📦 Release Process

### Version Numbering

Follow Semantic Versioning (SemVer):
- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes

### Release Checklist

- [ ] Update version in `src/__init__.py`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create git tag
- [ ] Build and test package
- [ ] Deploy to production

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers
- Focus on the project's goals

### Communication

- Use clear, professional language
- Be patient with responses
- Provide context in discussions
- Ask questions when unclear

## 📞 Getting Help

- **Issues:** Use GitHub Issues for bugs and features
- **Discussions:** Use GitHub Discussions for questions
- **Documentation:** Check README.md and ARCHITECTURE.md
- **Code Examples:** See `examples/` directory

## 🎓 Learning Resources

### Recommended Reading

- [Gemini API Documentation](https://ai.google.dev/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Architecture Guide](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [Python Best Practices](https://docs.python-guide.org/)

### Example Projects

- See `examples/` directory for sample implementations
- Check `tests/` for usage patterns

## 📋 Checklist for Contributors

Before submitting a contribution:

- [ ] Read and understood contribution guidelines
- [ ] Set up development environment
- [ ] Created feature branch
- [ ] Implemented changes with tests
- [ ] Updated documentation
- [ ] Ran test suite locally
- [ ] Committed with clear messages
- [ ] Created pull request with description

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Questions?** Open a GitHub Discussion or check existing documentation.

**Need Help?** Don't hesitate to ask - we're here to help!
