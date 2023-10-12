import os
import re
from typing import MutableMapping
#from typing_extensions import Required
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template
from flask.wrappers import Response
from werkzeug.utils import secure_filename
from config import Config
from filemanager import FileManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
folder_get = FileManager()
gmail = Mail(app)

token_default = "imwi2021"

class Users(db.Model):
    id = db.Column('id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(40))
    mail = db.Column(db.String(100))
    username = db.Column(db.String(40))
    images = db.Column(db.Integer)
    labels = db.Column(db.Integer)
    money = db.Column(db.Float)
    labelerror = db.Column(db.Integer)
    admin = db.Column(db.Integer)

    def __init__(self, name, password, mail, username):
        super().__init__()
        self.name = name
        self.password = password
        self.mail = mail
        self.username = username
        self.images = 0
        self.labels = 0
        self.money = 0
        self.labelerror = 0
        self.admin = 0

def recalculatrMoneyForUser():
    _users_ = Users.query.all()
    for _user in _users_:
        _new_money = 0
        _number_label_error = 0
        _number_image = 0
        _number_label = 0
        for project_name in os.listdir(FileManager.main_folder_url):
            entry_path = os.path.join(FileManager.main_folder_url + '/' + project_name + '/note.txt')
            if os.path.isfile(entry_path) == False :
                continue
            note_file = open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "r")
            list_in_note_file = note_file.read()
            note_file.close()
            note_files = list_in_note_file.split('\n')
            for note_file in note_files:
                if note_file == "":
                    continue
                note_file_element = note_file.split(':')
                if len(note_file_element) <= 4:
                    if len(note_file_element) <= 2:
                        continue
                    else:
                        if note_file_element[1] == _user.username and note_file_element[2] == "save":
                            _number_image += 1
                            txt_file = note_file_element[0].split('.')[0]
                            txt_open = open(FileManager.main_folder_url + '/' + project_name + "/labels/train/" + txt_file + ".txt", "r")
                            txt_open_str = txt_open.read()
                            txt_open.close()
                            _number_label += (len(txt_open_str.split('\n')) - 1)
                        
                        continue
                if note_file_element[1] == _user.username and note_file_element[4] == "browsed":
                    _number_image += 1
                    _number_label_error += int(note_file_element[5])
                    if len(note_file_element) >= 9:
                        if note_file_element[8] != "paid":
                            _new_money += int(note_file_element[7])
                    else:
                        _new_money += int(note_file_element[7])

                    txt_file = note_file_element[0].split('.')[0]
                    txt_open = open(FileManager.main_folder_url + '/' + project_name + "/labels/train/" + txt_file + ".txt", "r")
                    txt_open_str = txt_open.read()
                    txt_open.close()
                    _number_label += (len(txt_open_str.split('\n')) - 1 - int(note_file_element[6]))

                elif note_file_element[1] == _user.username and note_file_element[3] == "labeled":
                    _number_image += 1
                    txt_file = note_file_element[0].split('.')[0]
                    txt_open = open(FileManager.main_folder_url + '/' + project_name + "/labels/train/" + txt_file + ".txt", "r")
                    txt_open_str = txt_open.read()
                    txt_open.close()
                    _number_label += (len(txt_open_str.split('\n')) - 1)

        _user.images = _number_image
        _user.labelerror = _number_label_error
        _user.money = _new_money
        _user.labels = _number_label
        db.session.commit()
    return

def sendNewPasswordToUserGmail(_new_password_user, _user_gmail, _user_name):
    msg = Message('Hello '+_user_name + " [Reset mật khẩu]", sender="3ddanang.net@gmail.com", recipients = [_user_gmail])
    msg.body = "iMiU đã reset lại mật khẩu của bạn thành: " + str(_new_password_user) + '\n'
    msg.body += "Đăng nhập phần mềm để đổi lại mật khẩu." + '\n'
    msg.body += "Vui lòng không phản hồi lại mail này."
    gmail.send(msg)

