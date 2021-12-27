from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)  


# khai báo hàm đọc danh sách user.
def readUserList():
    userList = []
    file = open("accountLogin.txt", "r")
    for line in file:
        tmp = line.split('-')
        userList.append(tmp)
    file.close()
    return userList

#khai báo thêm tài khoản user:
def addNewUser(info):
    f = open("accountLogin.txt", "a")
    f.write('\n'+info)

#khai báo hàm kiểm tra username và password
def checkUser(username, password, userList):
    print(userList)
    for user in userList:
        if user[0] == username and user[1] == password:
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
        print(username)
        print(password)
        userList = readUserList()
        isUser = checkUser(username, password, userList)
        if (isUser == 1):
            print(True)
            return redirect(url_for("homeLogin")) #đăng nhập thành công -> vào trang chủ homeLogin.
    return render_template('login.html')

#khai báo home (login thành công)
@app.route('/homeLogin', methods=['GET', 'POST'])
def homeLogin():
    return render_template('home.html')

#khai báo register.
@app.route('/register', methods=['GET', 'POST'])  
def register():  
    if request.method == 'POST' and 'Username' in request.form and 'Password' in request.form and 'ConfirmPassword' in request.form:
        username = request.form['Username']
        password = request.form['Password']
        userList = readUserList()
        isUser = checkUser(username, password, userList)
        id = len(userList) + 1
        if (isUser == 0):
            addNewUser(username+'-'+password+'-'+str(id))
            return redirect(url_for("login")) #nếu đăng ký thành công, nhảy sang login
    return render_template('register.html')
  

if __name__ =="__main__":
    app.run(debug = True)