# from numpy import array
# from google.colab import files
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
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense
# from tensorflow.keras.optimizers import Adam
# import pickle
# import matplotlib.dates as mdates
# from datetime import datetime

def gen_plot_data(mu1,sigma1,s1,mu2,sigma2,s2):
  # plt.figure()
  s1 = np.random.normal(mu1,sigma1,s1)
  # plt.subplot(1,2,1)
  count1,bins1,ignored = plt.hist(s1,96)

  # plt.plot(bins1,1/(sigma* np.sqrt(2* np.pi))*np.exp(-(bins1-mu)**2/(2*sigma**2)))

  s2 = np.random.normal(mu2,sigma2,s2)
  # plt.subplot(1,2,2)
  count2,bins2,ignored = plt.hist(s2,96)

  # plt.plot(bins2,1/(sigma* np.sqrt(2* np.pi))*np.exp(-(bins2-mu)**2/(2*sigma**2)))

  count3=[]
  for i in range(72):
      count3.append(count1[i])

  for i in range(24):
      count3.append(count1[72+i]+count2[i]+random.randint(7,12))

  for i in range(72):
      count3.append(count2[24+i])

  for i in range(len(count3)):
    count3[i]+=random.randint(8,15)

  # plt.figure()

  # plt.bar(range(144),count3[12:156],0.5)
  # plt.plot(range(144),count3[12:156])
  # plt.title("Data generated from combination of two normal distributions")
  # plt.xlabel("Time instants")
  # plt.ylabel("Vehicles crossing intersection from given lane")
  return count3

def smooth_data_MA(arr):
  smoothened_data = []

  for i in range(12,156):
      sm=0
      for j in range(-4,4):
          if (j+i>=12 and i+j < 156):
              sm+=arr[i+j]
      if(sm!=0):
          sm = math.ceil(sm / (2*4))        
          smoothened_data.append(sm)

  # plt.figure()
  # plt.plot(range(144),smoothened_data)
  # plt.title("Data after applying moving averages method")
  # plt.xlabel("Time instants")
  # plt.ylabel("Vehicles crossing intersection from given lane")
  # plt.show()
  return smoothened_data

def generate_all_data(complete_data):
  
  # print(complete_data)
  for i in range(0,145):
    # print(i)
    str1=''
    hr=(int(i*5/60))+7
    mn=(i*5)%60
    str1+=str(int(hr/10))
    str1+=str(hr%10)
    str1+=':'
    str1+=str(int(mn/10))
    str1+=str(mn%10)
    complete_data[0].append(str1)

  # raw=[]
  rawtmp=gen_plot_data(1,1.5,2300,2,0.5,2000)
  tmp=smooth_data_MA(rawtmp)
  complete_data[1]=complete_data[1]+tmp

  rawtmp=gen_plot_data(2,0.7,2000,1,1.5,2300)
  tmp=smooth_data_MA(rawtmp)
  complete_data[2]=complete_data[2]+tmp

  rawtmp=gen_plot_data(1,0.4,2800,2,1.9,2500)
  tmp=smooth_data_MA(rawtmp)
  complete_data[3]=complete_data[3]+tmp

  rawtmp=gen_plot_data(1,3.6,2300,2,0.2,3200)
  tmp=smooth_data_MA(rawtmp)
  complete_data[4]=complete_data[4]+tmp
  return complete_data



def compute_timetaken(model,nodes,epochs,x,y):
  begin = time.time()
  model.fit(x,y,epochs=epochs,verbose=0)
  end = time.time()
  return end-begin


def compute_performance_metrics(x,y):
  mae=0
  mape=0
  rmse=0
  length_x= len(x)
  for i in range(length_x):
    tmp=abs(x[i]-y[i])
    mae+= tmp
    mape+= (tmp)/y[i]
    rmse+= tmp*tmp
  mae = mae/length_x
  mape = mape*100/length_x
  rmse = math.sqrt(rmse/length_x)
  return [mae,mape,rmse]


def predict_data(model,x_input):
  x_input= np.reshape(x_input,(1,12))
  yhat = model.predict(x_input, verbose=0)
  # print(yhat[0])
  return yhat[0]


def split_sequence(sequence, n_steps):
  X, y = list(), list()
  for i in range(len(sequence)):
    end_ix = i + n_steps
    # check if we are beyond the sequence
    if end_ix > len(sequence)-1:
      break
  # gather input and output parts of the pattern
    seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
    X.append(seq_x)
    y.append(seq_y)
  return X, y

# complete_data= []
# complete_data.append(['Time Instants'])
# complete_data.append(['Lane 1'])
# complete_data.append(['Lane 2'])
# complete_data.append(['Lane 3'])
# complete_data.append(['Lane 4'])

# generate_all_data(complete_data)

# # print(complete_data_transposed)
# df = pd.DataFrame(complete_data_transposed[1:], columns=complete_data_transposed[0])
# # # print(df)
# csv_filename='generated_traffic_dataset_1day.csv'
# df.to_csv(csv_filename, index=False)

# def generate_and_predict():
#     global generated_data
#     global predicted_data
#     generated_data= []
#     generated_data.append(['Time Instants'])
#     generated_data.append(['Lane 1'])
#     generated_data.append(['Lane 2'])
#     generated_data.append(['Lane 3'])
#     generated_data.append(['Lane 4'])
#     generated_data=Gpd.generate_all_data(generated_data)
#     splited=[[],[],[],[]]
#     y=[[],[],[],[]]
#     predicted_complete=[]

#     for i in range(4):
#         splited[i],y[i]=Gpd.split_sequence(generated_data[i][1:],12)
#         predicted=[]
#         filename = 'pickle_files/model_lane'+str(i+1)+'.sav'
#         loaded_model = pickle.load(open(filename, 'rb'))
#         for j in splited[i]:
#             predicted.append(Gpd.predict_data(loaded_model,j))
#         predicted_complete.append(predicted)
#     for l in range(1,len(predicted_complete)):
#         for j in range(len(predicted_complete[l])):
#             predicted_complete[l][j]=predicted_complete[l][j][0]
#     print("generated_data_for a day ")
#     print(generated_data)
#     print("predicted data")
#     print(predicted_complete)