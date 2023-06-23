import pygame
import threading
import sys
import random
from string import Template
import csv
import time
import math
import generate_dataset_for_day as Gpd
# 12*60*60 sec to 24*60 sec 
# 24/(12*60)
# implies each 1sec in real time equivalent to 1/30 sec in simulation time
# traffic junction distance = 20m 
# 200 ut ->20 m
# average length of car 4.48m
# average length of bike 2.28m
# average length of auto 2.72m
# average length of truck 8.5m

# Initialisation
window_width =  800
window_height =  800
size=200
red_color = (255,0,0)
green_color = (0,255,0)
yellow_color = (255,255,0)
sim_time =0
current_lane = 0
lane_color = "green"
current_lane_time = 0
previous_lane = 3
fixed_green_time = 20
yellow_time = 5
"""
@inproceedings{inproceedings,
author = {Tiwari, Geetam and Fazio, Joseph and Pavitravas, Sri},
year = {2000},
month = {06},
pages = {},
title = {Passenger Car Units for Heterogeneous Traffic Using A Modified Density Method}
}
"""
factor= 1
speeds = [8.33,10.44,11.34,7.79]  # average speeds of vehicles
for i in range(len(speeds)):
    speeds[i]= factor*speeds[i]
# speeds = speeds
vehicle_types_map= ["auto","bike","car","truck"]
gap=11
car_path = 'car3.png'
signal_coordinates = [
    [(window_width-size)/2,(window_width-size)/2,(window_width-size)/2,(window_width+size)/2],
    [(window_width-size)/2,(window_width-size)/2,(window_width+size)/2,(window_width-size)/2],
    [(window_width+size)/2,(window_width-size)/2,(window_width+size)/2,(window_width+size)/2],
   [(window_width-size)/2,(window_width+size)/2,(window_width+size)/2,(window_width+size)/2]
]
generated_vehicles = [[],[],[],[]]
lane_colors=[green_color,red_color,red_color,red_color]
lane_stop_idxs=[0,0,0,0]
lane_stop_widths=[0,0,0,0]
generated_data= []
predicted_data=[]
cur_gen_idx=1
cur_cycle_time=27
vehicle_gen_rate=[0,0,0,0]
vehicle_to_be_generated_at=[0,0,0,0]
sim_rate = 2
total_delay_units =0
total_vehicles=0
cur_signaling_order =[]
signaling_idx=0
tmp_sim_time= 0
vehicles_generated=[0,0,0,0]
green_times=[0,0,0,0]
cycle_completed=False
iteration=0
iter_vehicle_delay=0
iter_vehicle_cnt=0
total_vehicle_delay=0
total_vehicle_cnt=0
file_name='optimized_signal_analysis3.csv'



vehicles_group = pygame.sprite.Group()
pygame.init()
clock = pygame.time.Clock()
# open window
surface=pygame.display.set_mode((window_width,window_height))
pygame.display.set_caption('Traffic Simulator')
surface.fill((255,255,255))
running=True
max_upd_delay =0

def draw_intersection(window_width,window_height,size,lane_colors):
    pygame.draw.rect(surface,(71,72,76),pygame.Rect(0,(window_width-size)/2,window_width,size))
    pygame.draw.rect(surface,(71,72,76),pygame.Rect((window_width-size)/2,0,size,(window_width-size)/2))
    pygame.draw.rect(surface,(71,72,76),pygame.Rect((window_width-size)/2,(window_width+size)/2,size,(window_width-size)/2))
    
    pygame.draw.line(surface,lane_colors[0],((window_width-size)/2,(window_width-size)/2),((window_width-size)/2,(window_width+size)/2),5)
    pygame.draw.line(surface,lane_colors[1],((window_width-size)/2,(window_width-size)/2),((window_width+size)/2,(window_width-size)/2),5)
    pygame.draw.line(surface,lane_colors[2],((window_width+size)/2,(window_width-size)/2),((window_width+size)/2,(window_width+size)/2),5)
    pygame.draw.line(surface,lane_colors[3],((window_width-size)/2,(window_width+size)/2),((window_width+size)/2,(window_width+size)/2),5)

    pygame.draw.line(surface,(246,196,0),(0,(window_width-5)/2),((window_width-size-5)/2,(window_width-5)/2),5)
    pygame.draw.line(surface,(246,196,0),((window_width+size+5)/2,(window_width-5)/2),(window_width,(window_width-5)/2),5)
    pygame.draw.line(surface,(246,196,0),((window_width-5)/2,0),((window_width-5)/2,(window_width-size-5)/2),5)
    pygame.draw.line(surface,(246,196,0),((window_width-5)/2,((window_width+size)/2)+5),((window_width-5)/2,window_width),5)


