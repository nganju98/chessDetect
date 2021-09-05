# from beepy import beep

# import threading
# #import beepy
# import datetime


# from timeit import default_timer as timer

# ctr = 1
# entries = [timer()]
# #beep("coin")
# while True:
#     entry = timer()
#     entries.append(entry)
#     elapsed = (entry - entries[ctr-1]) * 1000
#     print(elapsed)
#     if (elapsed > 50):
#         break
    
#     ctr+=1  
#     if (ctr % 20 == 0):
#         print("beeping")
#         threading.Thread(target=beep, args=("coin",)).start()
    
# print("BROKE")