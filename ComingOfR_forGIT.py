import math
import xlrd
import numpy as np
import pandas as pd
import matplotlib as plot
import pylogit as pl
import statsmodels
from collections import OrderedDict
import time


#Calculating time to run each function with a decorator
def calculate_time(func): 
      
    # added arguments inside the inner1, 
    # if function takes any arguments, 
    # can be added like this. 
    def inner1(*args, **kwargs): 
  
        # storing time before function execution 
        begin = time.time() 
          
        returned_value = func(*args, **kwargs) 
  
        # storing time after function execution 
        end = time.time() 
        print("Total time taken in : ", func.__name__, end - begin) 
        return returned_value

    return inner1 

#import data as CSV file, return 
@calculate_time
def csvDataImport(csvImport):
    data = pd.read_csv(csvImport)
    print(data.keys())
    print(data.memory_usage())
    return data

@calculate_time
def pylogitModel(data):
    basic_specification = OrderedDict()
    basic_names = OrderedDict()
    basic_specification['Affordable'] = [[1, 2, 3, 4, 5]]
    basic_names['Affordable'] = ['Affordable']
    basic_specification['Ease'] = [[1, 2, 3, 4, 5]]
    basic_names['Ease'] = ['Ease']
    basic_specification['Power'] = [[1, 2, 3, 4, 5]]
    basic_names['Power'] = ['Power']
    basic_specification['Learning'] = [[1, 2, 3, 4, 5]]
    basic_names['Learning'] = ['Learning']
    basic_specification['Supplements'] = [[1, 2, 3, 4, 5]]
    basic_names['Supplements'] = ['Supplements']
    basic_specification['Support'] = [[1, 2, 3, 4, 5]]
    basic_names['Support'] = ['Support']
    basic_specification['Needs'] = [[1, 2, 3, 4, 5]]
    basic_names['Needs'] = ['Needs']
    basic_specification['IT'] = [[1, 2, 3, 4, 5]]
    basic_names['IT'] = ['IT']
    basic_specification["intercept"] = [1, 2, 3, 4, 5]
    basic_names["intercept"] = ['Matlab', 'R', 'SAS', 'SPSS', 'Stata']
    
    print(basic_names)
    print(basic_specification)
    
    mnl_model_r = pl.create_choice_model(data=data,
                                            alt_id_col='Alternative',
                                            obs_id_col= 'OrgID',
                                            choice_col='Choice',
                                            specification=basic_specification,
                                            model_type="MNL",
                                            names=basic_names)
    
    # Specify the initial values and method for the optimization.
    mnl_model_r.fit_mle(np.zeros(13))
    
    # Look at the estimation results
    # print('1')
    # mnl_model_r.get_statsmodels_summary()
    print('2')
    mnl_model_r.print_summaries()
    return mnl_model_r
    
@calculate_time
def computeP(mnl_model_r, p_data):
    coefs = pd.DataFrame(mnl_model_r.coefs)
    p_data['Utility'] = np.matmul(p_data[['Affordable', 'Ease', 'Power', 'Learning', 'Supplements', 'Support', 'Needs', 'IT', 'Matlab', 'R', 'SAS', 'SPSS', 'Stata']], coefs['coefficients'])
    p_data['U_max'] = p_data['Utility'] - p_data.groupby(['OrgID'])['Utility'].transform(max)
    p_data['U_max_e'] = np.exp(p_data['U_max'])
    p_data['P'] = p_data['U_max_e']/p_data.groupby(['OrgID'])['U_max_e'].transform(sum)
    print(p_data.memory_usage())

    return p_data

@calculate_time
def computeXP(xp_data, choiceVars):
    for var in choiceVars:
        xp_var = var + 'XP'
        xp_data[xp_var] = xp_data[var] * xp_data['P']
    print(xp_data.memory_usage())
    return xp_data

@calculate_time
def computeXPP(xpp_data, choiceVars):
    for var in choiceVars:
        xpp_var = var + 'XPP'
        xpp_data[xpp_var] = xpp_data[var] * xpp_data['P']
    print(xpp_data.memory_usage())
    return xpp_data

