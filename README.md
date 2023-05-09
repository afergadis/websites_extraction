# Life Expectancy Estimation

Machine Learning challenge: #4

## Description

Analyzing social, economic and health status of several countries, and trying to estimate the life expectancy using this [dataset](https://www.kaggle.com/datasets/lashagoch/life-expectancy-who-updated?select=Life-Expectancy-Data-Updated.csv) from Kaggle collected by the World Health Organization.

## Install

Run the command

`pip install -r requirements.txt`

## Requirements

- Jupyter Notebooks
- Numpy
- Pandas
- Matplotlib
- Seaborn
- Scipy
- Scikit-learn

## Usage

Within the `notebooks` folder, there are two notebooks, they should be run in the following order:

1. `1_visulizing.ipynb`: Exploratory data analysis, cleaning and visualization.
2. `2_modeling.ipynb`: Feature engineering, preprocessing, ML Modeling and evaluation

I have put the `life_expectancy.csv` file containing the dataset in the `data` folder, and put it in the `.gitignore` file to avoid uploading it to GitHub, however, you can download it from the Kaggle link above.
