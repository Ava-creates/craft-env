#!/bin/bash
#SBATCH --job-name=funsearch
#SBATCH --output=funsearch_%j.out
#SBATCH --error=funsearch_%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes=2
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=187G
#SBATCH --gres=gpu:v100:4
#SBATCH --account=rrg-lelis

# Load required modules (adjust these based on your cluster's setup)
module load cuda/11.8
module load python/3.10

# Create and activate virtual environment
python -m venv funsearch_env
source funsearch_env/bin/activate

# Upgrade pip and install requirements
pip install -r requirements.txt

# Set environment variables
export TOKENIZERS_PARALLELISM=false
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the FunSearch implementation using the Python from our virtual environment
./funsearch_env/bin/python -m funsearch.implementation.funsearch 