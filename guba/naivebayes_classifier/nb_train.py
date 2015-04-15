# -*- coding=utf-8 -*-

import os
import csv
import json
import random
from collections import Counter
from scws_utils import load_scws, cx_dict, load_black_words, single_word_whitelist

SECOND_LABEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './second_label'))
SECOND_LABEL_RESERVED_1 = os.path.join(SECOND_LABEL_PATH, 'second_label_reserved_1.csv')
SECOND_LABEL_RESERVED_2 = os.path.join(SECOND_LABEL_PATH, 'second_label_reserved_2.csv')
LABEL0403_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './label0403'))
LABEL_CSV = os.path.join(LABEL0403_PATH, './lab_labeled/label_csv/')

sw = load_scws()

def word_count(f_neg,f_neu,f_p):
    negative_total = sum([v for k,v in f_neg.iteritems()])#negative类下所有单词总数（含一个单词多次出现）
    negative_word_count = len(f_neg)#negative类下单词表总数（不算重复）

    positive_total = sum([v for k,v in f_p.iteritems()])
    positive_word_count = len(f_p)

    neutral_total = sum([v for k,v in f_neu.iteritems()])
    neutral_word_count = len(f_neu)

    total = negative_total+positive_total+neutral_total
    dic = f_neg.keys()
    dic.extend(f_neu.keys())
    dic.extend(f_p.keys())
    dic_len = len(set(dic))

    return negative_total,negative_word_count,neutral_total,neutral_word_count,positive_total,positive_word_count,total,dic_len

black = load_black_words()
addition = [u'!',u'如何',u'怎么',u'什么']

def freq_word(data):
    '''统计指定数据下词及词频
    '''
    word_list = []
    for i in range(len(data)):
        text = data[i][1] + '***' + data[i][2]
        words = sw.participle(text)
        word_list.extend([term for term,cx in words if cx in cx_dict and (3<len(term)<30 or term in single_word_whitelist) and (term not in black)])
    word_list.extend(addition)

    counter = Counter(word_list)
    freq_word = {k:v for k,v in counter.most_common()}

    return freq_word

def read_train():
    '''读入训练数据
    '''
    different_data = {}

    #问题标注
    reader = csv.reader(file(SECOND_LABEL_RESERVED_1, 'rb'))
    for id, content,title,em_info,stock_name,label in reader:
        different_data[id] = [id,content,title,em_info,stock_name,label]

    #问题标注，部标
    reader = csv.reader(file(SECOND_LABEL_RESERVED_2, 'rb'))
    for id,content,title,em_info,stock_name,label in reader:
        different_data[id] = [id,content,title,em_info,stock_name,label]

    data_neg = []
    data_neu = []
    data_p = []
    not_train_count = 0
    info_type = [u'数据', u'新闻', u'研报', u'公告']
    datadir = LABEL_CSV
    files = os.listdir(datadir)

    for fname in files:
        reader = csv.reader(file(datadir+fname,'rb'))
        for id,content,title,em_info,stock_name,label in reader:
            if id not in different_data.keys():
                text = content+title
                if len(text)<284 and (em_info!=None) and (em_info.decode("utf8") not in info_type):
                    if label == '-1' or label == '2':
                        data_neu.append([id,content,title,em_info,stock_name,'2'])
                    elif label == '1':
                        data_p.append([id,content,title,em_info,stock_name,label])
                    else:
                        data_neg.append([id,content,title,em_info,stock_name,label])
                else:
                    not_train_count += 1
            else:
                text = different_data[id][1]+different_data[id][2]
                lable = different_data[id][5]
                if len(text)<284 and (different_data[id][2]!=None) and (different_data[id][2].decode("utf8") not in info_type):
                    if label == '-1' or label == '2':
                        data_neu.append(different_data[id])
                    elif label == '1':
                        data_p.append(different_data[id])
                    else:
                        data_neg.append(different_data[id])
                else:
                    not_train_count += 1

    return data_neg,data_neu,data_p

def train_nb():
    '''训练分类模型
    '''
    data_neg,data_neu,data_p = read_train()
    train_neg = []
    train_neu = []
    train_p = []
    list_len = [len(data_neg),len(data_neu),len(data_p)]
    min_index = list_len.index(min(list_len))
    if min_index == 0:
        rand_neu = [random.randint(0,len(data_neu)-1)for i in range(min(list_len))]
        rand_p = [random.randint(0,len(data_p)-1)for i in range(min(list_len))]
        train_neg = data_neg
        for item in rand_neu:
            train_neu.append(data_neu[item])
        for item in rand_p:
            train_p.append(data_p[item])
    elif min_index == 1:
        rand_neg = [random.randint(0,len(data_neg)-1)for i in range(min(list_len))]
        rand_p = [random.randint(0,len(data_p)-1)for i in range(min(list_len))]
        train_neu = data_neu
        for item in rand_neg:
            train_neg.append(data_neg[item])
        for item in rand_p:
            train_p.append(data_p[item])
    else:
        rand_neg = [random.randint(0,len(data_neg)-1)for i in range(min(list_len))]
        rand_neu = [random.randint(0,len(data_neu)-1)for i in range(min(list_len))]
        train_p = data_p
        for item in rand_neg:
            train_neg.append(data_neg[item])
        for item in rand_neu:
            train_neu.append(data_neu[item])            
    #print 'train_neg:%s;train_neu:%s;train_p:%s'%(len(train_neg),len(train_neu),len(train_p))

    #统计每类下词频
    f_neg = freq_word(train_neg)
    f_neu = freq_word(train_neu)
    f_p = freq_word(train_p)

    #统计各类下单词总数（算重复）、估算重复单词数、文档单词个数
    negative_total,negative_word_count,neutral_total,neutral_word_count,positive_total,positive_word_count,total,dic_len=word_count(f_neg,f_neu,f_p)

    #参数列表
    para_list = [f_neg,f_neu,f_p,negative_total,negative_word_count,neutral_total,neutral_word_count,positive_total,positive_word_count,total,dic_len]

    with open('nb_model.json', 'w') as fw:
        fw.write('%s\n' % json.dumps(para_list))

    return para_list

if __name__=='__main__':
    train_nb()