def update_signal(surface,color,signal_idx):
    pygame.draw.line(surface,color,(signal_coordinates[signal_idx][0],signal_coordinates[signal_idx][1]),(signal_coordinates[signal_idx][2],signal_coordinates[signal_idx][3]),5)
    lane_colors[signal_idx]=color


def read_gen_data():
    global generated_data
    global predicted_data
    datafile = open('generated_traffic_dataset_for_single_day.csv', 'r')
    datareader = list(csv.reader(datafile))
    for i in range(1,len(datareader)):
        res = [eval(j) for j in datareader[i][1:]]
        generated_data.append(res)
        if i<=12:
            predicted_data.append(res)
    datafile = open('predicted_traffic_dataset.csv', 'r')
    datareader = list(csv.reader(datafile))
    for i in range(1,len(datareader)):
        res = [eval(j) for j in datareader[i][1:]]
        predicted_data.append(res)    


class Vehicle(pygame.sprite.Sprite):
    def __init__(self,lane,path,type,idx,created_at,curr_iter):
        super().__init__()
        self.image = pygame.image.load(path)
        self.type= type
        self.idx=idx
        self.lane = lane
        self.rect= self.image.get_rect()
        self.crossed=False
        self.delay =0
        self.create_time=created_at
        self.curr_iter=curr_iter

    def update(self):
        isMoving =False
        global iter_vehicle_delay
        global iter_vehicle_cnt
        global total_vehicle_delay
        global total_vehicle_cnt
        if (self.lane==0):
            if(self.rect.x<=800):
                if self.rect.x>signal_coordinates[0][0]:
                    if self.crossed==False:
                        self.crossed=True
                        # if iteration==self.curr_iter or self.curr_iter+1==iteration:
                        iter_vehicle_delay+= self.delay
                        iter_vehicle_cnt+=1
                        total_vehicle_delay+= self.delay
                        total_vehicle_cnt+=1

                        lane_stop_widths[0]-=(self.rect.width+gap)
                    # self.rect.move_ip(speeds[self.type],0)
                # else:
                #     if(lane_colors[0]!=green_color):
                #         tmp_width=0
                #         for vehicle in generated_vehicles[0]:
                #             if self.idx==vehicle.idx:
                #                 break
                #                 # print("break 1")
                #             else:
                #                 if vehicle.crossed==False:
                #                     tmp_width+=vehicle.rect.width+gap
                #         if self.rect.x+tmp_width+self.rect.width+gap<signal_coordinates[0][0]:
                #             self.rect.move_ip(speeds[self.type],0)
                #     else:
                #         lane_stop_idxs[0]=0
                #         self.rect.move_ip(speeds[self.type],0)
                # tmp_width=0
                lane_stop_idxs[0]=0
                cur_vidx0=-1
                prev=0
                vehicle0=None
                # print(len(generated_vehicles[0]),end="-> ")
                for vidx in range(len(generated_vehicles[0])):
                    vehicle1=generated_vehicles[0][vidx]
                    if self.create_time==vehicle1.create_time:
                        cur_vidx0=vidx
                        # print(generated_vehicles[0][vidx].rect.x)
                        break
                    # else:
                        # print(generated_vehicles[0][vidx].rect.x,end=", ")
                if cur_vidx0!=0:
                    vehicle0 = generated_vehicles[0][cur_vidx0-1]
                    prev=vehicle0.rect.x
                if cur_vidx0==0:
                    if self.crossed==False:
                        if(lane_colors[0]!=green_color):
                            if self.rect.x+self.rect.width+gap< signal_coordinates[0][0]:
                                self.rect.move_ip(speeds[self.type],0)
                                isMoving =True
                        else:
                            isMoving = True
                            self.rect.move_ip(speeds[self.type],0)
                    else:
                        self.rect.move_ip(speeds[self.type],0)
                        isMoving =True
                else:
                    # if self.crossed==False and vehicle0.crossed==True:
                    #     prev= signal_coordinates[3][1]
                    # else:
                    #     vehicle0.rect.y+vehicle0.rect.height
                    if self.rect.x+self.rect.width+gap<prev:
                        if vehicle0.crossed==True:
                            if self.crossed==False:
                                if(lane_colors[0]!=green_color):
                                    if self.rect.x+self.rect.width+gap< signal_coordinates[0][0]:
                                        self.rect.move_ip(speeds[self.type],0)
                                        isMoving =True
                                else:
                                    isMoving = True
                                    self.rect.move_ip(speeds[self.type],0)
                            else:
                                self.rect.move_ip(speeds[self.type],0)
                                isMoving =True
                        else:
                            self.rect.move_ip(speeds[self.type],0)
                            isMoving =True
            else:
                generated_vehicles[0].pop(0)
                self.kill()
                del self
                # print("update: lane 1-del")
                return ""
        elif (self.lane==1):
            if(self.rect.y<=800):
                if self.rect.y>signal_coordinates[1][1]:
                    if self.crossed==False:
                        self.crossed=True
                        # if iteration==self.curr_iter:
                        iter_vehicle_delay+= self.delay
                        iter_vehicle_cnt+=1
                        total_vehicle_delay+= self.delay
                        total_vehicle_cnt+=1
                        lane_stop_widths[1]-=(self.rect.height+gap)
                    # self.rect.move_ip(0,speeds[self.type])
                # else:
                #     if(lane_colors[1]!=green_color):
                #         tmp_width=0
                #         for vehicle in generated_vehicles[1]:
                #             if self.idx==vehicle.idx:
                #                 break
                                
                #                 # print("break 2")
                #             else:
                #                 if vehicle.crossed==False:
                #                     tmp_width+=vehicle.rect.height+gap
                #         if self.rect.y+tmp_width+self.rect.height+gap<signal_coordinates[1][1]:
                #             self.rect.move_ip(0,speeds[self.type])
                #     else:
                #         lane_stop_idxs[1]=0
                #         self.rect.move_ip(0,speeds[self.type])
                # tmp_width=0
                lane_stop_idxs[1]=0
                cur_vidx1=-1
                prev=0
                vehicle0=None
                # print(len(generated_vehicles[3]),end="-> ")
                for vidx in range(len(generated_vehicles[1])):
                    vehicle1=generated_vehicles[1][vidx]
                    if self.create_time==vehicle1.create_time:
                        cur_vidx1=vidx
                        # print(generated_vehicles[3][vidx].rect.y)
                        break
                    # else:
                    #     print(generated_vehicles[3][vidx].rect.y,end=", ")
                if cur_vidx1!=0:
                    vehicle0 = generated_vehicles[1][cur_vidx1-1]
                    prev=vehicle0.rect.y
                if cur_vidx1==0:
                    if self.crossed==False:
                        if(lane_colors[1]!=green_color):
                            if self.rect.y+self.rect.height+gap< signal_coordinates[1][1]:
                                self.rect.move_ip(0,speeds[self.type])
                                isMoving =True
                        else:
                            isMoving = True
                            self.rect.move_ip(0,speeds[self.type])
                    else:
                        self.rect.move_ip(0,speeds[self.type])
                        isMoving =True
                else:
                    # if self.crossed==False and vehicle0.crossed==True:
                    #     prev= signal_coordinates[3][1]
                    # else:
                    #     vehicle0.rect.y+vehicle0.rect.height
                    if self.rect.y+self.rect.height+gap<prev:
                        if vehicle0.crossed==True:
                            if self.crossed==False:
                                if(lane_colors[1]!=green_color):
                                    if self.rect.y+self.rect.height+gap< signal_coordinates[1][1]:
                                        self.rect.move_ip(0,speeds[self.type])
                                        isMoving =True
                                else:
                                    isMoving = True
                                    self.rect.move_ip(0,speeds[self.type])
                            else:
                                self.rect.move_ip(0,speeds[self.type])
                                isMoving =True
                        else:
                            self.rect.move_ip(0,speeds[self.type])
                            isMoving =True
                

            else:
                generated_vehicles[1].pop(0)
                self.kill()
                del self
                # print("update: lane 2-del")
                return ""    
        elif (self.lane==2):
            if(self.rect.x>0):
                if self.rect.x+self.rect.width+gap<signal_coordinates[2][0]:
                    if self.crossed==False:
                        self.crossed=True
                        # if iteration==self.curr_iter:
                        iter_vehicle_delay+= self.delay
                        iter_vehicle_cnt+=1
                        total_vehicle_delay+= self.delay
                        total_vehicle_cnt+=1
                        lane_stop_widths[2]-=(self.rect.width+gap)
                    # self.rect.move_ip(-1*speeds[self.type],0)
                # else:
                    # if(lane_colors[2]!=green_color):
                    #     tmp_width=0
                    #     for vehicle in generated_vehicles[2]:
                    #         if self.idx==vehicle.idx:
                    #             break
                    #             # print("break 3")
                    #         else:
                    #             if vehicle.crossed==False:
                    #                 tmp_width+=vehicle.rect.width+gap
                    #     if self.rect.x-tmp_width-gap>signal_coordinates[2][0]:
                    #         self.rect.move_ip(-1*speeds[self.type],0)
                    # else:
                lane_stop_idxs[2]=0
                cur_vidx2=-1
                prev=0
                vehicle0=None
                for vidx in range(len(generated_vehicles[2])):
                    vehicle1=generated_vehicles[2][vidx]
                    if self.create_time==vehicle1.create_time:
                        cur_vidx2=vidx
                        break
                if cur_vidx2!=0:
                    vehicle0 = generated_vehicles[2][cur_vidx2-1]
                    prev=vehicle0.rect.x+vehicle0.rect.width
                if cur_vidx2==0:
                    if self.crossed==False:
                        if(lane_colors[2]!=green_color):
                            if self.rect.x-gap> signal_coordinates[2][0]:
                                self.rect.move_ip(-1*speeds[self.type],0)
                                isMoving =True
                        else:
                            isMoving = True
                            self.rect.move_ip(-1*speeds[self.type],0)
                    else:
                        self.rect.move_ip(-1*speeds[self.type],0)
                        isMoving =True
                else:
                    # if self.crossed==False and vehicle0.crossed==True:
                    #     prev= signal_coordinates[3][1]
                    # else:
                    #     vehicle0.rect.y+vehicle0.rect.height
                    if self.rect.x>prev+gap:
                        if vehicle0.crossed==True:
                            if self.crossed==False:
                                if(lane_colors[2]!=green_color):
                                    if self.rect.x-gap> signal_coordinates[2][0]:
                                        self.rect.move_ip(-1*speeds[self.type],0)
                                        isMoving =True
                                else:
                                    isMoving= True
                                    self.rect.move_ip(-1*speeds[self.type],0)
                            else:
                                self.rect.move_ip(-1*speeds[self.type],0)
                                isMoving =True
                        else:
                            self.rect.move_ip(-1*speeds[self.type],0)
                            isMoving =True
                
            else:
                generated_vehicles[2].pop(0)
                self.kill()
                del self
                return ""
        else:
            if(self.rect.y>=0):
                if self.rect.y+self.rect.height<signal_coordinates[3][1]:
                    if self.crossed==False:
                        self.crossed=True
                        # if iteration==self.curr_iter:
                        iter_vehicle_delay+= self.delay
                        iter_vehicle_cnt+=1
                        total_vehicle_delay+= self.delay
                        total_vehicle_cnt+=1
                        lane_stop_widths[3]-=(self.rect.height+gap)
                    # self.rect.move_ip(0,-1*speeds[self.type])
                # else:
                #     if(lane_colors[3]!=green_color):
                #         tmp_width=0
                #         for vehicle in generated_vehicles[3]:
                #             if self.idx==vehicle.idx:
                #                 break
                #                 # print("break 4")
                #             else:
                #                 if vehicle.crossed==False:
                #                     tmp_width+=vehicle.rect.height+gap
                #         if self.rect.y-tmp_width-gap>signal_coordinates[3][1]:
                #             self.rect.move_ip(0,-1*speeds[self.type])
                #     else:
                #         lane_stop_idxs[3]=0
                #         self.rect.move_ip(0,-1*speeds[self.type])
                # tmp_width=0
                lane_stop_idxs[3]=0
                cur_vidx3=-1
                prev=0
                vehicle0=None
                # print(len(generated_vehicles[3]),end="-> ")
                for vidx in range(len(generated_vehicles[3])):
                    vehicle1=generated_vehicles[3][vidx]
                    if self.create_time==vehicle1.create_time:
                        cur_vidx3=vidx
                        # print(generated_vehicles[3][vidx].rect.y)
                        break
                    # else:
                    #     print(generated_vehicles[3][vidx].rect.y,end=", ")
                if cur_vidx3!=0:
                    vehicle0 = generated_vehicles[3][cur_vidx3-1]
                    prev=vehicle0.rect.y+vehicle0.rect.height
                if cur_vidx3==0:
                    if self.crossed==False:
                        if(lane_colors[3]!=green_color):
                            if self.rect.y-gap> signal_coordinates[3][1]:
                                self.rect.move_ip(0,-1*speeds[self.type])
                                isMoving =True
                        else:
                            self.rect.move_ip(0,-1*speeds[self.type])
                    else:
                        self.rect.move_ip(0,-1*speeds[self.type])
                        isMoving =True
                else:
                    # if self.crossed==False and vehicle0.crossed==True:
                    #     prev= signal_coordinates[3][1]
                    # else:
                    #     vehicle0.rect.y+vehicle0.rect.height
                    if self.rect.y>prev+gap:
                        if vehicle0.crossed==True:
                            if self.crossed==False:
                                if(lane_colors[3]!=green_color):
                                    if self.rect.y-gap> signal_coordinates[3][1]:
                                        self.rect.move_ip(0,-1*speeds[self.type])
                                        isMoving =True
                                else:
                                    self.rect.move_ip(0,-1*speeds[self.type])
                            else:
                                self.rect.move_ip(0,-1*speeds[self.type])
                                isMoving =True
                        else:
                            self.rect.move_ip(0,-1*speeds[self.type])
                            isMoving =True
                
            else:
                generated_vehicles[3].pop(0)
                self.kill()
                del self
                return ""
        if not isMoving and not self.crossed:
            self.delay += 1
        


