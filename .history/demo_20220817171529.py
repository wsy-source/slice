# import cv2

# outputFile = 'frame'
# c = 1

# vc = cv2.VideoCapture('/20220708_142017.mp4')
# rval, frame = vc.read()


# timeF = 1  # 视频帧计数间隔次数
# while rval:
#     rval, frame = vc.read()
#     if c % timeF == 0:
#         cv2.imwrite(outputFile + str(int(c / timeF)) + '.jpg', frame)
#     c += 1
#     cv2.waitKey(1)
#     vc.release()

# print()
# topic_name = 'step2-tobe-convert'
# from time import sleep
# from azure.servicebus import ServiceBusClient,ServiceBusMessage
# ConnectionSrting = 'Endpoint=sb://adas-demo.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=48Yvu9MwOEFOazLWelPB8YqnxgKY2ubceJfXl3ZVxeQ='
# client = ServiceBusClient.from_connection_string(ConnectionSrting)
# sender = client.get_topic_sender(topic_name)
# sender.send_messages(ServiceBusMessage('999999999'))
# print('=========================')
# demo = client.get_subscription_receiver('step3-tobe-upload','func-4-upload-image')
# for i in demo.receive_messages():
#     print(str(i))

# from azure.cosmos import CosmosClient
# CosmosDBClientURL = 'https://adas.documents.azure.com:443/'
# Key = 'A4Zx9DGgesgH93Jj12Rw50ItfLWcSdFlYXzh2zcuTeyu5VZ9vUZHNiIFWTVDdnH6pWKig0kCoxsC9gNfAryZjw=='
# fileid = 'c4b9b778-6483-4c4a-b92c-938fa10665c7'
# # 修改数据库步骤
# def updateCosmosDBStep(step: str, id:str):
#     client = CosmosClient(CosmosDBClientURL, Key)
#     database = client.get_database_client('asaddatabase')
#     container = database.get_container_client('history')
#     item = container.read_item(item=id, partition_key=id)
#     item['step'] = step
#     container.upsert_item(item)


# updateCosmosDBStep('视频开始切片',fileid)

def a():
    print('a')
    return
    print('b')

a()