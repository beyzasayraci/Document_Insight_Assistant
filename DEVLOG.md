# DEVLOG

*Bu dosyada proje boyunca aldığım teknik kararları, değerlendirdiğim alternatifleri ve geliştirme sürecindeki düşünce akışımı kronolojik olarak not ediyorum. Amacım sadece final sonucu değil, bu sonuca nasıl ulaştığımı da görünür kılmak.*

## Gün 1 – Problemi anlama

Case dokümanını inceledikten sonra bunun temel olarak bir **document question answering** problemi olduğunu netleştirdim. Kullanıcının PDF veya görsel yüklediği, sistemin belge içeriğini işleyip doğal dilde sorulan sorulara yalnızca belgeye dayanarak cevap verdiği bir yapı isteniyor.

Buradaki en kritik noktanın yalnızca cevap üretmek olmadığını, aynı zamanda **belgede olmayan bilgiyi üretmemek** olduğunu fark ettim. Bu yüzden sistemi doğrudan “LLM’e belgeyi ver ve cevap al” mantığında değil, daha kontrollü bir belge işleme ve retrieval akışı üzerinden tasarlamaya karar verdim.

İlk aşamada netleştirdiğim gereksinimler:
- PDF, JPG ve PNG desteği
- Türkçe ve İngilizce belgeleri işleyebilme
- Basit bir kullanıcı arayüzü
- Belgeye dayalı soru-cevap
- Hallucination riskini azaltma
- İşlevsel bir MVP üretme

## Gün 1 – İlk mimari alternatifleri değerlendirme

Başlangıçta iki temel yaklaşım düşündüm.

### Alternatif 1: Doğrudan multimodal LLM kullanmak
Bu yaklaşımda belge ya da görsel doğrudan bir vision-capable modele verilecek ve sistem tüm soruları bu model üzerinden cevaplayacaktı.

Bu yöntem ilk bakışta daha kısa yol gibi görünse de bazı sorunlar fark ettim:
- Çok sayfalı belgelerde maliyet artabilir
- Her soruda belgeyi tekrar işlemek gerekebilir
- Kaynak gösterme ve izlenebilirlik zayıf kalabilir
- Hallucination kontrolü daha zor olabilir

### Alternatif 2: Metin çıkarma + retrieval + LLM
Bu yaklaşımda önce belgeden metin çıkarılacak, sonra bu metin parçalara ayrılacak, ilgili parçalar retrieval ile bulunacak ve son aşamada LLM yalnızca bu parçalara dayanarak cevap üretecekti.

Bu yaklaşımın daha kontrollü, daha savunulabilir ve belgeye dayalı cevap üretme açısından daha uygun olduğuna karar verdim.

## Gün 1 – Ana mimari kararım

Şu aşamada seçtiğim ana akış şu şekilde:

**Belge Yükleme → Metin Çıkarma → Temizleme / Metadata → Chunking → Embedding → Retrieval → LLM ile Cevap Üretme**

Bu yapıyı seçme nedenlerim:
- LLM’i kontrollü kullanmak
- Belgede olmayan bilgi üretimini azaltmak
- Çok sayfalı dokümanlarda daha mantıklı bir yapı kurmak
- Cevapları belirli belge parçalarına dayandırabilmek
- Mülakatta teknik kararları daha rahat savunabilmek

Bu nedenle projeyi bir “tek adımlı LLM uygulaması” yerine bir **RAG tabanlı document QA sistemi** olarak ele almaya karar verdim.

## Gün 1 – Metin çıkarma tarafındaki kararlar

En çok düşündüğüm kısım metin çıkarma aşaması oldu. Çünkü belgeden hatalı metin çıkarsa retrieval kalitesi düşecek ve bu da final cevabı doğrudan etkileyecek.

Başta scanned belgeler ve görseller için doğrudan vision API kullanmayı düşündüm. Bunun modern bir yaklaşım olduğunu ve bazı karmaşık durumlarda klasik OCR’dan daha iyi sonuç verebileceğini değerlendirdim. Ancak tüm extraction katmanını buna dayandırmanın bazı pratik sorunlar doğurabileceğini fark ettim:
- Çok sayfalı belgelerde gecikme
- Maliyet
- Daha fazla dış bağımlılık
- MVP süresinde gereksiz karmaşıklık

Bu nedenle daha dengeli bir yapı seçtim:

- **Text tabanlı PDF’ler için:** PyMuPDF  
- **Scanned PDF / JPG / PNG için:** EasyOCR

Buradaki mantığım şu oldu:
- Eğer PDF içinde zaten gerçek metin varsa OCR çalıştırmaya gerek yok.
- Eğer belge bir tarama ya da görselse, o zaman OCR ile metne dönüştürmek gerekir.

Bu sayede hem daha hızlı hem daha sade hem de daha kolay savunulabilir bir extraction pipeline’ı elde etmiş oldum.

## Gün 1 – Neden hibrit bir yaklaşım seçtim?

Tüm belgeler için tek araç kullanmak yerine, belgenin tipine göre karar veren bir yönlendirme mantığı kurmanın daha doğru olacağını düşündüm.

