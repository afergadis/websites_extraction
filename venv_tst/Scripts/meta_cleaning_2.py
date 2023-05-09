import os
import re
import csv
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize, RegexpTokenizer
from nltk.corpus import stopwords
from time import sleep
from tqdm import tqdm
from alive_progress import alive_bar
import time
import pandas as pd
import argparse
import datetime

def timestamp_str():
    now = datetime.datetime.now()
    ts_str = str(now.day) + '.' + str(now.month) + '.' + str(now.year) + '_' + str(now.hour) + '.' + str(now.minute) + '.' + str(now.second)
    return ts_str
def has_404_error(inp_file):
    string1 = '404'
    string2 = 'error'

    string3 = 'not found'
    string4 = 'website'
    string3_el =  'Δεν βρέθηκε'
    string4_el = 'ιστοσελίδα'

    file_string = file_to_string(inp_file)

    flag = '0'
    # for line
    if ( string1    in file_string and string2    in file_string )  or\
       ( string3    in file_string and string4    in file_string )  or\
       ( string3_el in file_string and string4_el in file_string ) :
       flag = '1'

    return flag


def find_sent_with_tm(inp_file):
    tm_chars = ['Ⓡ','®',u'Ⓡ',u'®','™',u'™', '©', '℠', u'©', u'℠']
    tm_chars_unic = [u'\u00A9',u'\u2120',u'\u2122',u'\u24c7' ]
    # u"\u00A9" for copyright     ©
    # u'\u2120' for Service mark '℠'
    # u'\u2122' for Trade mark   '™'
    # u'\u24c7' for Registered trademark Ⓡ

    file_string = file_to_string(inp_file)

    for mark in tm_chars_unic:
        if mark in  file_string:
            print('Evrika trademark!!')

    for mark in tm_chars:
        if mark in  file_string:
            print('Ki omws, vrika !')
    return 0


# Function to convert list to string
def listToString(s):
    str1 = ""
    for ele in s:
        str1 += ele
        str1 += ' '
    return str1

# -*- coding: utf-8 -*-
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def file_to_string(inp_file):
    file1 = open(inp_file, "r", encoding='utf-8')
    file_string = file1.read()
    file1.close()
    return  file_string;

# gets a region of sentence with the significant word in the center
def sentence_region_of_interest(sent_words, word, margin=15):
    indx = sent_words.index(word)

    start = 0     if len(sent_words[:indx]) == 0 else -1
    end = indx +1 if len(sent_words[indx:]) == 1 else -1
    lv_margin = margin

    while lv_margin > 0 and start == -1:
        if len(sent_words[:indx]) + 1 > lv_margin:
            start = indx - lv_margin
        lv_margin -= 1

    lv_margin = margin
    while lv_margin > 0 and end == -1:
        if len(sent_words[indx:])  > lv_margin:
            end = indx + lv_margin + 1
        lv_margin -= 1

    return start, end

