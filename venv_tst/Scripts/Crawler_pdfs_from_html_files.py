from wakepy import set_keepawake, unset_keepawake
# from html.parser import HTMLParser
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
#  ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------
#  ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------ ------------


# parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(description='Extract ESG files from HTML files')
# parser.add_argument("--max_pages_to_visit", type=int, default=1000, help="Maximum pages to visit.",     required=False)


# parser.add_argument("--inpath",             type=str,               help="input json file.",            required=True)
parser.add_argument("--inpath",             type=str,               help="input path with folders of HTML files.",            required=True)
parser.add_argument("--out_dir",            type=str,               help="output root directory path.", required=True)
parser.add_argument("--max_pages_to_visit", type=int, default=1000, help="Maximum pages to visit.",     required=False)
parser.add_argument("--level_of_tolerance", type=int, default=2,    help="level of tolerance {1,2,3}", required=False)


# Parse the argument
args = parser.parse_args()
# # Print "Hello" + the user input argument
# print('give input folder,', args.inpath)

inp= args.inpath
ot = args.out_dir


# inp = r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\karfoma3.json"     #admie
# inp= r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\karfoma_hot.json"     #admie
# # inp= r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\data_from_dnb_rest.json"
# # inp= r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\empty of pddfs.json"
# # inp= r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\GenericWebPageCrawler-master\GenericWebPageCrawler-master\dnb_sample.json"     #admie
# # ot = r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\GenericWebPageCrawler-master\GenericWebPageCrawler-master\ott"
# ot = r"C:\Users\c.borovilou\Desktop\MSc\διπλωματική\hot"


# inp = r"C:\Users\c.borovilou\OneDrive - Public-Group\διπλωματική\boilerplate_removal\out"
# ot = r"C:\Users\c.borovilou\OneDrive - Public-Group\Desktop\MSc\διπλωματική\out"

extracted_files = 'files_found.csv'
ignored_files = 'ignored_files_' + str(timestamp_str()) +  '.csv'


set_keepawake(keep_screen_awake=False)


with open(os.path.join(ot, extracted_files), 'w', encoding='utf-8') as f_esg:         #check here
# with open(os.path.join(ot, extracted_files), 'a', encoding='utf-8') as f_esg:
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

# to_crawl    = json.load(open(inpath,'r',encoding='utf-8'))
# >> 20.04.2023
# with open(r'C:\Users\...site_1.html', "r") as f:
#     page = f.read()
# tree = html.fromstring(page)
os.environ['dir_name'] = inpath
os.chdir(os.environ['dir_name'])

# for f_name in os.listdir("."):
#     tree = html.parse(f_name)
#     print(html.tostring(tree))
# << 20.04.2023

# random.shuffle(to_crawl)

# pbar = tqdm(to_crawl)
download_html = False # True
download_pdf_b = True # False


# >> 20.04.2023
# for (pic_type, base_url, pic_id) in pbar:

    # # #  Temp -   pending to del >>
    # excl_list = ["20" ]
    #
    # if pic_id in  excl_list:
    #     pbar.close()
    #     continue
    # #  << Temp -   pending to del
c = i = 0
folders = [f for f in os.listdir(inpath) if os.path.isdir(os.path.join(inpath, f))]

# loop through the list of folders
for f_name in folders:
# for f_name in os.listdir("."):
    # tree = html.parse(f_name)
    # print(html.tostring(tree))


        num_of_files = len(os.listdir(f_name))

        if num_of_files == 0:
            continue
        else:
            websites = [f.name for f in os.scandir(f_name) if f.is_file()]
            for site in websites:

                # with open(f_name) as fp:
                path_dir = inpath + '\\' + f_name + '\\' + site
                with open(path_dir, encoding="utf8") as fp:

                    html = fp.read()

                soup = BeautifulSoup(html, 'html.parser')