def generate_vehicles():
    global running
    global vehicle_gen_rate
    global cur_gen_idx
    global vehicle_to_be_generated_at
    global total_vehicle_cnt
    global total_vehicle_delay
    global vehicles_generated
    global cycle_completed
    global iter_vehicle_delay
    global iter_vehicle_cnt
    global sim_time
    global current_lane_time
    # while True:
    # b=time.time()
    if not running:
        sys.exit(0)
    # for event in pygame.event.get():  
    #     if event.type == pygame.QUIT:  
    #         running=False
    #         pygame.quit()
    #         sys.exit()
    # # if sim_time==0:
        
    # # print("sim time",sim_time)
    if sim_time%300 ==0:
        vehicle_gen_rate= generated_data[cur_gen_idx]
        # print("f",vehicle_gen_rate)
        for i in range(4):
            vehicle_to_be_generated_at[i]=sim_time + (300/vehicle_gen_rate[i])
        print("vehicles ",vehicles_generated)
        vehicles_generated =[0,0,0,0]
    # if cycle_completed and iteration>0:
    #     cycle_completed=False
        # tmp_delay =0
        # tmp_vehicles=0
        # for lane_ in generated_vehicles:
        #     for veh_ in lane_:
        #         if veh_.crossed==False and veh_.curr_iter==iteration:
        #             tmp_delay += veh_.delay
        #             tmp_vehicles+=1
        # total_vehicle_delay+= tmp_delay
        # total_vehicle_cnt +=tmp_vehicles
        # iter_vehicle_delay+= tmp_delay
        # iter_vehicle_cnt+= tmp_vehicles
        # print('/n')
        # print("sim time ",sim_time)
        # print("Iteration: ", iteration)
        # print("Delay: ",iter_vehicle_delay)
        # print("vehicles crossed In this iteration: ",iter_vehicle_cnt)
        # print("Total Delay: ",total_vehicle_delay)
        # if iter_vehicle_cnt != 0:
        #     print("Average Delay In this Iteration: ", iter_vehicle_delay/iter_vehicle_cnt)
        # if total_vehicle_cnt != 0:
        #     print("Overall Average Delay: ", total_vehicle_delay/total_vehicle_cnt)
        # print("vehicles ",vehicles_generated)
        # file = open('optimized_signal_simulation_result.txt', 'a') # Open a file in append mode
        # with open('fixed_signal_analysis.csv', 'a',newline='') as f:
        #     # f.write('\n')
        #     write= csv.writer(f)
        #     write.writerows([[sim_time,iteration,iter_vehicle_delay,total_vehicle_delay,iter_vehicle_cnt,iter_vehicle_delay/iter_vehicle_cnt,total_vehicle_delay/total_vehicle_cnt]])
            # f.write("sim time " + str(sim_time) + '\n')
            # f.write("Iteration: " + str(iteration) + '\n')
            # f.write("Delay: " + str(iter_vehicle_delay) + '\n')
            # f.write("vehicles crossed In this iteration: " + str(iter_vehicle_cnt) + '\n')
            # f.write("Total Delay: " + str(total_vehicle_delay) + '\n')
            # if iter_vehicle_cnt != 0:
            #     f.write("Average Delay In this Iteration: "+str(iter_vehicle_delay/iter_vehicle_cnt)+'\n')
            # if total_vehicle_cnt != 0:
            #     f.write("Overall Average Delay: "+str(total_vehicle_delay/total_vehicle_cnt)+'\n')
            # if sim_time% 300==0 or sim_time%300==1:
            #     print("vehicles "+str(vehicles_generated)+'\n')
            # f.write('\n')
        # iter_vehicle_delay=0
        # iter_vehicle_cnt=0

    lines=[]
    # if sim_time==1:
    #     for i in range(500):
    #         lines.append(i%4)
    #     print("lines",lines)
    for i in range(4):
        if sim_time>= vehicle_to_be_generated_at[i]:
            lines.append(i)
            vehicle_to_be_generated_at[i] += (300/vehicle_gen_rate[i])
    



    for line_dir in lines:
        ulimit=874
        if cur_gen_idx<=25 or cur_gen_idx>=115:
            ulimit=950
        vehicle_type= int(random.randint(0,ulimit)/250)
        
        vehicle=None
        vehicle_img_path_str= "sim-"
        vehicle_img_path_str+= vehicle_types_map[vehicle_type]
        vehicle_img_path_str+="-"
        vehicle_img_path_str+=str(line_dir)
        vehicle_img_path_str+=".png"
        vehicle = Vehicle(line_dir,vehicle_img_path_str,vehicle_type,len(generated_vehicles[line_dir]),sim_time,iteration)
        if(line_dir==0):
            # vehicle.stop_distance=lane_stop_widths[0]
            vehicle.rect.centerx= (0-lane_stop_widths[0]-(vehicle.rect.width/2)-gap)
            vehicle.rect.centery= 370
            lane_stop_widths[0]+=vehicle.rect.width+gap
        elif line_dir==1:
            # vehicle = Vehicle(410,10,line_dir,vehicle_img_path_str,0,len(generated_vehicles))
            # vehicle.stop_distance=lane_stop_widths[1]
            vehicle.rect.centery= (0-lane_stop_widths[1]-(vehicle.rect.height/2)-gap)
            vehicle.rect.centerx= 425
            lane_stop_widths[1]+=vehicle.rect.height+gap
        elif line_dir==2:
            # vehicle = Vehicle(410,10,line_dir,vehicle_img_path_str,0,len(generated_vehicles))
            # vehicle.stop_distance=lane_stop_widths[2]
            vehicle.rect.centerx= 800+lane_stop_widths[2]+(vehicle.rect.width/2)+gap
            vehicle.rect.centery= 420
            lane_stop_widths[2]+=vehicle.rect.width+gap
        else:
            # vehicle = Vehicle(410,10,line_dir,vehicle_img_path_str,0,len(generated_vehicles))
            lane_stop_widths[3]+=vehicle.rect.height+gap
            # vehicle.stop_distance=lane_stop_widths[3]
            vehicle.rect.centery= 800+lane_stop_widths[3]+(vehicle.rect.height/2)+gap
            vehicle.rect.centerx= 380
        
        vehicles_group.add(vehicle)
        generated_vehicles[line_dir].append(vehicle)
        vehicles_generated[line_dir]+=1
    # e= time.time()
    # pygame.time.delay(max(math.ceil((1000/sim_rate)-(e-b)*1000),0))
        

