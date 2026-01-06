#!/bin/bash
# Update .env with correct model configuration

echo "Updating .env with correct Gemini models..."

# Backup current .env
cp .env .env.backup

# Update GEMINI_MODEL (for Live API)
sed -i 's/^GEMINI_MODEL=.*/GEMINI_MODEL=gemini-2.5-flash-native-audio-preview-12-2025/' .env

# Add or update GEMINI_PROCESSING_MODEL (for SOP processing)
if grep -q "^GEMINI_PROCESSING_MODEL=" .env; then
    sed -i 's/^GEMINI_PROCESSING_MODEL=.*/GEMINI_PROCESSING_MODEL=gemini-3-pro-preview/' .env
else
    echo "GEMINI_PROCESSING_MODEL=gemini-3-pro-preview" >> .env
fi

echo "✅ Updated .env file"
echo ""
echo "Current configuration:"
grep "GEMINI" .env

chmod +x update_env_models.sh
