import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time

# Import list of companies
company_list = pd.read_csv("wilshire5000_gd.csv")

# Store list of ratings to build urls
rating_categories = ['overallRating', 'cultureAndValues', 'workLife', 'seniorManagement', 'compAndBenefits',
		     'careerOpportunities', 'Recommend', 'CeoRating', 'BizOutlook']

# Function that takes a base url and rating category to generate a url and scrape high-chart
def scrape_glass_chart(base_url, company):

	# Open browser and scrape company name 
	driver = webdriver.Chrome()
	url = base_url + "#trends-overallRating"
	driver.get(url)
	time.sleep(3.5)
	company_title = driver.find_element_by_css_selector('h1').text
	company_title = company_title.replace(" Ratings and Trends", "")

	# Check if your scraping the right company
	if company_title.lower() in company.lower():
	
		try:
		   # Dataframe to store all ratings for an individual company
		   df = []
	
      		   # Loop through rating categories to scrape all values
		   for rating in rating_categories:
			   
  			   actions = webdriver.ActionChains(driver)

			   # Handle different structures	
			   if rating not in ['Recommend', 'CeoRating', 'BizOutlook']:
			   	   
				na_test = driver.find_element_by_css_selector('[data-category=\"' + rating + '\"]').find_element_by_class_name('ratingNum').text
				actions.move_to_element(driver.find_element_by_css_selector('[data-category=\"' + rating + '\"]'))
			   else:
				na_test = driver.find_element_by_id(rating).find_element_by_css_selector('text').text
				actions.move_to_element(driver.find_element_by_id(rating))
			   # Test if NA 
			   if na_test != 'N/A':
				   
			      actions.click().perform()
	  		      
                             # Instruct this to wait until active chart updates
                              while True:
                                if rating not in ['Recommend', 'CeoRating', 'BizOutlook']:
                                        update_check = driver.find_element_by_class_name('ui-accordion-header-active').find_element_by_css_selector('label').text
                                        if update_check == 'Comp & Benefits': 
                                                update_check = 'Compensation and Benefits'
                                else:
                                        update_check = driver.find_element_by_class_name('active').find_element_by_css_selector('span').text
        
                                label_check = driver.find_element_by_id('DesktopCharts').find_element_by_css_selector('label').text
                                if update_check.lower() in label_check.lower():
                                   break 

			      chart_number = driver.find_element_by_id('DesktopTrendChart').get_attribute('data-highcharts-chart')
			      chart_data = driver.execute_script('return Highcharts.charts[' + chart_number + '].series[0].options.data')
	
			      # Lists for dismembering the scraped data structure
			      dates = []
			      ratings = []
	
			      # Remove data from nested lists 
			      for item in chart_data:
			         dates.append(item[0])
				 ratings.append(item[1])

			      # Store data in individual dataframe
			      rating_df = pd.DataFrame({
					   "date": dates,
					   "rating": ratings
				      })

			         # Add category and append to main company df
			      rating_df['rating_category'] = rating
			      df.append(rating_df)
			      print("Scraped " + rating + " for " + company)
			   else:
			      print("Value for this category is NA: " + rating) 
	
		   # Concat into 1 df and add company name
		   company_df = pd.concat(df)
		   company_df['company_name'] = company	
		   driver.close()
		   return(company_df)

		except:
		   print("No rating trend data for: " + company)
	else:
	   print("Can't find company")
	
# Function that takes company short name and searchs for glassdoor url
def find_url(company_name):
	
	# Format company name for search 
	company_name = company_name.replace(" ", "+")	
		
	# Scrape url
	goog_search = "https://www.google.com/search?q=glassdoor+reviews+"
	query = requests.get(goog_search + company_name)
	soup = BeautifulSoup(query.text, 'html.parser')
	link = soup.find('cite').text
	return(link) 

# Empty list to append scraped companies into
scraped_companies = []

# Loop over list of companies to scrape all rating categories
for index, row in test_list.iterrows():
	
	# Generate url
	url = find_url(row['company_short_name'])
	
	# Call scrape function and store result
	scraped_df = scrape_glass_chart(url, row['company_short_name'])
	print("Finished scraping:  " + row['company_short_name'])

	# Append to list outside loop
	scraped_companies.append(scraped_df)
	
# Concat dataframes and write to csv
scraped_data = pd.concat(scraped_companies)
scrated_data.to_csv("glassdoor_historicals_test2.csv")