# << 20.04.2023

    # page_dir = os.path.join(out_dir, pic_type)
    # pic_dir = os.path.join(out_dir, pic_type, pic_id)
    # url_domain = get_domain(urlparse(base_url).netloc)
    #     # (urlparse(base_url).netloc).split(".")[1]
    # url_domain_full = urlparse(base_url).scheme + '://'  + urlparse(base_url).netloc

    # if not os.path.exists(pic_dir):
    #     os.makedirs(pic_dir)
    # else:
    #     # continue      ############## CHECK AGAIN 15.01.2023 ##################
    #     print('do not make dir that exists:{}'.format(pic_dir))

    # << PENDING TO UNCOMMENT - CB - END
    ################################################
    # # base_url = clear_url(base_url)        pending
    # clean_url = base_url.replace("'", '\"')
    # pbar.set_description(base_url)
    # ################################################
    # already_visited = set()
    # to_visit        = [base_url]
    # ################################################
    # visited_counter = 0
    # ################################################
                # c = i = 0
                c += 1
                # page_dir = os.path.join(out_dir, pic_type)
                page_dir = out_dir


                # μπες ιστοσελιδα και παρε ολα τα html απο ο,τι url βρεις
                # αν δε, βρεις τη λεξούλα esg, κοιτα μηπως καλείται κανενα ulr με pdf και κάνε το download
                # while(len(to_visit)>0):

                    # pbar.set_description('{}:{}:{}'.format(os.path.join(pic_type, pic_id), base_url,len(to_visit)))
                    # url         = to_visit[0]
                    # to_visit    = to_visit[1:]
                    # already_visited.add(url)

                    # start prison 28.01
                    # HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

                    # end prison 28.01
                    # try:
                    #     page = get_the_html(url)
                    #     # page = get_the_html(url, HEADERS)     #failed
                    #
                    # except:
                    #     print('Error for page: {}'.format(url))
                    #     if download_html == True:
                    #         pages_error.write('{}\n'.format(url))
                    #         continue
                    ###############################################

                    # soup = BeautifulSoup(page.text, "lxml")

                    # pending 22.04.2023 {+
                    # page_langs  = get_languages(soup)
                    # pending 22.04.2023 +}

                    # c += 1      # here

                    # pic_page_dir = os.path.join(pic_dir, str(c))
                    # if download_html == True:
                    #     if not os.path.exists(pic_page_dir):
                    #         os.makedirs(pic_page_dir)
                    # ################################################
                    #
                    #     with open(os.path.join(pic_page_dir,'source_of_page.html'), 'w', encoding='utf-8') as fp:
                    #         fp.write(page.text)
                    #         fp.close()
                    #     with open(os.path.join(pic_page_dir,'webpage_visited.txt'), 'w', encoding='utf-8') as fp:
                    #         fp.write(url)
                    #         fp.close()
                    #     ################################################
                    #     with open(os.path.join(pic_page_dir,'languages.json'), 'w', encoding='utf-8') as of:
                    #         of.write(json.dumps(dict(page_langs), indent=4, sort_keys=False))
                    #         of.close()
                    ####################################################################################
                    ################################################        12.01.2023 >>
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


                # delete me !!! PENDING >>
                if download_pdf_b == False:
                    esg_exists = False
                # << delete me !!! PENDING

                if esg_exists == True:

                    pdf_dir = ''
                    # # -- Isolate pdf links & download them --
                    links = soup.find_all('a')


                    gen_links = ( link for link in links if ('.pdf' in link.get('href', [])) )
                    # gen_links2 = ( link for link in links if ('.zip' in link.get('href', [])) )
                    for link in gen_links:
                        cnt = 0
                        # print('\n {}'.format(link))  #-cb 04.05.2023
                        esg_exists_in_url, dict_str = string_found_in_text(esg_dict, link['href'])
                        if level_of_tolerance > 1 and esg_exists_in_url == False:
                            ignore_dir = os.path.join(page_dir, 'ignored_urls')
                            if not os.path.exists(ignore_dir):
                                os.makedirs(ignore_dir)
                            with open(os.path.join(ignore_dir, ignored_files), 'a', encoding='utf-8') as f_ignr:
                                # f_ignr.write("ESG files have been found at the following paths:\n")
                                f_ignr.write(str(link['href']) + '\n')
                                f_ignr.close()
                            continue
                        # else:



                        pdf_dir = os.path.join(page_dir, dict_str.upper() + '_files')
                        if not os.path.exists(pdf_dir):
                            os.makedirs(pdf_dir)

                        # if link.contents[0] != '':
                        if link.text != '':

                            # file_descr = ''.join(e for e in link.contents[0] if e.isalnum())
                            file_descr = link.text
                        else:
                            i += 1
                            file_descr = str(i)
                        # f_name  = string_of_interest + '_' + str(url_domain) + '_' + str(i)

                        for soup_link in soup.select('link[rel*=canonical]'):
                            print(soup_link['href'])
                            base_url = soup_link['href']
                            url_domain = get_domain(urlparse(base_url).netloc)
                            #     # (urlparse(base_url).netloc).split(".")[1]
                            url_domain_full = urlparse(base_url).scheme + '://'  + urlparse(base_url).netloc

                            if (link['href'].startswith('/')):  # case when webpage is dynamically build in html#
                                if ('www.' in link['href']):
                                    print('check here please''{}\n'.format(link['href']))
                                    initial_url_full = ''
                                else:
                                    initial_url_full =  url_domain_full + str(link['href'])
                        cnt += 1
                        f_descr  = dict_str.upper() + '_' + str(url_domain) + '_' + str(cnt)       #new28

                        f_downl_status = download_pdf(link, f_descr, pdf_dir, url_domain_full)
                        # f_downl_status = download_zip(link, f_descr, pdf_dir) #, url_domain_full)
                        with open(os.path.join(ot, extracted_files), 'a', encoding='utf-8') as f_esg:
                            # f_esg.write(pdf_dir + '\t' + f_descr +  '\t' + f_downl_status + '\n')
                            # f_esg.write(base_url + '\t' + initial_url_full + '\t' + f_descr + '\t' + f_downl_status + '\t' + os.path.join(pic_type,pic_id) + '\n')
                            f_esg.write(base_url + '\t' + initial_url_full + '\t' + f_descr + '\t' + f_downl_status +  '\n')
                            f_esg.close()

                        initial_url_full = url_domain_full = url_domain = base_url = ''
                ################################################        12.01.2023 <<
                ####################################################################################

                # >>> 24.04.2023 >>>
                # accepted_links, discarded_links = filter_urls_2(
                #     base_url,
                #     [
                #         a.get('href')
                #         for a in soup.findAll('a')
                #     ]
                # )
                #
                # to_visit = to_visit + list(accepted_links - set(to_visit) - already_visited)

                ################################################
                #
                # visited_counter +=1
                # if(visited_counter >= max_pages_to_visit):
                #     # print('Max pages to visit limit WAS exceeded. Download of site {} stopped'.format(clean_url))
                #     print(f'Max pages to visit limit WAS exceeded. Download of site {clean_url} stopped')
                #     break
                # <<<<<<< 24.04.2023 <<<<<<<



unset_keepawake()