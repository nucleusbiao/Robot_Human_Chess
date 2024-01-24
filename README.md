# Robot_Human_Chess
human vs robot on Chinese chess
一、机械臂部分：
	catkin_workspace\src\ros_kortex\kortex_examples\src\full_arm\example_cartesian_poses_with_notifications.py
	ros控制机械臂核心代码，搭建好控制机械臂环境后，备份原文件，替换该文件运行

二、网页决策端：
	chess文件夹下浏览器打开index.html
	
三、棋盘识别：
	recognise.py

四、中转：
	server.nodejs
	
五、气泵：
	使用arduino ide刷入arduino设备
	
运行环境：
	nodejs，python，ros
	
运行方法：
	1、再更改三里的correct_mode=true，net_mode=false对准好棋盘，后改回
	2、先运行四，再运行二，再运行一，最后运行三
	
常见问题：
	运行一出现端口占用，同时修改一，三中对应端口号即可

 Demo Video<br/>
![](chess.gif)
