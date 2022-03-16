import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries
import boto3

def load_staging_tables(cur, conn):
    """
    This function copies all the data from a S3 Bucket to a staging
    table in Redshift. 
    
     INPUTS:
       *cur = the cursor variable from the database
       *conn = the variable that establishes connection to the database
       
    """
    
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    This function selects the data from the staging tables and inserts them into the 
    apropriate tables, performing any necessary transformation.
    
     INPUTS:
       *cur = the cursor variable from the database
       *conn = the variable that establishes connection to the database
       
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    
    """
    This is the main function. It first reads the configuration file, then connects to the 
    database, copies all the data from the S3 bucket to the staging tables and the insert 
    the data to the apropriate tables, performing any required transformations in the 
    proccess.
    
    After all the steps above are taken, it closes the connection.
    
    NO INPUTS
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    
    try:
        conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    except psycopg2.Error as e:
            print("Error: Could not connect to the DB")
            print(e) 
            
    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
            print("Error: Could not get cursor")
            print(e) 
    
    try:
        load_staging_tables(cur, conn)
    except psycopg2.Error as e:
            print("Error: Could not load staging tables")
            print(e) 
    
    try:
        insert_tables(cur, conn)
    except psycopg2.Error as e:
            print("Error: Could not insert data to table")
            print(e) 
    

    conn.close()


if __name__ == "__main__":
    main()