@app.route('/')
def hello_world():
    #users.query.filter_by(name = 'Than').update({users.name:"Mr."+users.name}, synchronize_session = False)
    #db.session.commit()
    # us = Users.query.filter_by(name = 'Mr.Than').all()
    # print(len(us))
    # for u in us:
    #     print(u.name)
    #     print(u.id)
    return "ok"

@app.route('/resetPasswordForUser', methods=['GET', 'POST'])
def resetPasswordForUserFunc():
    if not request.form['userName'] or not request.form['userMail']:
            return "reset=false"
    else:
        _user_name = request.form['userName']
        _uset_mail = request.form['userMail']       

        _users_filter_name = Users.query.filter_by(username = _user_name).first()
        if _users_filter_name != None:
            if _users_filter_name.mail == _uset_mail:
                new_pass = random.randrange(100000, 999999)
                _users_filter_name.password = new_pass                
                db.session.commit()
                sendNewPasswordToUserGmail(new_pass, _uset_mail, _users_filter_name.name)
                return "reset=done"
            else:
                return "reset=false"
        else:
            return "reset=false"

@app.route('/changePasswordForUser', methods=['GET', 'POST'])
def changePasswordForUserFunc():
    if not request.form['userName'] or not request.form['userPassword']:
            return "reset=false"
    else:
        _user_name = request.form['userName']
        _uset_password = request.form['userPassword']
        _uset_Newpassword = request.form['userNewPassword']

        _users_filter_name = Users.query.filter_by(username = _user_name).first()
        if _users_filter_name != None:
            if _users_filter_name.password != _uset_password:
                return "reset=false"
            else:
                _users_filter_name.password = _uset_Newpassword
                db.session.commit()
                return "reset=done"
        else:
            return "reset=false"

# @app.route('/images/<filename>/<passwork>')
# def display_image(filename, passwork):
#     print('image/' + filename + passwork)
#     return 'Hello, World!'   

# @app.route('/test')
# def testSendTemp():
#     return render_template('url-list.txt')

@app.route('/signIn', methods=['GET', 'POST'])
def signInRouteFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "signin=false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            #print('name:' + _name)
            #print('passwork:' + _password)
            # _token = request.form['token']
            # if _token != token_default:
            #     return "signup=false"

            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "signin=UserOrPasswrong" + '\n'
                else:
                    recalculatrMoneyForUser()
                    _requestString = ""
                    if _users_filter_name[0].admin == 1:
                        _requestString += "signin=censor" + '\n'
                    elif _users_filter_name[0].admin == 2:
                        _requestString += "signin=admin" + '\n'
                    else:                        
                        _requestString += "signin=Done" + '\n'
                    _requestString += _users_filter_name[0].name + '\n'
                    _requestString += _users_filter_name[0].password + '\n'
                    _requestString += _users_filter_name[0].mail + '\n'
                    _requestString += _users_filter_name[0].username + '\n'
                    _requestString += str(_users_filter_name[0].images) + '\n'
                    _requestString += str(_users_filter_name[0].labels) + '\n'
                    _requestString += str(_users_filter_name[0].money) + '\n'
                    _requestString += str(_users_filter_name[0].labelerror) + '\n'
                    _requestString += url_for('static', filename = 'AvatarUsers/' + _users_filter_name[0].username + '.jpg')                    
                    #print(_requestString)
                    return _requestString
            else:
                return "signin=UserOrPasswrong" + '\n'

