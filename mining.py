#요리 이름, 재료, 레시피, 인분, 조리시간
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

baseUrl = 'https://www.10000recipe.com'

def PageCrawler(Url):
	url = baseUrl + Url

	page = requests.get(url)
	recipe_source = [] #재료
	recipe_step = [] #레시피 순서
	recipe_title = ""
	recipe_num = ""
	recipe_time = ""

	if page.status_code == 200:
		soup= BeautifulSoup(page.content, 'html.parser')
	
		#이름 recipe_title
		#인분 recipe_num
		#조리시간 recipe_time

		try:
			title = soup.select_one('#contents_area_full > div.view2_summary.st3 > h3')
			recipe_title = title.get_text()
		except(AttributeError):
			return

		try:
			num = soup.select_one('#contents_area_full > div.view2_summary.st3 > div.view2_summary_info > span.view2_summary_info1')
			recipe_num = num.get_text()
		except(AttributeError):
			print("it is not have num")

		try:
			time = soup.select_one('#contents_area_full > div.view2_summary.st3 > div.view2_summary_info > span.view2_summary_info2')
			recipe_time = time.get_text()

		except(AttributeError):
			print("it is not have time")

		#재료
		try:
			ingredient_tags = soup.select('#divConfirmedMaterialArea > ul > li')  # 재료 목록 선택

			for ingredient in ingredient_tags:
				name_tag = ingredient.find('a')  # <a> 태그에서 재료 이름 추출
				if name_tag:
					recipe_source.append(name_tag.get_text().replace('\n','').replace(' ',''))
			
		
		except(AttributeError):
			return	
		
		# 조리 순서
		try:
			step_divs = soup.select('#obx_recipe_step_start > div[id^="stepDiv"]')  # 조리 단계 선택

			for step in step_divs:
				for p in step.find_all('p'):
					p.extract()

				recipe_step.append(step.get_text(strip=True))
	

		except(AttributeError):
			return
		
	else:
		print(page.status_code)
	
	
	recipe_all = [recipe_title, recipe_source, recipe_step, recipe_num, recipe_time]
	return (recipe_all)

def SaveData(rlist):
	data = {
		'title': [],
		'source': [],
		'step': [],
		'num': [],
		'time': []
	}

	for recipe in rlist:
		title, source, step, num, time = recipe
		data['title'].append(title if title is not None else '')
		data['source'].append(', '.join(source) if source is not None else '')  # 리스트를 문자열로 변환
		data['step'].append('; '.join(step) if step is not None else '')  # 리스트를 문자열로 변환
		data['num'].append(num if num is not None else 0)  # 기본값 0
		data['time'].append(time if time is not None else '')  # 빈 문자열

	df = pd.DataFrame(data)

	df.to_csv('recipes.csv', index=False, encoding='utf-8-sig')

def GetData(size):
	recipes = []

	for i in range(1,size+1):
		url = f'https://www.10000recipe.com/recipe/list.html?order=reco&page={i}'  

		page = requests.get(url) 
		
		if page.status_code == 200:
			soup = BeautifulSoup(page.content, 'html.parser')

			try:
				step_divs = soup.select('#contents_area_full > ul > ul > li')
				
				for step in step_divs:
					link = step.find('div',{'class':'common_sp_thumb'}).find('a')['href']
					re = PageCrawler(link)
					
					if re is not None:
						recipes.append(re)


			except(AttributeError):
				print("error")

		else:
			break
	

	SaveData(recipes)


page = 100000

GetData(2)




