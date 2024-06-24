from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, send_file
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import joblib
import os
import logging
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'predictive_system'

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Memuat model yang telah dilatih
model = joblib.load('model_c4_5.pkl')
# Memuat informasi kolom yang dihasilkan oleh pd.get_dummies() saat pelatihan
with open('dummy_columns.pkl', 'rb') as f:
    dummy_columns = joblib.load(f)

app.logger.info("Model loaded successfully")

# Variabel global untuk menyimpan hasil prediksi
global_results = None

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(user[0], user[1])
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1])
            login_user(user_obj)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    global global_results
    if 'file' not in request.files:
        app.logger.error("No file part")
        return jsonify({'error': "No file part"})
    
    file = request.files['file']
    
    if file.filename == '':
        app.logger.error("No selected file")
        return jsonify({'error': "No selected file"})
    
    if file:
        # Simpan file ke folder uploads
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # Membaca file Excel dan mengonversinya ke JSON
        try:
            spreadsheet = pd.read_excel(file_path)
            
            # Verifikasi dan tampilkan beberapa baris pertama
            app.logger.info(spreadsheet.head())
            
            # Ambil kolom identitas
            identities = spreadsheet[['NISN', 'NAMA']]
            
            # Ambil hanya kolom yang dibutuhkan untuk prediksi
            features = ['SIKAP', 'Peng', 'Ket', 'PTS', 'PAS']
            input_data = spreadsheet[features]
            
            # Lakukan one-hot encoding pada data baru
            input_data_encoded = pd.get_dummies(input_data)
            
            # Pastikan semua kolom yang dihasilkan saat pelatihan ada di data baru
            for col in dummy_columns:
                if col not in input_data_encoded:
                    input_data_encoded[col] = 0
            
            # Urutkan kolom agar sesuai dengan data pelatihan
            input_data_encoded = input_data_encoded[dummy_columns]

            # Melakukan prediksi
            prediction = model.predict(input_data_encoded)
            
            # Pemetaan hasil prediksi
            prediction_mapped = ["Memuaskan" if p == 1 else "Kurang Memuaskan" for p in prediction]
            
            # Gabungkan hasil prediksi dengan identitas siswa dan semua kolom asli
            results = spreadsheet.copy()
            results['prediction'] = prediction_mapped
            global_results = results

            result_list = results.to_dict(orient='records')

            app.logger.info("Prediction successful")
            return jsonify(result_list)

        except Exception as e:
            app.logger.error(f"Error processing file: {e}")
            return jsonify({'error': str(e)})

@app.route('/download', methods=['GET'])
@login_required
def download():
    global global_results
    if global_results is None:
        return "No predictions available to download.", 400
    
    # Convert dataframe to Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        global_results.to_excel(writer, index=False, sheet_name='Predictions')
    output.seek(0)
    
    return send_file(output, download_name='predictions.xlsx', as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
