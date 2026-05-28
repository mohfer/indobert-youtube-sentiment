import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from sklearn.model_selection import train_test_split
import numpy as np
import evaluate

MODEL_NAME = "indobenchmark/indobert-base-p1"
TEST_SIZE = 0.2
RANDOM_STATE = 42
MAX_LENGTH = 64
OUTPUT_DIR = "./checkpoints/sentiment-indobert"
LOG_DIR = "./logs"
MODEL_SAVE_DIR = "./models/sentiment-indobert"
LEARNING_RATE = 2e-5
TRAIN_BATCH_SIZE = 2
EVAL_BATCH_SIZE = 2
NUM_TRAIN_EPOCHS = 2
WEIGHT_DECAY = 0.01

# ======================
# LOAD CSV
# ======================

df = pd.read_csv("./data/sentiment.csv")

# ubah label text -> angka
label2id = {
    "negatif": 0,
    "netral": 1,
    "positif": 2
}

id2label = {
    0: "negatif",
    1: "netral",
    2: "positif"
}

df["label"] = df["label"].map(label2id)

# split train/test
train_df, test_df = train_test_split(
    df,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE
)

train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

# ======================
# TOKENIZER
# ======================

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(
        batch["content"],
        padding="max_length",
        truncation=True,
        max_length=MAX_LENGTH
    )

train_dataset = train_dataset.map(tokenize, batched=True)
test_dataset = test_dataset.map(tokenize, batched=True)

# ======================
# MODEL
# ======================

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=3,
    id2label=id2label,
    label2id=label2id
)

# ======================
# METRIC
# ======================

accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return accuracy.compute(
        predictions=predictions,
        references=labels
    )

# ======================
# TRAINING ARGUMENTS
# ======================

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=TRAIN_BATCH_SIZE,
    per_device_eval_batch_size=EVAL_BATCH_SIZE,
    num_train_epochs=NUM_TRAIN_EPOCHS,
    weight_decay=WEIGHT_DECAY,
    logging_dir=LOG_DIR,
)

# ======================
# TRAINER
# ======================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)

# ======================
# TRAIN
# ======================

trainer.train()

# save model
trainer.save_model(MODEL_SAVE_DIR)
tokenizer.save_pretrained(MODEL_SAVE_DIR)

print("Training selesai!")