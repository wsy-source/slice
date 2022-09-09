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
topic_name = 'step2-tobe-convert'
from time import sleep
from azure.servicebus import ServiceBusClient,ServiceBusMessage
ConnectionSrting = 'Endpoint=sb://adas-demo.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=48Yvu9MwOEFOazLWelPB8YqnxgKY2ubceJfXl3ZVxeQ='
client = ServiceBusClient.from_connection_string(ConnectionSrting)
sender = client.get_topic_sender(topic_name)
sender.send_messages(ServiceBusMessage('10df2d5f-7065-4294-9f71-69a14edf48e0'))
print('=========================')
demo = client.get_subscription_receiver('step3-tobe-upload','func-4-upload-image')
for i in demo.receive_messages():
    print(str(i))