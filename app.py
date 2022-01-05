from flask import Flask, render_template, request, redirect, url_for
import os
from pathlib import Path
downloads_path = str(Path.home() / "Downloads")
from rsa import * 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
app = Flask(__name__)  
authUsername = ""


# khai báo hàm đọc danh sách user.
def readUserList():
    userList = []
    file = open("accountLogin.txt", "r")
    for line in file:
        tmp = line.split('-')
        userList.append(tmp)
    file.close()
    return userList

# khai báo hàm đọc danh sách khóa công khai.
def readPublicKeyList():
    publicKey = []
    file = open("publicKey.txt", "r")
    for line in file:
        tmp = line.split('-')
        publicKey.append(tmp)
    file.close()
    return publicKey

# khai báo hàm đọc danh sách khóa bí mật.
def readPrivateKeyList():
    privateKey = []
    file = open("privateKey.txt", "r")
    for line in file:
        tmp = line.split('-')
        privateKey.append(tmp)
    file.close()
    return privateKey

#lấy khóa bí mật bằng username
def getPrivateByUsername(username, privateKey):
    for keys in privateKey:
        if keys[0] == username:
            return keys

#lấy khóa công khai bằng username
def getPublicByUsername(username, publicKey):
    for keys in publicKey:
        if keys[0] == username:
            return keys

#khai báo thêm tài khoản user:
def addNewUser(info):
    f = open("accountLogin.txt", "a")
    f.write('\n'+info)

#khai báo hàm kiểm tra username và password
def checkUser(username, password, userList):
    for user in userList:
        if user[0] == username and user[1] == password:
            return 1  
    return 0

#khai báo hàm kiểm tra username => username ko được trùng.
def checkUsername(username, userList):
    for user in userList:
        if user[0] == username:
            return 1  
    return 0

#các file html; buộc phải nằm trong thư mục templates (bắt buộc phải là templates)
#khai báo index. (trang chủ khi mới vào trang web)
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

#khai báo login.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form:
        username = request.form['Username']
        password = request.form['Password']
        userList = readUserList()
        isUser = checkUser(username, password, userList)
        if (isUser == 1):
            global authUsername 
            authUsername = username
            return redirect(url_for("homeLogin")) #đăng nhập thành công -> vào trang chủ homeLogin.
        else:
            return render_template('login.html', err_message = True)
    return render_template('login.html', err_message = False)

#khai báo home (login thành công)
@app.route('/homeLogin', methods=['GET', 'POST'])
def homeLogin():
    return render_template('home.html', username = authUsername)

#khai báo viewImgs (xem toàn bộ ảnh)
@app.route('/viewImgs', methods=['GET', 'POST'])
def viewImgs():
    if request.method == 'GET':
        directory_path = 'static/uploads/' + authUsername
        No_of_files = len(os.listdir(directory_path))
        return render_template('viewImgs.html', username = authUsername, numberofFile = No_of_files)
    if request.method == 'POST':
        filename = request.args.get('filename')
        privateKey = readPrivateKeyList()
        keys = getPrivateByUsername(authUsername,privateKey)
        print(keys)
        downloads_path = str(Path.home() / "Downloads")

        my_img = mpimg.imread('static/uploads/' + authUsername + '/'+filename)
        DecryptionIMIG(527, 131, my_img, my_img)

        
        cv2.imwrite(downloads_path + '/' + filename, my_img)

        directory_path = 'static/uploads/' + authUsername
        No_of_files = len(os.listdir(directory_path))
        return render_template('viewImgs.html',username = authUsername, numberofFile = No_of_files)

#khai báo register.
@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form and 'ConfirmPassword' in request.form:
        username = request.form['Username']
        password = request.form['Password']
        confirmPass = request.form['ConfirmPassword']
        if confirmPass != password:
            return render_template('register.html', err = True, message = "Mật khẩu không khớp!")
        userList = readUserList()
        isUser = checkUsername(username, userList)
        
        id = len(userList) + 1
        if (isUser == 0):
            addNewUser(username+'-'+password+'-'+str(id))
            return redirect(url_for("login")) #nếu đăng ký thành công, nhảy sang login
        else:
            return render_template('register.html', err = True, message = "Username đã tồn tại!")
    return render_template('register.html', err = False)


    



if __name__ =="__main__":\
    app.run('localhost', 5000)