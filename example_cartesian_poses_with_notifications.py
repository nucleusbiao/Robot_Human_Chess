#!/usr/bin/env python
###
# KINOVA (R) KORTEX (TM)
#
# Copyright (c) 2019 Kinova inc. All rights reserved.
#
# This software may be modified and distributed
# under the terms of the BSD 3-Clause license.
#
# Refer to the LICENSE file for details.
#
###

import sys
import rospy
import time
import serial
import json

import socket
import sys
import struct
from kortex_driver.srv import *
from kortex_driver.msg import *

SEND_BUF_SIZE = 256
lock_ = False
RECV_BUF_SIZE = 256

Communication_Count = 0

receive_count = 0


class ExampleCartesianActionsWithNotifications:
    def __init__(self):# 机械臂控制样例源码，未改动
        try:
            rospy.init_node(
                'example_cartesian_poses_with_notifications_python')

            self.HOME_ACTION_IDENTIFIER = 2

            self.action_topic_sub = None
            self.all_notifs_succeeded = True

            # Get node params
            self.robot_name = rospy.get_param('~robot_name', "my_gen3")

            rospy.loginfo("Using robot_name " + self.robot_name)

            # Init the action topic subscriber
            self.action_topic_sub = rospy.Subscriber(
                "/" + self.robot_name + "/action_topic", ActionNotification,
                self.cb_action_topic)
            self.last_action_notif_type = None

            # Init the services
            clear_faults_full_name = '/' + self.robot_name + '/base/clear_faults'
            rospy.wait_for_service(clear_faults_full_name)
            self.clear_faults = rospy.ServiceProxy(clear_faults_full_name,
                                                   Base_ClearFaults)

            read_action_full_name = '/' + self.robot_name + '/base/read_action'
            rospy.wait_for_service(read_action_full_name)
            self.read_action = rospy.ServiceProxy(read_action_full_name,
                                                  ReadAction)

            execute_action_full_name = '/' + self.robot_name + '/base/execute_action'
            rospy.wait_for_service(execute_action_full_name)
            self.execute_action = rospy.ServiceProxy(execute_action_full_name,
                                                     ExecuteAction)

            set_cartesian_reference_frame_full_name = '/' + self.robot_name + '/control_config/set_cartesian_reference_frame'
            rospy.wait_for_service(set_cartesian_reference_frame_full_name)
            self.set_cartesian_reference_frame = rospy.ServiceProxy(
                set_cartesian_reference_frame_full_name,
                SetCartesianReferenceFrame)

            activate_publishing_of_action_notification_full_name = '/' + self.robot_name + '/base/activate_publishing_of_action_topic'
            rospy.wait_for_service(
                activate_publishing_of_action_notification_full_name)
            self.activate_publishing_of_action_notification = rospy.ServiceProxy(
                activate_publishing_of_action_notification_full_name,
                OnNotificationActionTopic)
        except:
            self.is_init_success = False
        else:
            self.is_init_success = True

    def cb_action_topic(self, notif):# 机械臂控制样例源码，未改动
        self.last_action_notif_type = notif.action_event

    def wait_for_action_end_or_abort(self):# 机械臂控制样例源码，有改动
        while not rospy.is_shutdown():
            if (self.last_action_notif_type == ActionEvent.ACTION_END):
                rospy.loginfo("Received ACTION_END notification")
                return True
            elif (self.last_action_notif_type == ActionEvent.ACTION_ABORT):
                rospy.loginfo("Received ACTION_ABORT notification")
                self.all_notifs_succeeded = False
                # 机械臂控制过程中出现ACTION_ABORT，必须退出，否则出现机械臂异常行为
                # 之前的异常行为是出现了ACTION_ABORT还继续传入数据，导致机械臂卡顿
                exit()
                return False
            else:
                time.sleep(0.01)

    def example_clear_faults(self):# 机械臂控制样例源码，未改动
        try:
            self.clear_faults()
        except rospy.ServiceException:
            rospy.logerr("Failed to call ClearFaults")
            return False
        else:
            rospy.loginfo("Cleared the faults successfully")
            rospy.sleep(2.5)
            return True

    def example_home_the_robot(self):# 机械臂控制样例源码，未改动
        # The Home Action is used to home the robot. It cannot be deleted and is always ID #2:
        req = ReadActionRequest()
        req.input.identifier = self.HOME_ACTION_IDENTIFIER
        self.last_action_notif_type = None
        try:
            res = self.read_action(req)
        except rospy.ServiceException:
            rospy.logerr("Failed to call ReadAction")
            return False
        # Execute the HOME action if we could read it
        else:
            # What we just read is the input of the ExecuteAction service
            req = ExecuteActionRequest()
            req.input = res.output
            rospy.loginfo("Sending the robot home...")
            try:
                self.execute_action(req)
            except rospy.ServiceException:
                rospy.logerr("Failed to call ExecuteAction")
                return False
            else:
                return self.wait_for_action_end_or_abort()

    def example_set_cartesian_reference_frame(self):# 机械臂控制样例源码，未改动
        # Prepare the request with the frame we want to set
        req = SetCartesianReferenceFrameRequest()
        req.input.reference_frame = CartesianReferenceFrame.CARTESIAN_REFERENCE_FRAME_MIXED

        # Call the service
        try:
            self.set_cartesian_reference_frame()
        except rospy.ServiceException:
            rospy.logerr("Failed to call SetCartesianReferenceFrame")
            return False
        else:
            rospy.loginfo("Set the cartesian reference frame successfully")
            return True

        # Wait a bit
        rospy.sleep(0.25)

    def example_subscribe_to_a_robot_notification(self):# 机械臂控制样例源码，未改动

        # Activate the publishing of the ActionNotification
        req = OnNotificationActionTopicRequest()
        rospy.loginfo("Activating the action notifications...")
        try:
            self.activate_publishing_of_action_notification(req)
        except rospy.ServiceException:
            rospy.logerr("Failed to call OnNotificationActionTopic")
            return False
        else:
            rospy.loginfo("Successfully activated the Action Notifications!")

        rospy.sleep(1.0)

        return True

    def main(self, sx, sy, dx, dy, eat):# 主要程序部分
        # 之前为了避免机械臂异常行为，其实是执行过程中，出现abort，立马进入下一行为导致异常
        global lock_
        print(lock_)
        if lock_:
            return
        lock_ = True

        # For testing purposes
        success = self.is_init_success
        try:
            rospy.delete_param(
                "/kortex_examples_test_results/cartesian_poses_with_notifications_python"
            )
        except:
            pass

        if success:

            #*******************************************************************************
            # Make sure to clear the robot's faults else it won't move if it's already in fault
            success &= self.example_clear_faults()
            #*******************************************************************************

            #*******************************************************************************
            # Subscribe to ActionNotification's from the robot to know when a cartesian pose is finished
            success &= self.example_subscribe_to_a_robot_notification()
            #*******************************************************************************

            #*******************************************************************************
            # Start the example from the Home position
            # success &= self.example_home_the_robot()
            #*******************************************************************************

            #*******************************************************************************
            # Set the reference frame to "Mixed"
            success &= self.example_set_cartesian_reference_frame()

            #*******************************************************************************
            # Prepare and send pose 1
            my_cartesian_speed = CartesianSpeed()
            my_cartesian_speed.translation = 0.10  # m/s
            my_cartesian_speed.orientation = 15  # deg/s

            my_constrained_pose = ConstrainedPose()
            my_constrained_pose.constraint.oneof_type.speed.append(
                my_cartesian_speed)

            # calculate the table
            right_top = {"x": 0.272, "y": -0.097, "z": 0.13}
            left_bottom = {"x": 0.514, "y": 0.175, "z": 0.13}

            x_edge =( left_bottom["x"] - right_top["x"]) / 8
            y_edge =( left_bottom["y"] - right_top["y"]) / 9
            # # real code------------------------------------------------------------------------------------------
            port_def = "/dev/ttyUSB0"
            timex = 5
            portx = port_def

            bps = 9600  # put down

            # we need open this port previously
            ser = serial.Serial(portx, bps, timeout=timex)
            lift_up_z = 0.13
            total_z = 0.115
            #  move a piece

            #             if eaten==1:
            # # above  down suck up dest put
            # # above  down suck up dest put
            #             else:
            # above  down suck up dest put
            source_x = sy
            source_y = sx
            dest_x = dy
            dest_y = dx
            #  judge whether eating occurs
            #if  happen to eat piece
            eaten = eat

            cnt = 0
            while (cnt < 2):
                cnt += 1
                if eaten == 0:
                    cnt += 1

    # move to there above
                if cnt == 1:
                    receive_x = dest_x
                    receive_y = dest_y
                else:
                    receive_x = source_x
                    receive_y = source_y

                # process received x,y
                processed_x = round(( 8 - receive_x ) * x_edge + right_top['x'],3)
                processed_y =round( ( receive_y ) * y_edge + right_top['y'],3)
                print("source_x:" + str(processed_x) + " source_y:" +
                      str(processed_y))

                my_constrained_pose.target_pose.x = processed_x
                my_constrained_pose.target_pose.y = processed_y
                my_constrained_pose.target_pose.z = lift_up_z  #             change z
                my_constrained_pose.target_pose.theta_x = 180
                my_constrained_pose.target_pose.theta_y = 0
                my_constrained_pose.target_pose.theta_z = 90

                req = ExecuteActionRequest()
                req.input.oneof_action_parameters.reach_pose.append(
                    my_constrained_pose)
                req.input.name = "pose1"
                req.input.handle.action_type = ActionType.REACH_POSE
                req.input.handle.identifier = 1001

                rospy.loginfo("Sending pose 1...")
                self.last_action_notif_type = None
                try:
                    self.execute_action(req)
                except rospy.ServiceException:
                    rospy.logerr("Failed to send pose 1")
                    success = False
                else:
                    rospy.loginfo("Waiting for pose 1 to finish...")

                self.wait_for_action_end_or_abort()
                time.sleep(1)

                # down to suck
                # Prepare and send pose 2
                req.input.handle.identifier = 1002
                req.input.name = "pose2"
                my_constrained_pose.target_pose.z = total_z

                req.input.oneof_action_parameters.reach_pose[0] = my_constrained_pose

                rospy.loginfo("Sending pose 2...")
                self.last_action_notif_type = None
                try:
                    self.execute_action(req)
                except rospy.ServiceException:
                    rospy.logerr("Failed to send pose 2")
                    success = False
                else:
                    rospy.loginfo("Waiting for pose 2 to finish...")

                self.wait_for_action_end_or_abort()
                time.sleep(1)

                # suck
                try:  
                    result = ser.write(b'0')

                except Exception as e:
                    print("---error---", e)
                time.sleep(1)

                # lift it up
                req.input.handle.identifier = 1002
                req.input.name = "pose2"
                my_constrained_pose.target_pose.z = lift_up_z

                req.input.oneof_action_parameters.reach_pose[
                    0] = my_constrained_pose

                rospy.loginfo("Sending pose 2...")
                self.last_action_notif_type = None
                try:
                    self.execute_action(req)
                except rospy.ServiceException:
                    rospy.logerr("Failed to send pose 2")
                    success = False
                else:
                    rospy.loginfo("Waiting for pose 2 to finish...")

                self.wait_for_action_end_or_abort()
                #if  dont happen to eat piece
                time.sleep(1)

                # move to dest
                if cnt == 1:
                    receive_x = 10
                    receive_y = -2
                else:
                    receive_x = dest_x
                    receive_y = dest_y

                # process received x,y
                processed_x = round(( 8 - receive_x ) * x_edge + right_top['x'],3)
                processed_y =round( ( receive_y ) * y_edge + right_top['y'],3)
                print("dest_x:" + str(processed_x) + " dest_y:" +str(processed_y))

                my_constrained_pose.target_pose.x = processed_x
                my_constrained_pose.target_pose.y = processed_y
                my_constrained_pose.target_pose.z = lift_up_z  #----------------change z
                my_constrained_pose.target_pose.theta_x = 180
                my_constrained_pose.target_pose.theta_y = 0
                my_constrained_pose.target_pose.theta_z = 90

                req = ExecuteActionRequest()
                req.input.oneof_action_parameters.reach_pose.append(
                    my_constrained_pose)
                req.input.name = "pose1"
                req.input.handle.action_type = ActionType.REACH_POSE
                req.input.handle.identifier = 1001

                rospy.loginfo("Sending pose 1...")
                self.last_action_notif_type = None
                try:
                    self.execute_action(req)
                except rospy.ServiceException:
                    rospy.logerr("Failed to send pose 1")
                    success = False
                else:
                    rospy.loginfo("Waiting for pose 1 to finish...")

                self.wait_for_action_end_or_abort()
                time.sleep(1)


                # put down
                
                try: 
                    result = ser.write(b"1")

                except Exception as e:
                    print("---error---", e)
                time.sleep(1)
                # go away
                receive_x = 10
                receive_y = -2

                # process received x,y
                processed_x = round(( 8 - receive_x ) * x_edge + right_top['x'],3)
                processed_y =round( ( receive_y ) * y_edge + right_top['y'],3)
                print("dest_x:" + str(processed_x) + " dest_y:" +
                      str(processed_y))

                my_constrained_pose.target_pose.x = processed_x
                my_constrained_pose.target_pose.y = processed_y
                my_constrained_pose.target_pose.z = lift_up_z  #----------------change z
                my_constrained_pose.target_pose.theta_x = 180
                my_constrained_pose.target_pose.theta_y = 0
                my_constrained_pose.target_pose.theta_z = 90

                req = ExecuteActionRequest()
                req.input.oneof_action_parameters.reach_pose.append(
                    my_constrained_pose)
                req.input.name = "pose1"
                req.input.handle.action_type = ActionType.REACH_POSE
                req.input.handle.identifier = 1001

                rospy.loginfo("Sending pose 1...")
                self.last_action_notif_type = None
                try:
                    self.execute_action(req)
                except rospy.ServiceException:
                    rospy.logerr("Failed to send pose 1")
                    success = False
                else:
                    rospy.loginfo("Waiting for pose 1 to finish...")

                self.wait_for_action_end_or_abort()
                time.sleep(1)
                # ------------------------
            eaten = 0
            ser.close()
        success &= self.all_notifs_succeeded

        # For testing purposes
        rospy.set_param(
            "/kortex_examples_test_results/cartesian_poses_with_notifications_python",
            success)

        if not success:
            rospy.logerr("The example encountered an error.")
        lock_ = False


