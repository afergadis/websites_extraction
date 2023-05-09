from wakepy import set_keepawake, unset_keepawake
import os, requests, random, json, zipfile, io
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import Counter
from tqdm import tqdm
from my_lang_detect import lang_detect_on_txt_par
from timeout import timeout
from global_handlers import filter_urls_2, fix_the_html, filter_pdf_urls
from pathlib import Path
import pandas as pd
import shutil
import argparse
import re

def string_found_in_text(word_dict, l_text):
    found = False
    l_string = ''
    for l_string in word_dict:
        if l_string in l_text or\
            l_string.lower() in l_text or\
            l_string.upper() in l_text or\
            l_string.capitalize() in l_text:
            print('Evrika {}'.format(l_string))         #del me at final version
            found = True
            break
    return found, l_string

def clear_url(url):
    while(url.endswith('/')):
        url = url[:-1]
    if(url.startswith('www')):
        url = 'http://{}'.format(url)
    if not (url.startswith('http://') or url.startswith('https://')):
        try:
            page    = requests.get('http://{}'.format(url))
            url     = 'http://{}'.format(url)
        except:
            url     = 'https://{}'.format(url)
    url.replace("'",'\'')
    return url

def get_languages(soup):
    page_langs      = []
    all_text        = soup.text.strip()
    paragraphs      = all_text.split('\n\n')
    paragraphs      = [p for p in paragraphs if len(p.strip()) > 0]
    long_paragraphs = [p for p in paragraphs if len(p.strip()) > 100]
    if len(long_paragraphs) > 0:
        for lp in long_paragraphs:
            try:
                le_lang = lang_detect_on_txt_par(lp)
                page_langs.append(le_lang)
            except:
                le_lang = 'unsure'
                page_langs.append(le_lang)
    else:
        le_lang = 'unsure'
        page_langs.append(le_lang)
    return Counter(page_langs)

def get_the_html(url):
    print(url)
    page = requests.get(url)

    htmltext = page.text
    print(page)

    print(page.reason)
    return page

def get_domain(url):
    url = url.replace('www.', '')
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.split(".")[0]
    return url

def table_to_csv(url, f_path, f_name ):

    fin_path = os.path.join(f_path, f_name)
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-1]
    df.to_csv(fin_path)
    return 0

def download_pdf(url, pdf_name, dir,domain):

    print("Trying downloading file: ", pdf_name)

    # Get response object for link
    url_str = url['href']
    if (url_str.startswith('/')):           #case when webpage is dynamically build in html#
        if ('www.' in url_str):
            print('check here please''{}\n'.format(url_str))
            return None
        else:
            url_str =  domain + url_str

    try:
        response = requests.get(url_str)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        downl_status= "Http Error:" + str(errh)
        return downl_status;
    except requests.exceptions.ConnectionError as errc:
        downl_status = "Error Connecting:" + str(errc)
        return downl_status;
    except requests.exceptions.Timeout as errt:
        downl_status= "Timeout Error: " + str(errt)
        return downl_status;
    except requests.exceptions.RequestException as err:
        downl_status= "Url error occured: " + str(err)
        return downl_status;

    if response.status_code == 200:
        dir_f = os.path.join(dir, pdf_name + ".pdf")
        # Write content in pdf file
        pdf = open(dir_f, 'wb')
        pdf.write(response.content)
        pdf.close()

        print("File ", pdf_name, " downloaded")
        downl_status = 'Ok'
    else:
        downl_status = 'Failed'
    return downl_status;


#  ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------
#  ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------


parser = argparse.ArgumentParser()

parser.add_argument("--max_pages_to_visit", type=int, default=1000, help="Maximum pages to visit.",     required=False)

parser.add_argument("--inpath",             type=str,               help="input json file.",            required=True)
parser.add_argument("--out_dir",            type=str,               help="output root directory path.", required=True)
parser.add_argument("--level_of_tolerance", type=int, default=2,    help="level of tolerance {1,2,3}", required=False)


# Parse the argument
args = parser.parse_args()
# Print "Hello" + the user input argument
print('give input folder,', args.inpath)

# inp= r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\dnb_sample.json"     #admie
# inp= r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\karfoma_hot.json"     #admie
# ot = r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\ot"
extracted_files = 'files_found.csv'
ignored_files = 'ignored_files.csv'


set_keepawake(keep_screen_awake=False)


with open(os.path.join(ot, extracted_files), 'a', encoding='utf-8') as f_esg:
    f_esg.write("ESG files have been found at the following paths:\n")
    f_esg.write('Main URL'  + '\t' + 'Specific URL' + '\t' + 'File_name' + '\t' + 'Download_Status' + '\t' + "path_for_html"   + '\n')
    f_esg.close()


inpath = inp
out_dir = ot
max_pages_to_visit = 1000
level_of_tolerance = 2
# Documentation:     level_of_tolerance: Download all found Documents where:
# {
# 1: string of interest exist in page,                                                  #mild
# 2: string of interest exist in page & at url,                                         #normal
# 3: string of interest exist in page, at url & at pdf (requires more time)             #strict
# }

to_crawl    = json.load(open(inpath,'r',encoding='utf-8'))
# random.shuffle(to_crawl)

pbar = tqdm(to_crawl)
download_html = True
download_pdf_b = True

