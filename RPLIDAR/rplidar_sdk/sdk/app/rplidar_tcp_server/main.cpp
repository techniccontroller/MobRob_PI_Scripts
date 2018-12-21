/*
 *  RPLIDAR
 *  Ultra Simple Data Grabber Demo App
 *
 *  Copyright (c) 2009 - 2014 RoboPeak Team
 *  http://www.robopeak.com
 *  Copyright (c) 2014 - 2018 Shanghai Slamtec Co., Ltd.
 *  http://www.slamtec.com
 *
 */
/*
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */
#include <unistd.h> 
#include <stdio.h> 
#include <sys/socket.h> 
#include <stdlib.h> 
#include <netinet/in.h> 
#include <string.h> 
#define PORT 1234 


#include "rplidar.h" //RPLIDAR standard sdk, all-in-one header

#ifndef _countof
#define _countof(_Array) (int)(sizeof(_Array) / sizeof(_Array[0]))
#endif

static inline void delay(_word_size_t ms){
    while (ms>=1000){
        usleep(1000*1000);
        ms-=1000;
    };
    if (ms!=0)
        usleep(ms*1000);
}


using namespace rp::standalone::rplidar;

bool checkRPLIDARHealth(RPlidarDriver * drv)
{
    u_result     op_result;
    rplidar_response_device_health_t healthinfo;


    op_result = drv->getHealth(healthinfo);
    if (IS_OK(op_result)) { // the macro IS_OK is the preperred way to judge whether the operation is succeed.
        printf("RPLidar health status: %d\n", healthinfo.status);
        if (healthinfo.status == RPLIDAR_STATUS_ERROR) {
            fprintf(stderr, "Error, rplidar internal error detected. Please reboot the device to retry.\n");
            // enable the following code if you want rplidar to be reboot by software
            // drv->reset();
            return false;
        } else {
            return true;
        }

    } else {
        fprintf(stderr, "Error, cannot retrieve the lidar health code: %x\n", op_result);
        return false;
    }
}

#include <signal.h>
bool ctrl_c_pressed;
void ctrlc(int)
{
    ctrl_c_pressed = true;
}


int main(int argc, const char * argv[]) {
    // Variables for RPLIDAR
    const char * opt_com_path = "/dev/rplidar";
    _u32         opt_com_baudrate = 115200;
    u_result     op_result;
    
    // Variables for tcp server
    int server_fd, new_socket, read_count; 
    struct sockaddr_in address; 
    int opt = 1; 
    int addrlen = sizeof(address); 
    char buffer[1024] = {0}; 
    
    printf("Ultra simple LIDAR data grabber for RPLIDAR.\n"
           "Version: %s\n", RPLIDAR_SDK_VERSION);
    
    // Creating socket file descriptor 
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) 
    { 
        perror("socket failed"); 
        exit(EXIT_FAILURE); 
    } 
       
    // Forcefully attaching socket to the port 8080 
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, 
                                                  &opt, sizeof(opt))) 
    { 
        perror("setsockopt"); 
        exit(EXIT_FAILURE); 
    } 
    address.sin_family = AF_INET; 
    address.sin_addr.s_addr = INADDR_ANY; 
    address.sin_port = htons( PORT ); 
       
    // Forcefully attaching socket to the port 8080 
    if (bind(server_fd, (struct sockaddr *)&address,  
                                 sizeof(address))<0) 
    { 
        perror("bind failed"); 
        exit(EXIT_FAILURE); 
    } 
    if (listen(server_fd, 3) < 0) 
    { 
        perror("listen"); 
        exit(EXIT_FAILURE); 
    }


    // create the driver instance
	RPlidarDriver * drv = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
    if (!drv) {
        fprintf(stderr, "insufficent memory, exit\n");
        exit(-2);
    }
    
    rplidar_response_device_info_t devinfo;
    bool connectSuccess = false;
    // make connection to rplidar...

    if(!drv)
        drv = RPlidarDriver::CreateDriver(DRIVER_TYPE_SERIALPORT);
    if (IS_OK(drv->connect(opt_com_path, opt_com_baudrate)))
    {
        op_result = drv->getDeviceInfo(devinfo);

        if (IS_OK(op_result)) 
        {
            connectSuccess = true;
        }
        else
        {
            delete drv;
            drv = NULL;
        }
    }


    if (!connectSuccess) {
        fprintf(stderr, "Error, cannot bind to the specified serial port %s.\n"
            , opt_com_path);
        RPlidarDriver::DisposeDriver(drv);
        drv = NULL;
        return 0;
    }

    // print out the device serial number, firmware and hardware version number..
    printf("RPLIDAR S/N: ");
    for (int pos = 0; pos < 16 ;++pos) {
        printf("%02X", devinfo.serialnum[pos]);
    }

    printf("\n"
            "Firmware Ver: %d.%02d\n"
            "Hardware Rev: %d\n"
            , devinfo.firmware_version>>8
            , devinfo.firmware_version & 0xFF
            , (int)devinfo.hardware_version);



    // check health...
    if (!checkRPLIDARHealth(drv)) {
        RPlidarDriver::DisposeDriver(drv);
        drv = NULL;
        return 0;
    }

    signal(SIGINT, ctrlc);
    bool running = true;

    while(running){
       
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address,  
            (socklen_t*)&addrlen))<0) 
        { 
            perror("accept"); 
            exit(EXIT_FAILURE); 
        } 
        
        drv->startMotor();
        // start scan...
        drv->startScan(0,1);
        
        while(1){
            read_count = read( new_socket , buffer, 1024);
            printf("%d %s\n",read_count, buffer );
            if(read_count == 0){
                printf("No data!\n");
                break;
            }
            if(strcmp(buffer,"getData") == 0){
                char response [8192] = "";
                rplidar_response_measurement_node_hq_t nodes[8192];
                size_t   count = _countof(nodes);
                
                op_result = drv->grabScanDataHq(nodes, count);

                if (IS_OK(op_result)) {
                    drv->ascendScanData(nodes, count);
                    for (int pos = 0; pos < (int)count ; ++pos) {
                        sprintf(response, "%s;%.2f,%.2f", response, nodes[pos].angle_z_q14 * 90.f / 16384.f, nodes[pos].dist_mm_q2 / 4.0f);  
                        /*printf("%s theta: %03.2f Dist: %08.2f Q: %d \n", 
                            nodes[pos].flag ? "S ":"  ", 
                            nodes[pos].angle_z_q14 * 90.f / 16384.f,
                            nodes[pos].dist_mm_q2 / 4.0f,
                            nodes[pos].quality >> RPLIDAR_RESP_MEASUREMENT_QUALITY_SHIFT);*/
                    }
                    sprintf(response,"%s\n", response);
                } 
                write(new_socket , response , strlen(response)); 
                printf("Data sent\n");
            }else if(strcmp(buffer,"closeDriver") == 0){
                printf("closeDriver");
                running = false;
                break;
            }
            
            if (ctrl_c_pressed){ 
                break;
            }
        }

        drv->stop();
        drv->stopMotor();
        // done!
    }
    printf("Done!\n");
    RPlidarDriver::DisposeDriver(drv);
    drv = NULL;
    return 0;
}

