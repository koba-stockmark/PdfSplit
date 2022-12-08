import json
from pdf_split import pdf2struct_data

ret = pdf2struct_data("JSoC1319.pdf")
json_file = open("test.json", mode="w")
json.dump(ret, json_file, indent=2, ensure_ascii=False)
json_file.close()
with open("test.json") as f:
    data = json.load(f)
print(json.dumps(data, indent=2, ensure_ascii=False))