@app.route('/reloadUserInfor', methods=['GET', 'POST'])
def reloadUserInforFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "reload=false"
        else:
            _name = request.form['userName']
            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:                
                recalculatrMoneyForUser()
                _requestString = ""
                if _users_filter_name[0].admin == 1:
                    _requestString += "signin=admin" + '\n'
                else:                        
                    _requestString += "signin=Done" + '\n'

                _requestString += _users_filter_name[0].name + '\n'
                _requestString += _users_filter_name[0].password + '\n'
                _requestString += _users_filter_name[0].mail + '\n'
                _requestString += _users_filter_name[0].username + '\n'
                _requestString += str(_users_filter_name[0].images) + '\n'
                _requestString += str(_users_filter_name[0].labels) + '\n'
                _requestString += str(_users_filter_name[0].money) + '\n'
                _requestString += str(_users_filter_name[0].labelerror) + '\n'
                _requestString += url_for('static', filename = 'AvatarUsers/' + _users_filter_name[0].username + '.jpg')                    
                #print(_requestString)
                return _requestString
            else:
                return "reload=false" + '\n'   
	
# @app.route('/uploader', methods = ['GET', 'POST'])
# def uploader_file():
#    if request.method == 'POST':
#         _name = request.form['userName']
#         print("name:" + _name)
#         f = request.files['file']
#         f.save(secure_filename(f.filename))
#         return 'file uploaded successfully'

@app.route('/uploadAvatarUser', methods = ['GET', 'POST'])
def uploadAvatarUserRouteFunc():
    if request.method == 'POST':
        _name = request.form['userName']
        #print("name:" + _name)
        f = request.files['file']
        f.save(os.path.join("static/AvatarUsers" , secure_filename(f.filename)))
        return 'upload_Done'

@app.route('/load', methods = ['GET', 'POST'])
def loadRouteFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "load=false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "load=false" + '\n'
                else:                    
                    
                    return folder_get.getFileForUser(_name)
            else:
                return "load=false" + '\n'
    else:
        return "load=false"

@app.route('/submitMoneyUser', methods = ['GET', 'POST'])
def submitMoneyUserFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            #print("submit=false")
            return "submit=false"
        else:
            _name = request.form['userName']
            _userSTK = request.form['userSTK']
            _userBankName = request.form['userBankName']
            _userCardName = request.form['userSTKName']
            _userNote = request.form['userNote']

            submitFile = open('static/' + "submitMoney.txt", "r")
            submit_file_str = submitFile.read()
            submitFile.close()

            submit_element = submit_file_str.split('-\n')
            submit_file_str = ""
            for submit in submit_element:
                if submit == "":
                    continue
                submit_element = submit.split('\n')
                user_submit = submit_element[0].split(':')[1]
                if user_submit == _name:
                    continue
                else:
                    submit_file_str += submit + '-\n'

            submit_file_str += "UserName:" + _name + '\n'
            submit_file_str += "UserSTK:" + _userSTK + '\n'
            submit_file_str += "UserBankName:" + _userBankName + '\n'
            submit_file_str += "UserCardName:" + _userCardName + '\n'
            submit_file_str += "UserNote:" + _userNote + '\n'
            submit_file_str += "-" + '\n'

            submitFile = open('static/' + "submitMoney.txt", "w")
            submitFile.write(submit_file_str)
            submitFile.close()

            #print(submit_file_str)

            return "submit=done"
    return

def appentPaidForUser(user_appent_paid):
    for project_name in os.listdir(FileManager.main_folder_url):
        entry_path = os.path.join(FileManager.main_folder_url + '/' + project_name + '/note.txt')
        if os.path.isfile(entry_path) == False :
            continue
        note_file = open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "r")
        list_in_note_file = note_file.read()
        note_file.close()
        note_files = list_in_note_file.split('\n')

        for index, note_file_str in enumerate(note_files):
            if note_file_str == "":
                continue
            note_file_element = note_file_str.split(':')

            if len(note_file_element) <= 4:
                continue
            if note_file_element[1] == user_appent_paid and note_file_element[4] == "browsed":
                if len(note_file_element) >= 9:
                    if note_file_element[8] != "paid":
                        note_files[index] += "paid:"
                else:
                    note_files[index] += "paid:"

        new_note_file_str = ""
        for note_file_s in note_files:
            if note_file_s == "":
                continue
            new_note_file_str += note_file_s + '\n'

        note_file = open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "w")
        note_file.write(new_note_file_str)
        note_file.close()

