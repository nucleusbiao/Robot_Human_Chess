/*! 一叶孤舟 | qq:28701884 | 欢迎指教
*/

var play = play || {};
//ws
eaten=0;

play.init = function (depth, map) {
	var map = map || com.initMap;
	var depth = depth || 4
	play.my = 1;				//玩家方
	play.nowMap = map;
	play.map = com.arr2Clone(map);		//初始化棋盘
	play.nowManKey = false;			//现在要操作的棋子
	play.pace = [];				//记录每一步
	play.isPlay = true;			//是否能走棋

	play.bylaw = com.bylaw;
	play.show = com.show;
	play.showPane = com.showPane;
	play.isOffensive = true;			//是否先手
	play.depth = depth;			//搜索深度
	play.isFoul = false;			//是否犯规长将
	com.pane.isShow = false;			//隐藏方块

	//清除所有旗子
	play.mans = com.mans = {};

	//这么搞有点2，以后说不定出啥问题，先放着记着以后改
	com.childList.length = 3

	com.createMans(map)		//生成棋子	
	com.bg.show();

	//初始化棋子
	for (var i = 0; i < play.map.length; i++) {
		for (var n = 0; n < play.map[i].length; n++) {
			var key = play.map[i][n];
			if (key) {
				com.mans[key].x = n;
				com.mans[key].y = i;
				com.mans[key].isShow = true;
			}
		}
	}
	play.show();

	//绑定点击事件
	com.canvas.addEventListener("click", play.clickCanvas)
	//clearInterval(play.timer);
	//com.get("autoPlay").addEventListener("click", function(e) {
	//clearInterval(play.timer);
	//play.timer = setInterval("play.AIPlay()",1000);
	//	play.AIPlay()
	//})
	/*
	com.get("offensivePlay").addEventListener("click", function(e) {
		play.isOffensive=true;
		play.isPlay=true ;	
		com.get("chessRight").style.display = "none";
		play.init();
	})
	
	com.get("defensivePlay").addEventListener("click", function(e) {
		play.isOffensive=false;
		play.isPlay=true ;	
		com.get("chessRight").style.display = "none";
		play.init();
	})
	*/



	/*
	var initTime = new Date().getTime();
	for (var i=0; i<=100000; i++){
		
		var h=""
		var h=play.map.join();
		//for (var n in play.mans){
		//	if (play.mans[n].show) h+=play.mans[n].key+play.mans[n].x+play.mans[n].y
		//}
	}
	var nowTime= new Date().getTime();
	z([h,nowTime-initTime])
	*/

}
//悔棋
play.regret = function () {
	var map = com.arr2Clone(com.initMap);
	//初始化所有棋子
	for (var i = 0; i < map.length; i++) {
		for (var n = 0; n < map[i].length; n++) {
			var key = map[i][n];
			if (key) {
				com.mans[key].x = n;
				com.mans[key].y = i;
				com.mans[key].isShow = true;
			}
		}
	}
	var pace = play.pace;
	pace.pop();
	pace.pop();

	for (var i = 0; i < pace.length; i++) {
		var p = pace[i].split("")
		var x = parseInt(p[0], 10);
		var y = parseInt(p[1], 10);
		var newX = parseInt(p[2], 10);
		var newY = parseInt(p[3], 10);
		var key = map[y][x];
		//try{

		var cMan = map[newY][newX];
		if (cMan) com.mans[map[newY][newX]].isShow = false;
		com.mans[key].x = newX;
		com.mans[key].y = newY;
		map[newY][newX] = key;
		delete map[y][x];
		if (i == pace.length - 1) {
			com.showPane(newX, newY, x, y)
		}
		//} catch (e){
		//	com.show()
		//	z([key,p,pace,map])

		//	}
	}
	play.map = map;
	play.my = 1;
	play.isPlay = true;
	com.show();
}
//点击棋盘事件
play.clickCanvas = function (e) {
	if (!play.isPlay) return false;//是否玩家在玩
	var key = play.getClickMan(e);//获得棋子
	var point = play.getClickPoint(e);//获得点击的坐标

	var x = point.x;
	var y = point.y;

	if (key) {//如果点的不是空位，那就是选棋，或吃子
		play.clickMan(key, x, y);
	} else {//如果点的是空位，那只能是目标位置
		play.clickPoint(x, y);
	}
	play.isFoul = play.checkFoul();//检测是不是长将
}

play.clickMan = function (key, x, y) {//点击棋子，两种情况，选中或者吃子
	console.log(key,x,y)
	var man = com.mans[key];
	//吃子
	if (play.nowManKey && play.nowManKey != key && man.my != com.mans[play.nowManKey].my) {
		//man为被吃掉的棋子
		if (play.indexOfPs(com.mans[play.nowManKey].ps, [x, y])) {
			man.isShow = false;
			var pace = com.mans[play.nowManKey].x + "" + com.mans[play.nowManKey].y
			//z(bill.createMove(play.map,man.x,man.y,x,y))
			delete play.map[com.mans[play.nowManKey].y][com.mans[play.nowManKey].x];
			play.map[y][x] = play.nowManKey;
			com.showPane(com.mans[play.nowManKey].x, com.mans[play.nowManKey].y, x, y)
			com.mans[play.nowManKey].x = x;
			com.mans[play.nowManKey].y = y;
			com.mans[play.nowManKey].alpha = 1

			play.pace.push(pace + x + y);
			play.nowManKey = false;
			com.pane.isShow = false;
			com.dot.dots = [];
			com.show()
			com.get("clickAudio").play();
			setTimeout(play.AIPlay, 500);
			if (key == "j0") play.showWin(-1);
			if (key == "J0") play.showWin(1);
		}
		// 选中棋子
	} else {
		if (man.my === 1) {
			if (com.mans[play.nowManKey]) com.mans[play.nowManKey].alpha = 1;
			man.alpha = 0.8;
			com.pane.isShow = false;
			play.nowManKey = key;
			com.mans[key].ps = com.mans[key].bl(); //获得所有能着点
			com.dot.dots = com.mans[key].ps
			com.show();
			//com.get("selectAudio").start(0);
			com.get("selectAudio").play();
		}
	}
}

