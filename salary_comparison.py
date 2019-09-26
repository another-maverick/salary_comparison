#!/usr/bin/env python
# coding: utf-8

# In[5]:


from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import pickle
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns


# In[6]:


links = ['https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SAN+JOSE&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SANTA+CLARA&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SUNNYVALE&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=MOUNTAIN+VIEW&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=CUPERTINO&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=MENLO+PARK&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=PALO+ALTO&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=REDWOOD+CITY&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SAN+MATEO&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SAN+FRANCISCO&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SEATTLE&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=REDMOND&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=SANTA+MONICA&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=LOS+ANGELES&year=All+Years',
         'https://h1bdata.info/index.php?em=&job=Data+Scientist&city=AUSTIN&year=All+Years',
         'https://h1bdata.info/index.php?em=amazon&job=Data+Scientist+I&city=&year=All+Years'
        ]

# Scrape table data from each of the above links and store in a list
jobs_list = []
for link in links:
    page_link = link
    page_response = requests.get(page_link, timeout=1000)
    page_content = BeautifulSoup(page_response.content, 'lxml')

    for row in page_content.find_all('tr')[1:]:
        row_data = []
        for i in row:
            row_data.append(i.text)
        jobs_list.append(row_data)


# In[7]:


# Put everything into dataframes for easier processing
ds_jobs_df = pd.DataFrame()
ds_jobs_df['company'] = [i[0] for i in jobs_list]
ds_jobs_df['title'] = [i[1] for i in jobs_list]

ds_jobs_df['salary'] = [i[2].replace(',','') for i in jobs_list]
ds_jobs_df['salary'] = ds_jobs_df['salary'].astype(float)

ds_jobs_df['location'] = [i[3] for i in jobs_list]

ds_jobs_df['date'] = [i[4] for i in jobs_list]
ds_jobs_df['date'] = pd.to_datetime(ds_jobs_df['date'])
ds_jobs_df['year'] = [i.year for i in ds_jobs_df['date']]

# Drop pre 2014 data (very few observations pre 2014)
ds_jobs_df.drop(ds_jobs_df[ds_jobs_df['year']<2014].index, axis=0, inplace=True)

# Drop salaries over $1,000,000
ds_jobs_df.drop(ds_jobs_df[ds_jobs_df['salary']>1000000].index, axis=0, inplace=True)

# Sort by company and year
ds_jobs_df.sort_values(by=['year','company'], inplace=True, ascending=True)


# In[8]:


fig, ax = plt.subplots(figsize=(10,6))
ax = sns.barplot(x=ds_jobs_df['year'].value_counts().sort_index().index, 
                 y=ds_jobs_df['year'].value_counts().sort_index().values)
ax.set_xlabel("Year",fontsize=16)
ax.set_ylabel("Number of H1B Data Scientist Salaries",fontsize=16)
plt.tight_layout()
plt.savefig(fname='num_jobs', dpi=150)


# In[11]:


ds_jobs_df['salary'].median()


# In[13]:


median_salary = ds_jobs_df.groupby(by=['year']).median().reset_index()


# In[14]:


fig, ax = plt.subplots(figsize=(10,6))
ax = sns.barplot(x=median_salary['year'], 
                 y=median_salary['salary'])
ax.set_xlabel("Year",fontsize=16)
ax.set_ylabel("Median Data Scientist Salary",fontsize=16)
ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.tight_layout()
plt.savefig(fname='median_salary', dpi=150)


# In[15]:


fig, ax = plt.subplots(figsize=(10,8))
sns.boxplot(x='year', y='salary', data=ds_jobs_df, showfliers=False);
ax.set_xlabel("Year",fontsize=16)
ax.set_ylabel("Data Scientist Salary",fontsize=16)
ax.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
plt.tight_layout()
plt.savefig(fname='salary_box', dpi=150)


# In[16]:


print('All 25th perctile: ' + str(ds_jobs_df['salary'].quantile(0.25)))
print('All 50th perctile: ' + str(ds_jobs_df['salary'].quantile(0.50)))
print('All 75th perctile: ' + str(ds_jobs_df['salary'].quantile(0.75)))


# In[17]:


print('2015 25th perctile: ' + str(ds_jobs_df[ds_jobs_df['year']==2015]['salary'].quantile(0.25)))
print('2015 50th perctile: ' + str(ds_jobs_df[ds_jobs_df['year']==2015]['salary'].quantile(0.50)))
print('2015 75th perctile: ' + str(ds_jobs_df[ds_jobs_df['year']==2015]['salary'].quantile(0.75)))


# In[18]:


print('2019 25th perctile: ' + str(ds_jobs_df[ds_jobs_df['year']>=2019]['salary'].quantile(0.25)))
print('2019 50th perctile: ' + str(ds_jobs_df[ds_jobs_df['year']>=2019]['salary'].quantile(0.50)))
print('2019 75th perctile: ' + str(ds_jobs_df[ds_jobs_df['year']>=2019]['salary'].quantile(0.75)))


# In[19]:


# Histogram of salaries
fig, ax = plt.subplots(figsize=(14,7))
ax = plt.hist(ds_jobs_df['salary'], bins=50, alpha=0.5)
plt.axvline(ds_jobs_df['salary'].quantile(0.25), c='black')
plt.axvline(ds_jobs_df['salary'].quantile(0.50), c='red')
plt.axvline(ds_jobs_df['salary'].quantile(0.75), c='black')

plt.xlabel('Salary',fontsize=16)
plt.ylabel('Frequency',fontsize=16)

plt.savefig(fname='salary_hist', dpi=150)
plt.show()


# In[21]:


company_df = pd.DataFrame()
company_df['company'] = ds_jobs_df[['company','salary']].groupby(by=['company']).count().reset_index()['company']
company_df['count'] = ds_jobs_df[['company','salary']].groupby(by=['company']).count().reset_index()['salary']
company_df['salary'] = ds_jobs_df[['company','salary']].groupby(by=['company']).median().reset_index()['salary']
sorted_df = company_df.sort_values(by='salary', ascending=False)
sorted_df= sorted_df[sorted_df['count']>=10]

fig, ax = plt.subplots(figsize=(12,8))
ax = sns.barplot(x=sorted_df['salary'], 
                 y=sorted_df['company'])
ax.set_xlabel("Median Data Scientist Salary",fontsize=16)
ax.set_ylabel("Company",fontsize=16)
plt.tight_layout()
plt.savefig(fname='company_median_salary', dpi=150)


# In[22]:


sorted_df.iloc[0:10]


# In[23]:


sorted_df = company_df.sort_values(by='count', ascending=False)
sorted_df= sorted_df[sorted_df['count']>=10]

fig, ax = plt.subplots(figsize=(12,8))
ax = sns.barplot(x=sorted_df['count'], 
                 y=sorted_df['company'])
ax.set_xlabel("H1B Petitions Filed",fontsize=16)
ax.set_ylabel("Company",fontsize=16)
plt.tight_layout()
plt.savefig(fname='company_hired', dpi=150)


# In[ ]:




