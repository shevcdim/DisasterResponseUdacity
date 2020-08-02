# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 17:27:24 2020

@author: shevcdim
"""
import sys
import pandas as pd
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    '''
    Load messages and categories dataset, merge them to Pandas dataframe
    '''
    # load messages
    messages_df = pd.read_csv(messages_filepath)
    
    # load categories 
    categories_df = pd.read_csv(categories_filepath)
    
    # merge datasets using merge method on 'id' using default ‘inner’
    df = pd.merge(messages_df, categories_df, on='id')
    return df


def clean_data(df):
    '''
    clean categories values and transform it to columns
    '''
    #get categories to new dataframe and split using ;
    categories =  df.categories.str.split(';', expand=True)
    #extract categories labels from new DF
    categories_labels = categories.iloc[0].apply(lambda x: x[:-2])
    #change the name of columns in categories DF using extracted label values
    categories.columns = categories_labels
    
    #we need to extract value of each category in the rows and apply it to the value of each cell
    for column in categories:
        categories[column] = categories[column].apply(lambda x: x[-1:]).astype(int)
    
    # drop the original categories column from DF
    df.drop('categories', axis=1, inplace=True)

    # concatenate orig DF and newly created 'categories' dataframe
    df = pd.concat([df, categories], axis=1)
   
    # drop duplicates just in case
    df.drop_duplicates(inplace=True)
    
    #get rid of records with category definition not equal to 0 or 1
    for c in df.columns[4:]:
        df.drop(df.loc[~df[c].isin([0,1])].index,inplace=True)
    
    return df
 
def save_data(df, database_filename):
    '''
    upload data to DB table drmsg from df dataframe
    '''
    engine = create_engine('sqlite:///{}'.format(database_filename))
    df.to_sql('drmsg', engine, index=False, if_exists='replace')  


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()