Planladığım yönlendirme mantığı şu şekilde:
- Dosya JPG / PNG ise doğrudan OCR’a gider
- Dosya PDF ise önce PyMuPDF ile metin okunmaya çalışılır
- Eğer anlamlı metin çıkarsa parser sonucu kullanılır
- Eğer metin boşsa veya çok yetersizse belge taranmış kabul edilir ve OCR’a yönlendirilir

Bu hibrit yaklaşımın avantajları:
- Text tabanlı PDF’lerde gereksiz OCR maliyetini önlemek
- Scanned belgeleri de destekleyebilmek
- Sistemi daha hızlı ve daha verimli hale getirmek

## Gün 1 – Dil desteği konusunda verdiğim karar

Case’te Türkçe ve İngilizce destek beklendiği için dil tarafını da ayrıca düşündüm.

İlk anda çeviri katmanı eklemeyi değerlendirdim. Ancak ilk sürüm için bunun gereksiz bir karmaşıklık yaratabileceğini fark ettim. Belgeleri otomatik çevirmek:
- hata yüzeyini artırabilir
- özel terimleri bozabilir
- sayısal alanlarda risk yaratabilir

Bu yüzden ilk versiyonda şuna karar verdim:
- belge dili tespit edilecek
- soru dili tespit edilecek
- retrieval orijinal metin üzerinden yapılacak
- cevap mümkünse kullanıcının sorduğu dilde üretilecek

Bu çözüm, tam bir çeviri katmanı eklemekten daha sade ve daha güvenli göründü.

## Gün 1 – Kod organizasyonu kararı

Kod tarafında baştan itibaren her şeyi tek dosyada toplamak istemedim. Çünkü extraction, retrieval ve cevap üretme katmanları birbirinden mantıksal olarak ayrılıyor.

Bu yüzden kodu şu ana modüllere ayırmaya karar verdim:
- `ingestion`
- `extraction`
- `processing`
- `retrieval`
- `qa`
- `services`
- `ui`

Servis mantığını da iki ana akış etrafında kurmayı planladım:
- `document_service`: belge işlendiğinde çalışan akış
- `query_service`: soru sorulduğunda çalışan akış

Bu yapı sayesinde iş mantığını arayüzden ayırmak ve sistemi daha okunabilir tutmak mümkün olacak.

## Gün 1 – Şu anki net teknik seçimlerim

Şu aşamada belirlediğim temel teknoloji kararları:

- **Arayüz:** Streamlit
- **PDF metin çıkarma:** PyMuPDF
- **Scanned/image extraction:** EasyOCR
- **Dil tespiti:** hafif bir language detection yaklaşımı
- **Embedding:** sentence-transformers
- **Vector search:** FAISS
- **Final cevap üretimi:** LLM (yalnızca retrieval ile bulunan bağlama göre)

Bu seçimlerde önceliğim:
- hızlı MVP çıkarabilmek
- sistemi aşırı karmaşık hale getirmemek
- case’in asıl beklentilerine odaklanmak

## Gün 1 – Şu an gördüğüm riskler ve dikkat etmem gereken noktalar

Henüz geliştirme başlamadan önce dikkat etmem gereken bazı riskleri not ettim:

- OCR çıktısının düşük kaliteli belgelerde bozulabilmesi
- Tablo içeren belgelerde satır-sütun yapısının kaybolabilmesi
- Türkçe karakterlerin extraction kalitesine etkisi
- Chunk boyutunun retrieval başarısını etkilemesi
- Belge içinde olmayan sorulara sistemin tutarlı şekilde “bulunamadı” diyebilmesi

Bu riskleri geliştirme sırasında test senaryoları ile kontrol etmem gerekecek. Özellikle TESTING.md dosyasında bu sınırlamaları görünür kılmayı planlıyorum.

## Gün 1 – Şu anki genel sonuç

Şu aşamada proje için en uygun yaklaşımın:
- belge tipine göre yönlendirme yapan,
- önce güvenilir metin çıkarmaya odaklanan,
- ardından retrieval tabanlı çalışan,
- LLM’i ise yalnızca son cevap katmanında kullanan,

bir mimari olduğuna karar verdim.

Bu yaklaşımın hem teknik olarak daha sağlam, hem de süre kısıtı içinde uygulanabilir olduğunu düşünüyorum.

## Gün 2 – Test verisi & OCR odaklanması

Bugün öncelikle test verisini toparlamaya odaklandım. Başlangıçta tek bir tutarlı dataset bulmaya çalıştım fakat bunun bu case için şart olmadığını netleştirdim; amaç bir modeli eğitmek değil, farklı belge tiplerinde çalışan bir document QA pipeline kurmak. Bu yüzden belge setini konu birliğine göre değil, **belge tipi ve test senaryosu çeşitliliğine göre** oluşturmaya karar verdim. Burada hem Kaggle ve benzeri kaynaklardan daha önce geliştiriclerin kullandığı verisetlerinden faydalandım hem de tamamen search sistemine dayanarak veriler oluşturdum.

