#importing libraries
from airflow import DAG
from datetime import datetime
#import python operator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.hive_operator import HiveOperator
#import fetching tweets file
import fetching_tweet
#import Cleaning tweets file
import cleaning_tweet

#while using a library from contributors (make sure no bugs exist)
from airflow.contrib.sensors.file_sensor import FileSensor

#define default args
default_args = {
		"start_date" : datetime(2020,11,11),
		"owner" : "airflow"
		}

#instantiate the DAG object
with DAG(dag_id="twitter_dag", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:
	waiting_for_tweets = FileSensor(task_id="waiting_for_tweets", fs_conn_id="fs_tweet",filepath="data.csv",poke_interval=5)
	fetching_tweets = PythonOperator(task_id="fetching_tweets", python_callable=fetching_tweet.main)
	cleaning_tweets = PythonOperator(task_id="cleaning_tweets", python_callable=cleaning_tweet.main)
	storing_tweets = BashOperator(task_id="storing_tweets", bash_command="hadoop fs -put -f /tmp/data_cleaned.csv /tmp/")

	loading_tweets = HiveOperator(task_id="loading_tweets", hql="LOAD DATA INPATH '/tmp/data_cleaned.csv' INTO TABLE tweets")
#defining depemdencies
	waiting_for_tweets >> fetching_tweets >> cleaning_tweets >> storing_tweets >> loading_tweets