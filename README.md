# 📄 Document Insight Assistant
```text
1. Arayüz: Streamlit

2. PDF metin çıkarma: PyMuPDF

3. Scanned/image extraction: GLM-OCR

4. Chunking: metadata koruyan paragraph-aware / sentence-fallback chunking

5. Embedding: BAAI/bge-m3 (SentenceTransformer ile)

6. Retrieval: in-memory semantic search

7. Yerel LLM altyapısı: Ollama

8. Cevap üretim modeli: qwen2.5:7b
```
Document Insight Assistant, yerel bir LLM (Large Language Model) kullanarak belgelerinizle etkileşime girmenizi sağlayan, uçtan uca bir RAG (Retrieval-Augmented Generation) prototipidir.

Bu sistem, dokümanı doğrudan modele beslemek yerine; metni anlamlı parçalara ayırır, en ilgili kısımları "vektör tabanlı" olarak bulur ve sadece bu kanıtlara dayanarak cevap üretir. Bu sayede hallucination riskini minimize eder ve veri gizliliğini korur.

# ✨ Öne Çıkan Özellikler
Geniş Format Desteği: PDF, JPG ve PNG dosyalarını işleyebilir.

Hibrit Metin Çıkarma: Dijital PDF'lerden doğrudan metin çekebilir, taranmış belgeler/görseller için ise GLM-OCR modelini kullanır.

Semantic Search: Çok dilli BGE-M3 embedding modeli ile anahtar kelime değil, anlam eşleşmesi yapar.

Tamamen Yerel: Verileriniz dışarı çıkmaz; işlemler kendi makinenizde Ollama üzerinden gerçekleşir.

Çift Dilli Destek: Türkçe ve İngilizce dillerinde yüksek performans sergiler.

# 🛠️ Teknik Pipeline (Akış)
Sistem, bir soruyu cevaplamak için şu aşamalardan geçer:

Yükleme: Belgenin sisteme alınması (Ingestion).

Extraction: PyMuPDF veya GLM-OCR ile metne dönüştürme.

Chunking: Metnin paragraf ve cümle duyarlı parçalara bölünmesi.

Embedding: Her parçanın matematiksel vektörlere dönüştürülmesi.

Retrieval: Sorunuzla en alakalı parçaların vektör benzerliği ile bulunması.

Final Answer: İlgili bağlamın Qwen 2.5:7b modeline sunularak cevabın üretilmesi.

# 📦 Kurulum ve Hazırlık

## Sanal ortam oluşturun
```bash
python -m venv .venv
```
## Aktifleştirin (Windows)
```bash
.venv\Scripts\activate
```
# Aktifleştirin (Linux/macOS)
```bash
source .venv/bin/activate
```
## Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```
## GLM-OCR indirin

```text
Taranmış belgeler için GLM-OCR modelini indirin:
```
```bash
python -m pip install -U huggingface_hub

python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='zai-org/GLM-OCR', local_dir='./models/GLM-OCR', local_dir_use_symlinks=False)"
```

## BGE-M3 modeli
```text
BGE-M3 embedding modeli uygulama ilk çalıştığında otomatik olarak indirilecektir.
```
## Ollama'yı indirin ve kurun.
```text
Cevap üretimi için Ollama kurulu olmalıdır.
```
```bash
irm https://ollama.com/install.ps1 | iex
```
## Modeli çekin.
```bash
ollama pull qwen2.5:7b
```
```text
Doğrulayın: ollama list komutuyla modelin listede olduğunu görün.
```
# Uygulamayı başlatmak için:
```bash
python run.py
```
# Ardından tarayıcınızda açılan Streamlit arayüzünde:
```text
Belgenizi yükleyin.

İşleme butonuna basarak metin çıkarımını bekleyin.

Belge hakkında sorularınızı sormaya başlayın.
```
# 📂 Proje Yapısı
```text
app/
├── extraction/   # PDF parsing ve OCR mantığı
├── ingestion/    # Dosya yönlendirme ve yükleme akışı
├── qa/          # Prompt üretimi ve Ollama bağlantısı
├── processing/   # Chunking (parçalama) stratejileri
├── retrieval/    # Embedding ve vektör arama (In-memory)
├── ui/           # Streamlit arayüz bileşenleri
└── config.py     # Model yolları ve sistem ayarları
```
# ⚠️ Sınırlamalar
Düşük çözünürlüklü, eğik, bulanık veya gürültülü görseller taramalarda OCR kalitesi düşebilir.

Uzun kaynakça içeren belgelerde retrieval hassasiyeti değişebilir.

Zaman zaman cevaplarda dil karmaşası yaşanabilir.

# 🗺️ Gelecek Planları
[ ] Reranking: Arama sonuçlarını daha hassas sıralamak için Cross-Encoder kullanımı.

[ ] Citation: Cevaplarda metnin hangi sayfadan alındığını vurgulama.

[ ] Metadata Filtering: Tarih veya yazar gibi verilere göre filtreleme.

[ ] Model verimliliği: Model verimliliğini arttırmak ve Soru-Cevap verimini üst seviyeye çıkartmak için prompt üzerinde güncelleme yapılabilir.

Teknik kararlar ve gelişim süreci için DEVLOG.md dosyasını inceleyebilirsiniz.