Kullandığım örnekler:
- **İngilizce metin PDF:** Önceliğimi yayınlanan makalelere verdim. Buradaki amacım daha karmaşık ve uzun pdf'lere ulaşabilmekti.
- **Türkçe metin PDF:** Önceliğimi yayınlanan makalelere verdim. Buradaki amacım daha karmaşık ve uzun PDF'lere ulaşabilmekti.
- **Scanned / image örnekleri:** Fişler, fax/form, suggestion form gibi taranmış ya da fotoğraflanmış belgeler seçmeye özen gösterdim. Bu sayede sistemin karmaşık gelen belgelerde nasıl bir davranış izleyebileceğini gözlemlemekti.

Text tabanlı PDF’lerde çıkışın oldukça temiz olduğunu gördüm; hem İngilizce hem de Türkçe makale sayfa sayfa okunabilir şekilde parse edildi. Bu kısımda sadece problemim zaman zaman bu belgelerin içerisinde yer alan tablo vb. ifadeleri aktarmakta güçlük yaşamasıydı.

OCR tarafında ise belge yapısına göre performans çok değişti. Örneğin fiş PDF’sinde PASSENGER RECEIPT, tarih, ücret alanları ve toplam tutar gibi kritik alanlar okunabilir şekilde çıktı; bu tip belgelerde OCR’ın yeterli olacağını gördüm. Ancak çizgili, kutulu ve el yazısı içeren suggestion form tipindeki belgelerde OCR çıktısı ciddi biçimde bozuldu; satır yapısı, alan eşleşmeleri ve el yazısı notlar çok bozuldu.

Bu nedenle bugün önemli bir kapsam kararı aldım: OCR tarafını şu aşamada **"mükemmelleştirmeye" çalışmak yerine, çalışan bir baseline olarak dondurup** projenin geri kalanına geçmeye karar verdim.

- EasyOCR’ın form/ tablo/ kutulu layout ve el yazısı içeren belgelerle zayıf kaldığını gördüm.
- Bunu çözmek için Docling, Unstructured veya vision tabanlı daha gelişmiş belge ayrıştırıcılarına geçmek teorik olarak mantıklı olsa da, ek kurulum, yeni hata ayıklama ve zaman maliyeti getiriyor. Burada kullandığımda avantaj sağlayabileceğim OpenAI Vision API vb. API kullanımlarının ücretli olması da test süreçlerini aksatabileceği kanısına vardım.
- Bu yüzden **text PDF ve nispeten temiz OCR senaryolarını ana akışta kullanmak; zor formları “challenging cases / limitations” olarak belgeleme** kararına vardım.

Bu kapsam çerçevesinde kod tarafında da sadeleştirme yaptım:
- OCR extractor içinde fazla akıllı ama kırılgan davranışlar oluşturan denemeleri geri çektim.
- Özellikle **çok agresif preprocessing** denemeleri beklediğim iyileşmeyi getirmedi.
- Bunun yerine daha stabil bir yaklaşım benimsedim: mümkün olduğunca sade OCR, minimum preprocessing ve sonuçları kalite metriğiyle gözlemleme.

Bugün netleşen nokta: bu projede asıl değer **OCR tarafında sonsuz iyileştirme yapmak değil**, extraction’dan sonra chunking, retrieval ve grounded QA hattını kurmak. Yani OCR ve parsing, RAG’in kendisi değil; RAG öncesi hazırlık katmanı.

### Denemeyi bıraktığım yöntemler

- **Detaylı preprocessing + yeniden OCR çalıştırma**: Görüntü üzerinde çok agresif kontrast/threshold/filtre uygulayıp yeniden OCR çalıştırmak, bazı belgelerde outputu bozdu; toplamda hassasiyeti artırmadı.
- **`detail=1` (ayrık kutucuklar) kullanımı**: `detail=1` çıktısı çoğunlukla satır bazlı/boşluk bazlı düzensiz oluyordu; daha stabil sonuç için `detail=0` + `paragraph=True` tercih ediyorum.

### OCR extractor tarafında denediğim değişiklikler

`app/extraction/ocr_extractor.py` içinde uzun bir süre boyunca birçok deneme yaptım; sonunda bu denemelerin çoğunu geri aldım çünkü MVP hedefini ve stabiliteyi bozuyorlardı.

- **Dil tespiti + yeniden OCR**:
  1) Önce **raw OCR** çalışıyor.
  2) Sonra **preprocessing** (kontrast/filtre/threshold) sonrası OCR çalışıyor.
  3) İkisi kalite metriğine göre karşılaştırılıyor; daha iyi olan seçiliyor.
  4) Eğer `rerun_with_detected_language=True` ise (config’den), seçilen metin üzerinden **dil tespiti** yapılıyor.
  5) Tespit net (prob≥eşik) ve dil destekleniyorsa, OCR **sadece o dil için** tekrar çalıştırılıyor.
  6) Yeni sonuç kaliteyi bozmazsa, bu tekrar edilen sonuç kullanılıyor.

  Bu rerun mantığı işliyor ama pratikte gain çok az oldu; ek karmaşıklık ve hata noktası getirdiği için en sonunda "stabil olanı tutma" yaklaşımına döndüm.