def count_words(inp_file, ape_dict):
    i = 0
    prod_str = ''
    tm_products =[]
    ape_sentence = []
    tm_products.clear()
    ape_sentence.clear()
    tm_chars = ['Ⓡ','®',u'Ⓡ',u'®','™',u'™', '©', '℠', u'©', u'℠']
    tm_chars_unic = [u'\u00A9',u'\u2120',u'\u2122',u'\u24c7' ]

    num_of_words = num_of_clean_words = 0
    file_string = file_to_string(inp_file)
    str_file_low = file_string.lower()
    sentences = nltk.sent_tokenize(str_file_low)

    latin_flag = isEnglish(file_string[:30])    #CONDITION IS ENOUGH?
    str_lang = 'english' if latin_flag == True else 'greek'

    for sentence in sentences:
        i += 1

        sentence_copy = sentence
        sentence = re.sub(r'\d+', '', sentence)
        tokenizer = RegexpTokenizer(r'\w+')     #to remove punctuation
        # tokenizer2 = RegexpTokenizer()
        sent_words = tokenizer.tokenize(sentence)
        sent_words_copy = word_tokenize(sentence_copy)

        num_of_words += len(sent_words)
        words_excl_sw = [word for word in sent_words if not word in stopwords.words(str_lang)]   #PENDING FOR ENGLISH
        num_of_clean_words += len(words_excl_sw)

        for word in sent_words_copy:
            if word in tm_chars_unic:
                indx_start, indx_end = sentence_region_of_interest(sent_words_copy, word, 40)
                tm_products.append(sent_words_copy[indx_start : indx_end])

            indx_start = 0
            indx_end   = 0
            if word in ape_dict:
                indx_start, indx_end = sentence_region_of_interest(sent_words_copy, word, 40)
                ape_sentence.append(sent_words_copy[indx_start: indx_end])



    # get all products with trademark
    ll = list_tm = []
    for i in tm_products:
        kk = ''
        kk = listToString(i)

        ll.append(kk)
        list_tm = list(dict.fromkeys(ll))

        # prod_str.append(listToString(tm_products.index(i)))

    # get all enviromental actions of the companies
    mm = list_ape = []

    for i in ape_sentence:
        nn = ''
        nn = listToString(i)

        mm.append(nn)
        list_ape = list(dict.fromkeys(mm))

    # 2022.12 {+
    # get all URLs redirecting to files

    # +} 2022.12
    return num_of_words, num_of_clean_words, list_tm, list_ape

header = ['Folder','Failed entirely Bool', 'Num of Succeeded Pages', 'Succeeded pages perc', 'avg tokens per page', 'avg tokens (w cont) per page', 'tm1_chars','tm2_chars']#, 'Error Message concat']
data = []
total_failed = ['1', 0 , 0.0, 0.0, 0.0, 0, 0, [], [] ]


parser = argparse.ArgumentParser(description='Process HTML texts to find bussiness responsability')
# parser.add_argument("--max_pages_to_visit", type=int, default=1000, help="Maximum pages to visit.",     required=False)

parser.add_argument("--inpath",             type=str,               help="input path with folders of HTML files.",            required=True)
parser.add_argument("--out_dir",            type=str,               help="output root directory path.", required=True)

args = parser.parse_args()
inp= args.inpath
ot = os.path.join(args.out_dir, 'meta_results_' + str(timestamp_str() + ".csv") )

ape_dict_list = [
'Ανανεώσιμες',
'Ανανεώσιμ',
'πηγές ενέργειας',
'ΑΠΕ',
'ήπιες μορφές',
'μορφές ενέργειας',
'νέες πηγές ενέργειας',
'πράσινη ενέργεια',
'ΚΑΠΕ',
'Eξοικονόμησης Eνέργειας',
'ΕΞΟΙΚΟΝΟΜΙΣΗ ΕΝΕΡΓΕΙΑΣ',
'cres.gr',
'οικολογικ',
'υδροηλεκτρισμ',
'υδροηλεκτρισμού',
'Αιολική ',
'ανεμογεννήτρ',
'Ηλιακή ',
'θαλάσσι',
'Βιοµάζα',
'Γεωθερµική ',
'γεωθερμία',
'βιολογικ',
'θερμοκηπίου',
'θερμοκήπ',
# 'περιβάλλον',
'φωτοβολτα',
# 'προστασία',
# 'προστατεύ',
'υδροηλεκτρικ',
'υδροηλεκτρισμός',
'Περιβαλλοντικών',
# 'Περιβάλλον',
'βιοκαύσιμο',
'Βιομάζα',
# 'Ενέργεια από τη θάλασσα',
'Ωσμωτική',
'Υδραυλική ενέργεια',
'φιλικές προς το περιβάλλον',
'παλιρροϊκ',
'solar',
'wind',
'falling water',
'geothermal',
'biomass',
'waves',
'ocean currents',
'temperature differences in the oceans',
'energy of the tides',
'Greenhouse effect',
'renewable'
]
# nltk.download('punkt')
# nltk.download('stopwords')

