import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width',500)

# 1. Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
df_ = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
print("ADIM 1")
df.head()
print("###################################################################################")


# 2. Veri setinin betimsel istatistiklerini inceleyiniz.
print("ADIM 2")
print(df.describe().T) #Aykırı değerler için ön izleme; eksi değerler iadelerden kaynaklı
print(df.columns)


print(df[df["Quantity"] < 0].head())#Quantity değeri 0'dan küçük olan değerler var
df=df[df["Quantity"] > 0] #Bu sebeple iade işlemlerini hesaba katmayacağız
#df = df[~df["Invoice"].astype(str).str.contains("C", na=False)]  --> Soru 8'in cevabı ile de iade/iptal işlemlerini çıkarmış oluruz.
print("###################################################################################")


# 3. Veri setinde eksik gözlem varmı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
print("ADIM 3")
print(df.isnull().sum())
print("###################################################################################")


# 4. Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’parametresini kullanınız.
print("ADIM 4")
df.dropna(inplace=True)  #assignment ile de yapılabilirdi
#Satırda, herhangi bir veya daha fazla sütuna ait değer boş ise satırı drop eder.
print(df.isnull().sum()) #Drop işleminden sonra boş değerin olmaması beklenir.
print("###################################################################################")



# 5. Eşsiz ürün sayısı kaçtır?
print("ADIM 5")
print(df["StockCode"].nunique())
print("###################################################################################")


# 6. Hangi üründen kaçar tane vardır?
print("ADIM 6")
print(df["Description"].value_counts().head())
#df.groupby("StockCode").agg({"Quantity": lambda x:x.sum()})
print("###################################################################################")


# 7. En çok sipariş edilen 5 ürünü çoktan aza doğru sıralayınız.
print("ADIM 7")
print(df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head())
print("###################################################################################")


# 8. Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
print("ADIM 8")
df = df[~df["Invoice"].astype(str).str.contains("C", na=False)]
print(df)
print("###################################################################################")


# 9. Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
print("ADIM 9")
df["TotalPrice"] = df["Quantity"] * df["Price"]

print(df.groupby('Invoice').agg({'TotalPrice': lambda x:x.sum()})) #Fatura başına elde edilen toplam kazanç

print("###################################################################################")


###############################################################
# Görev 2: RFM Metriklerinin Hesaplanması
###############################################################

#Not 1: recency değeri için bugünün tarihini (2011, 12, 11) olarak kabul ediniz.
#Not 2: rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.

print("GÖREV 2")

print("Invoice Data Max")
print(df["InvoiceDate"].max())

today_date = dt.datetime(2011, 12, 11)
#InvoiceDate --> Recency'e ulaşabilmek için
#Invoice --> Frequency'e ulaşabilmek için
#TotalPrice --> Monetary'e ulaşabilmek için
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days, #bugünün tarihi - alışveriş yaptığı en son tarih
                                     'Invoice': lambda num: num.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

#Bir müşteriye gittik. Agg invoice date dediğimizde müşterinin yaptığı bütün alışveriş içinden en son alışveriş tarihini seçtik
#Frequency bulabilmek için müşterinin bütün Invoice larına gittik. Kaç tane unique fatura kesilmiş buna eriştik.
#Monetary erişmek için tüm faturalardaki toplam harcamasına eriştiğimiz TotalPrice'ı kullnadık
print(rfm.head())

rfm.columns = ['recency', 'frequency', 'monetary'] #InvoiceData, Invoice, TotalPrice olan sütun adlarını değiştirmek için

print(rfm.head())

print("###################################################################################")
###############################################################
# Görev 3: RFM Skorlarının Oluşturulması ve Tek Bir Değişkene Çevrilmesi
###############################################################

print("GÖREV 3")
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])  #Recency değerinin küçük olması bizim açımızdan iyidir; bu sebeple labels'ı 5ten 1e yapılır
#qcut fonksiyonu ile 5 tane çeyrekliğe böl demiş oluyoruz. Küçükten büyüğe sıraladığı için küçük değer bizim için değerli olduğu için buna 5 değerini vererek başla demiş olduk.
#Daha küçük olan değerler skor tarafında 5 ile etiketlensin demiş olduk
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
#Frekansta 1 değerlerinin çok olduğunu düşünelim. 100 tane mesela. Bunu 5 parçaya böleceğiz. İlk aralıkta 20 tane 1. İkinci aralığa geçtiğimizde hala 1'ler devam ediyorsa
#bu rpoblem yaratıyor, çünkü aralıkların unique olmasını istiyor fonksiyon. Bunun için rank(method="first") kullanılır. Böylece bu 1 değerleri 2 olarak etiketleyebiliyor.
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])


rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))
print(rfm["RFM_SCORE"])

print("###################################################################################")


###############################################################
# Görev 4: RFM Skorlarının Segment Olarak Tanımlanması
###############################################################

# RFM isimlendirmesi
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}


#Oluşturulan RFM skorlarının daha açıklanabilir olması için  segment tanımları yapmak amacıyla hazır olan regex yapısını kullandık
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

print("GÖREV 4")
print(rfm.head())


print("###################################################################################")
###############################################################
# Görev 5: Aksiyon zamanı!
###############################################################
print("GÖREV 5")


#Önemli bulduğunuz 3 segmenti seçiniz.
#Bu üç segmenti;-Hem aksiyon kararları açısından,-Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.

print(rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])) #segmentleri yorumlamak amacıyla


#"Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
new_df = pd.DataFrame()
new_df["loyal_customers"] = rfm[rfm["segment"] == "loyal_customers"].index
new_df.head()

new_df.to_csv("loyal_customers.csv")

print("###################################################################################")

