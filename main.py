import xml.etree.ElementTree as ET
import csv
import os
import re
import shutil
import argparse
import sys
from encode_dector import detect_encode_auto
from pathlib import Path

def key_value_seperator(data_dict):
    '''
    分離 dict 的 key, value
    回傳 key_list, value_list
    '''
    col_list = list(data_dict.keys())
    value_list = list(data_dict.values())
    return col_list, value_list

def tmp_dict_resetter(key_list):
    '''
    依據 key_list 建立一個 value 都為空字串的 dict
    '''
    empty_str_list = ["" for i in range(len(key_list))]
    empty_tmp_dict = dict(zip(key_list, empty_str_list))
    return empty_tmp_dict

class XmlToCsv:
    '''
    xml 轉 csv 檔案處理
    '''
    def __init__(self, input_file):
        self.input_file = input_file
        self.tmp_utf_file = ""
        self.output_file = ""

    def convert_to_utf8(self):
        input_file = self.input_file
        tmp_utf_file = input_file + '_tmp_utf8'
        file_encod = detect_encode_auto(input_file).upper()
        # 若來源檔案已確定是 UTF 相關編碼，則直接複製一份
        if "UTF" in file_encod:
            shutil.copyfile(input_file, tmp_utf_file)
        else:
            with open(input_file, 'r', encoding=file_encod) as ori_file:
                lines = ori_file.readlines()
                with open(tmp_utf_file, 'w', encoding='utf-8') as utf_file:
                    for idx, line in enumerate(lines):
                        if idx == 0:
                            line = re.sub(f'encoding="big5"|encoding="{file_encod}"', 'encoding="utf-8"', line)
                        utf_file.write(line)
        self.tmp_utf_file = tmp_utf_file
        return tmp_utf_file

    def xml_to_tmp_data(self, tmp_utf_file):
        data_list = []
        data_dict = {}

        tree = ET.parse(tmp_utf_file)
        root = tree.getroot()

        for ele in root.iter():
            if len(ele) > 0:
                if bool(data_dict): # 若 data_dict 為空，則不 append 資料
                    col_list, data_row_list = key_value_seperator(data_dict)
                    data_dict = tmp_dict_resetter(col_list)

                    if not all( i== "" for i in data_row_list): # 若整串為空字串，則不 append
                        data_list.append(data_row_list)
            else:
                data_dict[ele.tag] = ele.text
        # 讀完最後一筆資料，需要手動丟出，因為不會再觸發丟出條件
        if bool(data_dict):
            data_row_list = list(data_dict.values())
            if not all(i == "" for i in data_row_list):
                data_list.append(data_row_list)
        return data_list
    
    def data_to_file(self, data_list, dlmtr="\x06"):
        '''
        迴圈寫出單行資料
        '''
        input_file_name = self.input_file
        final_file = input_file_name.replace(".xml","") + ".csv"
        with open(final_file, 'w', encoding='big5', newline='') as csv_f:
            fwriter = csv.writer(csv_f, delimiter=dlmtr, quoting=csv.QUOTE_NONE, quotechar='')
            for data_row in data_list:
                fwriter.writerow(data_row)
        self.output_file = final_file

    def do_process(self):
        '''
        主流程
        '''
        # 轉來源檔案為 utf-8
        tmp_utf_file = self.convert_to_utf8()
        # 解析 utf-8 檔案的 xml 內容
        tmp_data_list = self.xml_to_tmp_data(tmp_utf_file)
        # 寫出資料
        self.data_write_file(tmp_data_list, dlmtr="\x06")

if __name__ == "__main__":
    srcfile = input("請輸出檔案名稱")
    pre_process = XmlToCsv(srcfile)
    pre_process.do_process()