def fixed_signaling():
    global lane_color
    global current_lane_time
    global current_lane
    global previous_lane
    global sim_time
    global lane_colors
    global running
    global cycle_completed
    global iteration
    global iter_vehicle_delay
    global iter_vehicle_cnt
    global cur_gen_idx

    while True:
        if not running:
            sys.exit(0)
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                pygame.quit()
                sys.exit()
        if sim_time%300==0 and sim_time>=300:
            cur_gen_idx+=1
            if cur_gen_idx>= len(generated_data):
                running=False
                pygame.quit()
                sys.exit()
        generate_vehicles()
        # print(current_lane_time,fixed_green_time,sim_time)
        if lane_color == "green" and current_lane_time==fixed_green_time:
            previous_lane= current_lane
            current_lane = (current_lane+1)%4
            current_lane_time= 0
            lane_color = "yellow"
            update_signal(surface,yellow_color,previous_lane)
            update_signal(surface,yellow_color,current_lane)
            cycle_completed=False
            
        elif lane_color == "yellow" and current_lane_time==yellow_time:
            current_lane_time= 0
            lane_color = "green"
            update_signal(surface,red_color,previous_lane)
            update_signal(surface,green_color,current_lane)
        
            if current_lane==0 and previous_lane==3:
                cycle_completed=True
                iteration+=1
            else:
                cycle_completed=False
        if cycle_completed:
            cycle_completed=False
            with open(file_name, 'a',newline='') as f:
                # f.write('\n')
                write= csv.writer(f)
                write.writerows([[sim_time,iteration,(iter_vehicle_delay)/10,(total_vehicle_delay)/10,iter_vehicle_cnt,(iter_vehicle_delay/iter_vehicle_cnt)/10,(total_vehicle_delay/total_vehicle_cnt)/10]])
            iter_vehicle_delay=0
            iter_vehicle_cnt=0
        sim_time = sim_time+1
        current_lane_time= current_lane_time+1
        pygame.time.delay(int(1000/sim_rate))


