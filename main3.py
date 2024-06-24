import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Membaca data dari file Excel
file_path = 'Data_FINAL.xlsx'
df = pd.read_excel(file_path)


# Misalkan kolom target adalah 'HASIL_BELAJAR'
target = 'HASIL_BELAJAR'
features = [col for col in df.columns if col != target]


# Encoding fitur kategorikal menjadi numerik
df_encoded = pd.get_dummies(df[features])
y = df[target].apply(lambda x: 1 if x == 'Memuaskan' else 0)

# Menampilkan beberapa baris pertama dari data
#print(df.head())

# Menampilkan tipe data dari setiap kolom
#print(df.dtypes)

# Membagi data menjadi training dan testing set
X_train, X_test, y_train, y_test = train_test_split(df_encoded, y, test_size=0.2, random_state=42)

# Melatih model dengan data training
model = DecisionTreeClassifier(criterion='entropy', random_state=42)
model.fit(X_train, y_train)

# Prediksi pada data test
y_pred = model.predict(X_test)

# Evaluasi
accuracy = accuracy_score(y_test, y_pred)
print(f'Akurasi: {accuracy * 100:.2f}%')
print(classification_report(y_test, y_pred))

# Menyimpan model ke file
joblib_file = "model_c4_5.pkl"
joblib.dump(model, joblib_file)
print(f'Model disimpan ke {joblib_file}')

# Simpan informasi kolom yang dihasilkan oleh pd.get_dummies()
dummy_columns = df_encoded.columns
with open('dummy_columns.pkl', 'wb') as f:
    joblib.dump(dummy_columns, f)

# Menampilkan ukuran dari masing-masing set
#print("Ukuran X_train:", X_train.shape)
#print("Ukuran X_test:", X_test.shape)
#print("Ukuran y_train:", y_train.shape)
#print("Ukuran y_test:", y_test.shape)

# Menampilkan beberapa contoh dari masing-masing set
#print("\nContoh data X_train:\n", X_train.head())
#print("\nContoh data X_test:\n", X_test.head())
#print("\nContoh label y_train:\n", y_train.head())
#print("\nContoh label y_test:\n", y_test.head())
