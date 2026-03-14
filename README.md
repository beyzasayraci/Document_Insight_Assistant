📄 Document Insight Assistant
Document Insight Assistant, yerel bir LLM (Large Language Model) kullanarak belgelerinizle etkileşime girmenizi sağlayan, uçtan uca bir RAG (Retrieval-Augmented Generation) prototipidir.

Bu sistem, dokümanı doğrudan modele beslemek yerine; metni anlamlı parçalara ayırır, en ilgili kısımları "vektör tabanlı" olarak bulur ve sadece bu kanıtlara dayanarak cevap üretir. Bu sayede hallucination (uydurma) riskini minimize eder ve veri gizliliğini korur.

✨ Öne Çıkan Özellikler
Geniş Format Desteği: PDF, JPG ve PNG dosyalarını işleyebilir.

Hibrit Metin Çıkarma: Dijital PDF'lerden doğrudan metin çekebilir, taranmış belgeler/görseller için ise GLM-OCR modelini kullanır.

Semantic Search: Çok dilli BGE-M3 embedding modeli ile anahtar kelime değil, anlam eşleşmesi yapar.

Tamamen Yerel: Verileriniz dışarı çıkmaz; işlemler kendi makinenizde Ollama üzerinden gerçekleşir.

Çift Dilli Destek: Türkçe ve İngilizce dillerinde yüksek performans sergiler.

🛠️ Teknik Pipeline (Akış)
Sistem, bir soruyu cevaplamak için şu aşamalardan geçer:

Yükleme: Belgenin sisteme alınması (Ingestion).

Extraction: PyMuPDF veya GLM-OCR ile metne dönüştürme.

Chunking: Metnin paragraf ve cümle duyarlı parçalara bölünmesi.

Embedding: Her parçanın matematiksel vektörlere dönüştürülmesi.

Retrieval: Sorunuzla en alakalı parçaların vektör benzerliği ile bulunması.

Final Answer: İlgili bağlamın Qwen 2.5:7b modeline sunularak cevabın üretilmesi.

📦 Kurulum ve Hazırlık

# Sanal ortam oluşturun
python -m venv .venv

# Aktifleştirin (Windows)
.venv\Scripts\activate
# Aktifleştirin (Linux/macOS)
source .venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt


# GLM-OCR indirin
python -m pip install -U huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='zai-org/GLM-OCR', local_dir='./models/GLM-OCR', local_dir_use_symlinks=False)"

Not: BGE-M3 embedding modeli uygulama ilk çalıştığında otomatik olarak indirilecektir.

3. Yerel LLM Yapılandırması (Ollama)
Cevap üretimi için Ollama kurulu olmalıdır.

# Ollama'yı indirin ve kurun.

irm https://ollama.com/install.ps1 | iex

# Modeli çekin.

ollama pull qwen2.5:7b

Doğrulayın: ollama list komutuyla modelin listede olduğunu görün.

# Uygulamayı başlatmak için:

python run.py

# Ardından tarayıcınızda açılan Streamlit arayüzünde:

Belgenizi yükleyin.

İşleme butonuna basarak metin çıkarımını bekleyin.

Belge hakkında sorularınızı sormaya başlayın.

📂 Proje Yapısı
Plaintext
app/
├── extraction/   # PDF parsing ve OCR mantığı
├── ingestion/    # Dosya yönlendirme ve yükleme akışı
├── llm/          # Prompt üretimi ve Ollama bağlantısı
├── processing/   # Chunking (parçalama) stratejileri
├── retrieval/    # Embedding ve vektör arama (In-memory)
├── ui/           # Streamlit arayüz bileşenleri
└── config.py     # Model yolları ve sistem ayarları

⚠️ Sınırlamalar
Düşük çözünürlüklü taramalarda OCR kalitesi düşebilir.

Uzun kaynakça içeren belgelerde retrieval hassasiyeti değişebilir.

Zaman zaman cevaplarda dil karmaşası yaşanabilir.

🗺️ Gelecek Planları
[ ] Reranking: Arama sonuçlarını daha hassas sıralamak için Cross-Encoder kullanımı.

[ ] Citation: Cevaplarda metnin hangi sayfadan alındığını vurgulama.

[ ] Metadata Filtering: Tarih veya yazar gibi verilere göre filtreleme.

Teknik kararlar ve gelişim süreci için DEVLOG.md dosyasını inceleyebilirsiniz.
