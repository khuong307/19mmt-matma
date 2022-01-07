from flask import Flask, render_template, request, redirect, url_for
import os
from pathlib import Path
downloads_path = str(Path.home() / "Downloads")
from rsa import * 
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
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

#khai báo thêm khóa công khai cho người dùng mới:
def addNewPublicKey(info):
    f = open("publicKey.txt", "a")
    f.write('\n'+info)

#khai báo thêm khóa công khai cho người dùng mới:
def addNewPrivateKey(info):
    f = open("privateKey.txt", "a")
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
    publicKey = readPublicKeyList()
    keys = getPublicByUsername(authUsername, publicKey)

    return render_template('home.html', username = authUsername, N = keys[1], E = keys[2])

#khai báo viewImgs (xem toàn bộ ảnh)
@app.route('/viewImgs', methods=['GET', 'POST'])
def viewImgs():
    if request.method == 'GET':
        directory_path = 'static/uploads/' + authUsername
        print(directory_path)
        No_of_files = len(os.listdir(directory_path)) // 2 
        return render_template('viewImgs.html', username = authUsername, numberofFile = No_of_files)
    if request.method == 'POST':
        filename = request.args.get('filename')
        privateKey = readPrivateKeyList()
        keys = getPrivateByUsername(authUsername,privateKey)
        downloads_path = str(Path.home() / "Downloads")

        my_img = mpimg.imread('static/uploads/' + authUsername + '/'+filename)
        stt_file = filename.split('_')
        enc = np.load('static/uploads/' + authUsername + "/"+authUsername+"_"+str(stt_file[1])+"_sub.npy")
        DecryptionIMIG(int(keys[1]), int(keys[2]), my_img,enc)
    
        data = Image.fromarray(my_img)
        data.save(downloads_path + '/' + filename)

        directory_path = 'static/uploads/' + authUsername
        No_of_files = len(os.listdir(directory_path)) // 2 
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
            #khởi tạo khóa cho người dùng.
            P = generatePrimeNumber(5)
            Q = generatePrimeNumber(5)
            N = P*Q
            eulerTotient=(P-1)*(Q-1)

            E = generatePrimeNumber(4)
            while GCD(E,eulerTotient)!=1:
                E = generatePrimeNumber(4)
            
            #thêm vào publicKey.txt
            addNewPublicKey(username+"-"+str(N)+"-"+str(E))

            #tính D + thêm vào privateKey.txt
            D=gcdExtended(E,eulerTotient)
            addNewPrivateKey(username+"-"+str(N)+"-"+str(D))

            #tạo 1 thư mục cho người dùng mới để upload ảnh
            os.mkdir('static/uploads/'+username)
            
            return redirect(url_for("login")) #nếu đăng ký thành công, nhảy sang login
        else:
            return render_template('register.html', err = True, message = "Username đã tồn tại!")
    return render_template('register.html', err = False)

@app.route('/uploadImg', methods=['GET', 'POST'])
def uploadImg():
    if request.method == 'POST':
        file = request.files['main']
        #lưu ảnh vào folder của ng dùng.
        directory_path = 'static/uploads/' + authUsername
        No_of_files = len(os.listdir(directory_path)) // 2 
        file.filename = authUsername+"_"+str(No_of_files+1)+"_enc.jpg"
        path_file = 'static/uploads/'+ authUsername + "/" + file.filename
        print(path_file)
        file.save(path_file)

        #lấy thông tin khóa công khai.
        publicKey = readPublicKeyList()
        keys = getPublicByUsername(authUsername,publicKey)

        # mã hóa tấm ảnh vừa upload
        my_img = mpimg.imread(path_file)
        enc = InitENC(my_img)
        npyFile = 'static/uploads/'+ authUsername + "/" + authUsername+"_"+str(No_of_files+1)+"_sub.npy"
        EncryptionIMG(int(keys[1]), int(keys[2]), my_img, enc, npyFile)
        data = Image.fromarray(my_img)
        data.save(path_file)
        return redirect(request.url)
    else:
        return render_template('uploadImg.html', username = authUsername)

    

#tải toàn bộ ảnh.
@app.route('/downloadAll', methods=['POST'])
def downloadAll():
    # kiểm tra xem người dùng có bao nhiêu file trong thư mục cảu mình
    directory_path = 'static/uploads/' + authUsername
    No_of_files = len(os.listdir(directory_path)) // 2 # chia 2 là do ko tính file .npy

    #lấy thông tin khóa bí mật.
    privateKey = readPrivateKeyList()
    keys = getPrivateByUsername(authUsername,privateKey)
    downloads_path = str(Path.home() / "Downloads")

    for i in range(1, No_of_files+1):
        my_img = mpimg.imread('static/uploads/' + authUsername + '/'+authUsername+"_"+str(i)+"_enc.jpg")
        enc = np.load('static/uploads/' + authUsername + "/"+authUsername+"_"+str(i)+"_sub.npy")
        DecryptionIMIG(int(keys[1]), int(keys[2]), my_img,enc)

        data = Image.fromarray(my_img)
        data.save(downloads_path + '/' + authUsername +"_" +str(i)+".jpg")
    return render_template('viewImgs.html',username = authUsername, numberofFile = No_of_files)


#chia sẻ hình ảnh với người khác
@app.route('/share', methods=['GET', 'POST'])
def shareImg():
    if request.method  == 'GET':
        return render_template('share.html',username = authUsername)
    else:
        shareUsername = request.form['shareUsername']
        userList = readUserList()
        isUser = checkUsername(shareUsername, userList)

        if (isUser == 0): #username muốn chia sẻ không tồn tại.
            return render_template('share.html',username = authUsername, err_message = True, success_message = False)
        else:
            filename = request.args.get('filename')
            info = filename.split('-')
            # giải mả ảnh của người chia sẻ.
            # lấy khóa bí mật của ng chia sẻ
            privateKey = readPrivateKeyList()
            keys = getPrivateByUsername(authUsername,privateKey)

            my_img = mpimg.imread('static/uploads/' + authUsername + '/'+filename)
            stt_file = filename.split('_')
            enc = np.load('static/uploads/' + authUsername + "/"+authUsername+"_"+str(stt_file[1])+"_sub.npy")
            DecryptionIMIG(int(keys[1]), int(keys[2]), my_img,enc)

            # mã hóa theo khóa bí mật cửa người được chia sẻ.

            #lấy thông tin khóa công khai.
            publicKey = readPublicKeyList()
            keysShareUser = getPublicByUsername(shareUsername,publicKey)

            No_of_files = len(os.listdir('static/uploads/' + shareUsername)) // 2 
            enc = InitENC(my_img)
            npyFile = 'static/uploads/'+ shareUsername + "/" + shareUsername+"_"+str(No_of_files+1)+"_sub.npy"
            EncryptionIMG(int(keysShareUser[1]), int(keysShareUser[2]), my_img, enc, npyFile)
            data = Image.fromarray(my_img)
            data.save("static/uploads/"+ shareUsername + "/" + shareUsername+"_"+str(No_of_files+1)+"_enc.jpg")


            return redirect(request.url)
if __name__ =="__main__":
    app.run('localhost', 5000)