@app.route('/deleteMoneySubmit', methods = ['GET', 'POST'])
def deleteMoneySubmitFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            _user_submit = request.form['userSubmit']

            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "false"
                else: 
                    submitFile = open('static/' + "submitMoney.txt", "r")
                    submit_file_str = submitFile.read()
                    submitFile.close()

                    submit_element = submit_file_str.split('-\n')
                    submit_file_str = ""
                    for submit in submit_element:
                        if submit == "":
                            continue
                        submit_element = submit.split('\n')
                        user_submit = submit_element[0].split(':')[1]
                        if user_submit == _user_submit:
                            continue
                        else:
                            submit_file_str += submit + '-\n'
                    
                    submitFile = open('static/' + "submitMoney.txt", "w")
                    submitFile.write(submit_file_str)
                    submitFile.close()
                    appentPaidForUser(_user_submit)
                    recalculatrMoneyForUser()
                    return "true"
            else:
                return "false"

@app.route('/upload', methods = ['GET', 'POST'])
def uploadRouteFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "upload=false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            _fileName = request.form['fileName']
            _projectName = request.form['projectName']
            _labeledString = request.form['labeledString']

            #print("label:" + _fileName)
            #print("label:" + _labeledString)

            label_path = os.path.join("static/Project/" + _projectName + "/labels/train/")
            if os.path.isdir(label_path) == False :
                os.mkdir(label_path)

            labeltext = open("static/Project/" + _projectName + "/labels/train/" + _fileName + ".txt", "w")
            labeltext.write(_labeledString)
            labeltext.close()

            note_file = open("static/Project/" + _projectName + "/note.txt", "r")
            note_file_read = note_file.read()
            note_file_lines = note_file_read.split('\n')
            note_file.close()

            note_new_str = ""
            for note_file_line in note_file_lines:
                if note_file_line == "":
                    continue
                if note_file_line.split('.')[0] == _fileName:
                    if note_file_line.find(":labeled:") < 0:
                        note_file_line = note_file_line + ":labeled:"
                note_new_str += note_file_line + '\n'
            
            note_file = open("static/Project/" + _projectName + "/note.txt", "w")
            note_file.write(note_new_str)
            note_file.close()

            return "upload=Done"

@app.route('/saveLabelForUser', methods=['GET', 'POST'])
def saveLabelForUserFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "upload=false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            _fileName = request.form['fileName']
            _projectName = request.form['projectName']
            _labeledString = request.form['labeledString']

            #print("label:" + _fileName)
            #print("label:" + _labeledString)

            label_path = os.path.join("static/Project/" + _projectName + "/labels/train/")
            if os.path.isdir(label_path) == False :
                os.mkdir(label_path)

            labeltext = open("static/Project/" + _projectName + "/labels/train/" + _fileName + ".txt", "w")
            labeltext.write(_labeledString)
            labeltext.close()

            note_file = open("static/Project/" + _projectName + "/note.txt", "r")
            note_file_read = note_file.read()
            note_file_lines = note_file_read.split('\n')
            note_file.close()

            note_new_str = ""
            for note_file_line in note_file_lines:
                if note_file_line == "":
                    continue
                if note_file_line.split('.')[0] == _fileName:
                    note_file_line_ele = note_file_line.split(':')
                    if note_file_line.find(":labeled:") < 0:
                        note_file_line = note_file_line_ele[0] + ':' + note_file_line_ele[1] + ':' + "save"

                note_new_str += note_file_line + '\n'
            
            note_file = open("static/Project/" + _projectName + "/note.txt", "w")
            note_file.write(note_new_str)
            note_file.close()

            return "upload=Done"