trg_path = ot
ot = os.path.join(args.out_dir, 'results_' + str(timestamp_str() ) )# path = r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\boilerplate_removal\1"
path = inp
os.chdir(path)

num_of_files = len(os.listdir(path))
# os.chdir(r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\1 test")    #28.07
# print( [name for name in os.listdir(".")] )
i = 0
data = []
# f_name stands for each folder name of the path's folders
with alive_bar(num_of_files) as bar:

    for f_name in os.listdir("."):

        flag_fail = '1'
        i = i + 1
        all_tm_prod =  []
        all_ape_sent = []
        lv_ape_sent = []
        tm_prod = []
        all_tm_prod.clear()
        all_ape_sent.clear()
        lv_ape_sent.clear()
        tm_prod.clear()


        n_suc = n_fail = words_cnt = clean_words_cnt = sum_clean_words_cnt = sum_words_cnt= 0
        num_of_files = len(os.listdir(f_name))

        # -- Field 1 ----------------------
        # -- Webpages with error ----------
        if num_of_files == 0:
            flag_fail = '1'

        elif num_of_files == 1:     #check the case it returned 404 error!

            path_dir = path + '\\' + f_name + '\\' + os.listdir(f_name)[0]
            flag_fail = has_404_error(path_dir)  #check me please! - pending
            n_suc = 1  if flag_fail == '0' else  0

            if flag_fail == '0':
                # sum_words_cnt, sum_clean_words_cnt = count_words(path_dir) #cb 28.07
                sum_words_cnt, sum_clean_words_cnt, tm_prod, lv_ape_sent = count_words(path_dir, ape_dict_list)
                if tm_prod != [] and tm_prod not in all_tm_prod:
                    all_tm_prod.append(tm_prod)

                if lv_ape_sent != [] and lv_ape_sent not in all_ape_sent:
                    all_ape_sent.append(lv_ape_sent)


        else:
            websites = [f.name for f in os.scandir(f_name) if f.is_file()]
            for site in websites:
                path_dir = path + '\\' + f_name + '\\' + site
                flag_fail = has_404_error(path_dir)
                if flag_fail == '0':
                    words_cnt, clean_words_cnt, tm_prod, lv_ape_sent  =  count_words(path_dir,ape_dict_list)
                    sum_words_cnt +=  words_cnt
                    sum_clean_words_cnt += clean_words_cnt
                    if tm_prod != [] :
                        if tm_prod not in all_tm_prod:
                            all_tm_prod.append(tm_prod)


                    if lv_ape_sent != [] :
                        if lv_ape_sent not in all_ape_sent:
                            all_ape_sent.append(lv_ape_sent)

                    if sum_words_cnt < sum_clean_words_cnt:
                        print('error')

                n_suc += 1 if flag_fail == '0'  else 0 #n_suc


        # Write the x-line of csv (out of 408)
        if n_suc == 0:
            line_fail = []
            line_fail.append(str(f_name))        #folder
            line_fail.extend(total_failed)
            data.append(line_fail)
        else:
            perc_suc            = "{:.2f}".format((n_suc / num_of_files))
            avg_tok_per_pg      = "{:.2f}".format((sum_words_cnt/n_suc))
            avg_cont_tok_per_pg = "{:.2f}".format((sum_clean_words_cnt/n_suc))
            line_succ = []
            line_succ.append(str(f_name))                   #folder
            line_succ.append('0')                           #field1
            line_succ.append(str(n_suc))                    #field2
            line_succ.append(str(perc_suc))                 #field3
            # line_succ.append(str(words_cnt))              #field4
            line_succ.append(str(sum_words_cnt))            #field4
            line_succ.append(str(sum_clean_words_cnt))      #field5
            line_succ.append(str(all_tm_prod))              #field6
            line_succ.append(str(all_ape_sent))             #field7

            data.append(line_succ)


        time.sleep(.001)
        bar()


with open(ot, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(data)