import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur, conn):
    
    """
       This function drops all existing tables. 
       
       INPUTS:
       *cur = the cursor variable from the database
       *conn = the variable that establishes connection to the database
   """
    
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    
    """
    This functions creates all tables defined in create_table_queries.
    
     INPUTS:
       *cur = the cursor variable from the database
       *conn = the variable that establishes connection to the database
       
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    
    """
    This is the main function. It first reads the configuration file, then connects to the 
    database, drops any existing table and create new ones.
    
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
        drop_tables(cur, conn)
    except psycopg2.Error as e:
            print("Error: Could not drop tables")
            print(e) 
            
    try:
        create_tables(cur, conn)
    except psycopg2.Error as e:
            print("Error: Could not create tables")
            print(e) 

    conn.close()


if __name__ == "__main__":
    main()