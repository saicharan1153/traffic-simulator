from generate_dataset_for_day import *
from numpy import array
# from google.colab import files
import numpy as np
import pandas as pd
import math
import random
import matplotlib.pyplot as plt
import pickle
import matplotlib.dates as mdates
from datetime import datetime
import time
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

days= 40

complete_data= []
complete_data.append(['Time Instants'])
complete_data.append(['Lane 1'])
complete_data.append(['Lane 2'])
complete_data.append(['Lane 3'])
complete_data.append(['Lane 4'])
for i in range(40):
    complete_data=generate_all_data(complete_data)
complete_data_transposed= list(map(list, zip(*complete_data)))


models=[]

model1 = Sequential()
model1.add(Dense(64, activation='relu', input_dim=12))
model1.add(Dense(1))
model1.compile(optimizer='adam', loss='mse')

model2 = Sequential()
model2.add(Dense(48, activation='relu', input_dim=12))
model2.add(Dense(1))
model2.compile(optimizer='adam', loss='mse')

model3 = Sequential()
model3.add(Dense(32, activation='relu', input_dim=12))
model3.add(Dense(1))
model3.compile(optimizer='adam', loss='mse')

model4 = Sequential()
model4.add(Dense(16, activation='relu', input_dim=12))
model4.add(Dense(1))
model4.compile(optimizer='adam', loss='mse')

models.append(model1)
models.append(model2)
models.append(model3)
models.append(model4)

lane1= complete_data[1][1:]
lane2= complete_data[2][1:]
lane3= complete_data[3][1:]
lane4= complete_data[4][1:]
# print(all_lane)
lane1_X,lane1_y = split_sequence(lane1,12)
lane2_X,lane2_y = split_sequence(lane2,12)
lane3_X,lane3_y = split_sequence(lane3,12)
lane4_X,lane4_y = split_sequence(lane4,12)


test=[]
test.append(['Time Instants'])
test.append(['Lane 1'])
test.append(['Lane 2'])
test.append(['Lane 3'])
test.append(['Lane 4'])
test1= generate_all_data(test)
print(test1)
splited= [[],[],[],[]]
y=[[],[],[],[]]
predicted_complete=[]
predicted_complete.append([])

dates=[]
for k in range(1,145):
  dates.append(datetime.strptime(test1[0][k], '%H:%M'))
  if k>=13:
    predicted_complete[0].append(test1[0][k])

node_arr= [64,48,32,16]
times= []
for i in range(4):
  # compute_timetaken(models[i],node_arr[i],100)
  times.append(compute_timetaken(models[i],node_arr[i],100,lane1_X,lane1_y))
for i in range(4):
  splited[i],y[i]=split_sequence(test1[1][1:],12)
  fig=plt.figure()
  ax=fig.add_subplot(111)
  str_tmp= "test data lane "+ str(i+1)
  plt.title("Lane "+str(i+1))
  plt.plot(dates[12:],y[i],"-b",label=str_tmp)
  predicted=[]
  filename = 'traffic_prediction_ML_models/model_lane'+str(i+1)+'.sav'
  # loaded_model= 
  # loaded_model= load_pickle_file(filename)
  # loaded_model = pickle.load(open(filename, 'rb'))
  for j in splited[i]:
    predicted.append(predict_data(models[i],j))
  predicted_complete.append(predicted)
  plt.plot(dates[12:],predicted,"-r",label="predicted data")
  plt.legend(loc="upper right")
  ax.xaxis_date()
  plt.gcf().autofmt_xdate()
  plt.gcf().axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
  # plt.savefig('lane '+str(i+1)+'.png')



for i in range(1,len(predicted_complete)):
  for j in range(len(predicted_complete[i])):
    predicted_complete[i][j]=predicted_complete[i][j][0]


statics_arr= []
statics_arr.append(["MAE","MAPE","RMSE","simulation time"])
for i in range(4):
  statics_arr.append(compute_performance_metrics(predicted_complete[i+1],y[i]))
  statics_arr[i+1].append(times[i])
  print("statics")
  print(statics_arr[i+1])
index_labels= ["64 nodes","48 nodes","32 nodes","16 nodes"]
df= pd.DataFrame(statics_arr[1:],columns=statics_arr[0],index=index_labels)
print(df)
print("predicted")
print(predicted_complete[1])
print(predicted_complete[2])
print(predicted_complete[3])
print(predicted_complete[4])
print("output")
print(y[0])
print(y[1])
print(y[2])
print(y[3])