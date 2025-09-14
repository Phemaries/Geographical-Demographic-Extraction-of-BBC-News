
# # https://newsapi.org/v2/top-headlines?country=us&category=business&apiKey=API_KEY

# # https://www.kaggle.com/datasets/gpreda/bbc-news/data

# # https://www.kaggle.com/datasets/oumaymael/aljazeera-news-dataset?select=economy.csv

# # https://huggingface.co/typeform/distilbert-base-uncased-mnli

# # https://www.figma.com/colors/charcoal/

# # https://www.geeksforgeeks.org/python/python-plotly-tutorial/


# from dotenv import load_dotenv
# import os
# import requests
# import json

# load_dotenv()


# API_KEY = os.getenv('API_KEY')

# categories = ['business', 'technology']

# for cat in categories:

#     url = f'https://newsapi.org/v2/top-headlines?country=us&from=2025-07-30&pageSize=100&category={cat}&apiKey={API_KEY}'

#     response = requests.get(url)

#     data = response.json()

# # print (response.json())

# with open('export.json', 'w') as f:
#         json.dump(data, f)


# # import requests

# # API_KEY = "your_api_key_here"
# # all_articles = []

# # for page in range(1, 6):  # try 5 pages = up to 500 results
# #     url = f"https://newsapi.org/v2/everything?q=business&from=2025-07-30&pageSize=100&page={page}&apiKey={API_KEY}"
# #     response = requests.get(url).json()
    
# #     if response.get("status") != "ok" or not response.get("articles"):
# #         break  # no more results
    
# #     all_articles.extend(response["articles"])

# # print(f"Collected {len(all_articles)} articles")
