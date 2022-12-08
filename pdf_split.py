# PDFファイルを読込んで、Pythonのコンソールに出力する

# 必要なPdfminer.sixモジュールのクラスをインポート
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
from io import StringIO
import cld3
import copy


def pdf2text(file):
    # 標準組込み関数open()でモード指定をbinaryでFileオブジェクトを取得
    fp = open(file, 'rb')

    # 出力先をPythonコンソールするためにIOストリームを取得
    outfp = StringIO()

    # 各種テキスト抽出に必要なPdfminer.sixのオブジェクトを取得する処理

    rmgr = PDFResourceManager()  # PDFResourceManagerオブジェクトの取得
    lprms = LAParams()  # LAParamsオブジェクトの取得
    device = TextConverter(rmgr, outfp, laparams=lprms)  # TextConverterオブジェクトの取得
    iprtr = PDFPageInterpreter(rmgr, device)  # PDFPageInterpreterオブジェクトの取得

    # PDFファイルから1ページずつ解析(テキスト抽出)処理する
    for page in PDFPage.get_pages(fp):
        iprtr.process_page(page)

    text = outfp.getvalue()  # Pythonコンソールへの出力内容を取得

    outfp.close()  # I/Oストリームを閉じる
    device.close()  # TextConverterオブジェクトの解放
    fp.close()  # Fileストリームを閉じる

    return text


def english_chek(text):
    for item in text:
        if item.isalpha():
            continue
        elif not item.isascii():
            cld3_languages = cld3.get_frequent_languages(text, num_langs=3, )
            language_list = []
            for l in cld3_languages:
                language_list.append(l[0])
            if language_list[0] == "en":
                return True
            return False
    return True


def space_cut(text):
    ret = ""
    sp_f = False
    for ch in text:
        if (ch == " " or ch == " ") and not sp_f:
            sp_f = True
            continue
        if not sp_f:
            ret = ret + ch
            continue
        if ch == " " or ch == " ":
            continue
        if ("A" <= ch <= "~" or "!" <= ch <= "?" or ch == "£") and ret and (
                "A" <= ret[-1] <= "~" or "!" <= ret[-1] <= "?" or ret[-1] == "£"):
            ret = ret + " " + ch
        else:
            ret = ret + ch
        sp_f = False
    if ret and ("A" <= ret[-1] <= "~" or "!" <= ret[-1] <= "?"):
        ret = ret + " "
    return ret


def p_report_split(file_name):
    ret = pdf2text(file_name)
    print(ret)
    topic_data = {}
    related_topic = []
    SoClink = []
    link = []
    not_connect = True
    SoCtopic = False
    Ptopic = False
    abstract = ""
    explanation = ""
    caption_english = ""
    result = {}
    result["document"] = {}
    result["document"]["topic"] = {}
    for org_line in ret.splitlines():
        line = space_cut(org_line)
        if not_connect and not line:
            continue
        if explanation and not line:
            explanation = explanation + "\n"
        if abstract and not line:
            abstract = abstract + "\n"
        if "id" not in result and line[0] == "P":
            result["id"] = line
            continue
        if "title_english" not in result and line:
            result["title_english"] = line
            continue
        if "title" not in result and line:
            result["title"] = line
            continue
        if "Relevance" in line:
            continue
        if "date" not in result and line:
            result["date"] = line
            continue
        if line.startswith("Timing"):
            continue
        if "Infrastructure" in line and "Organization" in line:
            continue
        if "Creation" in line and "Marketing" in line:
            continue
        if "All rights reserved" in line:
            continue
        if line.startswith("Initiate"):
            continue
        if line.startswith("By"):
            result["author"] = line
            continue
        if line.startswith("Description"):
            continue
        if line.startswith("Abstracts"):
            continue
        if line.startswith("本トピックスに関連する"):
            if explanation:
                topic_data["explanation"] = explanation
                related_topic.append(topic_data)
                result["document"]["topic"]["related_topic"] = related_topic
                explanation = ""
            SoCtopic = True
            continue
        if line.startswith("関連する"):
            Ptopic = True
            continue
        not_connect = False
        if line.startswith("SC-") and "abstract" not in result["document"]["topic"]:
            ab_l = ""
            for ll in abstract.split("。"):
                if len(ll) > 2:
                    ab_l = ab_l + ll + "。\n"
            abstract = ""
            result["document"]["topic"]["abstract"] = ab_l
        if "abstract" not in result["document"]["topic"]:
            abstract = abstract + line
            continue
        if line.startswith("SC-"):
            caption_english = line
            if explanation:
                exp = explanation.strip('\r\n')
                ex_l = ""
                for ll in exp.split("。"):
                    if len(ll) > 2:
                        ex_l = ex_l + ll + "。\n"
                topic_data["explanation"] = ex_l
                related_topic.append(topic_data)
                topic_data = {}
                explanation = ""
            continue
        if caption_english and english_chek(line):
            caption_english = caption_english + " " + line
            continue
        elif len(caption_english) > 1:
            topic_data["id"] = caption_english.split("—")[0]
            topic_data["caption_english"] = caption_english.split("—")[-1]
            caption_english = ""
            explanation = explanation + line
        elif explanation:
            explanation = explanation + line
        if line.startswith("SoC") and SoCtopic:
            SoClink.append(org_line)
        if line.startswith("P") and Ptopic:
            link.append(org_line)
    result["soc_link"] = SoClink
    result["partners_link"] = link
    return result


