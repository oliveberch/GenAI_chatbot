from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.contrib.sensors.gcs_sensor import GoogleCloudStorageObjectUpdatedSensor
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
import logging

load_dotenv()

# def send_notification_email(**kwargs): 
#     # Your email notification logic here
#     subject = "Document Upload Notification"
#     body = "The document has been successfully uploaded to Pinecone."

#     # Example EmailOperator usage
#     email_task = EmailOperator(
#         task_id='send_email_notification',
#         to='your@email.com',
#         subject=subject,
#         html_content=body,
#     )
#     email_task.execute(context=kwargs)

def process_and_upload_to_pinecone(**kwargs):
    print("Remotely received value of {} for key=message".format(kwargs['dag_run'].conf['file_name']))

    # Load text from GCS
    file_name = kwargs['dag_run'].conf['file_name']
    # loader = TextLoader("gs://your_gcs_bucket/your_file_in_gcs.txt")
    loader = TextLoader(file_name)
    pages = loader.load_and_split()

    # Split text into chunks
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=10)
    documents = text_splitter.split_documents(pages)

    # Initialize HuggingFace embeddings model
    embeddings_model = HuggingFaceEmbeddings(
        model_name="thenlper/gte-large",
        encode_kwargs={"normalize_embeddings": True},
    )

    # Upload embeddings to Pinecone
    index = "starter"
    namespace = 'documents' # new namespace in pinecone
    Pinecone.from_documents(documents, embeddings_model, index_name=index, namespace=namespace)

    # Log a message indicating successful upload
    logging.info("Document successfully uploaded to Pinecone.")

    # Send an email notification



default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.utcnow(),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='dag_conf',
    default_args=default_args,
    description='uploading data into pinecone',
    schedule_interval=None,  # Adjust as per your requirement
)

with dag:
    # Sensor task to wait for the file to be uploaded to GCS
    gcs_sensor = GoogleCloudStorageObjectUpdatedSensor(
        task_id='gcs_sensor',
        bucket='bucket_name',
        object='file_name.txt',
        google_cloud_storage_conn_id='google_cloud_default',
        timeout=600,  
    )

    # PythonOperator to process and upload to Pinecone
    process_and_upload_task = PythonOperator(
        task_id='process_and_upload_to_pinecone',
        python_callable=process_and_upload_to_pinecone,
        provide_context=True,
    )


bash_task = BashOperator(
    task_id="bash_task",
    bash_command='echo "Here is the message: '
                 '{{ dag_run.conf["message"] if dag_run else "" }}" ',
    dag=dag,
)
    # Set up task dependencies
    # gcs_sensor >> process_and_upload_task