for (pic_type, base_url, pic_id) in pbar:

    page_dir = os.path.join(out_dir, pic_type)
    pic_dir = os.path.join(out_dir, pic_type, pic_id)
    url_domain = get_domain(urlparse(base_url).netloc)
    url_domain_full = urlparse(base_url).scheme + '://'  + urlparse(base_url).netloc

    if not os.path.exists(pic_dir):
        os.makedirs(pic_dir)

    ################################################
    # base_url = clear_url(base_url)        pending
    clean_url = base_url.replace("'", '\"')
    pbar.set_description(base_url)
    ################################################
    already_visited = set()
    to_visit        = [base_url]
    ################################################
    visited_counter = 0
    ################################################
    c = i = 0
    if download_html == True:
        pages_visited   = open(os.path.join(pic_dir, 'pages_visited.txt'),   'a', encoding='utf-8')
        pages_error     = open(os.path.join(pic_dir, 'pages_error.txt'),     'a', encoding='utf-8')
        pages_discarded = open(os.path.join(pic_dir, 'pages_discarded.txt'), 'a', encoding='utf-8')

    # Parse url & from html call any other url you find
    # If word of interest is found in html, check if there is any pdf file at the same page and at called url & download it
    while(len(to_visit)>0):

        pbar.set_description('{}:{}:{}'.format(os.path.join(pic_type, pic_id), base_url,len(to_visit)))
        url         = to_visit[0]
        to_visit    = to_visit[1:]
        already_visited.add(url)

        try:
            page = get_the_html(url)

        except:
            print('Error for page: {}'.format(url))
            if download_html == True:
                pages_error.write('{}\n'.format(url))
                continue

        ################################################
        soup = BeautifulSoup(page.text, "lxml")
        page_langs  = get_languages(soup)

        c       += 1
        pic_page_dir = os.path.join(pic_dir, str(c))
        if download_html == True:
            if not os.path.exists(pic_page_dir):
                os.makedirs(pic_page_dir)
        ################################################

            with open(os.path.join(pic_page_dir,'source_of_page.html'), 'w', encoding='utf-8') as fp:
                fp.write(page.text)
                fp.close()
            with open(os.path.join(pic_page_dir,'webpage_visited.txt'), 'w', encoding='utf-8') as fp:
                fp.write(url)
                fp.close()
            ################################################
            with open(os.path.join(pic_page_dir,'languages.json'), 'w', encoding='utf-8') as of:
                of.write(json.dumps(dict(page_langs), indent=4, sort_keys=False))
                of.close()
        ####################################################################################

        esg_dict = [
        'ESG',
        'ΒΙΩΣΙΜΗ ΑΝΑΠΤΥΞΗ',
        'ΒΙΩΣΙΜΗ',
        'ΒΙΩΣΙΜΌΤΗΤΑ',
        'viosim',
        'viosimi',
        'Environmental Social Governance',
        'Sustainable',
        'Sustainability', 'CSR'
            #,'eba', 'εβα' , 'CDP', 'GRI'      #for εκθεση βιωσιμης ανάπτυξης
        ]

        # esg_exists = False
        # dict_str = ''
        esg_exists, dict_str = string_found_in_text(esg_dict, soup.text)


        if esg_exists == True and download_pdf_b == True:

            pdf_dir = ''
            # # -- Isolate pdf links & download them --
            links = soup.find_all('a')


            gen_links = ( link for link in links if ('.pdf' in link.get('href', [])) )
            for link in gen_links:
                print('\n {}'.format(link))
                esg_exists_in_url, dict_str = string_found_in_text(esg_dict, link['href'])
                if level_of_tolerance > 1 and esg_exists_in_url == False:
                    ignore_dir = os.path.join(page_dir, 'ignored_urls')
                    if not os.path.exists(ignore_dir):
                        os.makedirs(ignore_dir)
                    with open(os.path.join(ignore_dir, ignored_files), 'a', encoding='utf-8') as f_ignr:
                        f_ignr.write(str(link['href']) + '\n')
                        f_ignr.close()
                    continue
                # else:



                pdf_dir = os.path.join(page_dir, dict_str.upper() + '_files')
                if not os.path.exists(pdf_dir):
                    os.makedirs(pdf_dir)

                if link.text != '':
                    file_descr = link.text
                else:
                    i += 1
                    file_descr = str(i)
                f_name  = dict_str.upper() + '_' + str(url_domain) + '_' + str(i)       #new28

                f_downl_status = download_pdf(link, f_name, pdf_dir, url_domain_full)
                with open(os.path.join(ot, extracted_files), 'a', encoding='utf-8') as f_esg:
                    f_esg.write(base_url + '\t' + url + '\t' + f_name + '\t' + f_downl_status + '\t' + os.path.join(pic_type,pic_id) + '\n')
                    f_esg.close()
        ####################################################################################

        accepted_links, discarded_links = filter_urls_2(
            base_url,
            [
                a.get('href')
                for a in soup.findAll('a')
            ]
        )

        to_visit = to_visit + list(accepted_links - set(to_visit) - already_visited)


        if download_html == True:
            pages_visited.write('{}\n'.format(url))
            for disc_page in discarded_links:
                pages_discarded.write('{}\n'.format(disc_page))
        ################################################

        visited_counter +=1
        if(visited_counter >= max_pages_to_visit):
            print(f'Max pages to visit limit WAS exceeded. Download of site {clean_url} stopped')
            break

    if download_html == True:
        pages_visited.close()
        pages_discarded.close()
        pages_error.close()

unset_keepawake()