import requests
import json
import pandas as pd
import csv
import objectpath
import time

from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


driver_service_stats = Service(ChromeDriverManager().install())
driver_service_scores = Service(ChromeDriverManager().install())
stats_browser = webdriver.Chrome(service=driver_service_stats)
scores_browser = webdriver.Chrome(service=driver_service_scores)

url_stats = "https://www.timeshighereducation.com/world-university-rankings/2024/world-ranking#!/length/-1/sort_by/rank/sort_order/asc/cols/stats"
url_scores = "https://www.timeshighereducation.com/world-university-rankings/2024/world-ranking#!/length/-1/sort_by/rank/sort_order/asc/cols/scores"


# use the webdriver to request the ranking webpage
stats_browser.get(url_stats)
time.sleep(5)

# collect the webpage HTML after its loading
stats_page_html = stats_browser.page_source

# parse the HTML using BeautifulSoup
stats_page_soup = soup(stats_page_html, 'html.parser')

# collect HTML objects 
rank_obj = stats_page_soup.findAll("td", {"class":"rank sorting_1 sorting_2"})
names_obj = stats_page_soup.findAll("td", {"class":"name namesearch"})
stats_number_students_obj = stats_page_soup.findAll("td", {"class":"stats stats_number_students"})
stats_student_staff_ratio_obj = stats_page_soup.findAll("td", {"class":"stats stats_student_staff_ratio"})
stats_pc_intl_students_obj = stats_page_soup.findAll("td", {"class":"stats stats_pc_intl_students"})
stats_female_male_ratio_obj = stats_page_soup.findAll("td", {"class":"stats stats_female_male_ratio"})

# close the browser
stats_browser.quit() 


# use the webdriver to request the scores webpage
scores_browser.get(url_scores)
time.sleep(5)

# collect the webpage HTML after its loading
scores_page_html = scores_browser.page_source
scores_page_soup = soup(scores_page_html, 'html.parser')

# parse the HTML using BeautifulSoup
overall_score_obj = scores_page_soup.findAll("td", {"class":"scores overall-score"})
teaching_score_obj = scores_page_soup.findAll("td", {"class":"scores teaching-score"})
research_score_obj = scores_page_soup.findAll("td", {"class":"scores research-score"})
citations_score_obj = scores_page_soup.findAll("td", {"class":"scores citations-score"})
industry_income_score_obj = scores_page_soup.findAll("td", {"class":"scores industry_income-score"})
international_outlook_score_obj = scores_page_soup.findAll("td", {"class":"scores international_outlook-score"})

# close the browser
scores_browser.quit() 

rank, names, number_students, student_staff_ratio, intl_students, female_male_ratio, web_address =  [], [], [], [], [], [], []
overall_score, teaching_score, research_score, citations_score, industry_income_score, international_outlook_score = [], [], [], [], [], []
for i in range(len(names_obj)):
    href = ""
    name = ""
    if names_obj[i].a is not None : 
        href = names_obj[i].a.get("href")
        name = names_obj[i].a.text.strip()
    web_address.append('https://www.timeshighereducation.com' + href)
    rank.append(rank_obj[i].text.strip())
    names.append(name)
    number_students.append(stats_number_students_obj[i].text.strip())
    student_staff_ratio.append(stats_student_staff_ratio_obj[i].text.strip())
    intl_students.append(stats_pc_intl_students_obj[i].text.strip())
    female_male_ratio.append(stats_female_male_ratio_obj[i].text[:2].strip())
    
    overall_score.append(overall_score_obj[i].text.strip())
    teaching_score.append(teaching_score_obj[i].text.strip())
    research_score.append(research_score_obj[i].text.strip())
    citations_score.append(citations_score_obj[i].text.strip())
    industry_income_score.append(industry_income_score_obj[i].text.strip())
    international_outlook_score.append(international_outlook_score_obj[i].text.strip())
    
    
full_address_list, streetAddress_list, addressLocality_list, addressRegion_list, postalCode_list, addressCountry_list  = [], [], [], [], [], []
for web in web_address:
    try:
        page = urlopen(web)
        page_html = soup(page, 'html.parser')
        location = page_html.findAll('script', {'type':"application/ld+json"})
        jt = json.loads(location[0].text)
        json_tree = objectpath.Tree(jt)

        street_list = list(json_tree.execute('$..streetAddress'))
        streetAddress_list.append(street_list[0] if street_list is not None and len(street_list) > 0 else '')

        add_locality_list = list(json_tree.execute('$..addressLocality'))
        addressLocality_list.append(add_locality_list[0] if add_locality_list is not None and len(add_locality_list) > 0 else '')

        region_list = list(json_tree.execute('$..addressRegion'))
        addressRegion_list.append(region_list[0] if region_list is not None and len(region_list) > 0 else '')

        postal_list = list(json_tree.execute('$..postalCode'))
        postalCode_list.append(postal_list[0] if postal_list is not None and len(postal_list) > 0 else '')

        country_list = list(json_tree.execute('$..addressCountry'))
        addressCountry_list.append(country_list[0] if country_list is not None and len(country_list) > 0 else '')

        full_add_list = page_html.findAll('div', {
            'class': "institution-info__contact-detail institution-info__contact-detail--address"})

        ff = full_add_list[0].text.strip() if full_add_list is not None and len(full_add_list) > 0 else ''
        full_add_list.append(ff)

        print(f'{len(full_address_list)} out of {len(web_address)}: {ff}')

    except Exception as e:
        streetAddress_list.append('')
        addressLocality_list.append('')
        addressRegion_list.append('')
        postalCode_list.append('')
        addressCountry_list.append('')
        full_address_list.append('')
        print(f'Error fetching address for {web}: {e}')
        
    
df = pd.DataFrame({
    'rank' : rank,
    'name' : names,
    'number_students' : number_students,
    'student_staff_ratio' : student_staff_ratio,
    'intl_students' : intl_students,
    'female_male_ratio' : female_male_ratio,
    'overall_score' : overall_score,
    'teaching_score' : teaching_score,
    'research_score' : research_score,
    'citations_score' : citations_score,
    'industry_income_score' : industry_income_score,
    'international_outlook_score' : international_outlook_score,
    'address' : full_address_list, 
    'street_address' : streetAddress_list,
    'locality_address' : addressLocality_list,
    'region_address' : addressRegion_list,
    'postcode_address' : postalCode_list,
    'country_address' : addressCountry_list
})


df['intl_students'] = df['intl_students'].str.replace(pat='%', repl='')
df['rank'] = df['rank'].str.replace(pat='\–\d*|\+', repl='', regex=True)
df['overall_score'] = df['overall_score'].str.replace(pat='.*\–', repl='', regex=True)
df['number_students'] = df['number_students'].str.replace(pat=',', repl='', regex=True)
df = df.replace('n/a*', pd.NA, regex=True)


df.to_csv('world_university_ranking_2024.csv', encoding='utf-8', index=False)









