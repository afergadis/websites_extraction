from wakepy import set_keepawake, unset_keepawake
import os, requests, random, json, zipfile, io
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import datetime
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
import csv

def string_found_in_text(word_dict, l_text):
    found = False
    l_string = ''
    for l_string in word_dict:
        if l_string in l_text or\
            l_string.lower() in l_text or\
            l_string.upper() in l_text or\
            l_string.capitalize() in l_text:
            # print('Evrika {}'.format(l_string))         #del me at final version
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
    # if(url.endswith(")):
    #     print('errorrrrrs,,,,!!!!')
    url.replace("'",'\'')
    # if (url.startswith(")):
    #     print('Polllaaa errorrrrrs,,,,!!!!')
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
    # print(url)
    page = requests.get(url)
    # webpage = urlopen(page, timeout=10).read()            #failed

    htmltext = page.text
    # print(page)

    # print(page.reason)
    return page

def get_domain(url):
    url = url.replace('www.', '')
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.split(".")[0]
    return url

def table_to_csv(url, f_path, f_name ):

    # url = 'http://www.ffiec.gov/census/report.aspx?year=2011&state=01&report=demographic&msa=11500'
    # f_path  = r'C:\Users\c.borovilou\Desktop\tmp\my_data.csv'
    fin_path = os.path.join(f_path, f_name)
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-1]
    df.to_csv(fin_path)
    return 0

def download_pdf(url, pdf_name, dir,domain):

    print("Trying downloading file: ", pdf_name, ".pdf")

    # Get response object for link
    url_str = url['href']
    if (url_str.startswith('/')):           #case when webpage is dynamically build in html#
        if ('www.' in url_str):
            print('check here please''{}\n'.format(url_str))
            # downl_status = 'Failed'
            return None
        else:
            url_str =  domain + url_str

    try:
        response = requests.get(url_str)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        # print( "Error Connecting: ", errh )
        downl_status= "Http Error:" + str(errh)
        return downl_status;
    except requests.exceptions.ConnectionError as errc:
        # print( "Error Connecting: ", errc )
        downl_status = "Error Connecting:" + str(errc)
        return downl_status;
    except requests.exceptions.Timeout as errt:
        # print("Error Connecting: ", errt)
        downl_status= "Timeout Error: " + str(errt)
        return downl_status;
    except requests.exceptions.RequestException as err:
        # print("Error Connecting: ", err)
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

def timestamp_str():
    now = datetime.datetime.now()
    ts_str = str(now.day) + '.' + str(now.month) + '.' + str(now.year) + '_' + str(now.hour) + '.' + str(now.minute) + '.' + str(now.second)
    return ts_str

def set_dictionary(input_fold, dict_file):
    # this function initializes a words-dictionary and stores it in input path.
    # User can afterwards maintain the words use locally (at a csv file)
    if not os.path.exists(os.path.join(input_fold, dict_file)):
        dictionary = [
        'ESG',
        'ΒΙΩΣΙΜΗ ΑΝΑΠΤΥΞΗ',
        'ΒΙΩΣΙΜΗ',
        'ΒΙΩΣΙΜΌΤΗΤΑ',
        'viosim',
        'Biosim',
        'Environmental Social Governance', 'environmental-social-governance',  'environmental_social_governance', 'Environmentalsocialgovernance',
        'Sustainable', 'Sustainability',
        'CSR', 'CDP', 'GRI',
        'climate', 'footprint', 'greenhouse', 'ecological', 'biodiversity'
            #,'eba', 'εβα' , 'CDP', 'GRI'      #for εκθεση βιωσιμης ανάπτυξης
        ]


        with open(os.path.join(input_fold, dict_file ), 'w', encoding='utf-8') as f_dict:
            f_dict.write(','.join(map(str, dictionary)))

    else:
        inp = os.path.join(input_fold, dict_file)
        file = open(inp, "r", encoding="utf8")
        dictionary = list(csv.reader(file, delimiter=","))[0]
        file.close()
    return dictionary

def get_domains_from_soup(link, soup):
    initial_url_full = str(link['href'])
    base_url = url_domain = url_domain_full = ''
    for soup_link in soup.select('link[rel*=canonical]'):
        base_url = soup_link['href']
        url_domain = get_domain(urlparse(base_url).netloc)
        url_domain_full = urlparse(base_url).scheme + '://' + urlparse(base_url).netloc

        if (link['href'].startswith('/')):  # case when webpage is dynamically build in html#
            if ('www.' in link['href']):
                print('check here please''{}\n'.format(link['href']))
                initial_url_full = ''
            else:
                initial_url_full = url_domain_full + str(link['href'])
    return base_url, url_domain, url_domain_full, initial_url_full
#  ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------
#  ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------


# parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Extract ESG files from HTML files')
# parser.add_argument("--max_pages_to_visit", type=int, default=1000, help="Maximum pages to visit.",     required=False)

parser.add_argument("--inpath",             type=str,               help="input path with folders of HTML files.",            required=True)
parser.add_argument("--out_dir",            type=str,               help="output root directory path.", required=True)
parser.add_argument("--max_pages_to_visit", type=int, default=1000, help="Maximum pages to visit.",     required=False)
parser.add_argument("--level_of_tolerance", type=int, default=2,    help="level of tolerance {1,2,3}", required=False)


