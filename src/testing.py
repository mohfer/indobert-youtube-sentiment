from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="./models/sentiment-indobert"
)

text = "Saya sangat senang dengan produk ini! Kualitasnya luar biasa dan pengirimannya cepat."

print(classifier(text))