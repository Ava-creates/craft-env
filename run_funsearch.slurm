#!/bin/bash
#SBATCH --job-name=funsearch
#SBATCH --output=funsearch_%j.out
#SBATCH --error=funsearch_%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=100G
#SBATCH --gres=gpu:v100l:2
#SBATCH --account=rrg-lelis


# Create and activate virtual environment
# --gres=gpu:a100_4g.20gb:1 arval
source funsearch_env/bin/activate
pip install -r requirements.txt

# Set environment variables
export TOKENIZERS_PARALLELISM=false

# Run the FunSearch implementation
python -m funsearch.implementation.funsearch --model_type="huggingface"