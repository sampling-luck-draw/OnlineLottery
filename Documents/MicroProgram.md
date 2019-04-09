# 小程序通信流程

小程序与云端通信全部采用HTTPS方式，第一阶段不考虑Websocket。

1. 登录

   登录功能的作用是小程序通过code换取openid，openid作为判断用户身份的唯一依据，之后所有请求都必须带openid。登录接口还应附带用户的昵称、头像等基本信息，以供抽奖时使用。若用户通过扫码方式进入小程序，也可以在发送数据中附带activity_id，实现加入房间功能，以减少请求次数。

   POST: https://sampling.alphamj.cn/xcx/signin

   Payload:

   ```json
   {
       "code": "code",
       "nickName": "Anonymous",
       "avatarUrl": "avatarUrl",
       "gender": 0,
       "country": "Solar System",
       "province": "Alpha Centauri",
       "city": "Proxima Centauri",
       "language": "Xenolinguistics",
       "activity_id": 1
   }
   ```
   Response:

   ```json
   {
       "result": "ok",
       "openid": "openid",
       "session_key": "session_key",
       "activity_name": "才明洋表彰大会",   // 仅当设置activity_id时
       "activity_status": "Pedding|Running|Finished|no such activity"
   }
   ```

   ```json
   {"result":"error", "msg":"no code"}
   ```

2. 加入

   如果用户在打开程序后再扫码，可调用该API加入活动。可能出现的错误有：“无此用户”和“无此活动”，若返回“无此用户”则必须先调用login接口获得正确openid

   POST: https://sampling.alphamj.cn/xcx/join

   Payload

   ```json
   {
       "openid": "openid",
       "activity_id": 4
   }
   ```

   Response

   ```json
   {
       "result": "ok"
       "activity_name": "才明洋表彰大会",
       "activity_status": "Pedding|Running|Finished"
   }
   ```

   ```json
   {
       "result": "error",
       "msg": "no such user|no open id or activity|no such activity"
   }
   ```

3. 发送弹幕

   POST: https://sampling.alphamj.cn/xcx/sanddanmu

   Payload

   ```json
   {
       "openid": "openid",
       "danmu": "danmu"
   }
   ```

   Response

   ```json
   {"result": "ok"}
   ```

   ```json
   {"result":"error", "msg":"no openid"}
   ```

   ```json
   {"result":"error", "msg":"no danmu"}
   ```

   ```json
   {"result":"error", "msg":"no such user"}
   ```

   ```json
   {"result":"error", "msg":"no such activity"}
   ```
