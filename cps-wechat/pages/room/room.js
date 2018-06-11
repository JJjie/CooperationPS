// const io = require('../../utils/weapp.socket.io.js')
// const socket = io("http://localhost:8000")

var app = getApp()
Page({
  data: {
    // room_num:2875,
  },
  onLoad: function (options) {
    // socket.on('connect', function () {
    //   socket.emit('my event', { data: 'I\'m connected!' });
    // });
    // socket.on('disconnect', function () {
    //   $('#log').append('<br>Disconnected');
    // });
    // socket.on('my response', function (msg) {
    //   $('#log').append('<br>Received: ' + msg.data);
    //   console.log(msg)
    // });
  },
  start_ps:function(){
    wx.navigateTo({
      url: '../ps/ps'
    })
  }
  
})