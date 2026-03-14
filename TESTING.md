*** Test ve Doğrulama ***

Bu projede test süreci, sistemin uçtan uca hattının farklı belge türlerinde nasıl davrandığını gözlemlemek amacıyla gerçekleştirilmiştir. Amaç yalnızca tek bir belge üzerinde çalıştığını göstermek değil; extraction, OCR, chunking, embedding ve retrieval adımlarının birlikte ne kadar tutarlı çalıştığını görmekti. Bu nedenle testler hem metin tabanlı PDF’lerde hem de taranmış belge ve görsellerde manuel olarak yapılmıştır.

*** Test edilen senaryolar ***

*Sistem aşağıdaki temel senaryolar üzerinde denenmiştir:*

1. Metin tabanlı PDF dosyaları
İçinde seçilebilir metin bulunan PDF’lerde doğrudan PDF text extraction kullanılmıştır. Bu senaryoda amaç, OCR’a ihtiyaç duymadan doğru metin çıkarımı yapılıp yapılamadığını ve sonrasında retrieval hattının düzgün çalışıp çalışmadığını doğrulamaktı.

2. Taranmış PDF ve görsel dosyaları
JPG/PNG dosyaları ile taranmış PDF belgelerde OCR devreye alınmıştır. Bu aşamada önce farklı OCR çözümleri değerlendirilmiş, EasyOCR’un düşük kaliteli sonuç verdiği görülmüştür. PaddleOCR ve DeepSeek OCR da denenmiş, ancak mevcut proje kısıtları ve elde edilen çıktı kalitesi dikkate alındığında GLM-OCR daha uygun bir seçenek olarak tercih edilmiştir.

3. İngilizce ve Türkçe içerikler
Belgeler yalnızca tek bir dil ile sınırlandırılmamış, mümkün olduğunca İngilizce ve Türkçe örneklerle denenmiştir. Böylece OCR ve retrieval tarafında dil değişiminin etkisi gözlemlenmiştir.

4. Yapısal olarak zor belgeler
Form benzeri, alan bazlı veya tablo içeren belgeler üzerinde de test yapılmıştır. Bu belgeler özellikle OCR sonrası metnin bozulmaya daha açık olduğu senaryoları temsil etmektedir.

5. Belgede cevabı olmayan sorular
Sistemin yalnızca doğru cevap üretmesi değil, cevap belgede yoksa nasıl davrandığı da gözlemlenmiştir. Bu testler, retrieval tabanlı sistemlerin sınırlarını görmek açısından önemlidir.

*** Test yaklaşımı ***

Bu projede kapsamlı bir benchmark veri seti ve nicel metrik seti oluşturulmamıştır. Bunun yerine, MVP seviyesinde sistem davranışını anlamaya yönelik manuel ve senaryo bazlı doğrulama yapılmıştır. Değerlendirme sırasında özellikle şu noktalar incelenmiştir:

- Belgenin doğru işleme hattına yönlenip yönlenmediği

- OCR gereken belgelerde okunabilir metin üretilebilmesi

- Chunk’ların anlamsız yerlerden bölünmemesi

- Soruya karşılık dönen parçaların gerçekten ilgili olup olmaması

- Farklı belge türlerinde sistemin kararlılığı

- Farklı belge türlerinde gözlenen performans

### Metin tabanlı PDF’ler:
En başarılı sonuçlar bu belge tipinde elde edilmiştir. Çünkü bu tür dosyalarda OCR hatası oluşmadan doğrudan metin alınabilmiştir. Retrieval tarafında da daha temiz metin kullanıldığı için ilgili chunk’ların bulunması daha başarılı olmuştur.

### Taranmış PDF ve görüntüler:
Bu belgelerde performans büyük ölçüde OCR kalitesine bağlı kalmıştır. GLM-OCR ile önceki denemelere göre daha iyi sonuç alınsa da düşük çözünürlük, eğik tarama, gürültü ve bozuk baskı gibi durumlarda metin kalitesi düşmüştür. OCR hatası arttıkça retrieval başarısı da doğrudan etkilenmiştir. Fakat bu düşüş oldukça minimize edilmiş ve GLM-OCR ile birlikte yüklenen belgelerin temel yapısı bozulmadan metin hali çıkarılabilmiştir.

### İngilizce belgeler:
İngilizce belgelerde genel olarak daha stabil sonuçlar alınmıştır. Özellikle metin tabanlı PDF’lerde sistem daha tutarlı davranmıştır.

### Türkçe belgeler:
Türkçe belgelerde sistem çalışsa da OCR kaynaklı karakter hataları ve veri çeşitliliğinin sınırlı olması nedeniyle sonuçlar İngilizce kadar stabil olmamıştır. Özellikle taranmış Türkçe belgelerde kalite düşüşü daha belirgin olmuştur.

### Tablolu / form benzeri belgeler:
Bu tip belgelerde sistem bazı alan adlarını ve hücre içeriklerini yakalayabilmiştir; tablo yapısını veya belge düzenini büyük çoğunlukla koruduğu gözlemlenmiştir.

*** Örnek sorular ve gözlenen yanıt tipi ***

