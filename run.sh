#!/bin/bash

# 1. Navigate to the project directory (Optional, but safer)
# cd "$(dirname "$0")"

# 2. Check if virtual environment exists, if not, create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    # 3. Activate the environment
    source venv/bin/activate
fi

# 4. Set PYTHONPATH so Python can find assets.py and other modules
export PYTHONPATH=$PYTHONPATH:.

# 5. Launch Blim!
python3 blim.py