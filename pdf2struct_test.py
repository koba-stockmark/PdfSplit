import glob
import json

from pdf_split import pdf2struct_data

files = glob.glob("*.pdf")
for file in files:
    print(file)
    ret = pdf2struct_data(file)
    json_file_name = file.split(".")[0] + ".json"
    json_file = open(json_file_name, mode="w")
    json.dump(ret, json_file, indent=2, ensure_ascii=False)
    json_file.close()
