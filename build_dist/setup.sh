#!/bin/bash
echo "🚀 Setting up BLIM environment..."
pip install -r requirements.txt
if [ ! -f "config.json" ]; then
    echo '{"blog_id": "YOUR_ID_HERE", "word_goal": 500}' > config.json
    echo "✅ Created config.json template."
fi
echo "🎉 Setup complete. Don't forget to add your client_secrets.json!"