## Overview

This repository provides a lightweight end-to-end pipeline for building a sentiment analysis dataset from YouTube comments and fine-tuning a pretrained model on it.

The project is aimed at small-to-medium scale experiments, where the usual workflow is:

1. scrape comments from a YouTube video,
2. clean and normalize the text,
3. split the cleaned data for manual labeling,
4. merge labeled CSV files into one dataset,
5. fine-tune a pretrained transformer model.

The repo is focused on **text classification**. It is built around Indonesian sentiment analysis, but the same scaffold can be adapted for other text classification tasks by changing the dataset, label mapping, and sometimes the base model in `src/train.py`.

## Pipeline

### 1. Scrape

`src/scrape.py` collects comments from a YouTube video and saves raw JSON files into `scrape/`.

- Configure the target video with `VIDEO_URL` in `.env`.
- Limit the number of collected comments with `TARGET_COMMENT`.

### 2. Clean

`src/cleaning.py` normalizes the raw text and writes cleaned per-video CSV files into `cleaned/`.

- Output format: one quoted column named `content`.
- This script also triggers the split step automatically.

### 3. Split

`src/split.py` splits each cleaned CSV into smaller chunks for manual labeling.

- Default size: up to 100 comments per file.
- Output folder: `splits/<video_id>/`
- Output files: `part1.csv`, `part2.csv`, and so on.
- The size can be changed with `SPLIT_CHUNK_SIZE`.

### 4. Label

Label the split CSVs manually or with a labeling tool.

The training pipeline expects a file with these columns:

- `content`
- `label`

Allowed label values:

- `negatif`
- `netral`
- `positif`

### 5. Merge

`src/merge.py` merges all CSV files in `data/` into `data/sentiment.csv`.

- It ignores `data/sentiment.csv` while merging, so the command is safe to rerun.

### 6. Train

`src/train.py` loads `data/sentiment.csv`, tokenizes the text, and fine-tunes a pretrained model.

- Default base model: `indobenchmark/indobert-base-p1`
- Final model output: `models/sentiment-indobert/`
- Training checkpoints: `checkpoints/`

## Project Structure

- `scrape/` - raw scraped JSON files
- `cleaned/` - cleaned CSV files
- `splits/` - split CSV chunks for labeling
- `data/` - labeled CSV files and merged dataset
- `models/` - saved trained models
- `checkpoints/` - intermediate training checkpoints
- `src/` - pipeline scripts

## Environment Variables

Copy `.env.example` to `.env` and edit the values you need.

Important variables:

- `VIDEO_URL` - target YouTube video URL
- `TARGET_COMMENT` - number of comments to collect during scraping
- `SPLIT_CHUNK_SIZE` - number of comments per split file
- `MODEL_NAME` - pretrained model to fine-tune
- `TEST_SIZE` - fraction of data used for testing
- `RANDOM_STATE` - random seed for train/test split
- `MAX_LENGTH` - maximum token length
- `OUTPUT_DIR` - checkpoint directory
- `LOG_DIR` - training log directory
- `MODEL_SAVE_DIR` - final model output directory
- `LEARNING_RATE` - training learning rate
- `TRAIN_BATCH_SIZE` - training batch size
- `EVAL_BATCH_SIZE` - evaluation batch size
- `NUM_TRAIN_EPOCHS` - number of epochs
- `WEIGHT_DECAY` - optimizer weight decay

## Setup

This project is managed with `uv`, so there is no need for a `requirements.txt` file.

```bash
uv sync
```

If you need GPU-specific PyTorch wheels, you can add them with `uv add`.

```bash
uv add torch torchvision torchaudio --index pytorch-cu121
```

## Quick Start

### 1. Scrape comments

```bash
uv run src/scrape.py
```

### 2. Clean and split

```bash
uv run src/cleaning.py
```

### 3. Label the split files

Edit the CSVs in `splits/<video_id>/` and add a `label` column.

### 4. Merge labeled CSV files

```bash
uv run src/merge.py
```

### 5. Train the model

```bash
uv run src/train.py
```

## Output Summary

After a full run, you should have:

- `scrape/<video_id>_comments.json` - raw scraped comments
- `cleaned/<video_id>_comments.csv` - cleaned comments
- `splits/<video_id>/part1.csv`, `part2.csv`, ... - split chunks for labeling
- `data/sentiment.csv` - merged labeled dataset
- `models/sentiment-indobert/` - final trained model
- `checkpoints/` - training checkpoints

## Notes

- The pipeline uses UTF-8 and writes quoted CSVs to avoid delimiter issues.
- For training, GPU is recommended.
- If you want to adapt this repo for another text classification task or language, update the dataset, label mapping, and sometimes the base model/tokenization settings in `src/train.py`.
- This repository does not include a pretraining pipeline. It fine-tunes a pretrained transformer for the downstream sentiment task.
