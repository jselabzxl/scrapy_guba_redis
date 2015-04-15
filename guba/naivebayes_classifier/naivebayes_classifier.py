# -*- coding: utf-8 -*- 

import os
import json
from scws_utils import load_scws

NB_MODEL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'nb_model.json'))

sw = load_scws()

def load_para_list():
    with open(NB_MODEL_FILE) as f:
        return json.loads(f.readline().strip())

para_list = load_para_list()

#计算三类先验概率
p_negative = float(para_list[3]) / float(para_list[9])
p_neutral = float(para_list[5]) / float(para_list[9])
p_positive = float(para_list[7]) / float(para_list[9])

info_type = set([u'数据',u'新闻',u'研报',u'公告'])
addition_w = [u'如何',u'怎么',u'什么']

NEUTRAL = 2
POSITIVE = 1
NEGATIVE = 0

LABELS_LIST = [NEGATIVE, POSITIVE, NEUTRAL]

def naivebayes(item):
    '''朴素贝叶斯三类分类器, em_info, title, content为utf-8编码
    '''
    label = NEUTRAL # 分类后类别标签,默认中性

    em_info = None # item['em_info']
    title = item['title'].encode('utf-8')
    content = item['content'].encode('utf-8')

    #如果记录的em_info字段为数据、新闻、研报、公告，则直接将该条记录归为中性类
    if em_info and em_info.decode("utf8") in info_type:
        label = NEUTRAL

    else:
        text = title + '***' + content

        try:
            p_neg = 1
            p_neu = 1
            p_p = 1
            prob = []

            words = sw.participle(text)
            for word in words:
                if word[0] in para_list[0]:
                    p_w_neg = (float(para_list[0][word[0]])+1)/(float(para_list[3])+float(para_list[10]))
                else:
                    p_w_neg = 1.0/(float(para_list[3])+float(para_list[10]))
                p_neg = p_neg * p_w_neg

                if word[0] in para_list[1]:
                    p_w_neu = (float(para_list[1][word[0]])+1)/(float(para_list[5])+float(para_list[10]))
                else:
                    p_w_neu = 1.0/(float(para_list[5])+float(para_list[10]))
                p_neu = p_neu*p_w_neu

                if word[0] in para_list[2]:
                    p_w_p = (float(para_list[2][word[0]])+1)/(float(para_list[7])+float(para_list[10]))
                else:
                    p_w_p = 1.0/(float(para_list[7])+float(para_list[10]))
                p_p = p_p * p_w_p

            prob_neg = p_negative * p_neg
            prob_neu = p_neutral * p_neu
            prob_p = p_positive * p_p

            if prob_neg == prob_neu and prob_neg == prob_p:
                label = NEUTRAL

            else:
                prob.append(prob_neg)
                prob.append(prob_p)
                prob.append(prob_neu)

                label = LABELS_LIST[prob.index(max(prob))]
        except:
            label = NEUTRAL

    return label
