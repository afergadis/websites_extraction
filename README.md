# Websites extraction
In this repository there are files are part of the Thesis: <br>
[Automating the data acquisition of Businesses and their actions regarding environmental sustainability: The Energy Industry in Greece](content_for_user/Thesis_DI_CBorovilou.pdf)



Parts of the data engineering process that is described in the thesis file, written in Python, that all together consist the pipeline of the procedure shown in the image below:<br><br>
![Pipeline](content_for_user/pipeline.jpg)


## Pipeline
The steps are the following:
1. Extract a **list** with domains of all the Greek businesses that belong to the energy factor (result: [data_from_dnb](content_for_user/data_from_dnb.json)  (source www.dnb.com) )
2. Use a crawler algorithm that will navigate to the URLs in our [file](content_for_user/data_from_dnb.json) as well as all the subdomains that are called on these web pages & will extract their content (HTML files). Moreover it will extract document files (.pdf) refering to ESG factors using a _customizing_ dictionary of words as an content-filter method [ESG Dictionary](content_for_user/esg_dict.csv)
 (script related &rightarrow; [crawler_pdfs.py](venv_tst/Scripts/Crawler_pdfs.py))
3. Use a boiler plate removal algorithm that removes HTML syntax and keep only the text (not publicly available in the repository)
4. Evaluate web-scrapping process defining & calculating specific metrics. Filter accordingly also the content (text) that was extracted in order to distill the action of greek businesses regarding environmental responsability. Export the results in a csv (script related &rightarrow; [meta_cleaning_2.py](venv/Scripts/meta_cleaning_2.py) )

* There is also available a script of the crawler designed to read local HTML files (instead of URLs as decribed in step 2), in order to extract ESG pdf files. (script related &rightarrow; [Crawler_pdfs_from_html_files.py](venv_tst/Scripts/Crawler_pdfs_from_html_files.py))

## How to run
- Crawler_pdfs_from_html_files.py<br>
   In order to run the script, user needs to give as input 2 parameters: 
    1. The local input path that contains folders per website under which there are stored all HTML files (Input parameter parameter: _--inpath_) <br> (e.g. --inpath C:\Users\userXXX\inp) <br> 
    2. The local output path that user desires to store the results (ESG/Sustainability pdf files) per website  (Input parameter parameter: _--out_dir_) <br> (e.g. --out_dir C:\Users\userXXX\out) <br> 
   
   Thus the command at terminal will be similar to: `C:\Users\userXXX\...\python.exe C:\Users\userXXX\...\Crawler_pdfs_from_html_files.py --inpath C:\Users\userXXX\D..\inp --out_dir C:\Users\userXXX\..\out`
   
   Optional feature:
After first run a (default) dictionary for words of interest ([ESG Dictionary](content_for_user/esg_dict.csv)) is generated at input forlder so that user can maintain it. 

- Crawler_pdfs.py <br>
  Similarly, in order to run the script, user needs to give as input 2 parameters: 
    1. The local input path for [json file](content_for_user/data_from_dnb.json) that contains the websites under which there are stored all HTML files (Input parameter parameter: _--inpath_) <br> (e.g. --inpath C:\Users\userXXX\inp\data_from_dnb.json) <br> 
    2. The local output path that user desires to store the results (ESG/Sustainability pdf files) per website  (Input parameter parameter: _--out_dir_) <br> (e.g. --out_dir C:\Users\userXXX\out) <br>
    <br>
    Thus the command at terminal will be similar to: `C:\Users\userXXX\...\python.exe C:\Users\userXXX\...\Crawler_pdfs.py --inpath C:\Users\userXXX\...\inp\data_from_dnb.json --out_dir C:\Users\userXXX\...\out`


## Install

Run the command

`pip install -r requirements.txt`
<!-- 
## Requirements

- Jupyter Notebooks
- Numpy
- Pandas
- Matplotlib
- Seaborn
- Scipy
- Scikit-learn -->

<!-- ## Usage

Within the `notebooks` folder, there are two notebooks, they should be run in the following order:

1. `1_visulizing.ipynb`: Exploratory data analysis, cleaning and visualization.
2. `2_modeling.ipynb`: Feature engineering, preprocessing, ML Modeling and evaluation

I have put the `life_expectancy.csv` file containing the dataset in the `data` folder, and put it in the `.gitignore` file to avoid uploading it to GitHub, however, you can download it from the Kaggle link above. -->
