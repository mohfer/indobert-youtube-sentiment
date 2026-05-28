from transformers import pipeline

classifier = pipeline(
    "sentiment-analysis",
    model="./models/sentiment-indobert"
)

print(classifier("ah udahlah intinya lu pada wajib nonton ini dulu, udah di rangkumin sejelas jelasnya dan dalam tempo sesingkat singkatnya, bahasanya ringan, semua poin permasalahan jelas diuraikan dari hulu ke hilir tanpa ada yang terlewat, mewakili unek unek gw sebagai masyarakat, plus dikasih sedikit rem biar kita tidak termakan emosi sendiri, lebih baik kita mengendalikan emosi daripada dikendalikan emosi. lekas pulih indonesiaku, makasih suguhan dagingnya kali ini bang pandji"))