# 🌍 Multi-Stage Pipeline for BBC News (2022–2024): Geographical & Demographic Extraction, Zero-Shot Category Prediction, and Interactive Streamlit Dashboards

This project provides a **multi-stage pipeline** to process raw BBC news articles, extract geographical and demographic entities, and visualize insights through interactive **Streamlit dashboards**. The dataset utilized for this project can be found on Kaggle. [Download here](https://www.kaggle.com/datasets/gpreda/bbc-news/data). The dataset (~40K unique values) consist of articles and titles published from **March, 2022 to December, 2024.** 

The workflow includes:  
- **Data Preparation (Stage 1):** Extracting and standardizing countries, cities, and nationalities from raw BBC articles.  
- **Exploratory Dashboard (Stage 2):** Interactive maps and charts exploring mentions of countries, cities, and identities in news coverage.  
- **Sentiment & Category Dashboard (Stage 3):** Visualization of predicted news categories (using `Hugging Face zero-shot classification`) with geographical and demographic associations.  
- **Streamlit Navigation (Stage 4):** A unified navigation interface to switch between dashboards.  

---

## 📂 Project Structure  

```bash
NEWS_PROJECT/
│
├── app/                           # Application code
│   ├── .streamlit/                # Streamlit config folder
│   ├── exploration.py             # Geographical analysis dashboard
│   ├── newsapi.py                 # NewsAPI integration script
│   ├── prediction.py              # Prediction & category dashboard
│   └── streamlit_app.py           # Unified Streamlit entrypoint
│
├── dataset/                       # Dataset folder
│   ├── bbc_news.csv               # Raw BBC dataset
│   ├── new_data                   # Intermediate processed data
│   ├── new_data.csv               # Final processed dataset
│   ├── pred_streamlit.csv         # Prediction dataset for dashboard
│   ├── prediction.csv             # Prediction results export
│
├── distilbert-mnli-model/         # Pretrained DistilBERT model folder
├── images/                       # Images folder
├── newsenv/                       # Virtual environment
├── distilbert-mnli-model.zip      # Zipped model archive
├── newplot.png                    # Visualization plot
├── newsapi_exploration.ipynb      # Jupyter notebook for NewsAPI exploration
├── newsapi_prediction.ipynb       # Jupyter notebook for prediction workflow
├── newsapi.ipynb                  # General NewsAPI notebook
├── README.md                      # Project documentation
└── requirements.txt               # dependencies
```

&nbsp;

**Clone the Repositiory**
``` bash
git clone https://github.com/Phemaries/Geographical-Demographic-Extraction-of-BBC-News.git
cd <folder>
```
**Create & activate virtual environment**
``` bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

**Install dependencies**
``` bash
pip install -r requirements.txt
```

&nbsp;

### Stage 1 – Data Preprocessing

*Transforms raw BBC news into a structured dataset with countries, cities, and nationalities"*

***Input:*** bbc_news.csv => ***Output:*** new_data.csv 


```
python newsapi.py
```

*Raw Preprocessing and Exploration => newsapi.ipynb + newsapi_exploration.ipynb*

This explores the intersection of textual data analysis and geographical representation using a BBC News dataset. News articles often mention countries, cities, nationalities, and ideologies, which can be systematically extracted to study global narratives and sentiment distribution.

* The workflow begins with data cleaning and normalization, addressing inconsistencies in country names, nationalities, and city references (e.g., “USA” → “United States,” “Russians” → “Russian”). After preprocessing, the dataset is visualized through interactive geographical maps and bar charts. These visualizations allow for an examination of:

* Global coverage of news mentions across countries.

* City-level granularity, highlighting urban centers associated with particular nations.

* Identity linkages, where nationalities and ideologies are connected to specific countries and cities.

By integrating tools such as pandas, geopandas, plotly, and streamlit, the project provides an interactive platform that supports both exploratory data analysis and geo-spatial storytelling. This approach enables users to move beyond raw text, uncovering patterns in how global events are framed across geographical and cultural dimensions.


&nbsp;

### Stage 2 – Geographical Analysis Dashboard

*Interactive exploration of BBC coverage across countries, cities, and identities.*
```
streamlit run exploration.py
```

**=> Key Features and Functionality:**

🌍 Choropleth world map of coverage per country

📍 City-level geo-scatter plots

🏳️ Analysis of nationalities/ideologies"""


=> **Data Loading & Preprocessing**  
   * Loads the dataset: `new_data.csv`.  
   * Cleans up and standardizes:
     * `nationality` field (e.g., replacing "MUSLIM" → "ISLAM").  
     * City names (`"MEXICO"` → `"MEXICO CITY"`, `"CARACAS,"` → `"CARACAS"`).  

=> **Dashboard Structure**  
   - Built entirely with **Streamlit**.  
   - Divided into **five analysis sections**.  
   - Each section includes an interactive dropdown for country selection.  

=> **Analysis Modules**

   - **Global News Coverage (Choropleth)**  
     - A choropleth map shows **how frequently countries are mentioned**.  
     - Uses `geonamescache` + ISO3 codes for accurate mapping.  

   - **Cities Mentioned within a Country**  
     - Geo-scatter plot showing **cities located inside the chosen country**.  
     - Bubble size reflects number of mentions.  

   - **Global Cities Associated with a Country**  
     - Geo-scatter plot of **cities worldwide** that are frequently mentioned **alongside the chosen country**.  

   - **Nationality/Ideology Mentions per Country**  
     - Horizontal bar chart showing **top nationalities/ideologies** associated with the selected country.  

   - **Nationality–City Relationships**  
     - Bubble chart connecting **cities** and **nationalities/ideologies** within a country.  

=> **Visualization Tools**  
   - `plotly.express` → interactive maps, bar charts, and bubble charts.  
   - `geonamescache` → country/city coordinates & ISO mapping.  
   - `pandas` → data aggregation and grouping.  

***Geo-Scatter Plots of News Coverage Globally***

![City Countries Mentioned with Others](/images/globally_news_coverage.png)

***Other Geo-Scatter Plots***

![City Countries Mentioned with Others](/images/nationalities_alongcountry.png)

&nbsp;

### Stage 3 – Sentiment & Category Dashboard

`*Sentiment Analysis with Hugging Face*`

`newsapi_prediction.ipynb`
This script performs **zero-shot text classification** on news data using Hugging Face’s `transformers` library.  
It processes a dataset of text news records, assigns predicted categories, and explores how these categories relate to **countries, cities, and nationalities** mentioned in the dataset.)

***Global Geo-Scatter Plots according to Category***

![Global Prevalence](/images/global_prevalence_label.png)
&nbsp;

**=> Key Steps & Functionality**

=> **Data Preparation**  
   - Loads raw news text data from `dataset/new_data.csv`.  
   - Removes duplicate text entries.  
   - Cleans and standardizes categorical fields (e.g., nationalities → stripping plural forms).  

=> **Prediction with Hugging Face**  
   - Uses a **DistilBERT (MNLI) zero-shot classifier**.  
   - Candidate labels include:  
     `["sports", "politics", "business", "science", "climate", "weather", "entertainment", "travel", "crime", "war", "technology", "health", "education", "accidents"]`  
   - Runs classification in **batches** (default size: 32) for efficient processing.  
   - Saves predictions to `dataset/prediction.csv`.  

=> **Merging Predictions with Metadata**  
   - Combines original dataset with new predicted categories.  
   - Cleans and standardizes names (countries, cities, nationalities).  
   - Creates an enriched dataset saved as `dataset/pred_streamlit.csv` for later visualization.  

=> **Exploratory Analysis & Visualizations**  
   - **Category Distribution:** Overall frequency of predicted labels.  
   - **Country-Level Analysis (`country_labels`)** → News categories most associated with a given country.  
   - **City-Level Analysis (`city_labels`)** → News categories most associated with a given city.  
   - **Nationality-Level Analysis (`nat_labels`)** → News categories tied to a nationality.  
   - **Global Spread of Categories (`label_country`)** → Choropleth world map showing prevalence of a given label across countries.  

=> **Visualization Libraries Used**  
   - `matplotlib` → general plots.  
   - `plotly.express` → interactive bar charts & choropleths.  
   - `geopandas`, `geonamescache`, `shapely` → geographic data handling.  


#### Usage
- Adjust **batch size** depending on hardware (larger if GPU is available).  
- Replace `"./distilbert-mnli-model"` with a Hugging Face model path if needed.  
- Example calls:  
  ```python
  country_labels('Italy')
  city_labels('Gaza')
  nat_labels('Chinese')
  label_country('Technology')


*Fine-tune model to your taste. ~10K unique values were categorized. If running on GPU, increase the batch size and use ~40K values instead*
```
***Load classifier***
device = 0 if torch.cuda.is_available() else -1
classifier = pipeline(
    "zero-shot-classification",
    model="./distilbert-mnli-model",
    tokenizer="./distilbert-mnli-model",
    device=device
)

candidate_labels = ["sports", "politics", "business", "science", "climate", "weather", "entertainment", "travel", "crime", "war", "technology", "health", "education", "accidents"]

Batch function
def classify_batch(texts, labels):
     results = classifier(texts, labels)
#     Results is a list of dicts when you pass multiple texts
#     return [r["labels"][0] for r in results]

# # Batch process DataFrame
# batch_size = 32   # increase to 64/128 if you have GPU
# predictions = []

# for i in range(0, len(df_pred), batch_size):
#     batch_texts = df_pred["text"].iloc[i:i+batch_size].tolist()
#     preds = classify_batch(batch_texts, candidate_labels)
#     predictions.extend(preds)
    
#     # (Optional) progress
#     print(f"Processed {i+len(batch_texts)} / {len(df_pred)}")

# # Add predictions back
# df_pred["predicted_label"] = predictions
```

****Visualization of predicted categories and their geographical patterns****

```bash
streamlit run prediction.py
```
***What's common to a Particular Country?***

![Country Labels](/images/country_prevalence.png)
&nbsp;
***What's common to a Particular City?***

![City Labels](/images/city_prevalence.png)
&nbsp;

***What's common to a Particular Identity/Ideology?***

![Country Labels](/images/identity_prevalence.png)
&nbsp;


**=> Key Features and Functionality:**

* 🌍 Category prevalence choropleth maps

* 📊 Category distribution histograms

* 🗺️ Country/City/Nationality vs. Category relationships """

&nbsp;

 => **Data Loading & Preprocessing**
   * Reads enriched predictions dataset (`pred_streamlit.csv`).  
   * Standardizes text fields (capitalization for consistency).  

=> **Dashboard Structure**  
   - Built with **Streamlit** for interactive exploration.  
   - Responsive layout with multiple analysis sections.  

=> **Visual Analysis Modules**  

   - **Global Category Prevalence (`label_country`)**  
     - Choropleth map showing worldwide distribution of a selected news category.  
     - Uses `plotly.express` with ISO3 country codes from `geonamescache`.  

   - **Overall Category Distribution (`category_label`)**  
     - Interactive bar chart of category frequencies across the dataset.  

   - **Country-Specific Analysis (`country_labels`)**  
     - Displays which news categories are most associated with a selected country.  

   - **City-Specific Analysis (`city_labels`)**  
     - Bar chart of categories tied to a selected city.  

   - **Nationality-Specific Analysis (`nat_labels`)**  
     - Bar chart of categories connected to a selected nationality/ideology.  

=> **Visualization Libraries Used**  
   - `plotly.express` → interactive bar charts & choropleths.  
   - `matplotlib` → general plots (minimal usage here).  
   - `geonamescache`, `geopandas`, `shapely` → geographic data management.  


#### Usage
- Run the dashboard with:  
  ```bash
  streamlit run your_script.py
  ```

**Caveat**
* This dataset is not up to date has it is limited within 3 year span (2022 - 2024). A longer span of dataset may generate better insight and rich data exploration

* For prediction labelling, 10,000 unique text values were utilized, instead of ~40K unique values used for exploration (Geographical Analysis Dashboard) 