- **“Raw vs Preprocessed” karşılaştırması**: `extract_text_from_image()` içinde **önce ham OCR, sonra `ImageOps.autocontrast` + `median_filter` + `threshold` ile işlenmiş görüntüden OCR** alınıyor; ardından çıktılar `suspicious_char_ratio` bazında karşılaştırılıyor ve daha “temiz” olan metin seçiliyor. Bu basit iki A/B çalışmasını korudum; daha fazla varyasyon (farklı eşikler, ek preprocessing adımları, çoklu tekrarlar vb.) geri çekildi.
- **Kalite metriği denemeleri**: OCR çıktısındaki garip karakter oranını (`suspicious_char_ratio`) hesaplayıp buna göre seçme/makul bir eşik belirleme gibi metrikler ekledim. Metrikler bazı durumlarda faydalı olsa da, maksimum genel kullanım için gereğinden fazla optimizasyon yaptı.
- **EasyOCR Reader cache’leme**: Model yükleme maliyetini azaltmak için `languages` kombinasyonuna göre `easyocr.Reader` nesnesini cache’ledim. Bu kısım kaldı; modelin tekrar yüklenmesini engellemesi bakımından faydalı oldu.

> Not: Bu deneylerin çoğunu kodda bırakmadım; çoğunun mantığını denedikten sonra kaldırıp “minimum sürüm” haline getirdim. Amacım, OCR tarafını çok katmanlı algoritmalardan kurtarıp, downstream (chunking/retrieval) hattına daha hızlı ilerleyebilmekti.
---
## Gün 2 – Sonraki adım

Extraction çıktısını sabitleyip **chunking aşamasına** geçmeyi planlıyorum. Önce şu iki adımı tamamlayacağım:
1. Çıkan metni sayfa bilgisi ve kaynak metadata ile birlikte **chunk’lara bölmek**
2. Ardından **embedding** ve **retrieval** hattını kurmak.

Bu aşamada, zor form belgelerinin çıkardığı gürültüyü "başarım sınırı" olarak belgeleyeceğim; sonraki geliştirmelerim için bu sınırlamaları düzeltmeye çalışacağım.

---

## Gün 3 – OCR Yöntemlerini Deneme ve Karşılaştırma
Bugün dokümanlardan metin çıkarma kısmı için farklı OCR çözümlerinide araştırmaya karar verdim. İlk başta EasyOCR ile ilerlemeyi düşünmüştüm fakat aldığım sonuçlar oldukça yetersizdi. Özellikle belge yapısını koruma, metni doğru okuma ve genel çıktı kalitesi açısından beklediğim performansı vermedi.
Burada yer alan performans düşüklüğünü daha sonraki adımları da önemli bir şekilde etkileyecek ve halisülasyon gösterme ihtimalini arttıracaktı.

Bu yüzden EasyOCR ile devam etmek yerine farklı alternatifleri test etmeye karar verdim. Bu kapsamda PaddleOCR, DeepSeek OCR ve GLM-OCR taraflarını inceleyip denemeler yaptım. Amacım sadece metni çıkarmak değil, aynı zamanda LLM/RAG tarafında daha kullanılabilir, daha temiz ve daha anlamlı bir çıktı elde edebilmekti.

Yaptığım denemelerde her modelin çıktı yapısını, okunabilirliğini ve belgeyi ne kadar doğru yansıttığını gözlemledim. Bu süreçte özellikle GLM-OCR çıktıları bana daha iyi göründü. Çünkü sadece düz metin üretmekten ziyade, belgeyi anlama tarafında daha güçlü bir izlenim verdi. Özellikle işaretlemeler, tarihler ve bazı el yazılarında performansı Paddle'a göre olduçka yüksekti. DeepSeek OCR hem izinleri konusunda hem de sisteme entegrasyonu konusunda zaman kaybettiriyordu. Bağlılıkları oldukça fazlaydı. Literatüre baktığımızda performans sonuçlarında tablo, el yazısı vb. işlemlerde GLM-OCR diğer iki modelden en iyi performansı gösteren olmuştu. Modelin büyüklükleri açısından da GLM-OCR, DeepSeek-OCR'ın önüne geçmiş oldu. Paddle ve diğer denemeler de belirli açılardan faydalı oldu ama genel değerlendirmemde GLM-OCR daha umut verici bir seçenek gibi durdu. 

EasyOCR ile ilgili geliştirmelerimi ise **extraction** klasörü içerisinde yer alan *ocr_extractor_old* şeklinde saklamaktayım.

Bu geliştirmeler *file_router* içerisinde de değişikliklere neden oldu. Bir diğer açıdan *ocr_extractor_old* içerisinde yer alan preprocessing vb. yöntemlere GLM-OCR sayesinde ihtiyacımız kalmadı.

## Gün 3 - Chunking ve Metin Yapısını Retrieval’a Hazırlama
Extraction sonrasında elde ettiğim metni retrieval için daha uygun hale getirmeye odaklandım. Belgeden düz metin çıkarmak tek başına yeterli olmadığı için, bu metni küçük ama anlamlı parçalara bölmem gerektiğini fark ettim. Çünkü tüm belgeyi tek parça halinde embedding modeline vermek retrieval kalitesini düşürebilir ve LLM tarafına gereksiz uzun context taşınmasına neden olabilir.

