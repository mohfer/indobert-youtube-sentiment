from transformers import AutoTokenizer, AutoModel

model_name = "indobenchmark/indobert-base-p1"

# download tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# download model
model = AutoModel.from_pretrained(model_name)

# simpan ke folder lokal
save_path = "./models/indobert-base-p1"

tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print("Model berhasil disimpan!")