@app.route('/relabeledImage', methods = ['GET', 'POST'])
def relabeledImageFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "false"
        else:
            _user_name = request.form['userName']
            _password = request.form['userPassword']
            _project_name = request.form['projectName']
            _image_name = request.form['imageName']
            _users_filter_name = Users.query.filter_by(username = _user_name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "false"
                else:                    
                    entry_path = os.path.join(FileManager.main_folder_url + '/' + _project_name + '/note.txt')
                    if os.path.isfile(entry_path) == True:
                        note_file = open(FileManager.main_folder_url + '/' + _project_name + '/note.txt', "r")
                        note_lists = note_file.read().split('\n')
                        note_file.close()
                        new_note_string = ""
                        for index, note_list in enumerate(note_lists):
                            if note_list == "":
                                continue
                            image_name = note_list.split(':')[0]
                            if image_name == _image_name:
                                note_list_ele = note_list.split(':')
                                note_lists[index] = note_list_ele[0] + ':' + note_list_ele[1] + ':send' 
                            new_note_string += note_lists[index] + '\n'
                        note_file = open(FileManager.main_folder_url + '/' + _project_name + '/note.txt', "w")
                        note_file.write(new_note_string)
                        note_file.close()
                        return "done"
                    else:
                        return "false"      
                    #return folder_get.getFileForUser(_name)
            else:
                return "false"

@app.route('/deleteImageInProject', methods = ['GET', 'POST'])
def deleteImageInProjectFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "false"
        else:
            _user_name = request.form['userName']
            _password = request.form['userPassword']
            _project_name = request.form['projectName']
            _image_name = request.form['imageName']
            #print(_image_name)
            _users_filter_name = Users.query.filter_by(username = _user_name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "false"
                else:
                    image_path = os.path.join(FileManager.main_folder_url + '/' + _project_name + '/images/train/' + _image_name)
                    if os.path.isfile(image_path) == True:
                        os.remove(image_path)                     
                    entry_path = os.path.join(FileManager.main_folder_url + '/' + _project_name + '/note.txt')
                    if os.path.isfile(entry_path) == True:
                        note_file = open(FileManager.main_folder_url + '/' + _project_name + '/note.txt', "r")
                        note_lists = note_file.read().split('\n')
                        note_file.close()
                        new_note_string = ""
                        for index, note_list in enumerate(note_lists):
                            if note_list == "":
                                continue
                            image_name = note_list.split(':')[0]
                            if image_name != _image_name:  
                                new_note_string += note_lists[index] + '\n'
                        #print(new_note_string)
                        note_file = open(FileManager.main_folder_url + '/' + _project_name + '/note.txt', "w")
                        note_file.write(new_note_string)
                        note_file.close()
                        
                    return "done"      
            else:
                return "false"

@app.route('/redistributionProject', methods = ['GET', 'POST'])
def redistributionProjectFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "false"
        else:
            _user_name = request.form['userName']
            _project_name = request.form['projectName']
            _users_filter_name = Users.query.filter_by(username = _user_name).all()
            if len(_users_filter_name) > 0:
                entry_path = os.path.join(FileManager.main_folder_url + '/' + _project_name + '/note.txt')
                if os.path.isfile(entry_path) == True:
                    note_file = open(FileManager.main_folder_url + '/' + _project_name + '/note.txt', "r")
                    note_lists = note_file.read().split('\n')
                    note_file.close()
                    new_note_string = ""
                    for index, note_list in enumerate(note_lists):
                        if note_list == "":
                            continue
                        if note_list.find(":labeled:") > -1:
                            new_note_string += note_lists[index] + '\n'

                    #print(new_note_string)
                    note_file = open(FileManager.main_folder_url + '/' + _project_name + '/note.txt', "w")
                    note_file.write(new_note_string)
                    note_file.close()
                    
                return "done"         
            else:
                return "false"  

@app.route('/adminUploadLabel', methods=['GET', 'POST'])
def adminUploadLabelRouteFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "upload=false"
        else:
            _name = request.form['userName']
            _fileName = request.form['fileName']
            _projectName = request.form['projectName']
            _labeledString = request.form['labeledString']

            label_path = os.path.join("static/Project/" + _projectName + "/labels/train/")
            if os.path.isdir(label_path) == False :
                os.mkdir(label_path)

            labeltext = open("static/Project/" + _projectName + "/labels/train/" + _fileName + ".txt", "w")
            labeltext.write(_labeledString)
            labeltext.close()
            return "uploadtxt=done"

@app.route('/adminUploadProjectInfor',  methods=['GET', 'POST'])
def adminUploadProjectInforFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "upload=false"
        else:
            _name = request.form['userName']
            _projectName = request.form['projectName']
            _labeledString = request.form['projectInforString']
            folder_get.uploadProjectInforAdmin(_name, _projectName, _labeledString)
            recalculatrMoneyForUser()
            return "uploadinfor=done"

@app.route('/adminUploadTypeLabel', methods=['GET', 'POST'])
def adminUploadTypeLabelFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "upload=false"
        else:
            _name = request.form['userName']
            _projectName = request.form['projectName']
            _typeLabeledString = request.form['projectTypeString']

            return folder_get.uploadTypeLabelAdmin(_name, _projectName, _typeLabeledString)

@app.route('/adminUploadImageForLabel', methods=['GET', 'POST'])
def adminUploadImageForLabelFunc():
    if request.method == 'POST':
        #_name = request.form['userName']
        _projectName = request.form['projectName']

        f = request.files['file']

        #print("_name:" + _name)
        #print("project:" + _projectName)

        #print("file:" + f.filename)
        f.save(os.path.join("static/Project/" + _projectName + "/typelabel", secure_filename(f.filename)))
        return "save=done"
            

@app.route('/loadAllProjectInfor', methods=['GET', 'POST'])
def loadAllProjectInforRouteFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "load=false"
        else:
            _name = request.form['userName']
            return folder_get.getProjectInforForAdmin(_name)

@app.route('/loadProjectName', methods=['GET', 'POST'])
def loadProjectNameRouteFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "load=false"
        else:
            _name = request.form['userName']
            _project_name = request.form['projectName']
            return folder_get.getProjectForAdmin(_name, _project_name)

@app.route('/signUp', methods=['GET', 'POST'])
def signUpRouteFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userMail'] or not request.form['userPassword'] or not request.form['userFullname']:
            return "signup=false"
        else:
            _userName = request.form['userName']
            _userMail = request.form['userMail']
            _userPassword = request.form['userPassword']
            _userFullname = request.form['userFullname']
            # _token = request.form['token']
            # if _token != token_default:
            #     return "signup=false"

            _users_filter_name = Users.query.filter_by(username = _userName).all()
            if len(_users_filter_name) > 0:
                return "signup=Registered Name"

            _users_filter_mail = Users.query.filter_by(mail = _userMail).all()
            if len(_users_filter_mail) > 0:
                return "signup=Registered Mail"

            _newUser = Users(_userFullname, _userPassword, _userMail, _userName)

            db.session.add(_newUser)
            db.session.commit()

            newavatar = open("static/AvatarUsers/" + _userName + ".jpg" , "w+b")
            default_file = open("static/AvatarUsers/defaultavatar.jpg", "r+b")
            default_file_text = default_file.read()
            default_file.close()
            newavatar.write(default_file_text)
            newavatar.close()

            return "signup=Signup Done"

@app.route('/uploadImageNewProject', methods=['GET', 'POST'])    
def uploadImageNewProjectFunc():
    if request.method == 'POST':
        _projectName = request.form['projectName']
        uploaded_files = request.files['file']

        label_path = os.path.join("static/Project/" + _projectName + "/images/train")
        if os.path.isdir(label_path) == False :
            return "false"
            os.mkdir(os.path.join("static/Project/" + _projectName))
            os.mkdir(os.path.join("static/Project/" + _projectName + "/images"))
            os.mkdir(os.path.join("static/Project/" + _projectName + "/images/train"))

        new_image_part = os.path.join("static/Project/" + _projectName + "/images/train", secure_filename(uploaded_files.filename))
        if os.path.isfile(new_image_part) == False :
            uploaded_files.save(os.path.join("static/Project/" + _projectName + "/images/train", secure_filename(uploaded_files.filename)))
        else:
            uploaded_files.save(os.path.join("static/Project/" + _projectName + "/images/train", "1-" + secure_filename(uploaded_files.filename)))
        #print(_name)
        #print(_projectName)       
        return "ok"

@app.route('/uploadTextNewProject', methods=['GET', 'POST'])    
def uploadTextNewProjectFunc():
    if request.method == 'POST':
        _projectName = request.form['projectName']
        uploaded_files = request.files['file']

        label_path = os.path.join("static/Project/" + _projectName + "/labels/train/")
        if os.path.isdir(label_path) == False :
            os.mkdir(os.path.join("static/Project/" + _projectName + "/labels"))
            os.mkdir(os.path.join("static/Project/" + _projectName + "/labels/train"))
        
        uploaded_files.save(os.path.join("static/Project/" + _projectName + "/labels/train", secure_filename(uploaded_files.filename)))
        #print(_name)
        #print(_projectName)       
        return "ok"

@app.route('/uploadTypeNewProject', methods=['GET', 'POST'])    
def uploadTypeNewProjectFunc():
    if request.method == 'POST':
        _projectName = request.form['projectName']
        uploaded_files = request.files['file']

        label_path = os.path.join("static/Project/" + _projectName + "/typelabel")
        if os.path.isdir(label_path) == False :
            os.mkdir(label_path)
        
        uploaded_files.save(os.path.join("static/Project/" + _projectName + "/typelabel", secure_filename(uploaded_files.filename)))
        #print(_name)
        #print(_projectName)       
        return "ok"

@app.route('/saveProjectManager', methods=['GET', 'POST'])
def saveProjectManagerFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "upload=false"
        else:
            _name = request.form['userName']
            _projectRequestString = request.form['projectRequestString']

            project_infor_notes = open("static/projectInfor.txt", "w")
            project_infor_notes.write(_projectRequestString)
            project_infor_notes.close()

            return "upload=done"

@app.route('/deleteProject', methods=['GET', 'POST'])
def deleteProjectFunc():
    if request.method == 'POST':
        _projectName = request.form['projectName']
        _userName = request.form['userName']

        project_infor_notes = open("static/projectInfor.txt", "r")
        string_project_infor = project_infor_notes.read()
        project_infor_notes.close()
        project_infor_list = string_project_infor.split('\n')

        new_write_str = ""
        for index, project_infor in enumerate(project_infor_list):
            ele_project_infor = project_infor.split(':')
            if _projectName == ele_project_infor[2]:
                project_infor_list[index] = ""
                break

        for project_infor in project_infor_list:
            if project_infor == "":
                continue
            new_write_str += project_infor + '\n'

        project_infor_notes = open("static/projectInfor.txt", "w")
        project_infor_notes.write(new_write_str)
        project_infor_notes.close()

        deleteDir("static/Project/" + _projectName)
        return "delete=done"


def deleteDir(dirPath):
    deleteFiles = []
    deleteDirs = []
    for root, dirs, files in os.walk(dirPath, topdown=False):
        for f in files:
            deleteFiles.append(os.path.join(root, f))
        for d in dirs:
            deleteDirs.append(os.path.join(root, d))
    for f in deleteFiles:
        os.remove(f)   
    for d in deleteDirs:
        os.rmdir(d)
    os.rmdir(dirPath)

@app.route('/createNewProject', methods=['GET', 'POST'])
def createNewProjectFunc():
    if request.method == 'POST':
        if not request.form['userName']:
            return "create=false"
        else:
            _name = request.form['userName']
            _project_name = request.form['projectName']

            os.mkdir(os.path.join("static/Project/" + _project_name))
            os.mkdir(os.path.join("static/Project/" + _project_name + "/images"))
            os.mkdir(os.path.join("static/Project/" + _project_name + "/images/train"))
            os.mkdir(os.path.join("static/Project/" + _project_name + "/labels"))
            os.mkdir(os.path.join("static/Project/" + _project_name + "/labels/train"))
            os.mkdir(os.path.join("static/Project/" + _project_name + "/typelabel"))

            project_infor_notes = open("static/projectInfor.txt", "r")
            string_project_infor = project_infor_notes.read()
            project_infor_notes.close()
            project_infor_notes = open("static/projectInfor.txt", "w")
            project_infor_list = string_project_infor.split('\n')
            string_project_infor += str(len(project_infor_list) - 1) + ':true:' + _project_name + ':' + '\n'
            project_infor_notes.write(string_project_infor)
            project_infor_notes.close()

            return "create=done"

@app.route('/deleteUser', methods=['GET', 'POST'])
def deleteUserFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            _user_name_delete = request.form['userDelete']

            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "false"
                else: 
                    _user_delete = Users.query.filter_by(username = _user_name_delete).first()
                    db.session.delete(_user_delete)
                    db.session.commit()
                    os.remove(os.path.join("static/AvatarUsers/" + _user_name_delete + ".jpg"))  
                    return "true"
            else:
                return "false"

@app.route('/setRoleForUser', methods=['GET', 'POST'])
def setRoleForUserFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']
            _user_set_role = request.form['userSetRole']
            _user_role_value = request.form['userRoleValue']
            #print(_name)
            #print(_password)
            #print(_user_set_role)
            #print(_user_role_value)

            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "false"
                else: 
                    _user_ = Users.query.filter_by(username = _user_set_role).first()
                    _user_.admin = int(_user_role_value)
                    db.session.commit()
                    return "true"
            else:
                return "false"

@app.route('/getAllUsers', methods=['GET', 'POST'])
def getAllUsersFunc():
    if request.method == 'POST':
        if not request.form['userName'] or not request.form['userPassword']:
            return "false"
        else:
            _name = request.form['userName']
            _password = request.form['userPassword']

            _users_filter_name = Users.query.filter_by(username = _name).all()
            if len(_users_filter_name) > 0:
                if (_users_filter_name[0].password != _password):
                    return "false"
                else:      
                    _requestString = ""
                    submitFile = open('static/' + "submitMoney.txt", "r")
                    submit_file_str = submitFile.read()
                    submits = submit_file_str.split('-\n')
                    submitFile.close()

                    _users = Users.query.all()
                    for _user in _users:
                        _requestString += str(_user.admin) + ';'
                        _requestString += "static/AvatarUsers/" + _user.username + ".jpg" + ';'
                        _requestString += _user.username + ';'
                        _requestString += _user.name + ';'
                        _requestString += _user.mail + ';'
                        _requestString += str(_user.images) + ';'
                        _requestString += str(_user.labels) + ';'
                        _requestString += str(_user.labelerror) + ';'
                        _requestString += str(_user.money) + ';'

                        is_user_in_submit = 0
                        for submit in submits:
                            if submit == "":
                                continue
                            submit_element = submit.split('\n')
                            user_submit = submit_element[0].split(':')[1]
                            if user_submit == _user.username:
                                _requestString += submit_element[0] + '-,'
                                _requestString += submit_element[1] + '-,'
                                _requestString += submit_element[2] + '-,'
                                _requestString += submit_element[3] + '-,'
                                _requestString += submit_element[4] + '-,' + ';'
                                is_user_in_submit = 1
                                break

                        if is_user_in_submit == 0:
                            _requestString += ';'

                        _requestString += '\n'
                        #print(_requestString)

                    return _requestString
            else:
                return "false"

if __name__ == '__main__':
    #db.create_all()
    with app.app_context():
        db.create_all()

    app.run(host='192.168.1.29', port=5001)