Bu nedenle chunking katmanı için *app/processing/chunker.py* tasarlamaya başladım. İlk aşamada daha basit bir bölme mantığı denedim ancak bunun fazla kaba kaldığını gördüm. Bazı parçalar anlamsız yerlerden bölünüyor, bazıları ise paragraf bütünlüğünü bozuyordu. Özellikle overlap mantığında daha kontrollü bir yapıya ihtiyaç olduğunu fark ettim. Amacım sadece metni bölmek değil, extraction’dan çıkan ham veriyi retrieval için daha okunabilir ve daha kullanılabilir hale getirmekti.

Chunker tarafında metni önce normalize eden, ardından paragraf bazlı işleyen bir yapı kurdum. Eğer paragraf hedef boyutu aşıyorsa cümle bazlı fallback uyguladım; cümle de çok uzunsa bu kez kelime bazlı bölmeye geçtim. Böylece tamamen karakter bazlı kaba bir bölme yapmak yerine, mümkün olduğunca anlam bütünlüğünü koruyan ve daha dengeli parçalar üretmeye çalıştım.

Bunun yanında chunk metadata yapısını da oluşturdum. Her chunk için chunk_id, source_file, page_number, chunk_index, extraction_method ve char_length gibi alanlar tuttum. Bunun amacı retrieval sonucunu daha izlenebilir hale getirmek ve ileride answer katmanında kaynak takibi yapabilmek için temel bir veri yapısı hazırlamaktı.

Günün sonunda chunking katmanı, extraction sonrası elde edilen sayfa metinlerini retrieval’a daha uygun, daha düzenli ve metadata içeren küçük parçalara ayırabilen bir hale geldi. Yapı hâlâ geliştirilmeye açıktı, ancak sistemin sonraki aşamaları için yeterince sağlam bir temel oluşturdu.

---

## Gün 4 - Embedding seçimi ve sisteme entegrasyonu
Bugün projede extraction ve chunking sonrasında gelen metin parçalarını retrieval’a hazırlamak için embedding katmanını oluşturmaya odaklandım. Önceki aşamalarda belge metnini çıkarıp chunk’lara bölmüştüm; bugün amacım bu chunk’ları anlamsal olarak temsil edecek vektörlere dönüştürmek ve daha sonra kullanıcı sorusu ile bu chunk’lar arasında similarity search yapılabilecek yapıyı hazırlamaktı.

İlk olarak embedding modeli seçimi üzerinde durdum. Bu projede belgelerin sadece tek bir dilde gelmeyeceğini düşündüğüm için embedding modeli seçiminde çok dilli destek benim için önemliydi. Sisteme hem Türkçe hem İngilizce belgeler gelebilir, kullanıcı soruları da iki dilde gelebilir. Bu yüzden sadece İngilizce odaklı daha temel sentence-transformer modelleri başlangıçta benim için yeterli görünmedi. Amacım, hem Türkçe hem İngilizce metinleri aynı anlamsal uzayda temsil edebilecek bir model kullanmaktı.

Bu nedenle retrieval tarafında ilk tercih olarak **BAAI/bge-m3** modelini seçtim. Bu modeli seçmemin birkaç nedeni vardı. İlk olarak çok dilli bir yapı sunması, **Türkçe ve İngilizce** karışık senaryolarda daha mantıklı bir aday haline getiriyordu. İkinci olarak retrieval odaklı bir model olması benim kullanım senaryoma doğrudan uyuyordu; çünkü benim ihtiyacım genel metin temsili üretmekten çok, kullanıcı sorusu ile belge chunk’ları arasındaki anlamsal yakınlığı yakalamaktı. Üçüncü olarak, daha önce daha basic ve genel amaçlı embedding modelleri düşünmüş olsam da, bu proje için biraz daha güçlü ve retrieval tarafında daha ciddi duran bir model seçmek istedim.

Model seçimi sırasında bazı alternatifleri de değerlendirdim ama çeşitli nedenlerle elemek zorunda kaldım. Daha küçük ve daha basit çok dilli sentence-transformers modelleri kurulum açısından daha kolay görünse de, retrieval kalitesi ve “bu proje için biraz daha güçlü bir tercih yapma” hedefim nedeniyle onları ilk tercih yapmadım. Öte yandan embedding yerine doğrudan generative LLM’leri retrieval katmanında kullanmak da mantıklı gelmedi. Çünkü burada ihtiyacım cevap üretmek değil, chunk ile soru arasında semantic matching yapmak olduğu için embedding modeli kullanmak daha doğru olacağını düşündüm. Yani generative model ile retrieval çözmeye çalışmak yerine, retrieval için üretilmiş bir embedding modeli seçmeyi daha temiz buldum.

İlk teknik denemeyi **FlagEmbedding** üzerinden yaptım. Buradaki hedefim **BAAI/bge-m3** modelini kendi doğal kullanım biçimiyle ayağa kaldırmaktı. Ancak bu aşamada bağımlılık tarafında ciddi sorunlar yaşadım. Özellikle FlagEmbedding ile transformers sürümü arasında uyumsuzluk çıktı ve **is_torch_fx_available** import hatasıyla karşılaştım. Bu noktada sorunun benim retrieval mantığımdan değil, doğrudan package ekosisteminden kaynaklandığını gördüm. Yani burada modelin teorik olarak uygun olması yetmiyordu; pratikte environment ile sağlıklı ayağa kalkması da gerekiyordu.

