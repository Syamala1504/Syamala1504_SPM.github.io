from flask import Flask, request, render_template, redirect, url_for, flash, session, send_file
from flask_session import Session
import mysql.connector
from otp import genotp
from cmail import sendmail
from keys import secret_key, salt, salt2
from itsdangerous import URLSafeTimedSerializer
from tokens import token
from io import BytesIO

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

mydb = mysql.connector.connect(host='localhost', user='root', password='admin', db='spm')
app.secret_key = secret_key

@app.route('/')
def home():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['cpassword']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(*) FROM user WHERE email=%s', [email])
        count = cursor.fetchone()[0]
        if count == 1:
            flash('Email already exists')
            return redirect(url_for('register'))
        else:
            if password == cpassword:
                otp = genotp()
                var1 = {'name': name, 'password': password, 'email': email, 'aotp': otp}
                subject = 'Verification OTP for SPM'
                body = f'OTP for SPM Application: {otp}'
                sendmail(to=email, subject=subject, body=body)
                flash('Verification OTP sent to your email')
                return redirect(url_for('verifyotp', aotp=token(data=var1, salt=salt)))
            else:
                flash('Passwords do not match')
                return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT COUNT(*) FROM user WHERE email=%s', [email])
        count = cursor.fetchone()[0]
        if count == 1:
            cursor.execute('SELECT password FROM user WHERE email=%s', [email])
            cpassword = cursor.fetchone()[0]
            if cpassword == password:
                session['user'] = email
                if not session.get(email):
                    session[email] = {}
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect password')
                return redirect(url_for('login'))
        else:
            flash('Email not registered')
            return redirect(url_for('register'))
    return render_template('login.html')

@app.route('/verifyotp/<aotp>', methods=['GET', 'POST'])
def verifyotp(aotp):
    try:
        serializer = URLSafeTimedSerializer(secret_key)
        var1 = serializer.loads(aotp, salt=salt, max_age=120)
    except Exception:
        flash('OTP expired')
        return render_template('otp.html')
    if request.method == 'POST':
        uotp = request.form['otp']
        if var1['aotp'] == uotp:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('INSERT INTO user(name, email, password) VALUES(%s, %s, %s)', 
                           [var1['name'], var1['email'], var1['password']])
            mydb.commit()
            cursor.close()
            flash('Registration successful')
            return redirect(url_for('login'))
        else:
            flash('Incorrect OTP')
    return render_template('otp.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        subject = 'Reset Link for Forgot Password'
        body = f'Click the link to reset your password: {url_for("verifyforgot", data=token(data=email, salt=salt2), _external=True)}'
        sendmail(to=email, subject=subject, body=body)
        flash('Reset link sent to your email')
        return redirect(url_for('forgot'))
    return render_template('forgot.html')

@app.route('/verifyforgot/<data>', methods=['GET', 'POST'])
def verifyforgot(data):
    try:
        serializer = URLSafeTimedSerializer(secret_key)
        data = serializer.loads(data, salt=salt2, max_age=180)
    except Exception:
        flash('Link expired')
        return redirect(url_for('forgot'))
    if request.method == 'POST':
        npassword = request.form['npassword']
        cpassword = request.form['cnpassword']
        if npassword == cpassword:
            cursor = mydb.cursor(buffered=True)
            cursor.execute('UPDATE user SET password=%s WHERE email=%s', [npassword, data])
            mydb.commit()
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match')
    return render_template('updatepassword.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/addnotes', methods=['GET', 'POST'])
def addnotes():
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT id FROM user WHERE email=%s', [session.get('user')])
        u_id = cursor.fetchone()[0]
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['content']
            cursor.execute('INSERT INTO notes(title, description, u_id) VALUES(%s, %s, %s)', [title, description, u_id])
            mydb.commit()
            cursor.close()
            flash(f'Note titled "{title}" added successfully')
            return redirect(url_for('dashboard'))
        return render_template('addnotes.html')
    return redirect(url_for('login'))

@app.route('/view_allnotes')
def view_allnotes():
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT id FROM user WHERE email=%s', [session.get('user')])
        u_id = cursor.fetchone()[0]
        cursor.execute('SELECT notes_id, title, created_at FROM notes WHERE u_id=%s', [u_id])
        data = cursor.fetchall()
        return render_template('table.html', data=data)
    return redirect(url_for('login'))

@app.route('/view_notes/<nid>')
def view_notes(nid):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT title, description, created_at FROM notes WHERE notes_id=%s', [nid])
        data1 = cursor.fetchall()
        return render_template('viewnotes.html', data1=data1)
    return redirect(url_for('login'))

@app.route('/update/<nid>', methods=['GET', 'POST'])
def update(nid):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            cursor.execute('UPDATE notes SET title=%s, description=%s WHERE notes_id=%s', [title, content, nid])
            mydb.commit()
            flash(f'Note with ID {nid} updated successfully.')
            return redirect(url_for('view_allnotes'))
        cursor.execute('SELECT title, description FROM notes WHERE notes_id=%s', [nid])
        data1 = cursor.fetchall()
        return render_template('update.html', data1=data1)
    return redirect(url_for('login'))

@app.route('/delete/<nid>')
def delete_notes(nid):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('DELETE FROM notes WHERE notes_id=%s', [nid])
        mydb.commit()
        cursor.close()
        flash(f'Note with ID {nid} deleted successfully')
        return redirect(url_for('view_allnotes'))
    return redirect(url_for('login'))

@app.route('/fileupload', methods=['GET', 'POST'])
def fileupload():
    if session.get('user'):
        if request.method == 'POST':
            data = request.files['file']
            file_data = data.read()
            file_name = data.filename
            cursor = mydb.cursor(buffered=True)
            cursor.execute('SELECT id FROM user WHERE email=%s', [session.get('user')])
            u_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO files(filename, filedata, u_id) VALUES(%s, %s, %s)', [file_name, file_data, u_id])
            mydb.commit()
            cursor.close()
            flash('File uploaded successfully.')
        return render_template('fileupload.html')
    return redirect(url_for('login'))

@app.route('/view_allfiles')
def view_allfiles():
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT id FROM user WHERE email=%s', [session.get('user')])
        u_id = cursor.fetchone()[0]
        cursor.execute('SELECT * FROM files WHERE u_id=%s', [u_id])
        count = cursor.fetchall()
        cursor.close()
        return render_template('fileview.html', count=count)
    return redirect(url_for('login'))

@app.route('/view_file/<fid>')
def view_file(fid):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT filename, filedata FROM files WHERE fid=%s', [fid])
        data = cursor.fetchone()
        cursor.close()
        filename = data[0]
        bin_file = data[1]
        byte_data = BytesIO(bin_file)
        return send_file(byte_data, download_name=filename)
    return redirect(url_for('login'))

@app.route('/download_file/<fid>')
def download_file(fid):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('SELECT filename, filedata FROM files WHERE fid=%s', [fid])
        data = cursor.fetchone()
        cursor.close()
        filename = data[0]
        bin_file = data[1]
        byte_data = BytesIO(bin_file)
        return send_file(byte_data, download_name=filename, as_attachment=True)
    return redirect(url_for('login'))

@app.route('/fdelete/<fid>')
def fdelete(fid):
    if session.get('user'):
        cursor = mydb.cursor(buffered=True)
        cursor.execute('DELETE FROM files WHERE fid=%s', [fid])
        mydb.commit()
        cursor.close()
        flash(f'File with ID {fid} deleted successfully')
        return redirect(url_for('view_allfiles'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
