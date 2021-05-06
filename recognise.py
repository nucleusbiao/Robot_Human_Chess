# -*- coding: utf-8 -*-
import cv2
import numpy as np
import time
from socket import *
import json

confirm_rate = 0.25# 黑白判定比例
red_rate = 0.035# 红色判定比例
gray_rate = 200# 灰色图分割阈值
debug = False# 是否开启调试模式
debug = True
correct_mode = False# 是否开启校准位置模式
# correct_mode = True
net_mode = False# 是否开启网络，用于调试
net_mode = True
line = False# 是否开启画线
line = True
camera_id = 1# 摄像头编号
param = np.float32([[45, 57], [415, 53], [0, 480], [480, 480]])# 梯度标定坐标
data = [{
    "purpose": "update_map",
    "pick_up": {
        "x": 0,
        "y": 9
    },
    "put_down": {
        "x": 0,
        "y": 8
    }
}]# 数据交互格式

if correct_mode == False and net_mode:
    tcp_client_socket = socket(AF_INET, SOCK_STREAM)# 网络连接
    tcp_client_socket_for_ros = socket(AF_INET, SOCK_STREAM)
# connect server
if correct_mode == False and net_mode:
    tcp_client_socket_for_ros.connect(("localhost", 8008))# 连接机械臂端
    print("please open website first.")
    tcp_client_socket.connect(("localhost", 8003))# 连接中转
    data_start = [{"purpose": "newGame"}]
    data_start = json.dumps(data_start[0])
    tcp_client_socket.send(data_start.encode())
    recv_data = tcp_client_socket.recv(1024)
    # tcp_client_socket_for_ros.send(recv_data.encode())
    if recv_data:
        print("返回的消息为:", recv_data.decode())
    else:
        print("服务器已离线。。")
start = True
first_in = True
move_cnt = 0
state_code = 0  # 状态码
# 0 无错误
# 1 起始位置错误
# 2 终点位置错误
# 3 所移动棋子值错误
# 4 正在移动棋子

# 计算棋盘格子边长
left_top_corner = [36, 36]
right_bottom_corner = [451, 451]
square_y = (451 - 36) / 8
square_x = (451 - 36) / 9

