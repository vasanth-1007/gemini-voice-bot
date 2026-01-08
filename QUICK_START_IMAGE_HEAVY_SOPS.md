# 🚀 Quick Start: Image-Heavy SOPs

## 2-Minute Setup for Image Support

### Step 1: Install Image Dependencies (30 seconds)
```bash
pip install PyMuPDF Pillow
```

### Step 2: Verify Setup (30 seconds)
```bash
python test_image_support.py
```

### Step 3: Add Your SOPs (1 minute)
```bash
# Copy your image-heavy PDFs to sops folder
cp your_handbook.pdf sops/
cp your_procedures.pdf sops/
```

### Step 4: Run & Index (30 seconds)
```bash
python main.py
# Select Option 1: Load and index SOPs
# Watch as images are automatically processed!
```

---

## 🎯 That's It!

Your bot now understands:
- ✅ Text content (as before)
- ✅ **Images in PDFs (NEW!)**
  - Flowcharts
  - Tables
  - Screenshots
  - Diagrams
  - Forms

---

## 💬 Example Usage

**Your image-heavy SOP has:**
- Page 1: Text + Escalation Flowchart
- Page 2: Text + Expense Limits Table
- Page 3: Text + Portal Screenshot

**You can now ask:**

```
Q: "What is the escalation process?"
A: "Escalation process la three levels iruku. First level team lead, 
   second level manager, third level senior management ku escalate 
   pannanum. Flowchart la clearly show pannirukanga each step."
```

```
Q: "What are the expense limits?"
A: "Expense limits table la detail-a iruku. Travel ku no limit but 
   receipt mandatory. Client entertainment ku $500 per month. 
   Office supplies ku manager approval venumnu."
```

---

## 📊 What Happens During Indexing

```
Processing your_handbook.pdf...
├── ✓ Extracting text from 10 pages (3 seconds)
├── ✓ Found 5 images
├── ✓ Analyzing image 1/5 (flowchart) (2 seconds)
├── ✓ Analyzing image 2/5 (table) (2 seconds)
├── ✓ Analyzing image 3/5 (screenshot) (2 seconds)
├── ✓ Analyzing image 4/5 (diagram) (2 seconds)
└── ✓ Analyzing image 5/5 (form) (2 seconds)

Total: 13 seconds for first-time processing
Future queries: 2-5 seconds (descriptions cached!)
```

---

## ⚡ Key Features

1. **Automatic**: No configuration needed
2. **Smart Filtering**: Ignores logos, icons, small images
3. **Fast Queries**: Image descriptions cached in vector DB
4. **Tanglish**: Answers about images in natural Tamil-English mix
5. **Seamless**: Works alongside text content

---

## 🔍 Behind the Scenes

```python
# When you load SOPs:

1. Text Extraction (PyPDF2)
   → "Leave policy requires manager approval..."

2. Image Detection (PyMuPDF)
   → Found flowchart on page 3

3. Vision Analysis (Gemini Vision API)
   → "This flowchart shows a 3-tier escalation process..."

4. RAG Indexing (ChromaDB)
   → Both text and image descriptions searchable

5. Your Query
   → "What is the escalation process?"

6. Retrieval (Top-K Search)
   → Text: "Follow escalation process..."
   → Image: "Flowchart shows 3 levels..."

7. Response (Gemini + Tanglish)
   → Combined answer using both sources!
```

---

## ✅ Verification Checklist

- [ ] PyMuPDF installed: `pip show PyMuPDF`
- [ ] Pillow installed: `pip show Pillow`
- [ ] API key in .env: `cat .env | grep GOOGLE_API_KEY`
- [ ] PDF files in sops/: `ls sops/*.pdf`
- [ ] Test passed: `python test_image_support.py`

---

## 🎓 Tips for Best Results

### ✅ DO:
- Use high-quality PDFs (not scanned)
- Keep images clear and readable
- Add your most important documents first
- Check logs for processing progress

### ❌ DON'T:
- Don't use very low-resolution images
- Don't worry about small logos (auto-filtered)
- Don't re-process unnecessarily (use existing index)

---

## 📱 Mobile Quick Reference

```bash
# Install
pip install PyMuPDF Pillow

# Test
python test_image_support.py

# Run
python main.py
> Option 1 (Load SOPs)
> Option 2 (Ask questions!)
```

---

## 🆘 Common Issues

**"PyMuPDF not available"**
→ `pip install PyMuPDF`

**"Image extraction disabled"**
→ Check API key in .env file

**"No images found"**
→ Make sure files are PDFs with embedded images

**Processing too slow?**
→ Normal for first time (images are analyzed)
→ Future queries are fast!

---

## 📞 Need Help?

1. Read: `IMAGE_SUPPORT_GUIDE.md` (detailed guide)
2. Test: `python test_image_support.py`
3. Check logs: `tail -f gemini_voice_bot.log`

---

## 🎉 Success Indicators

When you load SOPs, you should see:

```
✓ Image extraction enabled
✓ Extracting images from handbook.pdf...
✓ Found 8 images on page 3
✓ Generated description for image from page 3
✓ Loaded 5 image chunks from handbook.pdf
```

Then you can ask questions about images naturally!

---

**Total time:** 2 minutes
**New capabilities:** Unlimited
**Your SOPs:** Fully understood (text + images)! 📸✨
