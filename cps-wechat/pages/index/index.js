const io = require('../../utils/weapp.socket.io.js')

var app = getApp()
Page({
  data: {
    // userInfo: {}
  },
  
  onLoad: function () {
    console.log('onLoad');
    const socket = io.connect("ws://localhost:8000");
    socket.on('connect', function () {
      console.log('connect');
      socket.emit('my event', { data: 'I\'m connected!' });
    });
    socket.on('disconnect', function () {
      console.log('Disconnected');
    });
    socket.on('my response', function (msg) {
      console.log('response');
      console.log(msg);
    });
   
  },
  //事件处理函数
  enter: function () {

    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  build: function () {
    
    socket.emit('createRoom', { userid: $('#create_room').val() });
    wx.navigateTo({
      url: '../room/room'
    })
  },
})
