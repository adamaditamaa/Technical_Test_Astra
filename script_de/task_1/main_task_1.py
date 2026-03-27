import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from prefect import flow, task,get_run_logger
from datetime import datetime, timedelta

##################################################################
# load env
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST_FOR_PREFECT")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
FOLDER_BASE_SHARING = os.getenv("FILE_BASE_SHARING")
FILE_BASE_SHARING = f'{FOLDER_BASE_SHARING}/customer_address'

# Variables

# Prefect Config
retry_count = 1
retry_delay = 10 # in seconds

# Activate if you want to test ingest file
manual=False

# Datetime Config
yesterday = ((datetime.now())-timedelta(1)).strftime('%Y%m%d') if manual == False else '20260301'

# Query Check
query_check = '''
select count(*)
from customer_address_raw
where datefile = {yesterday}
'''

###################################################################################

def conn_dwh():
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600
    )

@task(name='Check Filesharing',
      log_prints=True,
      cache_result_in_memory=False,
      retries=retry_count,
      retry_delay_seconds=retry_delay)
def check_file(engine,logger):
    
    files = [
        f for f in os.listdir(FILE_BASE_SHARING)
        if f.startswith("customer_address") and f.endswith(".csv")
    ]
    logger.info(datetime.now())
    # To check data yesterday already there or not
    with engine.connect() as conn:
        count_check_data = conn.execute(text(query_check.format(yesterday=yesterday))).scalar()
        logger.info(count_check_data)

    if manual == True:
        logger.info('Manual Test Data Activated')
        return True
    elif count_check_data>0:
        logger.info('Data Already On Dwh')
        return False
    elif f'customer_address_{yesterday}' in files:
        logger.info('File is ready to execute')
        return True
    elif f'customer_address_{yesterday}' not in files:
        logger.info('No File Yesterday on folder')
        return False
    else:
        raise ValueError('Unexpected Command on Check Files')
        

@task(name='Load Data To Mysql',
      log_prints=True,
      cache_result_in_memory=False,
      retries=retry_count,
      retry_delay_seconds=retry_delay)
def load(engine,logger,notes):

    query = f"""
    LOAD DATA INFILE '{FILE_BASE_SHARING}/customer_address_{yesterday}.csv'
    INTO TABLE customer_address_raw
    FIELDS TERMINATED BY ','
    ENCLOSED BY '"'
    LINES TERMINATED BY '\r\n'
    IGNORE 1 ROWS;
    """


    with engine.begin() as conn:
        conn.execute(text(query))

    logger.info('Success To Load data to customer_address_raw')



@flow(log_prints=True)
def ingestion_flow():
    try:
        logger = get_run_logger()
        engine_conn = conn_dwh()
        result_check = check_file(engine=engine_conn,logger=logger)
        if result_check:
            load(engine=engine_conn,logger=logger,notes=result_check)
    except Exception as eror:
        raise ValueError(eror)


if __name__ == "__main__":
    ingestion_flow()