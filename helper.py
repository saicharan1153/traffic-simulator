import pygame
import threading
import sys
import random
from string import Template
import csv
import time
import math

# 12*60*60 sec to 24*60 sec 
# 24/(12*60)
# implies each 1sec in real time equivalent to 1/30 sec in simulation time

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
green_time = 20
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
speeds = [8.33,10.44,11.54,7.41]  # average speeds of vehicles
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
cur_gen_idx=20
predicted_idx=20
cur_cycle_time=27
vehicle_gen_rate=[0,0,0,0]
vehicle_to_be_generated_at=[0,0,0,0]
sim_rate = 1
total_delay_units =0
total_vehicles=0



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
    datafile = open('generated_traffic_dataset_1day.csv', 'r')
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
# def draw_signal(surface,x,y):
#     gap= 7
#     rad= 17
#     pygame.draw.rect(surface,(0,0,0),pygame.Rect(x,y,50,130))
#     pygame.draw.circle(surface,(210,210,210),(x+25,y+gap+rad),rad)
#     pygame.draw.circle(surface,(210,210,210),(x+25,y+2*gap+3*rad),rad)
#     pygame.draw.circle(surface,(210,210,210),(x+25,y+3*gap+5*rad),rad)


class Vehicle(pygame.sprite.Sprite):
    def __init__(self,lane,path,type,idx):
        super().__init__()
        # self.x=x
        # self.y=y
        self.image = pygame.image.load(path)
        self.type= type
        self.idx=idx
        self.lane = lane
        self.rect= self.image.get_rect()
        self.crossed=False
        self.delay =0
        
        # print(self.rect)
        
        # print(self.rect)
        # if(lane==0):

        # elif(lane==1):
        # elif(lane==2):
        # else:
    def update(self):
        # global max_upd_delay
        # b= time.time()
        isMoving =False
        if (self.lane==0):
            if(self.rect.x-self.rect.width<=800):
                if self.rect.x>signal_coordinates[0][0]:
                    if self.crossed==False:
                        self.crossed=True
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
                tmp_width=0
                lane_stop_idxs[0]=0
                cur_vidx0=-1
                prev=0
                for vidx in range(len(generated_vehicles[0])):
                    vehicle1=generated_vehicles[0][vidx]
                    if self.idx==vehicle1.idx:
                        cur_vidx0=vidx
                        break
                    else:
                        if vehicle1.crossed==False:
                            tmp_width+=vehicle1.rect.width+gap
                if cur_vidx0!=0:
                    prev= generated_vehicles[0][cur_vidx0-1].rect.x
                if cur_vidx0==0:
                    if self.crossed==False:
                        if(lane_colors[0]!=green_color):
                            if self.rect.x+self.rect.width+gap < signal_coordinates[0][0]:
                                isMoving=True
                                self.rect.move_ip(speeds[self.type],0)
                        else:
                            isMoving=True
                            self.rect.move_ip(speeds[self.type],0)
                    else:
                        self.rect.move_ip(speeds[self.type],0)
                else:
                    if self.rect.x+self.rect.width+gap< prev:
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
                tmp_width=0
                lane_stop_idxs[1]=0
                cur_vidx1=-1
                prev=0
                for vidx in range(len(generated_vehicles[1])):
                    vehicle1=generated_vehicles[1][vidx]
                    if self.idx==vehicle1.idx:
                        cur_vidx1=vidx
                        break
                    else:
                        if vehicle1.crossed==False:
                            tmp_width+=vehicle1.rect.height+gap
                if cur_vidx1!=0:
                    prev=generated_vehicles[1][cur_vidx1-1].rect.y
                if cur_vidx1==0:
                    if self.crossed==False:
                        if(lane_colors[1]!=green_color):
                            if self.rect.y+self.rect.height+gap<signal_coordinates[1][1]:
                                self.rect.move_ip(0,speeds[self.type])
                                isMoving = True
                        else:
                            self.rect.move_ip(0,speeds[self.type])
                    else:
                        isMoving =True
                        self.rect.move_ip(0,speeds[self.type])
                else:
                    if self.rect.y+self.rect.height<prev-gap :
                        self.rect.move_ip(0,speeds[self.type])
                        isMoving =True
                # print(self.rect.y,self.rect.height,gap,signal_coordinates[1][1])
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
                tmp_width=0
                lane_stop_idxs[2]=0
                cur_vidx=-1
                prev=0
                for vidx in range(len(generated_vehicles[2])):
                    vehicle1=generated_vehicles[2][vidx]
                    if self.idx==vehicle1.idx:
                        cur_vidx=vidx
                        break
                    else:
                        if vehicle1.crossed==False:
                            tmp_width+=vehicle1.rect.width+gap
                if cur_vidx!=0:
                    prev=generated_vehicles[2][cur_vidx-1].rect.x+generated_vehicles[2][cur_vidx-1].rect.width
                if cur_vidx==0:
                    if self.crossed==False:
                        if(lane_colors[2]!=green_color):
                            if self.rect.x> signal_coordinates[2][0]+gap:
                                self.rect.move_ip(-1*speeds[self.type],0)
                                isMoving =True
                        else:
                            self.rect.move_ip(-1*speeds[self.type],0)
                    else:
                        self.rect.move_ip(-1*speeds[self.type],0)
                        isMoving =True
                else:
                    if self.rect.x>prev+gap :
                        self.rect.move_ip(-1*speeds[self.type],0)
                        isMoving =True
                        # 
            else:
                generated_vehicles[2].pop(0)
                self.kill()
                del self
                # print("update: lane 3-del")
                return ""
        else:
            if(self.rect.y>=0):
                if self.rect.y+gap<signal_coordinates[3][1]:
                    if self.crossed==False:
                        self.crossed=True
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
                tmp_width=0
                lane_stop_idxs[3]=0
                cur_vidx3=-1
                prev=0
                vehicle0=None
                for vidx in range(len(generated_vehicles[3])):
                    vehicle1=generated_vehicles[3][vidx]
                    if self.idx==vehicle1.idx:
                        cur_vidx3=vidx
                        break
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
                    if self.crossed==False and vehicle0.crossed==True:
                        prev= signal_coordinates[3][1]
                    if self.rect.y>prev+gap :
                        self.rect.move_ip(0,-1*speeds[self.type])
                        isMoving =True
                
            else:
                generated_vehicles[3].pop(0)
                self.kill()
                del self
                # print("update: lane 4-del")
                return ""
        if not isMoving and not self.crossed:
            self.delay += 1
        # e= time.time()
        # print(e-b,"each upd")
        # max_upd_delay = max(max_upd_delay,e-b)
        # self.rect.center= pygame.mouse.get_pos()
    # def remove(self, *groups: AbstractGroup) -> None:
    #     return super().remove(*groups)