def optimizationAlgoSignalling():
    global lane_color
    global current_lane_time
    global current_lane
    global previous_lane
    global sim_time
    global lane_colors
    global running
    global cur_signaling_order
    global cur_gen_idx
    global signaling_idx
    global tmp_sim_time
    global green_times
    global cycle_completed
    global iteration
    global iter_vehicle_delay
    global iter_vehicle_cnt

    while True:
        b= time.time()
        if not running:
            sys.exit(0)
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                pygame.quit()
                sys.exit()
        

        if sim_time%300==0:
            if sim_time>=300:
                cur_gen_idx+=1
                if cur_gen_idx>= len(generated_data):
                    running=False
                    pygame.quit()
                    sys.exit()
            tmp_sim_time =0
            tmparr=predicted_data[cur_gen_idx]
            tmp2 = dict()
            vcnt=0
            for j in range(len(tmparr)):
                if tmp2.get(tmparr[j])==None:
                    tmp2[tmparr[j]]= [j]
                else:
                    tmp2[tmparr[j]].append(j)
                vcnt+=tmparr[j]
            keyslist = list(tmp2.keys())
            keyslist.sort()
            keyslist.reverse()
            ordered_signals= {i: tmp2[i] for i in keyslist}
            cur_signaling_order =[]
            for keys in ordered_signals.values():
                cur_signaling_order += keys
            gtime=0
            for j in range(len(tmparr)):
                green_times[j]= math.floor((4*fixed_green_time)*(tmparr[j]/vcnt))
                gtime+=green_times[j]
            diff_gt= (4*fixed_green_time)-gtime
            if diff_gt==1:
                green_times[cur_signaling_order[3]]+=1
            elif diff_gt==2:
                green_times[cur_signaling_order[3]]+=1
                green_times[cur_signaling_order[0]]+=1
            elif diff_gt==3:
                green_times[cur_signaling_order[3]]+=1
                green_times[cur_signaling_order[2]]+=1
                green_times[cur_signaling_order[0]]+=1
            else:
                green_times[cur_signaling_order[3]]+=1
                green_times[cur_signaling_order[2]]+=1
                green_times[cur_signaling_order[1]]+=1
                green_times[cur_signaling_order[0]]+=1
            # print("green times", green_times)
            
            for idx in range(len(lane_colors)):
                lane_colors[idx]= red_color
            lane_colors[cur_signaling_order[0]] = green_color
            current_lane_time=0
            lane_color = "green"
            current_lane= cur_signaling_order[0]
            previous_lane=cur_signaling_order[3]
            update_signal(surface,red_color,previous_lane)
            update_signal(surface,green_color,current_lane)
            signaling_idx=0
            if sim_time>0:
                iteration+=1
                cycle_completed=True
        generate_vehicles()

        if lane_color == "green" and current_lane_time==green_times[cur_signaling_order[(signaling_idx)%4]]:
            previous_lane= cur_signaling_order[(signaling_idx)%4]
            current_lane = cur_signaling_order[(signaling_idx+1)%4]
            current_lane_time= 0
            lane_color = "yellow"
            update_signal(surface,yellow_color,previous_lane)
            update_signal(surface,yellow_color,current_lane)
            
            cycle_completed=False
        
        elif lane_color == "yellow" and current_lane_time==yellow_time:
            # if (sim_time)%300!=0:
            current_lane_time= 0
            lane_color = "green"
            update_signal(surface,red_color,previous_lane)
            update_signal(surface,green_color,current_lane)
            signaling_idx = (signaling_idx+1)%4
            if signaling_idx==0:
                cycle_completed=True
                iteration+=1
            # else:
            #     current_lane_time= 0
            #     lane_color = "red"
            #     update_signal(surface,red_color,previous_lane)
            #     update_signal(surface,red_color,current_lane)
            # print("lane colors",lane_colors)
            # signaling_idx = (signaling_idx+1)%4
        
        # print()
        if cycle_completed:
            cycle_completed=False
            with open(file_name, 'a',newline='') as f:
                # f.write('\n')
                write= csv.writer(f)
                write.writerows([[sim_time,iteration,(iter_vehicle_delay)/10,(total_vehicle_delay)/10,iter_vehicle_cnt,(iter_vehicle_delay/iter_vehicle_cnt)/10,(total_vehicle_delay/total_vehicle_cnt)/10]])
            # print([sim_time,iteration,(iter_vehicle_delay)/10,(total_vehicle_delay)/10,iter_vehicle_cnt,(iter_vehicle_delay/iter_vehicle_cnt)/10,(total_vehicle_delay/total_vehicle_cnt)/10])
            iter_vehicle_delay=0
            iter_vehicle_cnt=0
        sim_time = sim_time+1
        tmp_sim_time = tmp_sim_time+1
        current_lane_time= current_lane_time+1
        e= time.time()
        pygame.time.delay(max(round((1000/sim_rate)-((e-b)*1000)),0))