Bu problemi çözmek için yaklaşım değiştirdim. FlagEmbedding tarafında zaman kaybetmek yerine, aynı modeli bu kez **SentenceTransformer("BAAI/bge-m3")** üzerinden kullanmayı denedim. Bu yöntem benim ortamımda çok daha stabil çalıştı. Böylece modelin dense embedding üretme tarafını daha sade ve yönetilebilir bir biçimde projeye entegre edebildim. Bu değişiklik önemliydi çünkü model seçimini tamamen bırakmak yerine, aynı modeli daha stabil bir kullanım yoluyla sisteme dahil etmiş oldum.

Embedding katmanını kurarken şu tasarımı benimsedim: chunk’lar için bir embed_texts() metodu, kullanıcı sorgusu için ise bir embed_query() metodu yazdım. Her iki tarafta da normalize edilmiş numpy embedding’ler ürettim. Normalizasyon kullanmamın nedeni similarity hesabını daha stabil hale getirmekti. Bu sayede chunk embedding’leri ile soru embedding’i arasında doğrudan dot product kullanarak semantic benzerlik hesaplayabildim.

Başlangıçta ayrı bir vector database ya da FAISS katmanı eklemeyi düşündüm. Ancak günün bu aşamasında önceliğim retrieval davranışını hızlı şekilde ayağa kaldırmak ve embedding modelinin çalıştığını doğrulamaktı. Bu yüzden önce daha sade bir in-memory semantic search yapısı kurdum. Chunk’lar bir kez embed ediliyor, bellekte tutuluyor ve kullanıcı sorusu geldiğinde sorgu embedding’i ile similarity hesaplanarak en ilgili chunk’lar sıralanıyordu. Bu yaklaşım büyük ölçek için ideal olmayabilir ama MVP ve hızlı doğrulama açısından bana ciddi hız kazandırdı.

Bugün uğraştığım önemli konulardan biri de modelin ilk yüklenme maliyetiydi. Özellikle BAAI/bge-m3 ilk kez kullanıldığında model dosyalarının indirilmesi ve cache’e alınması zaman aldı. Bunun, benim kodumun yavaşlığından çok modelin ilk setup maliyetinden kaynaklandığını gözlemledim. Bu yüzden daha sonra README tarafında ilk çalıştırmada modelin indirileceğini ve ilk kullanımın daha yavaş olabileceğini not etmeye karar verdim. Bu, projeyi ilk kez çalıştıracak kişi için de önemli bir bilgi oldu.

Günün sonunda embedding katmanı çalışır hale geldi. Extraction ve chunking sonrasında gelen belge parçaları artık vektörel olarak temsil edilebiliyordu. Ayrıca bu aşamada sadece teknik bir implementasyon yapmış olmadım; aynı zamanda neden bu embedding modelini seçtiğimi, neden bazı daha basit alternatifleri ikinci plana attığımı ve neden ilk denediğim kütüphane yaklaşımını değiştirip daha stabil bir entegrasyona geçtiğimi de netleştirmiş oldum.

1. paraphrase-multilingual-mpnet-base-v2 → daha genel amaçlı, retrieval için daha basic kaldı

2. multilingual-e5-large-instruct → güçlü ama daha ağır ve entegrasyon riski daha yüksek

3. Qwen embedding ailesi → yeni ve ilgi çekici ama proje süresine göre fazla riskli

4. generative LLM yaklaşımı → retrieval yerine generation problemi çözüyor, bu yüzden uygun değil

5. BAAI/bge-m3 → çok dilli + retrieval odaklı + proje ihtiyacıyla uyumlu

---
## Gün 5- Question-Answer için seçilen LLM modeline verilen karar
Bugün projede retrieval sonrasındaki final answer katmanını oluşturmaya odaklandım. Önceki aşamalarda extraction, chunking ve retrieval yapısını kurmuştum; bugün amacım bu yapıyı gerçek bir document question-answering akışına dönüştürmekti. Bu nedenle çalışmalarımı özellikle yerel LLM seçimi, LLM entegrasyonu, prompt tasarımı, cevap kalitesi ve son testler üzerine yoğunlaştırdım.

İlk olarak retrieval sonucunu gerçek bir cevap üretim katmanına bağlamak istedim. Ücretli bir API kullanmak istemediğim için bu aşamada yerel ve ücretsiz bir LLM tercih etmeye karar verdim. Bu yüzden **Ollama** üzerinden çalışan bir model kullanmayı seçtim. Model olarak **qwen2.5:7b** kullandım. Bu modeli seçmemin temel nedenleri, çok dilli desteğe sahip olması, lokalde ücretsiz çalışabilmesi ve retrieval’dan gelen birkaç chunk üzerinden kısa ve anlamlı cevap üretmeye uygun görünmesiydi. Böylece sistem ilk kez upload → extraction → chunking → retrieval → final answer hattına kavuşmuş oldu.

