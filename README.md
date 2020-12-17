# Covid_NL

## General Information:
Hobby project dealing with COVID-19 data for The Netherlands.

Collection of various methods to scrape and display data.

## Web scrapping:
Using the requests module, data on reported infections, hospital admissions, and deaths are retrieved from the [RIVM website](https://data.rivm.nl/covid-19/) in JSON form. Furthermore, a weekly published [RIVM PDF rapport](https://www.rivm.nl/coronavirus-covid-19/actueel/wekelijkse-update-epidemiologische-situatie-covid-19-in-nederland) is also retrieved. Finally, data regarding current usage and capacity of hospital beds, and intensive care units
are retrieved from the stichting [NICE website](https://stichting-nice.nl/).

## Data processing:
All data processing/manipulations are done using the pandas module.

## PDF parsing:
To obtain data on the number of tests that are performed, the weekly RIVM rapport on the status of the pandemic in The Netherlands is parsed. This is done by first locating the page number of the table with the data of interest by searching for the table name in the page text by using the pdfminer module. Next, to extract the actual table data, tabula-py (a Python wrapper of tabula-java) is used.

## Visualization/plotting:
Various plots, both on a basis of daily and weekly reported data, are created using the matplotlib module. 

![Total reported COVID-19 patients hospitalized over time](/plots/currenticzkh.png)
![Daily reported COVID-19 data over time](/plots/dailycombined.png)
![Weekly reported testing data](/plots//testingweekly2.png)

## Regression:
To investigate whether the daily reported figures are evenly distributed throughout the days of the week, a categorical variable OLS regression is run. The ratio of a given day's reported figures to the weekly total is taken as the dependent variable, and the categorical variable(day of the week) is taken as the independent variable.

```

                            OLS Regression Results                            
==============================================================================
Dep. Variable:     infect_pct_of_week   R-squared:                       0.259
Model:                            OLS   Adj. R-squared:                  0.244
Method:                 Least Squares   F-statistic:                     16.35
Date:                Thu, 17 Dec 2020   Prob (F-statistic):           3.82e-16
Time:                        16:09:46   Log-Likelihood:                 637.70
No. Observations:                 287   AIC:                            -1261.
Df Residuals:                     280   BIC:                            -1236.
Df Model:                           6                                         
Covariance Type:            nonrobust                                         
===========================================================================================
                              coef    std err          t      P>|t|      [0.025      0.975]
-------------------------------------------------------------------------------------------
Intercept                   0.1585      0.004     38.227      0.000       0.150       0.167
C(weekday)[T.Monday]       -0.0341      0.006     -5.822      0.000      -0.046      -0.023
C(weekday)[T.Saturday]      0.0007      0.006      0.124      0.901      -0.011       0.012
C(weekday)[T.Sunday]       -0.0047      0.006     -0.798      0.426      -0.016       0.007
C(weekday)[T.Thursday]     -0.0077      0.006     -1.311      0.191      -0.019       0.004
C(weekday)[T.Tuesday]      -0.0396      0.006     -6.746      0.000      -0.051      -0.028
C(weekday)[T.Wednesday]    -0.0244      0.006     -4.159      0.000      -0.036      -0.013
==============================================================================
Omnibus:                       60.771   Durbin-Watson:                   1.411
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              354.941
Skew:                           0.687   Prob(JB):                     8.42e-78
Kurtosis:                       8.272   Cond. No.                         7.87
==============================================================================

Notes:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.

```
The resulting F-statistic indicates that the null hypothesis that all of the regression coefficients are statistically not significantly different from zero is rejected. Examining the t-statistics of each of the coefficients on the day of the week, we find a statistically significant negative non-zero value for Monday, Tuesday, and Wednesday. We find a relatively low R-squared, and adjusted R-squared, indicating that only a small part of the variance in the dependent variable is explained by the independent variables. Finally, we observe a Durbin-Watson test result of 1.411, indicating statistical evidence that the error terms are positively correlated. Due to this being a violation of the 4th OLS assumption, no real statistical inferences can be made from the above regression.

## Technologies:
Project created with Python 3.8. Packages used:
* Requests
* Beautifullsoup
* Pandas
* Statsmodels
* Matplotlib
* Pdfminer
* Tabula-Py

## Development:
Ideas for possible future extensions to the project include the following:

The addition of data on the usage of Intensive Care units from [LCPS](https://lcps.nu/datafeed/). The NICE data is more focused on the amount of COVID-19 patients, whereas the LCPS is more focused on IC capacity. Furthermore, the 'status' in terms of suspected and proven COVID-19 can cause differences between the two datasets.

Using demographic data from [CBS](https://www.cbs.nl/nl-nl/onze-diensten/open-data) (the Dutch Central Bureau of Statistics), a regression on the proportion of elderly citizens in a municipality and the amount
of deaths and hospital admissions.

The weekly RIVM rapport on the status of the pandemic in The Netherlands also rapports data on sources of infection based on contact tracing. It might of interest to parse this data and plot the changes over time, to investigate whether the effects of different lockdown measures taken by the Dutch government are reflected in this data.   
