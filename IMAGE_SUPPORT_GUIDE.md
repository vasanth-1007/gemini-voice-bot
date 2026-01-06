# 📸 Image Support Guide - Gemini Voice Bot

## Overview

Your Gemini Voice Bot now supports **image-heavy SOP documents**! The system can:
- ✅ Extract images from PDF files
- ✅ Analyze images using Gemini Vision API
- ✅ Understand diagrams, flowcharts, tables, and screenshots
- ✅ Include image descriptions in search results
- ✅ Answer questions about visual content in your SOPs

---

## 🚀 Quick Setup

### 1. Install Additional Dependencies

```bash
pip install PyMuPDF Pillow
```

These packages enable advanced image extraction from PDFs.

### 2. That's It!

The image extraction is **automatically enabled** when you have:
- ✅ PyMuPDF installed
- ✅ Your Gemini API key configured in `.env`

No additional configuration needed!

---

## 🎯 How It Works

### Automatic Processing

When you load SOP documents (Option 1 in the menu):

1. **Text Extraction** - Extracts all text content as before
2. **Image Detection** - Finds all images in PDF files
3. **Image Filtering** - Removes small images (logos, icons)
4. **Vision Analysis** - Uses Gemini Vision to understand each image
5. **Indexing** - Adds image descriptions to the searchable knowledge base

### Example Flow

```
PDF Document
    ├── Page 1: Text + Flowchart
    ├── Page 2: Text + Table
    └── Page 3: Text + Screenshot

After Processing:
    ├── Text Chunks (1, 2, 3)
    ├── [IMAGE from page 1]: "Flowchart showing the leave approval process..."
    ├── [IMAGE from page 2]: "Table listing expense categories and limits..."
    └── [IMAGE from page 3]: "Screenshot of the HR portal login page..."
```

---

## 🎨 What Images Are Analyzed

### ✅ Supported Image Types

- **Flowcharts** - Process diagrams, decision trees
- **Tables** - Data tables, comparison charts
- **Screenshots** - Software UI, portal pages
- **Diagrams** - Architecture diagrams, org charts
- **Forms** - Templates, checklists
- **Infographics** - Visual guides, posters

### ⚠️ Filtered Out (Automatically)

- Small images (< 100x100 pixels)
- Logos and icons
- Decorative elements
- Page numbers, headers, footers

---

## 💬 Example Questions You Can Ask

### About Flowcharts
```
Q: "What is the escalation process?"
A: "Escalation process la three levels iruku. First level la team lead ku report pannanum. 
   Issue resolve aakaatina, department manager ku escalate pannanum. Critical issues ku 
   senior management kitta poga vendiyathu."
```

### About Tables
```
Q: "What are the expense limits?"
A: "Expense limits table la iruku. Travel expenses ku limit illa, but receipts mandatory. 
   Client entertainment ku 500 dollars per month. Office supplies ku manager approval venumnu."
```

### About Screenshots
```
Q: "How to reset password in the portal?"
A: "Portal la 'Forgot Password' link click pannunga. Employee ID enter pannanum. 
   Apram registered mobile number ku OTP varum. OTP enter panna new password set panna mudiyum."
```

---

## 🔧 Configuration Options

### Control Image Processing

Edit `config.py` to customize:

```python
# In config.py, add these options:
class Config(BaseModel):
    # ... existing config ...
    
    # Image extraction settings
    extract_images: bool = True  # Enable/disable image extraction
    max_images_per_doc: Optional[int] = None  # Limit images processed (None = all)
    min_image_size: int = 100  # Minimum width/height in pixels
```

### Disable Image Extraction (If Needed)

If you want text-only processing:

```python
# In src/voice_assistant.py
self.document_parser = DocumentParser(
    sop_folder=self.config.sop_folder,
    api_key=self.config.google_api_key,
    extract_images=False  # Disable image extraction
)
```

---

## 📊 Viewing Image Processing Stats

After loading documents, check the logs to see:

```
INFO - Extracting images from policy_handbook.pdf...
INFO - Found 8 images on page 3
INFO - Filtered to 5 significant images (>=100px)
INFO - Generated description for image from page 3
INFO - Image extraction stats: {'total_images': 5, 'images_with_descriptions': 5, 'pages_with_images': 3}
INFO - Loaded 5 image chunks from policy_handbook.pdf
```

Use **Option 5** (System Statistics) to see if image extraction is enabled:
```
SOP Documents:
  total_files: 3
  supported_files: 3
  image_extraction_enabled: True  ← Check this
```

---

## 🎯 Best Practices for Image-Heavy SOPs

### 1. **Use High-Quality PDFs**
- Clear, readable images work best
- Avoid heavily compressed or pixelated images
- Native PDFs better than scanned documents

### 2. **Organize Images Logically**
- Keep related images on the same page as explanatory text
- Use captions when possible
- Label diagrams clearly

### 3. **First-Time Indexing May Take Longer**
- Image analysis uses Gemini Vision API
- Processing time: ~2-5 seconds per image
- Subsequent queries are fast (uses cached descriptions)

### 4. **Monitor API Usage**
- Each image requires one Gemini API call
- For documents with many images, consider:
  - Processing in batches
  - Setting `max_images_per_doc` limit
  - Using high-quality images only

---

## 🐛 Troubleshooting

### Issue: "PyMuPDF not available"

**Solution:**
```bash
pip install PyMuPDF Pillow
```

### Issue: "Image extraction disabled"

**Check:**
1. PyMuPDF installed? `pip list | grep PyMuPDF`
2. API key configured? Check `.env` file
3. Logs show: `logger.info("Image extraction enabled")`

**Force enable:**
```python
# Verify in logs when starting:
# Should see: "Image extraction enabled"
```

### Issue: Images not being analyzed

**Possible causes:**
- Images too small (< 100x100 pixels)
- API quota exceeded
- Network issues

**Check logs:**
```bash
tail -f gemini_voice_bot.log | grep -i image
```

### Issue: Processing too slow

**Solutions:**
1. Limit images per document:
```python
processed_images = self.image_extractor.process_document_images(
    pdf_path=file_path,
    max_images=10  # Process first 10 only
)
```

2. Increase minimum image size:
```python
min_size = 200  # Only process images >= 200px
```

3. Process documents in batches (manual)

---

## 💡 Performance Considerations

### Processing Times

| Document Type | Text Extraction | Image Extraction | Total |
|--------------|----------------|------------------|-------|
| Text-only PDF (10 pages) | 2-3 seconds | - | 2-3 seconds |
| PDF with 5 images | 2 seconds | 10-15 seconds | 12-17 seconds |
| Image-heavy PDF (20 images) | 3 seconds | 40-60 seconds | 43-63 seconds |

### After Initial Indexing

- **Query time:** 2-5 seconds (same as text-only)
- **Image descriptions cached** in vector database
- No re-processing needed unless you rebuild index

### Optimization Tips

1. **First Run:** Allow time for image processing
2. **Subsequent Runs:** Use existing index (skip Option 1)
3. **Large Documents:** Process offline, then deploy index
4. **Production:** Consider pre-processing documents before deployment

---

## 🎨 What Gemini Vision Extracts

### From Flowcharts
- Process steps and sequence
- Decision points
- Start/end points
- Connections between steps
- Labels and annotations

### From Tables
- Column headers
- Row data
- Relationships between data
- Key figures and statistics

### From Screenshots
- UI elements visible
- Navigation paths
- Button labels
- Input fields
- Instructions or text overlay

### From Diagrams
- Component names
- Relationships/connections
- Hierarchy or structure
- Labels and legends
- Directional flows

---

## 📈 API Usage & Costs

### Gemini API Calls

**Per Document:**
- Text processing: 1-2 calls (chunking)
- Per image: 1 call (vision analysis)

**Example:**
- 10-page PDF with 8 images = ~10 API calls
- Text extraction is free, vision calls count toward quota

### Managing Costs

1. **Filter small images** (done automatically)
2. **Set max images per document**
3. **Process high-priority documents first**
4. **Batch process during off-hours**

---

## 🧪 Testing Image Support

### Test with Sample Image-Heavy PDF

1. **Add an image-heavy PDF** to `sops/` folder

2. **Run the bot:**
```bash
python main.py
```

3. **Select Option 1** (Load and index SOPs)
   - Watch logs for "Extracting images from..."
   - Note: First time will take longer

4. **Select Option 2** (Ask a question)
   - Ask about content in images
   - Example: "What does the process flowchart show?"

5. **Check the response** includes image descriptions

### Verify in Logs

```bash
# View image processing
grep -i "image" gemini_voice_bot.log

# Should see:
# - "Image extraction enabled"
# - "Extracting images from [filename]"
# - "Generated description for image from page X"
# - "Loaded X image chunks from [filename]"
```

---

## 🔄 Updating SOPs with Images

### When You Add New Image-Heavy Documents

1. Copy new PDF to `sops/` folder
2. Run application: `python main.py`
3. Select **Option 6** (Rebuild index)
4. Images will be automatically extracted and analyzed
5. New content immediately searchable

### When You Update Existing Documents

Same process - rebuild index to re-extract everything including new images.

---

## 🎯 Real-World Examples

### HR Policy Handbook
```
Text: "Follow the escalation matrix for all customer issues"
Image: Flowchart showing 3-tier escalation process
Result: Bot can explain the visual escalation steps in Tanglish
```

### IT Support Guide
```
Text: "Reset password using the employee portal"
Image: Screenshot of portal login and reset process
Result: Bot can guide users through the visual interface
```

### Expense Reimbursement
```
Text: "Refer to the expense category table"
Image: Table with categories, limits, and approval requirements
Result: Bot can answer specific questions about limits and categories
```

---

## ✅ Summary

Your Gemini Voice Bot now handles image-heavy SOPs automatically:

- ✅ **Zero configuration** needed (works out of the box)
- ✅ **Automatic filtering** of insignificant images
- ✅ **Intelligent analysis** using Gemini Vision
- ✅ **Seamless integration** with existing RAG pipeline
- ✅ **Natural responses** including visual content in Tanglish

**Questions about images are answered just like text questions** - the system automatically retrieves relevant image descriptions along with text content.

---

## 🆘 Need Help?

1. **Installation issues:** Check PyMuPDF and Pillow installation
2. **Processing issues:** Review logs for specific errors
3. **Performance issues:** Consider limiting images or processing in batches
4. **API issues:** Check quota and rate limits in Google Cloud Console

---

**Ready to test with your image-heavy SOPs?**

```bash
# Install dependencies
pip install PyMuPDF Pillow

# Run the bot
python main.py

# Load your image-heavy SOPs (Option 1)
# Ask questions about visual content!
```

---

*Image support powered by Gemini Vision API* 📸🤖
