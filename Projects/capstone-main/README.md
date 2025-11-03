# Capstone Project - Exploring connections between Internet and Economy
This project, titled "Exploring the Internet’s Role in Economic Change", is part of a undergraduate capstone project for the Bachelor in Computational Social Science at the University of Amsterdam. Working in collaboration with RIPE NCC as a project partner, this study aims to discover potential links or connections between internet infrastructure and economy across 76 countries.

## Objectives
- Explore potential links between Internet and Economic indicators at international level
- Generate meaningful and valuable insights from qualitative and quantitative data analysis
- Develop an interactive, data-driven platform that shows relevant information regarding internet infrastructure and economic mindicators


## Table of Contents
- [Capstone Project - Exploring connections between Internet and Economy](#capstone-project---exploring-connections-between-internet-and-economy)
  - [Objectives](#objectives)
  - [Table of Contents](#table-of-contents)
  - [Web Development](#web-development)
    - [Tech Stack](#tech-stack)
    - [Setup Instructions](#setup-instructions)
    - [Deployment](#deployment)
    - [Limitations](#limitations)
  - [Data Science](#data-science)
    - [Dataset Description and Sources](#dataset-description-and-sources)
    - [Important note: There are two main data files in this repository. The first, all\_data.json, contains the scaled data used for modeling. The second, website\_data.json, includes the unscaled data used on the website. This file has been renamed real\_values.json in the web development processing. All other JSON files created during notebook development have been excluded to avoid confusion, as they are not final versions.](#important-note-there-are-two-main-data-files-in-this-repository-the-first-all_datajson-contains-the-scaled-data-used-for-modeling-the-second-website_datajson-includes-the-unscaled-data-used-on-the-website-this-file-has-been-renamed-real_valuesjson-in-the-web-development-processing-all-other-json-files-created-during-notebook-development-have-been-excluded-to-avoid-confusion-as-they-are-notfinalversions)
    - [Data Cleaning (data-merging.ipynb)](#data-cleaning-data-mergingipynb)
    - [Indexing (economic\_index.ipynb \& economic\_index\_sorted.ipynb)](#indexing-economic_indexipynb--economic_index_sortedipynb)
    - [Machine Learning Models (logistic\_regression.ipynb \& randomforest.ipynb)](#machine-learning-models-logistic_regressionipynb--randomforestipynb)
    - [Limitations](#limitations-1)
  - [Authors and Acknowledgements](#authors-and-acknowledgements)


## Web Development

The web application provides an interactive platform for visualizing the Internet infrastructure and economy of 76 countries. Users can explore overall index scores and ranking, compare regions or analyze specific data for each country through it's profile.


### Tech Stack
- **Python**: Used for backend scripts, data processing, and logic for the website
- **Django**: Python framework used for developing website backend, manage routine and serve content
- **Node.js**: Supports frontend tools
- **Tailwind CSS**: Used for building consistent style and design on website
- **Javascript**: Used for interactive elements or features and data loading
- **Plotly.js**: Used to create the interactive Internet graphs and international map with index scores

### Setup Instructions
All key commands are available in the Makefile for convenience.

1. Navigate to web-dev directory.
   ```bash
   cd web-dev
   ```
2. Set up a Python virtual environment.
   ```
   python -m venv venv
   source venv/bin/activate #for macOS/Linux
   venv\Scripts\activate #for Windows
   ```
3. Install project dependencies (requirements.txt) and development dependencies if needed (Requirements_dev.txt).
    ```
    pip install -r requirements.txt
    pip install -r requirements_dev.txt
    ```
4. Start the Django development server.
   ```
   python manage.py runserver
   ```
### Deployment
The website is deployed on PythonAnywhere using a free-tier account. The deployment is configured to automatically pull updates from the project's GitHub repository when changes are pushed to the main branch. A CI/CD pipeline was included to enable the process where any pushed changes trigger the script and the PythonAnywhere bash is opened via an API. Once opened, the script runs the general setup commands to update installed libraries and pull latest changes.

Note: On PythonAnywhere's free tier, the platform requires manual reloading after pulling updates.

### Limitations
1. Static or Pre-Processed Data:
While the website dynamically loads its content from local datasets on each visit, the data itself is manually pre-processed and cleaned in advance. This means that any data updates require manual intervention before they are reflected on the platform.

2. Limited Mobile Performance:
The website implements responsive and accessible design principles, however, performance on mobile devices is limited. The visualizations rendered with Plotly.js impact load times and layout responsiveness on smaller screens, leading to a lower performance for mobile users.

## Data Science

### Dataset Description and Sources
The datasets used include a variety of available data regarding different internet metrics and economic indicators.

1. Internet Data

- General Internet Resources of Countries(RIPE NCC): https://stat.ripe.net/docs/02.data-api/country-resource-list.html ; https://stat.ripe.net/docs/02.data-api/country-resource-stats.html
- Internet Penetration Rate :https://data.worldbank.org/indicator/IT.NET.USER.ZS?end=2023&start=2023&view=map
- Internet Speed: https://datahub.io/@cheredia19/ookla-speedtest-global-index-fixed-broadband-2017-2024
- International Bandwidth Usage per Internet User: https://data360.worldbank.org/en/indicator/ITU_DH_INT_BAND_PER_INT_USR

2. Economic Data:
- Income Classification: https://datahelpdesk.worldbank.org/knowledgebase/articles/378834-how-does-the-world-bank-classify-countries

- GNI per capita: https://data.worldbank.org/indicator/NY.GNP.PCAP.CD ; https://data.un.org/Data.aspx?q=gni+per+capita&d=SNAAMA&f=grID%3a103%3bcurrID%3aUSD%3bpcFlag%3a1
- Foreign Direct Investment: https://data.worldbank.org/indicator/BN.KLT.DINV.CD
- Labor Force Participation Rate: https://data.worldbank.org/indicator/SL.TLF.ACTI.ZS
- Unemployment Rate: https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS

Supplementary Economic Data: https://www.estadistica.ad/portal/apps/sites/#/estadistica-ca/; https://betadata.imf.org/en/Data-Explorer?datasetUrn=IMF.STA:LS(9.0.0)&INDICATOR=U
The larger raw data used in this project can be found here: https://amsuni-my.sharepoint.com/:f:/g/personal/maja_kubara_student_uva_nl/EqtBowOq4PhEjkbG4fhc-rsBW2PEllckobDFsptJciVUug?e=ryTA6m

### Important note: There are two main data files in this repository. The first, all_data.json, contains the scaled data used for modeling. The second, website_data.json, includes the unscaled data used on the website. This file has been renamed real_values.json in the web development processing. All other JSON files created during notebook development have been excluded to avoid confusion, as they are not final versions.

### Data Cleaning (data-merging.ipynb)
1. Data from public sources was cleaned to fit with RIPE NCC region criteria.
2. Granularity of data was changed to be yearly.
3. Merging between all datasets (RIPE data, speed, bandwidth, economic features, & economic index) based on columns 'country' and 'year'.
4. Data was both kept with missing values and imputed in order to try both versions when modelling.
5. Final file used to store data is named: 'all_data.json'

### Indexing (economic_index.ipynb & economic_index_sorted.ipynb)
Indexing was done through normalizing and weighting important features. An economic and internet index was created.

### Machine Learning Models (logistic_regression.ipynb & randomforest.ipynb)
To create and run the machine learning models various libraries were implemented. Inclusing pandas, sklearn, statsmodels, seaborn, matplotlib, and numpy.

1. Logistic Regression (Run all cells in notebook)
- Defining X and Y. Where X is internet features and Y (the target variable) is the encoded income group.
- Train, test, split logistic regression model.
- Evaluate the model using precision, recall, f1-score, support, and ROC CURVE.
- Look into which features influence classification of income classes the most through analyzing coefficients.

2. Random forest for regression and classification (Run all cells in notebook)
- Define X and Y. X being various internet metrices and Y being the GNI economic index.
- First random forest regressor is run.
- Feature importance is analyzed throughout to evaluate which variables have more of an influence on the model results.
- Logarithmic transformation is done to better fit the data to the model.
- Various features are adjusted to understand when the model performs best.

- Classification is executed in a similar way. Classification models do better with the dataset. Hence, the classifiaction model performs better than the regressor.

### Limitations
Data needs to be manually cleaned and updated as it contains publicly available data collected yearly. The regression models do not score as well as the classification models most probably due to constraints in the dataset size.

## Authors and Acknowledgements
The authors of this repository include the student team for this capstone project: Maria Baba, Paula Biazik, Maja Kubara, Mika Shaham, Alyssa Telescu and Beatris Tretiacov.
