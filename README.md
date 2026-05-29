## Overview

This repository provides a lightweight end-to-end pipeline for building a sentiment analysis dataset from YouTube comments and fine-tuning a pretrained model on it.

The project is aimed at small-to-medium scale experiments, where the usual workflow is:

1. scrape comments from one or multiple YouTube videos,
2. clean and normalize the text,
3. split the cleaned data into chunks,
4. automatically label the data using an OpenAI-compatible LLM API,
5. merge labeled CSV files into one dataset,
6. fine-tune a pretrained transformer model.

The repo is focused on **text classification**. It is built around Indonesian sentiment analysis, but the same scaffold can be adapted for other text classification tasks by changing the dataset, label mapping, and sometimes the base model in `src/training.py`.

## Pipeline

### 1. Scrape

`src/scraping.py` collects comments from YouTube video(s) and saves raw JSON files into `scraped/`.

- Configure the target video(s) with `VIDEO_URL` in `.env`. You can provide multiple URLs separated by commas.
- Limit the number of collected comments per video with `TARGET_COMMENT`.

### 2. Clean

`src/cleaning.py` normalizes the raw text and writes cleaned per-video CSV files into `cleaned/`.

- Output format: one quoted column named `content`.
- This script also triggers the split step automatically.

### 3. Split

`src/splitting.py` splits each cleaned CSV into smaller chunks for labeling.

- Default size: up to 100 comments per file.
- Output folder: `splits/<video_id>/`
- Output files: `part1.csv`, `part2.csv`, and so on.
- The size can be changed with `SPLIT_CHUNK_SIZE`.

### 4. Label

`src/labeling.py` automatically processes chunked files from `splits/` and asks an LLM (via an OpenAI-compatible API) to apply labels based on the text's sentiment.

- Connected to local/custom endpoint defined in `src/labeling.py`.
- Outputs generated sequentially (e.g., `data1.csv`, `data2.csv`) to the `data/` directory.
- Appends `.done` to the original splits file to ensure data is not labeled repeatedly.

The training pipeline expects a file with these columns:

- `content`
- `label`

Allowed label values:

- `negatif`
- `netral`
- `positif`

### 5. Merge

`src/merging.py` merges all CSV files in `data/` into `data/sentiment.csv`.

- It ignores `data/sentiment.csv` while merging, so the command is safe to rerun.

### 6. Train

`src/training.py` loads `data/sentiment.csv`, tokenizes the text, and fine-tunes a pretrained model.

- Default base model: `indobenchmark/indobert-base-p1`
- Final model output: `models/sentiment-indobert/`
- Training checkpoints: `checkpoints/`

## Project Structure

```text
indobert-youtube-sentiment/
├── main.py                  # main entry script
├── pyproject.toml           # uv project configuration
├── README.md                # project documentation
├── checkpoints/             # intermediate training checkpoints
│   └── sentiment-indobert/
│       ├── checkpoint-40/
│       └── checkpoint-80/
├── cleaned/                 # cleaned CSV files
│   └── *_comments.csv
├── data/                    # labeled CSV files and merged dataset
│   ├── data1.csv
│   └── sentiment.csv
├── models/                  # saved trained models
│   ├── indobert-base-p1/
│   └── sentiment-indobert/
├── scraped/                 # raw scraped JSON files
│   └── *_comments.json
├── splits/                  # split CSV chunks for manual/auto labeling
│   └── <video_id>/
│       ├── part1.csv
│       ├── part2.csv
│       └── part1.csv.done
└── src/                     # pipeline scripts
    ├── cleaning.py          # normalizes raw text and triggers split
    ├── download_model.py    # script to download pretrained model
    ├── labeling.py          # auto-label comments using AI via API
    ├── merging.py           # merges labeled CSV files
    ├── scraping.py          # collects comments from YouTube
    ├── splitting.py         # splits clean CSVs into chunks
    ├── testing.py           # evaluation/test script
    └── training.py          # fine-tunes the pretrained model
```

## Environment Variables

Copy `.env.example` to `.env` and edit the values you need.

Important variables:

- `VIDEO_URL` - target YouTube video URL(s), comma-separated for multiple videos
- `TARGET_COMMENT` - number of comments to collect per video during scraping
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
- `CLIENT_BASE_URL` - OpenAI-compatible API endpoint for auto-labeling
- `CLIENT_API_KEY` - API key for the OpenAI-compatible API
- `MODEL` - model to use for auto-labeling (should be compatible with the API you're using)

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

You can run the entire pipeline through the `main.py` entry script.

### Default Pipeline (Scrape -> Clean & Split)

```bash
uv run main.py
```

### Data Preparation Pipeline (Scrape -> Clean -> Label)

Run the end-to-end data preparation (stops before merge and train for manual inspection):

```bash
uv run main.py --prepare
```

### Full Pipeline (Scrape -> Clean -> Label -> Merge -> Train -> Test)

Run the full pipeline from data collection to model training and testing:

```bash
uv run main.py --all
```

### Running Specific Steps

You can also trigger individual components manually:

```bash
uv run main.py --scrape   # Only scrape new data
uv run main.py --label    # Run AI automatic labeling
uv run main.py --merge    # Merge updated data/*.csv into sentiment.csv
uv run main.py --train    # Run fine-tuning training loop
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
- If you want to adapt this repo for another text classification task or language, update the dataset, label mapping, and sometimes the base model/tokenization settings in `src/training.py`.
- This repository does not include a pretraining pipeline. It fine-tunes a pretrained transformer for the downstream sentiment task.
