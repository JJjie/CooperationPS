const io = require('utils/weapp.socket.io.js')
//app.js
App({
  onLaunch: function () {
    var that=this;
    //调用API从本地缓存中获取数据
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs);
    //全局socketio
    const socket = io.connect("ws://localhost:8000/cps")
    socket.on('connect', function () {
      console.log('connect');
      socket.emit('my event', { data: 'I\'m connected!' });
    });
    socket.on('disconnect', function () {
      console.log('Disconnected');
    });
    socket.on('my response', function (msg) {
      if (msg.data == 'I\'m connected!'){
        console.log(msg);
      }
      // that.globalData.msg = msg;
    });
    that.globalData.socket = socket;
  },
  
  globalData:{
    userInfo:null,
    nickName:'',
    msg:''

  }
})