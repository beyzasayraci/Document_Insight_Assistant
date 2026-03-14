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

```bash
Upload File → Extraction → Chunking → Embedding → Retrieval → Final Answer
```
Sistem, bir soruyu cevaplamak için şu aşamalardan geçer:

Upload File: Belgenin sisteme alınması (Ingestion).

Extraction: PyMuPDF veya GLM-OCR ile metne dönüştürme.

Chunking: Metnin paragraf ve cümle duyarlı parçalara bölünmesi.

Embedding: Her parçanın matematiksel vektörlere dönüştürülmesi.

Retrieval: Sorunuzla en alakalı parçaların vektör benzerliği ile bulunması.

Final Answer: İlgili bağlamın Qwen 2.5:7b modeline sunularak cevabın üretilmesi.

# Ana bileşenler
```text
•	PDF metin çıkarma: PyMuPDF
•	Scanned/image OCR: GLM-OCR
•	Chunking: paragraph-aware / sentence-fallback chunking
•	Embedding: BAAI/bge-m3 (SentenceTransformer üzerinden)
•	Retrieval: in-memory semantic search
•	Yerel LLM çalışma katmanı: Ollama
•	Cevap üretim modeli: qwen2.5:7b
```

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
Varsayılan model dizini:
models/GLM-OCR
Bu yol app/config.py içinden yönetilir.

```
```bash
python -m pip install -U huggingface_hub

python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='zai-org/GLM-OCR', local_dir='./models/GLM-OCR', local_dir_use_symlinks=False)"
```

## BGE-M3 modeli
```text
Bu projede belge parçaları ve kullanıcı sorguları için BAAI/bge-m3 embedding modeli kullanılmaktadır.
Model SentenceTransformer üzerinden yüklenir ve ilk kullanımda otomatik olarak indirilir.
Notlar
•	Aynı embedding modeli hem:
o	belge chunk’ları
o	hem de kullanıcı sorguları
için kullanılır.
•	İlk açılış biraz uzun sürebilir; çünkü model indirilecek ve cache’e alınacaktır.
Ekstra manuel model indirme adımı gerekmez; bağımlılıkları kurmak yeterlidir.
```
## Yerel LLM Kurulumu (Ollama)
```text
Cevap üretimi için Ollama kurulu olmalıdır.
```
```bash
#Windows PowerShell için:
irm https://ollama.com/install.ps1 | iex
```
```text
Kurulumu doğrulama
```
```bash
ollama --version
```
## Modeli çekin.
```bash
ollama pull qwen2.5:7b
```
Doğrulayın:
```bash
ollama --version
ollama list
```text
Projeyi çalıştırmadan önce şunlardan emin olun:
•	Ollama kurulmuş olmalı
•	qwen2.5:7b modeli indirilmiş olmalı
•	Ollama servisi yerelde erişilebilir olmalı
Varsayılan Ollama adresi:
http://localhost:11434
```
```text
Modeli test etme:
```
```bash
ollama run qwen2.5:7b
 ```

# Uygulamayı başlatmak için:
```bash
python run.py
```
# Ardından tarayıcınızda açılan Streamlit arayüzünde:
```text
Belgenizi yükleyin.

İşleme butonuna basarak metin çıkarımını bekleyin.

Extraction ve Chunks çıktılarını gözlemleyin.

Ask&Answer seçeneğinden belge hakkında sorularınızı sormaya başlayın.

Sorularınızın cevaplarını görüntüleyin.
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
└── utils.py      # Sistem için gerekli dil ayarları
```
# Mevcut Tasarım Kararları
Bu proje özellikle retrieval-augmented bir yapı olarak tasarlanmıştır; yani tüm belge doğrudan LLM’e gönderilmez.
Bunun nedenleri:
•	cevap üretimini daha kontrollü hale getirmek
•	hallucination riskini azaltmak
•	hangi bağlamdan cevap verildiğini daha görünür kılmak
•	extraction / retrieval / answer katmanlarını ayrı ayrı debug edebilmek
Son katmandaki LLM, tüm belgeyi değil, yalnızca retrieval ile bulunan ilgili bağlamı görür


# Sınırlamalar
Düşük çözünürlüklü, eğik, bulanık veya gürültülü görseller taramalarda OCR kalitesi düşebilir.

Uzun kaynakça içeren belgelerde retrieval hassasiyeti değişebilir.

Zaman zaman cevaplarda dil karmaşası yaşanabilir.

Bu sistem MVP niteliğindedir; öncelik tam üretim kalitesinden çok, uçtan uca çalışan bir pipeline kurmaktır.

# Geliştirme Notları
Bu repoda ayrıca bir DEVLOG.md dosyası bulunur. Burada:
•	alınan teknik kararlar,
•	değerlendirilen alternatifler,
•	geliştirme sırasında yaşanan problemler,
•	ve sistemin zaman içinde nasıl evrildiği
kronolojik olarak not edilmiştir.

# Örnek Kullanım Senaryoları
•	Belgenin tarihini sormak
•	Belgenin kime gönderildiğini sormak
•	Bir makalenin ne hakkında olduğunu sormak
•	Belgede geçen isimleri veya referansları listelemek
•	Aynı belge üzerinde Türkçe veya İngilizce soru sormak

# Gelecek Planları
Olası sonraki adımlar:
•	daha güçlü OCR / layout-aware parsing
•	metadata-aware retrieval
•	reranking
•	cevaplarda daha güçlü citation formatı
•	çok dilli cevap kontrolünü daha sağlam hale getirme
•	tablo / form alanları için yapılandırılmış veri çıkarımı

