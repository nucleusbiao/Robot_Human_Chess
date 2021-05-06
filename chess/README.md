## 使用方法
1. 在js/ws.js文件开头填写正确nodejs所在电脑ip
2. 安装nodejs后，先运行server.nodejs（桥梁作用 网页-机器人）
3. 打开index.html
4. 识别端/机器人端程序tcp client连接 8003端口
## 通讯接口    

### 新对局（robot->server）
```json
{
    "purpose":"newGame", // 目的。新对局
}
反馈
{
    "feedback":200,//收到请求
}
```
### 更新棋盘（robot->server）
```json
{
    "purpose":"update_map", // 目的。更新棋盘 
    "pick_up":{
        "x":0,//范围[0,8],int
        "y":0,//范围[0,9],int
        }, // 拿起棋子位置。
    "put_down":{
        "x":0,
        "y":0
        }, // 棋子目标位置。
}
反馈决策
{
    "feedback":200, //收到请求 400不合法走法 500 拿子位置为空
    "isEat":0,//是否吃子。0不吃子，1吃子
    "pick_up":{
        "x":0,
        "y":0
        }, // 拿起棋子位置。
    "put_down":{
        "x":0,
        "y":0
        }, // 棋子目标位置。
}
```

### 反馈结果（server->robot）
```json
{
    "purpose":"result", // 目的。反馈结果
    "winner":"robot",//谁赢了。or player
}
反馈
{
    "feedback":200,//收到请求
}
```
map[y][x]  
--0--1--2--3--4--5--6--7--8-->X
0  
1  
2  
3  
4  
5  
6  
7  
8  
9  
Y  
### 参考
https://github.com/itlwei/Chess