Yerel LLM entegrasyonu sırasında cevabı doğrudan retrieval sonucundan üretmek yerine, bu katmanı daha kontrollü hale getirmek için ayrı bir prompt yapısı kurdum. Bunun için *prompt_builder.py* ve *answer_service.py* bileşenlerini ayırdım. *prompt_builder.py* ile kullanıcı sorusunu ve retrieval’dan gelen chunk’ları düzenli bir bağlama dönüştürdüm; *answer_service.py* ise bu bağlamı **Ollama** üzerinden çalışan modele gönderip cevabı geri döndürdü. Bu ayrım sayesinde sistemin son katmanı daha modüler hale geldi ve prompt üzerinde daha rahat iyileştirme yapabildim.

İlk testlerde modelin bazı istenmeyen davranışlar gösterdiğini gördüm. Bunlardan ilki, final answer vermek yerine retrieval’dan gelen chunk’ın tamamını basmasıydı. Bu davranış retrieval testi için faydalı olsa da gerçek kullanıcı deneyimi açısından iyi değildi. Bu yüzden prompt içinde modelin sadece bağlama dayalı kısa ve net cevap üretmesini, tüm evidence metnini tekrar etmemesini ve mümkün olduğunca kısa bir answer vermesini vurguladım.

Bir diğer önemli problem çok dilli cevap üretiminde ortaya çıktı. Model bazı durumlarda doğru bilgiyi bulmasına rağmen cevapta dil karıştırabiliyordu. Özellikle İngilizce soruya Türkçe cevap verip araya Çince benzeri ifadeler sıkıştırdığı örneklerle karşılaştım. Burada problemin temel nedeninin modelin çok dilli olması ve dil kontrolünün prompt içinde yeterince sert tanımlanmamış olması olduğunu düşündüm. Bunu çözmek için prompt kurallarını güçlendirdim. Modelden yalnızca kullanıcının sorduğu dilde cevap vermesini, cevap içinde farklı diller karıştırmamasını ve tek dil kullanmasını açıkça istedim. Ayrıca daha deterministik ve tutarlı cevaplar elde etmek için temperature değerini düşürdüm.

Bugün karşıma çıkan bir başka önemli durum da liste ve referans tipi sorularda ortaya çıktı. Örneğin **“Bu makale hangi makalelere atıfta bulunmuştur?”** gibi sorularda model kaynakçanın tamamını vermiyor, sadece retrieval’dan gelen birkaç chunk içindeki maddeleri sıralıyordu. Bu noktada sorunun doğrudan LLM’den değil, retrieval recall’ından kaynaklandığını fark ettim. Çünkü model yalnızca kendisine verilen bağlam kadar cevap verebiliyordu. Bu nedenle liste, referans ve kaynakça odaklı sorularda retrieval sonucunu biraz genişletmeye karar verdim. Eğer soru references, citations, bibliography, kaynakça veya referanslar gibi liste odaklıysa, retrieval’dan dönen sonuçların bulunduğu sayfalardaki diğer chunk’ları da bağlama dahil etmeye başladım. Ayrıca prompt tarafında da liste sorularında mümkün olduğunca tüm öğelerin toplanması gerektiğini modele ek kurallarla belirttim.

Bugün ayrıca sistemin hallucination davranışını gözlemlemeye başladım. Bunun için hem belgede açıkça bulunan tarih, isim, kurum ve sayısal alanları sordum, hem de belgede yer almayan bilgileri bilinçli olarak test ettim. Bu aşamada modelin bazen eksik cevap verdiğini, ancak çoğu durumda tamamen uydurmak yerine “belgede bulunamadı” şeklinde daha güvenli bir davranış sergilediğini gördüm. Bu da retrieval-augmented answer yapısının en azından kısmen grounding mantığını koruduğunu gösterdi.

Bugünün sonunda sistem, retrieval’dan gelen chunk’lar üzerinden yerel bir LLM ile cevap üretebilen bir hale geldi. Artık uygulama yalnızca ilgili metin parçalarını göstermekle kalmıyor, bu parçaları kullanarak final answer da oluşturabiliyor. Sistem hâlâ mükemmel değil; özellikle çok uzun liste sorularında retrieval’ın daha da iyileştirilmesi ve çok dilli cevap formatının daha kararlı hale getirilmesi gerekiyor. Ancak bugün itibarıyla proje, sadece retrieval yapan bir prototip olmaktan çıkıp, yerel LLM ile çalışan gerçek bir document **question-answering** akışına dönüşmüş oldu.

## Gün 5 – Şu anki net teknik seçimlerim

**Şu aşamada belirlediğim temel teknoloji kararları:**

1. Arayüz: Streamlit

2. PDF metin çıkarma: PyMuPDF

3. Scanned/image extraction: GLM-OCR

4. Chunking: metadata koruyan paragraph-aware / sentence-fallback chunking

5. Embedding: BAAI/bge-m3 (SentenceTransformer ile)

6. Retrieval: in-memory semantic search

7. Yerel LLM altyapısı: Ollama

8. Cevap üretim modeli: qwen2.5:7b

