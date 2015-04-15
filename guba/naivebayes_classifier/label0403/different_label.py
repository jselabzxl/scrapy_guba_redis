# -*- coding: cp936 -*-
import os
import csv

def read_label_csv(datadir):
    '''
    读入标注数据
    输入数据：
    data_dir:输入数据路径
    输出数据：
    label_data:标记数据，{"id":[id,content,title,em_info,stock_name,label]}
    '''
    label_data = {}
    files = os.listdir(datadir)
    for fname in files:
        print fname
        reader = csv.reader(file(datadir+fname,'rb'))
        for id,content,title,em_info,stock_name,label in reader:
            if label == '-1':
                label = '2'
            label_data[id] = [id,content,title,em_info,stock_name,label]

    return label_data

def compare_label(label1,label2):
    '''
    比较两组标注数据
    输入数据：
    label1:第一组标注数据
    label2:第二组标注数据
    输出数据：
    different_label:两组标注差异数据，{"id":[id,content,title,em_info,stock_name,label1,label2]}
    same_label:两组标注相同的数据，{"id":[id,content,title,em_info,stock_name,label1]}
    '''
    different_label = {}
    same_label = {}
    for k,v in label1.iteritems():
        label_1 = label1[k][5]
        if label2.has_key(k):
            label_2 = label2[k][5]
            if label_1 != label_2:
                different_label[k] = label1[k]
                different_label[k].append(label2[k][5])
            else:
                same_label[k] = label1[k]

    return different_label,same_label

def revise_label(original_dir,different_label):
    '''
    将二次标注有异的同原始标注比较，如果有两个标签相同则归入标签相同类，否则归入无情感类
    输入数据：
    original_dir:原始标注数据路径
    different_label:标注不同的数据
    输出数据：
    revised_label:修改后的数据标签
    '''
    reader = csv.reader(file(original_dir,'rb'))
    original_label = {}
    for id,content,title,em_info,stock_name,label in reader:
        if label == '-1':
            label = '2'
        original_label[id] = [id,content,title,em_info,stock_name,label]

    revised_label = {}
    pass_list = []
    for k,v in different_label.iteritems():
        label_1 = different_label[k][5]
        label_2 = different_label[k][6]
        try:
            label_original = original_label[k][5]
            if label_original == label_1:
##                different_label[k].extend(label_1)
##                revised_label[k] = different_label[k]
                revised_label[k] = [different_label[k][0],different_label[k][1],different_label[k][2],different_label[k][3],different_label[k][4],label_1,label_2,label_original]
            elif label_original == label_2:
##                different_label[k].extend(label_2)
##                revised_label[k] = different_label[k]
                revised_label[k] = [different_label[k][0],different_label[k][1],different_label[k][2],different_label[k][3],different_label[k][4],label_1,label_2,label_original]
            elif label_original!=label_1 and label_original != label_2:
##                different_label[k].extend('2')
##                revised_label[k] = different_label[k]
                revised_label[k] = [different_label[k][0],different_label[k][1],different_label[k][2],different_label[k][3],different_label[k][4],label_1,label_2,label_original]
        except:
            pass_list.append(k)

    print pass_list
    return revised_label

if __name__ == '__main__':
    lab_csv = './lab_labeled/label_csv/'
    bu_csv = './bu_labeled/label_csv/'
    lab_label = read_label_csv(lab_csv)
    bu_label = read_label_csv(bu_csv)
    print len(bu_label)

    difference,same = compare_label(lab_label,bu_label)
    original_dir = './guba_original_label.csv'
    revised = revise_label(original_dir,difference)
    sort_revised = sorted(revised.iteritems(),key=lambda(k,v):k,reverse=False)
##    with open('./different_label.csv','wb')as f:
##        writer = csv.writer(f)
##        for k,v in difference.iteritems():
##            writer.writerow((v))
##    print len(difference)
##
##    with open('./same_label.csv','wb')as f:
##        writer = csv.writer(f)
##        for k,v in same.iteritems():
##            writer.writerow((v))
##    print len(same)
    with open('./three_labeling_result.csv','wb')as f:
        writer = csv.writer(f)
        for item in sort_revised:
            writer.writerow((item[1]))

    
        