dic = {
    '5': 'Black King',
    '9': 'Black 车',
    '1': 'Black 车',
    '2': 'Black 马',
    '8': 'Black 马',
    '10': 'Black 跑',
    '11': 'Black 炮',
    '4': 'Black 士',
    '6': 'Black 士',
    '3': 'Black 象',
    '7': 'Black 象',
    '12': 'Black 卒',
    '13': 'Black 卒',
    '14': 'Black 卒',
    '15': 'Black 卒',
    '16': 'Black 卒',
    '17': 'Red 兵',
    '18': 'Red 兵',
    '19': 'Red 兵',
    '20': 'Red 兵',
    '21': 'Red 兵',
    '24': 'Red 车',
    '32': 'Red 车',
    '25': 'Red 马',
    '31': 'Red 马',
    '22': 'Red 炮',
    '23': 'Red 炮',
    '27': 'Red 士',
    '29': 'Red 士',
    '28': 'Red 帅',
    '26': 'Red 相',
    '30': 'Red 相'
}
rows = 10
columns = 9
mat1 = [[1, 2, 3, 4, 5, 6, 7, 8, 9], [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 10, 0, 0, 0, 0, 0, 11, 0], [12, 0, 13, 0, 14, 0, 15, 0, 16],
        [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [17, 0, 18, 0, 19, 0, 20, 0, 21], [0, 22, 0, 0, 0, 0, 0, 23, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0], [24, 25, 26, 27, 28, 29, 30, 31, 32]]
rate_map = [[0 for i in range(columns)] for j in range(rows)]
rate_map_red = [[0 for i in range(columns)] for j in range(rows)]

if __name__ == '__main__':
    cap = cv2.VideoCapture(camera_id)
    if cap.isOpened():# 初始化，抛弃前20帧
        for j in range(20):
            cap.read()
        ret, current_frame = cap.read()
        current_frame = current_frame[0:480, 0:480]
    else:
        exit('相机未打开.')
    print('相机已初始化.')
    if correct_mode:# 纠正模式下，对准棋盘位置
        while (cap.isOpened()):
            ret, current_frame = cap.read()
            if not ret:
                break
            current_frame = current_frame[0:480, 100:580]
            img = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
            H_rows, W_cols = img.shape[:2]

            # 原图中书本的四个角点(左上、右上、左下、右下),与变换后矩阵位置
            pts1 = param
            pts2 = np.float32([
                [0, 0],
                [W_cols, 0],
                [0, H_rows],
                [H_rows, W_cols],
            ])

            # 生成透视变换矩阵；进行
            # 透视变换
            M = cv2.getPerspectiveTransform(pts1, pts2)
            dst = cv2.warpPerspective(img, M, (480, 480))
            for i in range(columns):
                cv2.line(dst, (int(36 + i * square_y), 36),
                         (int(36 + i * square_y), 451), 0, 1)
            for j in range(rows):
                cv2.line(dst, (36, int(36 + j * square_x)),
                         (451, int(36 + j * square_x)), 0, 1)
            cv2.imshow('', dst)

            cv2.waitKey(1)
    while (cap.isOpened()):
        # 按回车后继续
        if start == False:
            ccc = raw_input()  # 在python27中需要raw_input
            cnttt = 0
            while cnttt < 10:
                cnttt += 1
                cap.read()
        ret, current_frame = cap.read()
        if not ret:
            break
        current_frame = current_frame[0:480, 100:580]
        H_rows, W_cols = current_frame.shape[:2]

        # 原图中书本的四个角点(左上、右上、左下、右下),与变换后矩阵位置
        pts1 = param
        pts2 = np.float32([
            [0, 0],
            [W_cols, 0],
            [0, H_rows],
            [H_rows, W_cols],
        ])

        # 生成透视变换矩阵；进行
        # 透视变换
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(current_frame, M, (480, 480))
        gray_img = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

        ret, thresh2 = cv2.threshold(gray_img, gray_rate, 255,
                                     cv2.THRESH_BINARY)
        showblock = thresh2
        if line:# 划线
            for i in range(columns):
                cv2.line(showblock, (int(36 + i * square_y), 36),
                         (int(36 + i * square_y), 451), 255, 1)
            for j in range(rows):
                cv2.line(showblock, (36, int(36 + j * square_x)),
                         (451, int(36 + j * square_x)), 255, 1)
        cv2.imshow('', showblock)
        cv2.waitKey(1)
        move_cnt = 0
        legal = True
        from_pos = [-1, -1]
        to_pos = [-1, -1]
        key_val = -1
        # 得到红色遮罩
        hsv = cv2.cvtColor(dst, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 43, 46])
        upper_red = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)
        lower_red = np.array([156, 43, 46])
        upper_red = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red, upper_red)
        mask = cv2.add(mask1, mask2)
        # show the red mask
        # cv2.imshow('1', mask)

        # 计算白色占比
        for i in range(10):
            for j in range(9):
                x = left_top_corner[0] + i * square_x
                y = left_top_corner[1] + j * square_y
                white_cnt = 0
                red_cnt = 0
                a = int(x - square_x / 2)
                b = int(x + square_x / 2)
                c = int(y - square_y / 2)
                d = int(y + square_y / 2)
                img = thresh2[a:b, c:d]
                red_mask = mask[a:b, c:d]
                # if debug:
                #     if i == 9 and j == 8:
                #         cv2.imshow("red_mask", red_mask)
                rows, cols = img.shape[:2]
                for row in range(rows):
                    for col in range(cols):
                        if img[row, col] == 255:
                            white_cnt += 1
                        if red_mask[row, col] == 255:
                            red_cnt += 1
                total_point = square_y * square_x
                white_percent = round(float(white_cnt) / total_point, 3)
                red_percent = round(float(red_cnt) / total_point, 3)  # in py 2.7 int/int return int
                rate_map[i][j] = white_percent
                rate_map_red[i][j] = red_percent

                if (white_percent > confirm_rate):
                    # 现在这有一颗棋子
                    if mat1[i][j] == 0:
                        # 之前这没有棋子，这是目的地
                        to_pos[0] = i
                        to_pos[1] = j
                    else:
                        # 之前就有一颗棋子
                        if (red_percent >= red_rate):
                            # 现在是红色的
                            if mat1[i][j] > 16:
                                # 之前就是红色的，没事发生
                                pass
                            else:
                                # 之前是黑的，红吃黑
                                if debug:
                                    print("红吃黑")
                                to_pos[0] = i
                                to_pos[1] = j
                        else:
                            # 现在是黑色的
                            if mat1[i][j] <= 16:
                                # 之前就是黑色的
                                pass
                            else:
                                # 之前是红色的，黑吃红
                                if debug:
                                    print("黑吃红")
                                to_pos[0] = i
                                to_pos[1] = j

                else:
                    # 现在这没子
                    if mat1[i][j] != 0:
                        # 之前这有子，这是起点
                        from_pos[0] = i
                        from_pos[1] = j
                        move_cnt += 1
                        key_val = mat1[i][j]
        if debug:
            print(" ")
            print("红色比例图")
            for i in range(10):
                print(rate_map_red[i])
            print("比例图")
            for i in range(10):
                print(rate_map[i])
            print("棋子图")
            for i in range(10):
                print(mat1[i])
        if start == True and move_cnt != 0:
            print("待归位棋子数量：" + str(move_cnt))
            continue
        elif start == True and move_cnt == 0:
            print("已归位，游戏开始")
            start = False
        if debug:
            print("移动数量：" + str(move_cnt))
        if move_cnt == 0:
            pass
        elif move_cnt == 1 and legal == True:
            if (from_pos[0] == -1):
                if state_code != 1:
                    print("起始位置非法")
                state_code = 1
                continue
            if (to_pos[0] == -1):
                if state_code != 2:
                    print("终点位置非法")
                state_code = 2
                continue
            if (key_val == -1):
                if state_code != 3:
                    print("所拿棋子值非法")
                state_code = 3
                continue
            state_code = 0
            data[0]["pick_up"]["y"] = from_pos[0]
            data[0]["pick_up"]["x"] = from_pos[1]
            data[0]["put_down"]["y"] = to_pos[0]
            data[0]["put_down"]["x"] = to_pos[1]
            data1 = json.dumps(data[0])
            if key_val > 16:# 红子
                if net_mode:
                    tcp_client_socket.send(data1.encode())
                    recv_data = tcp_client_socket.recv(1024)
                    recv_data = recv_data.replace('{"purpose":"keepalive"}',
                                                  '')
                    cnt_error = 0
                    print("out of  recv1")
                    while (recv_data == ""):
                        print("may be recognize error")
                        time.sleep(0.1)
                        cnt_error += 1
                        if cnt_error > 40:
                            print("piece recognize error")
                            legal = False
                            break
                        print("out of  recv2")
                        recv_data = tcp_client_socket.recv(1024)
                        print(recv_data)
                        print("out of  recv3")
                        recv_data = recv_data.replace(
                            '{"purpose":"keepalive"}', '')
                    tcp_client_socket_for_ros.send(recv_data)
                    print("out of  recv")

                    if recv_data:
                        print("返回的消息为:", recv_data)

                        if recv_data == "{\"feedback\":400}":
                            legal = False
                    else:
                        print("对方已离线。。")
            if legal:
                mat1[from_pos[0]][from_pos[1]] = 0
                mat1[to_pos[0]][to_pos[1]] = key_val
                print("棋子图")
                for i in range(10):
                    print(mat1[i])
                print(dic[str(key_val)] + "从[" + str(from_pos[0]) + "," +
                      str(from_pos[1]) + "]走到了[" + str(to_pos[0]) + "," +
                      str(to_pos[1]) + "]")
        else:
            legal = False
            if state_code != 4:
                print("等待移动棋子...")
            state_code = 4
            continue
    cap.release()
    cv2.destroyAllWindows()