play.clickPoint = function (x, y) {//点击着点
	var key = play.nowManKey;
	var man = com.mans[key];
	if (play.nowManKey) {
		if (play.indexOfPs(com.mans[key].ps, [x, y])) {
			var pace = man.x + "" + man.y
			//z(bill.createMove(play.map,man.x,man.y,x,y))
			delete play.map[man.y][man.x];
			play.map[y][x] = key;
			com.showPane(man.x, man.y, x, y)
			man.x = x;
			man.y = y;
			man.alpha = 1;
			play.pace.push(pace + x + y);
			play.nowManKey = false;
			com.dot.dots = [];
			com.show();
			com.get("clickAudio").play();
			setTimeout(play.AIPlay, 500);
		} else {
			if(ws.readyState){
				ws.send(JSON.stringify({
					"feedback":400, //不能这么走
				}))
			}
		}
	}

}

play.AIPlay = function () {//Ai自动走棋
	//return
	play.my = -1;//是不是人在下棋
	var pace = AI.init(play.pace.join(""))
	console.log(pace)//显示ai走法
	//赢了
	if (!pace) {
		play.showWin(1);
		return;
	}
	//记录走法
	play.pace.push(pace.join(""));
	var key = play.map[pace[1]][pace[0]]
	play.nowManKey = key;

	var key = play.map[pace[3]][pace[2]];
	eaten=0;
	if (key) {
		eaten=1;
		play.AIclickMan(key, pace[2], pace[3]);//吃子	
	} else {
		eaten=0;
		play.AIclickPoint(pace[2], pace[3]);	//走子
	}
	com.get("clickAudio").play();//播放声音
	if(ws.readyState==true){
		let s={
			"feedback":200, //收到请求
			"eat":eaten,
			"pick_up":{//pace是 y x y x 存储的
				"x":play.pace[play.pace.length-1][1],
				"y":play.pace[play.pace.length-1][0]
				}, // 拿起棋子位置。
			"put_down":{
				"x":play.pace[play.pace.length-1][3],
				"y":play.pace[play.pace.length-1][2]
				}, // 棋子目标位置。
		}
		ws.send(JSON.stringify(s))
	}else{
		console.log("ws is not ready")
	}
}

play.checkFoul = function () {//检查是否长将
	var p = play.pace;
	var len = parseInt(p.length, 10);
	if (len > 11 && p[len - 1] == p[len - 5] && p[len - 5] == p[len - 9]) {
		return p[len - 4].split("");
	}
	return false;
}

play.AIclickMan = function (key, x, y) {//AI吃子
	console.log(key,x,y)
	var man = com.mans[key];
	//吃子
	man.isShow = false;
	//删除原位置棋子
	delete play.map[com.mans[play.nowManKey].y][com.mans[play.nowManKey].x];
	play.map[y][x] = play.nowManKey;
	play.showPane(com.mans[play.nowManKey].x, com.mans[play.nowManKey].y, x, y)

	com.mans[play.nowManKey].x = x;
	com.mans[play.nowManKey].y = y;
	play.nowManKey = false;

	com.show()
	if (key == "j0") play.showWin(-1);
	if (key == "J0") play.showWin(1);
}

play.AIclickPoint = function (x, y) {//AI走子
	var key = play.nowManKey;
	var man = com.mans[key];
	if (play.nowManKey) {
		delete play.map[com.mans[play.nowManKey].y][com.mans[play.nowManKey].x];
		play.map[y][x] = key;

		com.showPane(man.x, man.y, x, y)
		man.x = x;
		man.y = y;
		play.nowManKey = false;

	}
	com.show();
}
play.indexOfPs = function (ps, xy) {
	for (var i = 0; i < ps.length; i++) {
		if (ps[i][0] == xy[0] && ps[i][1] == xy[1]) return true;
	}
	return false;
}

play.getClickPoint = function (e) {//获得点击的着点
	var domXY = com.getDomXY(com.canvas);
	var x = Math.round((e.pageX - domXY.x - com.pointStartX - 20) / com.spaceX)
	var y = Math.round((e.pageY - domXY.y - com.pointStartY - 20) / com.spaceY)
	console.log({ "x": x, "y": y })
	return { "x": x, "y": y }
}

play.getClickMan = function (e) {//获得棋子
	var clickXY = play.getClickPoint(e);
	var x = clickXY.x;
	var y = clickXY.y;
	if (x < 0 || x > 8 || y < 0 || y > 9) return false;
	return (play.map[y][x] && play.map[y][x] != "0") ? play.map[y][x] : false;
}
play.showWin = function (my) {//胜负已分
	play.isPlay = false;
	if (my === 1) {
		if(ws.readyState){
			ws.send(JSON.stringify({
				"purpose":"result", // 目的。反馈结果
				"winner":"player",//谁赢了。
			}))
		}
		alert("恭喜你，你赢了！");
	} else {
		if(ws.readyState){
			ws.send(JSON.stringify({
				"purpose":"result", // 目的。反馈结果
				"winner":"robot",//谁赢了。
			}))
		}
		alert("很遗憾，你输了！");
	}
}

