import logging
import os
import time
from azure.storage.fileshare import ShareFileClient
import azure.functions as func
import cv2
from azure.storage.fileshare import ShareDirectoryClient
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from azure.cosmos import CosmosClient, ContainerProxy
import datetime
# 存储账户连接字符串(过时)
connection_string = 'DefaultEndpointsProtocol=https;AccountName=adasdemostorage;AccountKey=7x5iWZKa2A1AkUmTD9s3jyIqBZefxB6yIAZ52t3Q+1BmFdsjG82VTuM9PGV49pU4SUpgvzmv26w0+ASt2Mf7yQ==;EndpointSuffix=core.windows.net'
# 存储账户连接字符串

file_connection_string = 'DefaultEndpointsProtocol=https;AccountName=adasdemostorage;AccountKey=zIySEZAoIzXUr9Hzs9nj+YecuiNR4p7fTssgygyzMfQMGY91fWe4T0uiceQACo8mvVm3AVTpYgvs+AStnvMzPA==;EndpointSuffix=core.windows.net'
# 服务总线连接字符串

service_bus_connection_string = 'Endpoint=sb://adas-demo.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=48Yvu9MwOEFOazLWelPB8YqnxgKY2ubceJfXl3ZVxeQ='
topic_name = 'step3-tobe-upload'


# 数据库连接字符串
CosmosDBClientURL = 'https://adas.documents.azure.com:443/'
Key = 'A4Zx9DGgesgH93Jj12Rw50ItfLWcSdFlYXzh2zcuTeyu5VZ9vUZHNiIFWTVDdnH6pWKig0kCoxsC9gNfAryZjw=='

# 创建存放图片的目录


def create_directory(connection_string, share_name, dir_name):
    # Create a ShareDirectoryClient from a connection string
    dir_client = ShareDirectoryClient.from_connection_string(
        connection_string, share_name, dir_name)
    logging.info("Creating directory:" + share_name + "/" + dir_name)
    dir_client.create_directory()


def get_histroy_container(url: str, key: str) -> ContainerProxy:
    client = CosmosClient(CosmosDBClientURL, Key)
    database = client.get_database_client('asaddatabase')
    history_container = database.get_container_client('history')
    return history_container


def update_time(id: str, start_time: str, end_time: str, history_container: ContainerProxy):
    item = history_container.read_item(
        item=id, partition_key=id)
    history = item['history']
    record = {
        'start_time': start_time,
        'end_time': end_time,
        'step': '视频切片'  # 写自己的状态
    }
    history.append(record)
    history_container.upsert_item(item)

def update_end_time(id: str, end_time: str, history_container: ContainerProxy):
    item = history_container.read_item(
        item=id, partition_key=id)
    item['history'][2]['end_time']=end_time
    history_container.upsert_item(item)
    pass


def main(message: func.ServiceBusMessage):

    start_time = (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    # 消息内容
    fileid = str(message.get_body().decode("utf-8"))
    container = get_histroy_container(url=CosmosDBClientURL, key=Key)
    logging.info('获取到文件id：'+fileid)
    logging.info('开始切割文件')
    try:
        filename = get_filename_by_id(id=fileid)
        create_directory(file_connection_string, 'func-shared-folder',
                     fileid)
        update_time(id=fileid, start_time=start_time,end_time='',history_container=container)

        updateCosmosDBStep('视频正在切片',fileid)

        # 修改状态
        update_Cosmos_Mp4_Status(fileid)

        # 切片逻辑  
        slice(filename, dir=fileid)
        
    except Exception as e:
        end_time = (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
        update_time(id=fileid, start_time=start_time,end_time=end_time,history_container=container)
        updateCosmosDBStep('视频切片失败',fileid)
        return
    end_time = (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")   
    update_end_time(id=fileid,end_time=end_time,history_container=container)
    # 修改MP4表结束时间
    updateCosmosDBTime(fileid,'end_time',end_time)
    updateCosmosDBStep('视频切片完成',fileid)

    logging.info('开始修改视频状态')
    # 对数据库操作。
    update_Cosmos_Mp4_Status(fileid)

    logging.info('开始向topic发送消息'+fileid)
    sendMessage(getClient(service_bus_connection_string),
                ServiceBusMessage(fileid))

    
    
    


def save_image(image, addr, num):
    address = addr + str(num) + '.jpg'
    cv2.imwrite(address, image)
    logging.info('创建'+address)

# 切片逻辑


def slice(filename: str, dir: str):
    # os.mkdir('hello')
    logging.info('开始进行切片')
    source_file = '/share/' + filename
    vode = cv2.VideoCapture(
        source_file
    )
    success, frame = vode.read()
    i = 0  # 帧计数
    j = 0  # 图片计数
    timeF = 1
    while success:
        i = i + 1
        if (i % timeF == 0):
            j = i + 1
            save_image(frame, '/share'+'/'+dir+'/image_', j)
            logging.info('保存图片:'+str(j))
        success, frame = vode.read()

# 获取消息发送客户端


def getClient(connection_string: str) -> ServiceBusClient:
    client = ServiceBusClient.from_connection_string(
        conn_str=connection_string)
    return client


# 发送消息
def sendMessage(client: ServiceBusClient, message: ServiceBusMessage):
    sender = client.get_topic_sender(topic_name=topic_name)
    sender.send_messages(message=message)


def updateCosmosDBTime(id: str, key: str, time: str):
    logging.info('开始修改记录时间')
    client = CosmosClient(CosmosDBClientURL, Key)
    database = client.get_database_client('asaddatabase')
    container = database.get_container_client('history')
    item = container.read_item(item=id, partition_key=id)
    item[key] = time
    container.upsert_item(item)
# 修改数据库


# 修改数据库步骤
def updateCosmosDBStep(step: str, id:str):
    client = CosmosClient(CosmosDBClientURL, Key)
    database = client.get_database_client('asaddatabase')
    container = database.get_container_client('history')
    item = container.read_item(item=id, partition_key=id)
    item['history'][2]['status'] = step
    container.upsert_item(item)

def update_Cosmos_Mp4_Status(id: str):
    client = CosmosClient(CosmosDBClientURL, Key)
    database = client.get_database_client('asaddatabase')
    container = database.get_container_client('asadmp4')
    item = container.read_item(item=id, partition_key=id)
    item['status'] = '视频切片'
    container.upsert_item(item)

def updateCosmosDB(id: str):
    client = CosmosClient(CosmosDBClientURL, Key)
    database = client.get_database_client('asaddatabase')
    container = database.get_container_client('asadmp4')
    item = container.read_item(item=id, partition_key=id)

    str = (datetime.datetime.now()+datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
    item['end_time'] = str
    container.upsert_item(item)
# 根据文件id获取文件名字


def get_filename_by_id(id: str) -> str:
    client = CosmosClient(CosmosDBClientURL, Key)
    database = client.get_database_client('asaddatabase')
    container = database.get_container_client('asadmp4')
    item = container.read_item(item=id, partition_key=id)
    return item['name']