Aşağıdaki örnekler, sistemin nasıl davrandığını göstermek amacıyla hazırlanmıştır:

1. Soru: Belgenin başlığı nedir?
Gözlem: Başlık çoğunlukla tüm belge türlerinde doğru şekilde bulunmuştur.

2. Soru: Belgedeki tarih bilgisi nedir?
Gözlem: Net yazılmış ve okunabilir alanlarda tarih bilgisi bulunabilmiştir; ancak taranmış belgelerde OCR hataları nedeniyle tarih alanında yanlış ya da eksik sonuç görülebilmiştir.

3. Soru: Dokümanda hangi departman / bölüm adı geçiyor?
Gözlem: Form benzeri belgelerde bu tür alan bazlı bilgiler bazen doğru çekilmiş, bazen de chunk yapısı nedeniyle eksik bilgi ile dönmüştür.

4. Soru: Bu belge ne anlatıyor?
Gözlem: Retrieval aşaması ilgili chunk’ı döndürebildiğinde genel içerik hakkında anlamlı bir cevap üretmek mümkün olmuştur; ancak bu kalite tamamen çıkarılan metnin doğruluğuna bağlı kalmıştır.

*** Sistemin başarısız olduğu veya yetersiz kaldığı durumlar ***

Sistem şu durumlarda zayıf kalmıştır:

- Düşük kaliteli taramalar

- Eğik, bulanık veya gürültülü görseller

- OCR sonrası karakterlerin ciddi bozulduğu içerikler

- İngilizce sorulan sorularda cevapların türkçe gelmesi

- Bazı cevaplarda birer kelimenin sistemde beklenmeyen dil yapısıyla gelmesi

Bu noktada en kritik gözlem şudur:
Sistem cevaplarında ingilizce ve türkçeden farklı olarak örneğim çince bazı kelimeleri de bulundurması. Burada promptları daha kesin cümleler eklenerek önüne geçilmeye çalışılmıştır.

*** Belgede olmayan bilgi sorulduğunda sistemin davranışı: ***

Sistem retrieval tabanlı olduğu için, soru belgede hiç geçmediği durumlarda  mevcut haliyle sistem her zaman “bu bilgi belgede yok” demiştir. 
Mevcut prototipte, soru belgede bulunmasa bile embedding tabanlı arama en yakın chunk’ı getirmektedir. Bu nedenle sistem bazen gerçekten olmayan bir bilgi için de ilgiliymiş gibi görünen bir parça döndürebilmektedir. Bu durum, nadir gözlemlenmiştir.

*** Bu problemi azaltmak için ileride şu geliştirmeler planlanabilir: ***

1. similarity threshold kullanmak

2. retrieval sonrası ek doğrulama katmanı eklemek

3. cevap üretmeden önce kaynak chunk ile soru arasındaki tutarlılığı kontrol etmek

*** Genel değerlendirme ***

Sistem; özellikle metin tabanlı PDF’lerde ve yüksek çözünürlüklü dokümanlarda, Document QA (Soru-Cevap) mimarisinin temel prensiplerini başarıyla sergilemiştir. Projenin en güçlü yönü; doküman türünü (dijital veya taranmış) otomatik olarak analiz ederek uygun extraction (metin çıkarma) yöntemini seçmesi ve bu veriyi retrieval (erişim) katmanı için optimize edilmiş bir yapıya dönüştürebilmesidir.

Sistemin Performans Analizi:

OCR ve Görsel İşleme: GLM-OCR entegrasyonu ile görsel tabanlı ve taranmış belgeler, yüksek doğrulukla işlenebilir metin formatına dönüştürülmüştür. Ancak; verinin eğik, bulanık veya gürültülü (noise) olduğu senaryolarda karakter düzeyinde hatalar (character recognition errors) gözlemlenmiştir.

Yanıt Üretimi ve Dil Yapısı: Mevcut iterasyonda tespit edilen temel kısıt, LLM katmanının yanıt üretirken zaman zaman dil karmaşası (code-switching) yaşamasıdır. Özellikle Türkçe veya İngilizce sorgularda farklı dillerde terimlerin yoğun kullanımı raporlanmıştır.

Bağlam Derinliği: Sistem, retrieval aşamasında elinde daha geniş bir kanıt metni (context) bulunmasına rağmen, final aşamasında yanıtları beklenenden daha kısa veya özet formda iletebilmektedir. Bu durum, prompt üzerindeki kısıtlamaların veya modelin verbosity (söz kalabalığı) ayarlarının optimize edilmesi gerektiğini göstermektedir.

*** Neleri Düzelttim? ***
Terminoloji: "Doğru metin belgeleri haline getirilmiştir" yerine "yüksek doğrulukla işlenebilir metin formatına dönüştürülmüştür" gibi daha teknik bir dil kullandım.

Akış: Sorunları (OCR hataları, dil karmaşası, kısa cevaplar) maddeler halinde ayırarak okunabilirliği artırdım.

Hata Tanımları: "Döndürebileceği daha fazla metin varken" ifadesini "Bağlam Derinliği" ve "Context kullanımı" çerçevesinde daha profesyonelce ifade ettim.