random.seed(9876)
# 
file = open(file_name, 'w', newline ='')
with file:
    header = ['Simulation Time', 'Iteration', 'Iteration Delay','Total Delay','vehicles crossed In this iteration','Iteration Average Delay','Overall Average Delay']
    writer = csv.DictWriter(file, fieldnames = header)
    writer.writeheader()

read_gen_data()

# thread1 = threading.Thread(target=generate_vehicles,args=())
# thread1.setDaemon=True
# thread1.start()


thread2 = threading.Thread(target=optimizationAlgoSignalling,args=())
thread2.setDaemon=True
thread2.start()


while running:
    b= time.time()
    # for vehicle in generated_vehicles:
    #     surface.blit(vehicle.img,(vehicle.x,vehicle.y))
    #     vehicle.x+= 35
    # signaling()
    # if lane_color == "green" and current_lane_time==fixed_green_time:
    #     previous_lane= current_lane
    #     current_lane = (current_lane+1)%4
    #     current_lane_time= 0
    #     lane_color = "yellow"
    #     update_signal(surface,yellow_color,previous_lane)
    #     update_signal(surface,yellow_color,current_lane)
        
    # elif lane_color == "yellow" and current_lane_time==yellow_time:
    #     current_lane_time= 0
    #     lane_color = "green"
    #     update_signal(surface,red_color,previous_lane)
    #     update_signal(surface,green_color,current_lane)
    
    # sim_time = sim_time+1
    # current_lane_time= current_lane_time+1
    # pygame.time.delay(1000)
    # pygame.display.flip()
    # print(len(generated_vehicles))
    # pygame.time.delay(1000)
    # b1= time.time()
    draw_intersection(window_width,window_height,size,lane_colors)
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            running = False
            pygame.quit()
            sys.exit()
    b2=time.time()
    vehicles_group.update()
    e2=time.time()
    vehicles_group.draw(surface)
    pygame.display.flip()
    e = time.time()
    max_upd_delay = max(max_upd_delay,e-b)
    pygame.time.delay(max(math.ceil(((1000/sim_rate)/10)-(e-b)*1000),0))


