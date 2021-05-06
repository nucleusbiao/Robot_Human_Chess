var ip =    "localhost";
var port = "8004";
var ws = new WebSocket("ws://" + ip + ":" + port + "/echo");
ws.onopen = function ()
{
	setInterval(() => {
		let s={"purpose":"keepalive"}
		ws.send(JSON.stringify(s))
	}, 30000);// 保活操作
}

ws.onmessage = function (evt)
{
	let msg =  JSON.parse(evt.data);
	console.log(msg)
	switch(msg['purpose']){

		case "sync_map":// 无用
			if(msg['isInit'])
				play.init(4)
			else{

			}
			break;
		case "update_map"://更新棋盘
			ws.send(JSON.stringify({"purpose":"keepalive"}))
			console.log(msg)
			//拿子
			var x=msg.pick_up.x;
			var y=msg.pick_up.y;
			var key=play.map[y][x];//map是 y x 布局
			console.log(key,x,y);
			if(key == undefined){
				ws.send(JSON.stringify({"feedback":500}))
				break;
			}
			
			play.clickMan(key, x, y);
			//落子
			var x=msg.put_down.x;
			var y=msg.put_down.y;
			console.log(x,y)
			var key=play.map[y][x];
			if (key == undefined){//落子
				play.clickPoint(x, y);
			}else{//吃子
				play.clickMan(key, x, y);
			}
			
			break;
		case "newGame":// 新一局游戏
			play.isPlay=true ;
			play.init( play.depth,play.nowMap );
			msg.whoFirst=="robot"?play.isOffensive=false:play.isOffensive=true;	
			let s={
				"feedback":200, //收到请求
			}
			ws.send(JSON.stringify(s))
			break;
		default:
			break;
	}	
}

ws.onclose = function (evt){
	document.getElementById("xycoordinates").innerHTML=("sorry,服务器已关闭");
}
function user_click(x,y){
    var ev = document.createEvent("MouseEvent");
    var el = document.elementFromPoint(x,y);
    ev.initMouseEvent(
        "click",
        true /* bubble */, true /* cancelable */,
        window, null,
        x, y, 0, 0, /* coordinates */
        false, false, false, false, /* modifier keys */
        0 /*left*/, null
    );
	el.dispatchEvent(ev);
}