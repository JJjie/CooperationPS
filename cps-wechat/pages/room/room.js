var app = getApp()
const socket = app.globalData.socket;

Page({
  data: {
    room_id:0,
    userlist:[]
  },
  onLoad: function (options) {
    var that=this;
    console.log(app.globalData.msg);
    that.setData({
      roomid:options.roomid,
      userlist:app.globalData.msg.userid
    });
    // socket.on('my response', function (msg) {
    //   console.log('response');
    //   console.log(msg);
    // });
    // socket.on('connect', function () {
    //   socket.emit('my event', { data: 'I\'m connected!' });
    // });
    // socket.on('disconnect', function () {
    //   $('#log').append('<br>Disconnected');
    // });
    socket.on('my response', function (msg) {
      console.log(msg);
      app.globalData.msg = msg;
      that.setData({
        userlist: app.globalData.msg.userid
      });
    });
  },
  start_ps:function(){
    wx.navigateTo({
      url: '../ps/ps'
    })
  }
  
})