**Final answer stratejisi: yalnızca retrieval ile bulunan bağlama dayalı cevap üretimi**

## Gün 6 - Arayüzü Düzenleme ve Demo Deneyimini İyileştirme
Bugün teknik olarak çalışan pipeline’ı daha profesyonel ve anlaşılır bir demo akışına dönüştürmeye odaklandım. Amaç sadece extraction, retrieval ve answer katmanlarının çalışması değil; bu akışı kullanıcı açısından daha okunabilir ve daha güçlü sunmaktı. Bu nedenle Streamlit arayüzünde başlık yapısını, bilgi kartlarını, sekme isimlerini ve final answer sunumunu yeniden düzenledim. “Document QA - Retrieval + Final Answer” başlığını daha ürün benzeri bir isim olan **“Document Insight Assistant”** ile değiştirdim. Ayrıca üst bölümde sistemin ne yaptığını anlatan kısa bir alan ve kullanılan modelleri gösteren bilgi kartları ekledim. Sekme yapısını daha anlaşılır hale getirerek “Retrieval + Final Answer” yerine **“Ask & Answer”** kullanımını tercih ettim. Final answer bölümünü daha belirgin göstermek için ayrı bir görsel kart yapısı kullandım; retrieval sonucu dönen kanıt parçalarını ise ikincil ama okunabilir bir yapı içinde bırakmaya devam ettim. Bugün yaptığım değişiklikler sistemin çekirdek mantığını değiştirmedi, ancak demoda algılanan kaliteyi ve kullanıcı deneyimini belirgin şekilde iyileştirdi. Daha sonra kod içerisinde anlaşılabilecek kısa açıklamalar ekledim. Bazı fonksiyonların ne işe yaradıklarını kısa cümlelerle açıkladım. **README.md** ve *requirements.py* dosyalarının üzerinden geçerek gerekli düzenlemeleri gerçekleştirdim. Diğer yandan sistem üzerindeki testlerime devam ettim. Zaman zaman cevaplarda yer alan dil karışması olayı ile yeniden karşılaştım. Bu problemlerin önüne geçmek için promptlarımda düzenlemeler yapmaya devam ettim.

## Gün 7 - Son Düzenlemeler
Bugün document QA akışında özellikle cevap dilinin kontrolü üzerine çalıştım. Sistemde soru İngilizce sorulmasına rağmen modelin Türkçe cevap verdiğini fark ettim ve bunun nedenini katman katman incelemeye başladım. İlk olarak *AnswerService.py* tarafını kontrol ettim. Bu katmanda doğrudan dili Türkçeye zorlayan bir yapı olmadığını gördüm; servis yalnızca oluşturulan mesajları LLM’e gönderip yanıtı geri alıyordu. Bu yüzden asıl odak noktamı *prompt_builder.py* tarafına çevirdim.

Prompt yapısını incelediğimde, aslında kurallar arasında “cevap kullanıcı sorusuyla aynı dilde olmalı” gibi doğru yönergeler bulunduğunu gördüm. Yani problem doğrudan promptta açık bir Türkçe zorlama olması değildi. Buna rağmen özellikle yerel ve daha küçük modellerin bu tür yönergeleri her zaman tutarlı şekilde uygulamadığını fark ettim. Bu yüzden dil kontrolünü sadece modele bırakmak yerine, soru dilini kod tarafında belirleyip prompta daha sert ve net şekilde ekleme fikrini değerlendirdim. Bu aşamada mevcut kuralları silmeden, yalnızca dil kısmını daha bağlayıcı hale getirecek bir yaklaşım tasarladım.

Günün ilerleyen kısmında sorunun yalnızca prompttan kaynaklanmayabileceğini düşündüm. Çünkü yapılan değişikliklere rağmen arayüzde hâlâ Türkçe cevap görünüyordu. Bunun üzerine sorunun Streamlit tarafında yanlış alanın gösterilmesinden kaynaklanabileceği ihtimalini ele aldım. Özellikle answer yerine ham model çıktısının (raw_response) ekrana basılıyor olması, ya da cache / eski process nedeniyle güncel kodun çalışmıyor olması gibi senaryoları değerlendirdim. Bu nedenle debug için hangi cevabın gerçekten UI’da gösterildiğini kontrol etmeye, çalışan dosya yollarını doğrulamaya ve cache / session state kaynaklı olası sorunları incelemeye yönelik adımlar planladım.

Bugünün sonunda en önemli çıktım, problemin tek başına retrieval ya da prompt kuralı seviyesinde değil, model davranışı ve uygulama katmanlarının etkileşimi içinde ele alınması gerektiğini görmek oldu. Ayrıca bu süreç bana, LLM çıktısını doğrudan doğru kabul etmek yerine gerektiğinde sonradan kontrol etme, yeniden yazdırma veya UI katmanında hangi verinin gösterildiğini doğrulama gibi savunmacı tasarım yaklaşımlarının önemli olduğunu gösterdi. Yani bugün yalnızca bir bug fix denemesi yapmadım; aynı zamanda sistemin cevap üretim zincirini daha sağlam ve izlenebilir hale getirmek için hangi noktaların kritik olduğunu netleştirmiş oldum.
