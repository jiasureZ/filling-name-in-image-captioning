import html.parser as h
import re
import requests
import nltk
import shutil
import os


def word_replace_title(text, idict):
    # 替换一句话中的单词
    rx = re.compile('|'.join(map(re.escape, idict)))

    def one_xlat(match):
        return idict[match.group(0)]

    return rx.sub(one_xlat, text)


class Link_HTMLParser(h.HTMLParser):
    start = False
    infobox_start = False
    useful = False
    table_num = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) > 2:
            if attrs[0][0] == 'id' and attrs[0][1] == 'mw-content-text':
                self.start = True

        if tag == 'table':
            self.table_num += 1
            self.start = False
        # if tag == 'table' and attrs != []:
        #     if attrs[0][1].startswith('infobox'):
        #         self.infobox_start = True
        #         self.start = False
        #
        # if tag == 'table' and self.infobox_start:
        #     self.table_num += 1

        if tag == 'p' and self.start:
            self.useful = True
            # elif tag == 'p' and self.start == False:
            #     self.wait_b = True
            # elif tag == 'b' and self.wait_b:
            #     self.start = True

    def handle_data(self, data):
        # print('data:', data)
        if self.useful:
            # print('****************', data)
            # self.link_text += data
            # print('+++++++++', self.link_text)
            link_sents.append(data)
            # self.a_t = False

    def handle_endtag(self, tag):
        # if tag == 'table' and self.table_num and self.infobox_start:
        #     self.table_num -= 1
        if tag == 'table' and self.table_num:
            self.table_num -= 1
        if tag == 'table' and self.table_num == 0:
            self.start = True


class MyHTMLParser(h.HTMLParser):
    title_flag = False
    title = ''

    def __init__(self, person_list, img_name):
        h.HTMLParser.__init__(self)  # 继承了父类，也要对父类初始化
        self.list = person_list
        self.name = img_name

    def handle_starttag(self, tag, attrs):
        if tag == 'h1':
            if len(attrs) > 2:
                for at in attrs:
                    if at[0] == 'id' and at[1] == 'firstHeading':
                        self.title_flag = True
        if str(tag).startswith("a"):
            if len(attrs) > 1:
                flag = False
                link = ''
                for at in attrs:
                    if at[0] == 'title':
                        for li in self.list:
                            if (li in at[1] and (len(nltk.word_tokenize(at[1])) < 4 or (
                                        '(' in at[1] and ')' in at[1] and len(nltk.word_tokenize(at[1])) < 7))) or (
                                at[1] in li):
                                print(at)
                                link = at[1]
                                flag = True
                                break
                if flag:
                    print('link of ' + link + ':')
                    global link_sents
                    global link_text
                    global person_num
                    link_text = ''
                    link_sents = []
                    new_link = 'https://en.wikipedia.org' + attrs[0][1]
                    print(new_link)
                    html = requests.get(new_link)
                    page = html.text
                    p_p = Link_HTMLParser()
                    p_p.feed(page)
                    if link in self.list:
                        self.list.remove(link)
                    else:
                        for li in self.list:
                            if li in link:
                                self.list.remove(li)
                    print('person_list:', self.list)
                    for item in link_sents:
                        if item == '\n' or item == '':
                            link_sents.remove(item)
                    # print('link_sents:', link_sents)
                    link_text = ''.join(link_sents)
                    change_dict = {'\t': '', '\n': '', '[citation needed]': ''}
                    link_text = word_replace_title(link_text, change_dict)
                    index = link_text.find('Contents1')
                    link_text = link_text[:index]
                    num = re.findall('\[\d+\]', link_text)
                    # print('num:', num)
                    ## 处理参考索引 [10]
                    changedict = {}
                    if len(num) > 0:
                        for n in num:
                            changedict[n] = ''
                        link_text = word_replace_title(link_text, changedict)
                    # print('link_text:', link_text)
                    #first_sentens = link_text.split('. ')[0] + '. '
                    #print('first sentence:', first_sentens)
                    if len(link_text.split('. ')) > 2:
                        top_three = link_text.split('. ')[0] + '. ' + link_text.split('. ')[1] + '. ' + link_text.split('. ')[2] + '. '
                    else:
                        top_three = link_text
                    print('top_three:', top_three)
                    with open('top_three_sentences/first_three_page/' + self.name.replace('.', '#'), 'a', encoding='utf8') as f_w:
                        f_w.write(top_three)
                    person_num += 1
                    print('\n')

    def handle_data(self, data):
        # print('data:', data)
        if self.title_flag:
            self.title = data
            print('Title:', self.title)
            flag = False
            for li in self.list:
                if li in self.title or (self.title in li):
                    flag = True
            if flag:
                global person_num
                global link_sents
                global link_text
                link_text = ''
                link_sents = []
                new_link = 'https://en.wikipedia.org/wiki/' + self.title
                print(new_link)
                html = requests.get(new_link)
                page = html.text
                p_p = Link_HTMLParser()
                p_p.feed(page)
                if self.title in self.list:
                    self.list.remove(self.title)
                else:
                    for li in self.list:
                        if li in self.title:
                            self.list.remove(li)
                for item in link_sents:
                    if item == '\n' or item == '':
                        link_sents.remove(item)
                # print('link_sents:', link_sents)
                link_text = ''.join(link_sents)
                change_dict = {'\t': '', '\n': '', '[citation needed]': ''}
                link_text = word_replace_title(link_text, change_dict)
                index = link_text.find('Contents1')
                link_text = link_text[:index]
                num = re.findall('\[\d+\]', link_text)
                # print('num:', num)
                ## 处理参考索引 [10]
                changedict = {}
                if len(num) > 0:
                    for n in num:
                        changedict[n] = ''
                    link_text = word_replace_title(link_text, changedict)
                # print('link_text:', link_text)
                #first_sentens = link_text.split('. ')[0] + '. '
                person_num += 1
                #print('++++++++++++++++++++++++Title first sentence:', first_sentens)
                if len(link_text.split('. ')) > 2:
                    top_three = link_text.split('. ')[0] + '. ' + link_text.split('. ')[1] + '. ' + link_text.split('. ')[2] + '. '
                else:
                    top_three = link_text
                with open('top_three_sentences/first_three_page/' + self.name.replace('.', '#'), 'a', encoding='utf8') as f_w:
                    f_w.write(top_three)
                print('++++++++++++++++++++++++Title top_three sentence:', top_three)
            self.title_flag = False


def find_source_page(page_id, img_name, person_list):
    html = requests.get("https://en.wikipedia.org/wiki?curid=" + page_id)
    page = html.text
    # print(page)
    p = MyHTMLParser(person_list, img_name)
    p.feed(page)
    p.close()


f_r = open('img_name_pner_pageid1', 'r', encoding='utf8')
person_num = 0
for line in f_r.readlines():
    dict = eval(line)
    if "PERSON" in dict['new_page_ner']:
        person_list = dict['new_page_ner']['PERSON']
        img_name = dict['img_name']
        page_id = dict['page_id']
        link_text = ''
        link_sents = []
        print('****************************************************************')
        print(img_name, '\t', page_id.strip(), '\t person_num:', person_num)
        print('****************************************************************')
        find_source_page(page_id, img_name, person_list)
    else:
        print(line)
        print('cap_ner not has person!')
        print('\n')
print('person_num', person_num)

