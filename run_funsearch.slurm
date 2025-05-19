#!/bin/bash
#SBATCH --job-name=funsearch
#SBATCH --output=funsearch_%j.out
#SBATCH --error=funsearch_%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=100G
#SBATCH --gres=gpu:a100:1
#SBATCH --account=rrg-lelis


# Create and activate virtual environment
python -m venv funsearch_env
source funsearch_env/bin/activate

# Upgrade pip and install requirements
pip install -r requirements.txt

# Set environment variables
export TOKENIZERS_PARALLELISM=false

# Run the FunSearch implementation
python -m funsearch.implementation.funsearch 