# def actual_gen():




def generate_vehicles():
    global vehicle_gen_rate
    global cur_gen_idx
    global vehicle_to_be_generated_at
    global total_delay_units
    global total_vehicles
    # while True:
    if not running:
        sys.exit(0)
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            pygame.quit()
            sys.exit()
    # line_dir = int(random.randint(0,999)/250)
    if sim_time%300 ==0:
        tmp_delay =0
        cur_gen_idx=cur_gen_idx+ 1
        vehicle_gen_rate= generated_data[cur_gen_idx]
        for i in range(4):
            vehicle_to_be_generated_at[i]=sim_time + int(300/vehicle_gen_rate[i])
        for lane_ in generated_vehicles:
            for veh_ in lane_:
                tmp_delay += veh_.delay
        total_delay_units += tmp_delay
        print("Iteration: ", int((sim_time)/300))
        print("Delay: ",tmp_delay)
        print("Total Delay: ",total_delay_units)
        if total_vehicles != 0:
            print("Average Delay: ", total_delay_units/total_vehicles)
        print("max upd delay ",max_upd_delay)

    lines=[]
    # for i in range(4):
    #     if sim_time>= vehicle_to_be_generated_at[i]:
    #         lines.append(i)
    #         total_vehicles+= 1
    #         vehicle_to_be_generated_at[i] += int(300/vehicle_gen_rate[i])
    lines.append(0)
    lines.append(1)
    lines.append(2)
    lines.append(3)



    for line_dir in lines:
        vehicle_type= int(random.randint(0,999)/250)
        # line_dir=3
        vehicle=None
        vehicle_img_path_str= "sim-"
        vehicle_img_path_str+= vehicle_types_map[vehicle_type]
        vehicle_img_path_str+="-"
        vehicle_img_path_str+=str(line_dir)
        vehicle_img_path_str+=".png"
        vehicle = Vehicle(line_dir,vehicle_img_path_str,vehicle_type,len(generated_vehicles[line_dir]))
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

    pygame.time.delay(int(1000/sim_rate))

def signaling():
    global lane_color
    global current_lane_time
    global current_lane
    global previous_lane
    global sim_time
    global lane_colors
    global running

    while True:
        if not running:
            sys.exit(0)
        for event in pygame.event.get():  
            if event.type == pygame.QUIT:  
                pygame.quit()
                sys.exit()

        if lane_color == "green" and current_lane_time==green_time:
            previous_lane= current_lane
            current_lane = (current_lane+1)%4
            current_lane_time= 0
            lane_color = "yellow"
            update_signal(surface,yellow_color,previous_lane)
            update_signal(surface,yellow_color,current_lane)
            
        elif lane_color == "yellow" and current_lane_time==yellow_time:
            current_lane_time= 0
            lane_color = "green"
            update_signal(surface,red_color,previous_lane)
            update_signal(surface,green_color,current_lane)
        
        sim_time = sim_time+1
        current_lane_time= current_lane_time+1
        pygame.time.delay(int(1000/sim_rate))



# draw_signal(surface,30,50)

# update_signal(surface,green_color,0)
# update_signal(surface,red_color,1)
# update_signal(surface,red_color,2)
# update_signal(surface,red_color,3)
read_gen_data()
# thread1 = threading.Thread(target=generate_vehicles,args=())
# thread1.setDaemon=True
# thread1.start()
generate_vehicles()
generate_vehicles()
generate_vehicles()

thread2 = threading.Thread(target=signaling,args=())
thread2.setDaemon=True
thread2.start()


while running:
    b= time.time()
    # for vehicle in generated_vehicles:
    #     surface.blit(vehicle.img,(vehicle.x,vehicle.y))
    #     vehicle.x+= 35
    # signaling()
    # if lane_color == "green" and current_lane_time==green_time:
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
    # e1= time.time()
    # print("intersection",e1-b1)
    # signaling()
    for event in pygame.event.get():  
        if event.type == pygame.QUIT:  
            running = False
            pygame.quit()
            sys.exit()
    
    # vehicles_group.
    # clock.tick(75)
    # pygame.display.update()
    vehicles_group.update()

    # print(e-b)
    vehicles_group.draw(surface)
    pygame.display.flip()
    e = time.time()
    # max_upd_delay = max(max_upd_delay,e-b)
    del_ = max(math.ceil(((1000/sim_rate))-(e-b)),0)
    print(del_)
    pygame.time.delay(del_)


    