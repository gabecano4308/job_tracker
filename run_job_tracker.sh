#!/bin/zsh

export PATH="/opt/anaconda3/bin:$PATH"
# export HOME="/Users/gcano01"

source /opt/anaconda3/etc/profile.d/conda.sh
conda activate rag_proj

cd /Users/gcano01/projects/agentic_projects/job_helper

set -a        # export variables
source .env   # load environment variables from .env file
set +a        # stop exporting variables

# Run the Python script and capture stdout and stderr
echo "$(date): Starting job search..." >> job_search.log
python main.py >> job_search.log 2>&1

# Log completion
echo "$(date): Job search completed" >> job_search.log
echo "----------------------------------------" >> job_search.log