@calculate_time
def computeXPQ(xpq_data, choiceVars, brandVars):
    #need to redo using modulo instead of
    varscreated = []
    for var in choiceVars:
        thisChoiceVar = var + 'XPQ'
        for brand in brandVars:
            thisChoiceBrandVar = thisChoiceVar + '.' + brand
            xpq_data[thisChoiceBrandVar] = np.nan
            varscreated.append(thisChoiceBrandVar)
            tempSeries = pd.Series(dtype=object)

            # for org in range(1, xpq_data['OrgID'].max() + 1):
    zorp = 0
    dataforfunc = xpq_data.loc[:, 'OrgID':'ITXP']
    print(dataforfunc)
    for newvar in varscreated:
        print(newvar)
        print(type(newvar.split('.')[0]))
        print(newvar.split('.')[1])
        for org in range(1, dataforfunc['OrgID'].max() + 1):
            needXP = newvar.split('.')[0]
            filtered_data = dataforfunc.loc[xpq_data['OrgID'] == org, ['Brand','P', needXP]] ##PROBLEMS HERE
            
            comparingTo = newvar.split('.')[1]
            # print('comparingTo = ', comparingTo)
            comparingToRow = filtered_data.loc[filtered_data['Brand'].str.contains(comparingTo) == True]
            #print(comparingToRow.index)
            #print('**********comparingToRow*************')
            #print(comparingToRow)
            # comparingToXP = comparingToRow[var] * comparingToRow['P']
            needXP = var + 'XP'
            needIndex = comparingToRow.index.values[0]
            comparingToXP = comparingToRow.at[needIndex, needXP]
            # comparingToXP1 = comparingToRow.index.values[0]
            # print(comparingToXP1)
            # print(type(comparingToXP1))
            # print(type(comparingToXP))
            #print('comparingToXP', comparingToXP)
            thisP = filtered_data['P']
            # filtered_data.loc[filtered_data['Brand'] == comparingTo, thisChoiceBrandVar] = np.nan
            filtered_data.loc[filtered_data['Brand'] != comparingTo, newvar] = (thisP * comparingToXP)
            tempSeries = tempSeries.append(filtered_data[newvar])
            zorp += 1

        xpq_data[newvar] = tempSeries
        tempSeries = pd.Series(dtype=object)
        print('*******************', zorp, '********************')
        
        # for org in range(1, 5):
        #     filtered_data = xpq_data.loc[xpq_data['OrgID'] == org]
        #     print(filtered_data)
        #     comparingTo = brand
        #     print('comparingTo = ', comparingTo)
        #     comparingToRow = filtered_data.loc[filtered_data['Brand'].str.contains(comparingTo) == True]
        #     print(comparingToRow.index)
        #     print('**********comparingToRow*************')
        #     print(comparingToRow)
        #     # comparingToXP = comparingToRow[var] * comparingToRow['P']
        #     needXP = var + 'XP'
        #     needIndex = comparingToRow.index.values[0]
        #     comparingToXP = comparingToRow.at[needIndex, needXP]
        #     # comparingToXP1 = comparingToRow.index.values[0]
        #     # print(comparingToXP1)
        #     # print(type(comparingToXP1))
        #     # print(type(comparingToXP))
        #     print('comparingToXP', comparingToXP)
        #     thisP = filtered_data['P']
        #     # filtered_data.loc[filtered_data['Brand'] == comparingTo, thisChoiceBrandVar] = np.nan
        #     filtered_data.loc[filtered_data['Brand'] != comparingTo, thisChoiceBrandVar] = (thisP * comparingToXP)
        #     tempSeries = tempSeries.append(filtered_data[thisChoiceBrandVar])

        # xpq_data[thisChoiceBrandVar] = tempSeries
        # tempSeries = pd.Series(dtype=object)
    print(xpq_data.memory_usage())
    return xpq_data

@calculate_time
def sumEverything(sum_data, brandVars):
    sum_dictionary = {}
    keys = pd.Series(sum_data.keys())
    keybrand = ''
    for key in keys[24:]:
        print('key = ', key)
        for brand in brandVars:
            if 'XPQ' in key:
                keybrand = key.split('.')[0] + '.' + brand + '.' + key.split('.')[1]
                sum_dictionary[keybrand] = sum_data.loc[sum_data['Brand'] == brand, key].sum()
                print('keybrand = ', keybrand)
                print(sum_dictionary[keybrand])
            # elif 'XPQ' in key and brand in :

            else:
                keybrand = key + '.' + brand
                print('keybrand = ', keybrand)
                sum_dictionary[keybrand] = sum_data.loc[sum_data['Brand']==brand, key].sum()
                print (sum_dictionary[keybrand])
    return sum_dictionary



#### Import Variables ####
csv1 = 'ComingOfRData_forGIT.csv'
choiceVars = ['Affordable', 'Ease', 'Power', 'Learning', 'Supplements', 'Support', 'Needs', 'IT']
brandVars = ['Matlab', 'R', 'SAS', 'SPSS', 'Stata']


#### Main ####
start = time.time()
data_import = csvDataImport(csv1)
print(data_import['OrgID'].max())

mnl_model = pylogitModel(data_import)
compute_p = computeP(mnl_model, data_import)
compute_xp = computeXP(compute_p, choiceVars)
# compute_xp.to_csv('viewXPQImport.csv')
print(compute_xp.dtypes)
compute_xpq = computeXPQ(compute_xp, choiceVars, brandVars)
compute_xpq.to_csv('viewXPQOutput4.csv')

# #avoidXPQ = csvDataImport('combinedfiletest.csv')
# allsums = sumEverything(compute_xpq, brandVars)

# for row in allsums
#
end = time.time()
print(f"Runtime of the program is {end - start}")

# test_data = compute_xpq
# test_data.to_csv('combinedfiletest.csv')


# COMPUTE Affordable_Coef = 1.083131. /*ENTER COEFFICIENT FOR Affordable.
# COMPUTE Ease_Coef = 0.752969. /*ENTER COEFFICIENT FOR EASE.
# COMPUTE Power_Coef = 0.358822.  /*ENTER COEFFICIENT FOR POWER.
# COMPUTE Learning_Coef = 0.634930. /*ENTER COEFFICIENT FOR LEARNING.
# COMPUTE Supplements_Coef = 0.117636.  /*ENTER COEFFICIENT FOR SUPPLEMENTS.
# COMPUTE Support_Coef = 0.253764.  /*ENTER COEFFICIENT FOR SUPPORT.
# COMPUTE Needs_Coef = 0.820132.  /*ENTER COEFFICIENT FOR NEEDS.
# COMPUTE IT_Coef = 0.109758. /*ENTER COEFFICIENT FOR IT.