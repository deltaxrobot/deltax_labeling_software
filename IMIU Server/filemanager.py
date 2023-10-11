import os
import re

class FileManager:
    main_folder_url = 'static/Project'
    number_file_once = 5
    money_error_label = 100

    def __init__(self) -> None:
        pass
    
    def getFileForUser(self, user_name):
        file_image_count = 0
        file_for_user_list = ""

        project_infor_notes = open("static/projectInfor.txt", "r")
        project_infor_str = project_infor_notes.read()
        project_infor_notes.close()
        project_infor_list = project_infor_str.split('\n')

        for project_infor in project_infor_list:
            if project_infor == "":
                continue
            ele_project_infor = project_infor.split(':')
            if ele_project_infor[1] == "false":
                continue
            entry_name = ele_project_infor[2]
            #print(entry_name)

        #for entry_name in os.listdir(FileManager.main_folder_url):
            if file_image_count != 0:
                return file_for_user_list

            file_for_user_list = ""
                
            entry_path = os.path.join(FileManager.main_folder_url + '/' + entry_name + '/note.txt')
            if os.path.isfile(entry_path) == False :               
                open(FileManager.main_folder_url + '/' + entry_name + "/note.txt", "x")
                note_file = open(FileManager.main_folder_url + '/' + entry_name + "/note.txt", "a", encoding="utf-8")                
                file_for_user_list += "labelinfor:" + FileManager.main_folder_url + '/' + entry_name + "/typelabel/infor.txt" + '\n'
                file_for_user_list += "labelimageurl:" + FileManager.main_folder_url + '/' + entry_name + "/typelabel/" + '\n'
                for entry_image_name in os.listdir(FileManager.main_folder_url + '/' + entry_name + '/images/train'):
                    file_for_user_list += FileManager.main_folder_url + '/' + entry_name + "/images/train/" + entry_image_name + ';' + 'null' + '\n'
                    note_file.write(entry_image_name + ":" + user_name + ":send" + '\n')
                    file_image_count += 1
                    if file_image_count > FileManager.number_file_once :
                        note_file.close()
                        return file_for_user_list
            else :
                list_images = os.listdir(FileManager.main_folder_url + '/' + entry_name + '/images/train')
                note_file = open(FileManager.main_folder_url + '/' + entry_name + "/note.txt", "r", encoding="utf-8")
                list_in_note_file = note_file.read()
                note_file.close()
                note_file = open(FileManager.main_folder_url + '/' + entry_name + "/note.txt", "a", encoding="utf-8")
                file_for_user_list += "labelinfor:" + FileManager.main_folder_url + '/' + entry_name + "/typelabel/infor.txt" + '\n'
                file_for_user_list += "labelimageurl:" + FileManager.main_folder_url + '/' + entry_name + "/typelabel/" + '\n'

                note_files = list_in_note_file.split('\n')

                if (len(list_images) > len(note_files)) - 2:
                    for entry_image_name in list_images:
                        
                        is_have_file_name = 0
                        for ele_note_files in note_files:
                            file_name = ele_note_files.split(':')[0]
                            if file_name == entry_image_name:
                                
                                is_have_file_name = 1
                                user_name_bf = ele_note_files.split(':')[1]
                                if user_name_bf == user_name and ele_note_files.find(":labeled:") < 0:
                                    save_note = ""
                                    if ele_note_files.find(":save") < 0:
                                        save_note = "null"
                                    else:
                                        save_note = FileManager.main_folder_url + '/' + entry_name + "/labels/train/" + entry_image_name.split('.')[0] + ".txt"
                                    file_for_user_list += FileManager.main_folder_url + '/' + entry_name + "/images/train/" + entry_image_name + ';' + save_note + '\n'
                                    file_image_count += 1
                                    
                                    if file_image_count > FileManager.number_file_once :
                                        note_file.close()
                                        return file_for_user_list                                    
                                break
                         
                        if is_have_file_name == 0:
                            file_for_user_list += FileManager.main_folder_url + '/' + entry_name + "/images/train/" + entry_image_name + ';' + 'null' + '\n'
                            note_file.write(entry_image_name + ":" + user_name + ":send" + '\n')
                            file_image_count += 1
                            if file_image_count > FileManager.number_file_once :
                                note_file.close()
                                return file_for_user_list                        
                                           
        if file_image_count == 0:
            return "none_file"

    def getProjectInforForAdmin(self, user_name):
        project_infor_string = ""
        project_infor_notes = open("static/projectInfor.txt", "r")
        project_infor_str = project_infor_notes.read()
        project_infor_notes.close()
        project_infor_list = project_infor_str.split('\n')

        for project_infor in project_infor_list:
            if project_infor == "":
                continue
            ele_project_infor = project_infor.split(':')

        #for entry_name in os.listdir(FileManager.main_folder_url):
            number_image = 0
            number_labeled = 0
            number_browsed = 0
            entry_name = ele_project_infor[2]

            entry_images = os.listdir(FileManager.main_folder_url + '/' + entry_name + '/images/train')
            number_image = len(entry_images)
            entry_path = os.path.join(FileManager.main_folder_url + '/' + entry_name, 'note.txt')
            if os.path.isfile(entry_path) == False :
                number_labeled = 0
                number_browsed = 0
            else:
                note_file = open(FileManager.main_folder_url + '/' + entry_name + "/note.txt", "r", encoding="utf-8")
                list_in_note_file = note_file.read()
                note_file.close()
                number_labeled = list_in_note_file.count("labeled")
                number_browsed = list_in_note_file.count("browsed")

            project_infor_string += entry_name + ":" + str(number_image) + ":" + str(number_labeled) + ":" + str(number_browsed) + ":"
            project_infor_string += ele_project_infor[1] + ":"
            if number_image > 0:
                project_infor_string += FileManager.main_folder_url + '/' + entry_name + "/images/train/" + entry_images[0] + ":" '\n'
            else:
                project_infor_string += ":" '\n'

        #print(project_infor_string)
        return project_infor_string

    def getProjectForAdmin(self, user_name, project_name):
        string_request = ""
        string_request += FileManager.main_folder_url + '/' + project_name + '/images/train/' + '\n'
        string_request += FileManager.main_folder_url + '/' + project_name + '/labels/train/' + '\n'

        type_infor_path = os.path.join(FileManager.main_folder_url + '/' + project_name + '/typelabel/infor.txt')
        if os.path.isfile(type_infor_path) == False :
            string_request += "null" + '\n'
        else:            
            string_request += FileManager.main_folder_url + '/' + project_name + '/typelabel/' + '\n'

        note_file_path = os.path.join(FileManager.main_folder_url + '/' + project_name + '/note.txt')
        note_file_string = ""
        if os.path.isfile(note_file_path) == False :
            open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "x")
        else:
            note_file = open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "r", encoding="utf-8")
            note_file_string = note_file.read()
            note_file.close()

        for entry_image_name in os.listdir(FileManager.main_folder_url + '/' + project_name + '/images/train'):
            string_request += entry_image_name + ":"
            file_txt_name = entry_image_name.split('.')[0]
            txt_path = os.path.join(FileManager.main_folder_url + '/' + project_name + "/labels/train/" + file_txt_name + '.txt')
            if os.path.isfile(txt_path) == False :
                string_request += "null:"
            else:
                string_request += file_txt_name + ".txt" + ":"

            note_file_lists = note_file_string.split('\n')
            is_labeles = 0
            is_label_name = ""
            is_have_image_name = 0
            for note_file_list in note_file_lists:
                if entry_image_name == note_file_list.split(':')[0]:
                    is_have_image_name = 1
                    is_labeles = 1
                    is_label_name = note_file_list.split(':')[1]
                    if note_file_list.find(":labeled:") > -1:
                        string_request += "labeled:"
                        
                    else:
                        string_request += "null:"
                    if note_file_list.find(":browsed:") > -1:
                        string_request += "browsed:"
                        string_request += note_file_list.split(':')[5] + ':'
                        string_request += note_file_list.split(':')[6] + ':'
                    else:
                        string_request += "null:"
                    break

            if is_have_image_name == 0:
                string_request += "null:null:null:"
            if is_labeles == 1:
                string_request += is_label_name + ':'
            string_request += '\n'
        #print(string_request)
        return string_request

    def uploadProjectInforAdmin(self, user_name, project_name, labeled_string):

        note_file = open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "r", encoding="utf-8")
        note_file_string = note_file.read()

        note_file.close()
        note_file_string_lines = note_file_string.split('\n')
        labeled_string_lines = labeled_string.split('\n')

        for labeled_string_line in labeled_string_lines:
            if labeled_string_line == "":
                continue
            element_label = labeled_string_line.split(':')
            for index, note_file_string_line in enumerate(note_file_string_lines):
                element_notefile = note_file_string_line.split(':')
                if element_label[0] == element_notefile[0]:
                    is_paid = ""
                    if len(element_notefile) >= 9:
                        if element_notefile[8] == "paid":
                            is_paid = "paid:"
                    if note_file_string_line.find(":browsed:") > -1:
                        note_file_string_lines[index] = element_notefile[0] + ':' + element_notefile[1] + ':' + element_notefile[2] + ':' + element_notefile[3] + ':'

                    if note_file_string_line.find(":labeled:") > -1:
                        note_file_string_lines[index] += "browsed:"
                    else:
                        note_file_string_lines[index] += ":labeled:browsed:"

                    note_file_string_lines[index] += element_label[2] + ':' + element_label[3] + ':'                    
                    monay_buffer = int(element_label[4]) - int(element_label[2]) * FileManager.money_error_label
                    note_file_string_lines[index] += str(monay_buffer) + ':'
                    note_file_string_lines[index] += is_paid
                    break
        
        note_file = open(FileManager.main_folder_url + '/' + project_name + "/note.txt", "w", encoding="utf-8")       

        note_file_str_new = ""
        for note_file_string_line in note_file_string_lines:
            if note_file_string_line == "":
                continue
            note_file_str_new += note_file_string_line + '\n'

        note_file.write(note_file_str_new)
        note_file.close()

        #print("note:" + note_file_str_new)

    def uploadTypeLabelAdmin(self, user_name, project_name, type_label_string):
        type_infor_path = os.path.join(FileManager.main_folder_url + '/' + project_name + '/typelabel')
        if os.path.isdir(type_infor_path) == False :
            dirpath = os.path.join(FileManager.main_folder_url + '/' + project_name + "/typelabel")
            #dirpath.mkdir(parents=True, exist_ok=True)
            #print("infor_txt_lists" + type_infor_path);
            os.mkdir(dirpath)

        #infor_txt_file = open(FileManager.main_folder_url + '/' + project_name + '/typelabel/infor.txt', "r")
        #infor_txt_str = infor_txt_file.read()
        #infor_txt_file.close()

        infor_txt_lists = ""
        type_label_lists = type_label_string.split('\n')
        response_reupload = ""
        
        for index, type_label_list in enumerate(type_label_lists):
            if type_label_list == "":
                continue
            element_type = type_label_list.split(':')
            infor_txt_lists += "type:" + element_type[0] + ':' + element_type[1] + ':' + element_type[2] + ':' + element_type[3] + ':'+ element_type[4] + ':' + element_type[5] + ':' + '\n'
            image_infor_path = os.path.join(FileManager.main_folder_url + '/' + project_name + '/typelabel/' + element_type[2])
            if os.path.isfile(image_infor_path) == False :
                response_reupload += str(index) + ':'

        infor_txt_f = open(FileManager.main_folder_url + '/' + project_name + '/typelabel/infor.txt', "w", encoding="utf-8")
        infor_txt_f.write(infor_txt_lists)
        infor_txt_f.close()

        if response_reupload == "":
            response_reupload = "null"

        return response_reupload
        

            
        
