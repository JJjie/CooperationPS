
var app = getApp()
const socket = app.globalData.socket;
Page({
  data: {
    nickName: '',
    hidden:true,
    input_num:''
  },
  
  onLoad: function () {
    // console.log('onLoad');
    socket.on('my response', function (msg) {
      console.log('response');
      console.log(msg);
      app.globalData.msg = msg;
      wx.navigateTo({
        url: '../room/room?roomid=' + msg.roomid
      });
    });
  },
  //事件处理函数
  enter: function () {
    var that = this;
    that.setData({hidden:false});
    
    // wx.navigateTo({
    //   url: '../logs/logs'
    // })
  },
  build: function () {
    var that = this;
    socket.emit('createRoom', { userid: that.data.nickName });
    
    // const msg = app.globalData.msg;
    // console.log(msg);
    
  },
  confirm: function(){
    var that = this;
    var roomid = that.data.input_num;
    var userid = that.data.nickName
    console.log(roomid,userid);
    socket.emit('joinRoom', { roomid: roomid, userid: userid });
    wx.navigateTo({
      url: '../room/room?roomid=' + roomid
    })
  },
  cancel: function(){
    var that = this;
    that.setData({ hidden: true });
  },
  bindnum:function(e){
    var that = this;
    that.setData({
      input_num: e.detail.value
    });  
  },
  getUserInfo: function (cb) {
    var that =this;
    if (app.globalData.userInfo) {
      typeof cb == "function" && cb(app.globalData.userInfo)
    } else {
      //调用登录接口
      wx.login({
        success: function () {
          wx.getUserInfo({
            withCredentials: true,
            success: function (res) {
              app.globalData.userInfo = res.userInfo
              typeof cb == "function" && cb(app.globalData.userInfo)
              that.setData({ nickName: res.userInfo.nickName})
            }
          })
        }
      })
    }
  },
  
})
