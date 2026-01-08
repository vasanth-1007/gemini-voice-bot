#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}==================================================================${NC}"
echo -e "${CYAN}  Push Gemini Voice Bot to GitHub${NC}"
echo -e "${CYAN}==================================================================${NC}"
echo ""

# Step 1: Remove sensitive files from git (if accidentally added)
echo -e "${YELLOW}[1/4] Removing sensitive files from git...${NC}"
git rm --cached .env.backup 2>/dev/null && echo -e "${GREEN}✓ Removed .env.backup from git${NC}" || echo -e "${YELLOW}  (already removed or not tracked)${NC}"
git rm --cached .env 2>/dev/null && echo -e "${GREEN}✓ Removed .env from git${NC}" || echo -e "${YELLOW}  (already removed or not tracked)${NC}"
git rm --cached -r venv/ 2>/dev/null && echo -e "${GREEN}✓ Removed venv/ from git${NC}" || echo -e "${YELLOW}  (already removed or not tracked)${NC}"
git rm --cached *.log 2>/dev/null && echo -e "${GREEN}✓ Removed log files from git${NC}" || echo -e "${YELLOW}  (already removed or not tracked)${NC}"
echo ""

# Step 2: Verify .gitignore is working
echo -e "${YELLOW}[2/4] Verifying .gitignore...${NC}"
if git ls-files | grep -E "^\.env$|^\.env\.backup$|^venv/"; then
    echo -e "${RED}✗ ERROR: Sensitive files still in git!${NC}"
    echo -e "${RED}Please manually run: git rm --cached <file>${NC}"
    exit 1
else
    echo -e "${GREEN}✓ No sensitive files in git${NC}"
fi
echo ""

# Step 3: Amend commit to remove sensitive files
echo -e "${YELLOW}[3/4] Updating commit...${NC}"
git add .
git commit --amend -m "feat: Add Gemini Voice Bot with Live API support

- Implement voice-enabled RAG system for SOP queries
- Add Gemini 2.0 Flash Live API integration with real-time audio
- Support text, voice, and web interfaces
- Include image processing and extraction from PDFs
- Add vector store with ChromaDB for efficient retrieval
- Fix audio format handling for browser PCM to Gemini API
- Configure proper realtime_input_config for Live API
- Add comprehensive documentation and setup guides

Key Features:
- Real-time voice conversations with Gemini 2.0
- Multi-modal SOP processing (text, images, tables)
- Web interface with live audio streaming
- RAG pipeline with context-aware responses
- Voice Activity Detection (VAD) support

Tech Stack:
- Google Gemini 2.0 Flash (Live API)
- Flask + Socket.IO for web interface
- ChromaDB for vector storage
- PyMuPDF for document processing
- Web Audio API for browser audio capture"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Commit updated${NC}"
else
    echo -e "${RED}✗ Commit update failed${NC}"
    exit 1
fi
echo ""

# Step 4: Push to GitHub
echo -e "${YELLOW}[4/4] Pushing to GitHub...${NC}"
echo -e "${CYAN}Remote: https://github.com/vasanth-1007/gemini-voice-bot.git${NC}"
echo ""

git push -u origin master --force

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓✓✓ Successfully pushed to GitHub! ✓✓✓${NC}"
    echo ""
    echo -e "${CYAN}==================================================================${NC}"
    echo -e "${GREEN}View your repository at:${NC}"
    echo -e "${CYAN}https://github.com/vasanth-1007/gemini-voice-bot${NC}"
    echo -e "${CYAN}==================================================================${NC}"
    echo ""
    echo -e "${YELLOW}Important: Verify these files are NOT visible on GitHub:${NC}"
    echo "  ❌ .env"
    echo "  ❌ .env.backup"
    echo "  ❌ venv/"
    echo "  ❌ *.log files"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Push failed${NC}"
    echo "Please check your GitHub credentials and network connection"
    exit 1
fi
