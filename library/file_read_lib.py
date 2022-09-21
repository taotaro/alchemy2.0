import os
import re
import oss2

def get_list_from_text_file(category, folder):
    file_list=[]
    for file in os.listdir(folder):
        if re.search(category, file):
            file_list.append(file)

    #first file from file_list picked as it will be the lastest obtained data
    open_file=open(folder+'/'+file_list[0], 'r')
    content=open_file.readlines()
    main_list=[]
    for lines in content:
        line=lines.strip('\n')
        main_list.append(line)
    return main_list

def get_file_from_bucket(bucket, folder, category):
    file_list=[]
    for obj in oss2.ObjectIteratorV2(bucket, prefix=folder):
        # print(obj.key)
        #check if subfolder, if yes ignore
        if obj.is_prefix():
            continue
        else:
            filename=obj.key
            if re.search(category, filename):
                return bucket.get_object(filename)
              

def get_content_from_file(file):
    if file==None:
        print('no files found for category')
        return -1
    content=file.read()
    content_list=[]
    for lines in content.splitlines():
        line=lines.strip(b'\n')
        line=line.decode('utf-8')
        content_list.append(line)
    return content_list