# Parse the argument
args = parser.parse_args()
inp= args.inpath
# ot = args.out_dir
ot = os.path.join(args.out_dir, 'results_' + str(timestamp_str() ) )
if not os.path.exists(ot):
    os.makedirs(ot)


extracted_files = 'files_found.csv'
esg_dict_f = 'esg_dict.csv'
ignored_files = 'ignored_files_' + str(timestamp_str()) +  '.csv'


set_keepawake(keep_screen_awake=False)


with open(os.path.join(ot, extracted_files), 'w', encoding='utf-8') as f_esg:         #check here
# with open(os.path.join(ot, extracted_files), 'a', encoding='utf-8') as f_esg:
#     f_esg.write("ESG files have been found at the following paths:\n")
    f_esg.write('Main URL'  + '\t' + 'Specific URL' + '\t' + 'File_name' + '\t' + 'Download_Status' + '\t' + "folder_name_of_HTML"   + '\n')
    f_esg.close()


inpath = inp
# out_dir = ot
max_pages_to_visit = 1000
level_of_tolerance = 2
# Documentation:     level_of_tolerance: Download all found Documents where:
# {
# 1: string of interest exist in page,                                                  #mild
# 2: string of interest exist in page & at url,                                         #normal
# 3: string of interest exist in page, at url & at pdf (requires more time)             #strict
# }

os.environ['dir_name'] = inpath
os.chdir(os.environ['dir_name'])

download_pdf_b = True # False
c = i = 0

# Create the list of file found inside folder of input path:
folders = [f for f in os.listdir(inpath) if os.path.isdir(os.path.join(inpath, f))]

# loop through the list of folders
for f_name in tqdm(folders):

    num_of_files = len(os.listdir(f_name))
    if num_of_files == 0:
        continue
    else:

        websites = [f.name for f in os.scandir(f_name) if f.is_file()]
        for site in websites:

            # Use Beautiful Soup to parse HTML
            path_dir = inpath + '\\' + f_name + '\\' + site
            with open(path_dir, encoding="utf8") as fp:

                html = fp.read()

            soup = BeautifulSoup(html, 'html.parser')

            c += 1

            # A. Create a "dictionary of words" file defining specific-enough content for the scope of our search
            # B. Export it as a .csv file at input folder so that user can maintain the "dictionary" easily.
            # C. Read it in a list so that program can use it
            esg_dict = set_dictionary(inp, esg_dict_f )

            # Checkpoint 1: Check if HTML file contains any word that exists in a our dictionary
            esg_exists, dict_str = string_found_in_text(esg_dict, soup.text)


            # Checkpoint 2: Check if URL itself contains any word that exists in a our dictionary
            if esg_exists == True and download_pdf_b == True:

                pdf_dir = ''
                # # -- Isolate pdf links & download them --
                links = soup.find_all('a')
                gen_links = ( link for link in links if ('.pdf' in link.get('href', [])) )

                cnt = 0
                for link in gen_links:
                    cnt += 1
                    initial_url_full = str(link['href'])

                    #  --- 1. Get domain & Correct dynamical URLs ---
                    base_url,url_domain, url_domain_full, initial_url_full = get_domains_from_soup(link, soup)

                    # --- 2. Choose if you will ignore pdf (but log it in file) or you will download it ---
                    esg_exists_in_url, dict_str = string_found_in_text(esg_dict, link['href'])
                    if level_of_tolerance > 1 and esg_exists_in_url == False:
                        ignore_dir = os.path.join(ot, 'ignored_urls')
                        if not os.path.exists(ignore_dir):
                            os.makedirs(ignore_dir)
                        with open(os.path.join(ignore_dir, ignored_files), 'a', encoding='utf-8') as f_ignr:
                            # f_ignr.write(str(link['href']) + '\n')
                            f_ignr.write(str(initial_url_full) + '\n')
                            f_ignr.close()
                        continue

                    print(initial_url_full)

                    # pdf_dir = os.path.join(ot, dict_str.upper() + '_files')
                    pdf_dir = os.path.join(ot, url_domain.upper() + '_files')
                    if not os.path.exists(pdf_dir):
                        os.makedirs(pdf_dir)

                    # if link.text != '':
                    #     file_descr = re.sub(r'[^\w]+', '', link.text)
                    # else:
                    #     i += 1
                    #     file_descr = str(i)

                    # Build pdf description
                    f_descr  = dict_str.upper() + '_' + str(url_domain) + '_' + str(cnt)       #new28

                    f_downl_status = download_pdf(link, f_descr, pdf_dir, url_domain_full)
                    # f_downl_status = download_zip(link, f_descr, pdf_dir) #, url_domain_full)
                    with open(os.path.join(ot, extracted_files), 'a', encoding='utf-8') as f_esg:
                        f_esg.write(base_url + '\t' + initial_url_full + '\t' + f_descr + '\t' + f_downl_status + '\t' + f_name + '\n')
                        f_esg.close()

                    initial_url_full = url_domain_full = url_domain = base_url = ''

unset_keepawake()