def jsoc_report_split(file_name):
    ret = pdf2text(file_name)
    print(ret)
    topic_data = {}
    related_topic = []
    SoClink = []
    link = []
    abstract = ""
    explanation = ""
    caption = ""
    captino_connect = False
    caption_ok = False
    SoCtopic = False
    summary_start = False
    summary = ""
    last_len = 0
    result = {}
    result["document"] = {}
    result["document"]["topic"] = {}
    for org_line in ret.splitlines():
        line = space_cut(org_line)
        if "date" not in result and line:
            result["date"] = line
            continue
        if "id" not in result and line and line[0] == "S":
            result["id"] = line
            continue
        if "title_english" not in result and line:
            result["title_english"] = line
            continue
        if line.startswith("By"):
            result["author"] = line
            continue
        if "title" not in result and line:
            result["title"] = line
            continue
        if "abstract" not in result["document"]["topic"] and "title" in result and not abstract:
            if len(line) <= 2:
                continue
            abstract = line
            continue
        if line.startswith("SoC") and not SoCtopic:
            if explanation:
                exp = explanation.strip('\r\n')
                ex_l = ""
                for ll in exp.split("。"):
                    if len(ll) > 2:
                        ex_l = ex_l + ll + "。\n"
                topic_data["explanation"] = ex_l
                related_topic.append(topic_data)
                result["document"]["topic"]["related_topic"] = related_topic
                explanation = ""
            continue
        if line.startswith("本トピックスに関連する"):
            SoCtopic = True
            continue
        if line.startswith("(cid:") and "abstract" not in result["document"]["topic"]:
            ab_l = ""
            for ll in abstract.split("。"):
                if len(ll) > 2:
                    ab_l = ab_l + ll + "。\n"
            abstract = ""
            result["document"]["topic"]["abstract"] = ab_l
        if len(line) < 14 and not line.startswith("(cid:"):
            if len(line) < 2:
                if not summary_start and not summary:
                    summary_start = True
                else:
                    summary_start = False
                if not caption:
                    continue
            if summary_start:
                summary = summary + line
                if not caption:
                    continue
        else:
            summary_start = False
        if abstract:
            abstract = abstract + line
            continue
        if line.startswith("(cid:"):
            caption = line
            if explanation:
                exp = explanation.strip('\r\n')
                ex_l = ""
                for ll in exp.split("。"):
                    if len(ll) > 2:
                        ex_l = ex_l + ll + "。\n"
                topic_data["explanation"] = ex_l
                related_topic.append(topic_data)
                topic_data = {}
                explanation = ""
            if "cid:122" in line:
                caption_less = True
                topic_data["id"] = line.split(")")[0] + ")"
                topic_data["caption"] = ""
                caption_ok = False
                captino_connect = False
                explanation = line.split(")")[-1]
                caption = ""
            continue
        if caption and len(line) < 2 and "caption" not in topic_data:
            if captino_connect:
                caption_ok = True
                continue
            if not caption_ok:
                captino_connect = True
            continue
        elif captino_connect and "caption" not in topic_data and not caption_ok:
            caption = caption + line
            captino_connect = False
            caption_ok = True
            continue
        elif len(caption) > 1 and "caption" not in topic_data:
            topic_data["id"] = caption.split(")")[0] + ")"
            topic_data["caption"] = caption.split(")")[-1]
            caption = ""
            caption_ok = False
            captino_connect = False
            explanation = explanation + line
#        elif len(caption) <= 10 and "caption" not in topic_data:
#            caption = caption + line
#            captino_connect = False
#            caption_ok = True
            continue
        elif explanation:
            if len(line) < 14:
                if len(line) < 2:
                    if not summary_start and not summary:
                        summary_start = True
                    else:
                        summary_start = False
                    continue
                if summary_start:
                    summary = summary + line
                    continue
            else:
                summary_start = False
            explanation = explanation + line
        if line.startswith("SoC") and SoCtopic:
            SoClink.append(org_line)
        if line.startswith("P") and SoCtopic:
            link.append(org_line)
    result["summary"] = summary
    result["soc_link"] = SoClink
    result["partners_link"] = link
    return result


def pdf2struct_data(file_name):
    if file_name.startswith("JP"):
        return p_report_split(file_name)
    elif file_name.startswith("JSoC"):
        return jsoc_report_split(file_name)
    return ""


