import requests
from bs4 import BeautifulSoup

url = 'https://www.10000recipe.com/recipe/7038182'

response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.select_one('#contents_area_full > div.view2_summary.st3 > h3')
    print(title.get_text())
else : 
    print(response.status_code)
