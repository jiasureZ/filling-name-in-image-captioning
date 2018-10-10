import html.parser as h
import re
import requests


class MyHTMLParser(h.HTMLParser):
    a_t = False
    all_text = ''
    flag = 0
    h_tag_per = ''
    h_tag_final = ''                ###########################
    def __init__(self, img_name):
        h.HTMLParser.__init__(self)  # 继承了父类，也要对父类初始化
        self.name = img_name

    def handle_starttag(self, tag, attrs):
        global final_text
        global text
        if str(tag).startswith("p") or str(tag).startswith("li"):
            # print(tag)
            self.a_t = True
        if str(tag).startswith("h"):
            if self.h_tag_final != '':
                if self.h_tag_final == tag:                ################################
                    if self.flag:
                        final_text.append(text)
                        self.h_tag_final = ''
            else:
                self.a_t = False
                text = ''
                self.all_text = ''

        if str(tag).startswith("a"):
            # print("start with a!")
            for att in attrs:
                # print(self.name)
                if att[0] == 'href' and att[1] == '/wiki/File:' + self.name:
                    self.h_tag_final = self.h_tag_per  # 将此链接前一个出现的 hi 作为起始终止符
                    print('h----h:', self.h_tag_final)
                    # print("find!")
                    self.flag = 1
                    # else:
                    #     print("not find!")

    def handle_endtag(self, tag):
        if tag == "p":
            self.a_t = False
            #print('text:', text)
        #if tag == 'h3':
        if str(tag).startswith("h"):          ##########################################
            self.h_tag_per = tag
            #self.flag = 0
            #self.a_t = True                  #####################################

    def handle_data(self, data):
        global text
        if self.a_t is True:
            #print("得到的数据: ", data)
            self.all_text = self.all_text + data
            # print(self.all_text)
            text = self.all_text


def find_short_page(img_name, page_id):
    html = requests.get("https://en.wikipedia.org/wiki?curid=" + page_id)
    page = html.text
    # print(page)
    p = MyHTMLParser(img_name)
    p.feed(page)
    p.close()
    # print('text:', text)
    #print('final_text', final_text)
    try:
        return final_text[0]
    except IndexError as e:
        with open('no_page_img', 'a', encoding='utf8') as f_w:
            f_w.write(img_name + '\t' + page_id + '\n')
        return None


text = ''
final_text = []
#find_short_page('Little_Barrier_Island_From_Above_Great.jpg', '1214344')

with open('tmp.json', 'r', encoding='utf8') as f_r:
    for line in f_r.readlines():  # {"img_name": "050907-M-7747B-002-Judo.jpg", "img_id": 0, "page_id": "147777", "caption": "Judoka in Okinawa"}
        dict = eval(line)
        name = dict["img_name"]
        page_id = dict['page_id']
        name = name.replace(' ', '_')
        print('###################################')
        print(name, '\t', page_id)
        print('###################################')
        page = find_short_page(name, page_id)
        if page is not None:
            page_name = name.replace('.', '#')
            f_w = open('short_page_tmp/' + page_name, 'w', encoding='utf8')
            f_w.write(page)
            final_text = []
            print('\n\n')
