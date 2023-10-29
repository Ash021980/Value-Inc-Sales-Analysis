# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 06:22:54 2023

@author: Malcomb

Value Inc. Sales Analysis.
"""

# Import libraries
import warnings
import pandas as pd
import numpy as np

warnings.simplefilter('ignore', FutureWarning)
pd.set_option("display.precision", 2)


# Load Value Inc. sales data into a DataFrame
raw_df = pd.read_csv("Data/transaction2.csv", sep=";")

# Save a working copy of the raw data
sales_df = raw_df.copy()

# Inpect the metadata
# sales_df.info()

# Check for duplicate records
sales_df.duplicated().sum()

# Drop duplicate rows
sales_df.drop_duplicates(ignore_index=True, inplace=True)

# Check for Null values
sales_df.isnull().sum()
# 'ItemDescription' is the only column with Null values.
# As this is not important to my analysis, I will not remove any rows.


# Inpect the metadata
# sales_df.info()

# Add additional cost and profit feature columns
# Calculate Transaction Total
sales_df["TransactionTotal"] = sales_df.SellingPricePerItem.mul(sales_df.NumberOfItemsPurchased)

# Calculate Cost per Transaction
sales_df["CostPerTransaction"] = sales_df.CostPerItem.mul(sales_df.NumberOfItemsPurchased)

# Calculate Profit per Transaction
sales_df["ProfitPerTransaction"] = sales_df.TransactionTotal.sub(sales_df.CostPerTransaction)

# Calculate the Profit Margin
# use the fillna() method to account for any zero division errors
sales_df["MarginPerTransaction"] = sales_df.ProfitPerTransaction.div(sales_df.CostPerTransaction)\
                                           .round(2).fillna(0.00)

# Verify the 'Year' column is viable
# sales_df.Year.unique()

# Check how many records have a year of 2028
# sales_df.query("Year == '2028'")
# 5,321 records are affected

# Change the records for 'Year' column from 2028 to 2020
sales_df["Year"] = np.where(sales_df.Year == '2028', '2020', sales_df.Year)

# Verify 'Year' column changes were made
# sales_df[sales_df["Year"] == '2028']

# Split the 'ClientKeywords' column into 3 new columns
split_df = pd.DataFrame(sales_df.ClientKeywords.str.split(",", expand=True).values,
                        columns=["ClientAge", "ClientType", "ClientLevel"])
sales_df = pd.concat([sales_df, split_df], axis=1)

# Clean the 'ClientAge', 'ClientType', and 'ClientLevel' columns
sales_df["ClientAge"] = sales_df.ClientAge.str.replace("[", "")
sales_df["ClientAge"] = sales_df.ClientAge.str.replace("'", "")
sales_df["ClientType"] = sales_df.ClientType.str.replace("'", "")
sales_df["ClientLevel"] = sales_df.ClientLevel.str.replace("]", "")
sales_df["ClientLevel"] = sales_df.ClientLevel.str.replace("'", "")

# Change the 'NumberOfItemsPurchased' column to an int32 data type
sales_df["NumberOfItemsPurchased"] = sales_df.NumberOfItemsPurchased.astype("int16")

# Optimize Column data types
# Turn 'UserId', 'TransactionId', 'Year', 'Month', 'Day', 'ItemCode', and 'Country'
# into categorical data types
cat_cols = ('UserId', 'TransactionId', 'ItemCode', 'Country',
            'ClientAge', 'ClientType', 'ClientLevel')

# String columns
str_cols = ("Year", "Month", "Day", "Time", "ItemDescription")

# Change the 'ProfitPerItem', 'ProfitPerTransaction', 'CostPerTransaction',
# and 'TransactionTotal' columns to a float32 data type
float_cols = ("CostPerItem", "SellingPricePerItem", "ProfitPerTransaction",
              "CostPerTransaction", "TransactionTotal", "MarginPerTransaction")

for col in sales_df.columns:
    if col in cat_cols:
        DTYPE = "category"
    elif col in float_cols:
        DTYPE = "float32"
    elif col in str_cols:
        DTYPE = "string"
    else:
        continue

    sales_df[f"{col}"] = sales_df[f"{col}"].astype(DTYPE)

# Create a 'Date' column yyyy-mm-day
date = sales_df.Year.str.cat([sales_df.Month, sales_df.Day], sep="-")
sales_df["Date"] = pd.to_datetime(date)

# Create an 'Hour' column
sales_df["Hour"] = pd.to_datetime(sales_df.Time).dt.hour
sales_df["Hour"] = sales_df.Hour.astype("category")

# Get Summary Statistics for Numerical and Categorical variables
# sales_df.describe()
# sales_df.describe(include="category")
# sales_df.describe(include="string")

# Load seasonal data into a dataframe
seasons_df = pd.read_csv("Data/value_inc_seasons.csv", sep=";")

# Merge seasons dataframe with sales dataframe
sales_df = sales_df.merge(seasons_df, left_on="Month", right_on="Month")

# Drop columns that aren't needed for Tableau
sales_df.drop(columns=["ClientKeywords", "Day", "Year", "Month"], inplace=True)

# Inpect the metadata
# sales_df.info()

# Export DataFrame into a CSV file for visualizing in Tableau
sales_df.to_csv("Data/ValueInc_cleaned.csv", index=False)
