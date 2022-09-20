import os
import re

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