def start_tcp_server(ip, port):
    # 机械臂通讯部分
    global lock_
    # create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)

    # bind port
    print("starting listen on ip %s, port %s" % server_address)
    sock.bind(server_address)

    # get the old receive and send buffer size
    s_send_buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    s_recv_buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print("socket send buffer size[old] is %d" % s_send_buffer_size)
    print("socket receive buffer size[old] is %d" % s_recv_buffer_size)

    # set a new buffer size
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF_SIZE)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF_SIZE)

    # get the new buffer size
    s_send_buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    s_recv_buffer_size = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    print("socket send buffer size[new] is %d" % s_send_buffer_size)
    print("socket receive buffer size[new] is %d" % s_recv_buffer_size)

    # start listening, allow only one connection
    try:
        sock.listen(1)
    except socket.error:
        print("fail to listen on port %s" % e)
        sys.exit(1)
    while True:
        print("waiting for connection")
        client, addr = sock.accept()
        print("having a connection")
        break
    msg = 'welcome to tcp server' + "\r\n"
    receive_count = 0
    receive_count += 1
    while True:
        global lock_
        # print("\r\n")
        msg = client.recv(1024)
        if msg != "":
            print(msg)
            da = json.loads(msg)
            if da['feedback'] == 200 and lock_ == False:
                # 调用执行控制机械臂
                ExampleCartesianActionsWithNotifications().main(
                    int(da['pick_up']['x']), int(da['pick_up']['y']),
                    int(da['put_down']['x']), int(da['put_down']['y']),
                    int(da['eat']))
        time.sleep(1)

    print("finish test, close connect")
    client.close()
    sock.close()
    print(" close client connect ")


if __name__ == "__main__":
    # ex = ExampleCartesianActionsWithNotifications()
    # ex.main()
    # 启动服务器
    start_tcp_server('127.0.0.1',8008)
    # 调试直接调用机械臂移动棋子
    # ExampleCartesianActionsWithNotifications().main(0, 0, 9, 8, 0)
