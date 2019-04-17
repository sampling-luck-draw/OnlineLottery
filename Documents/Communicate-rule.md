## 与云端通信流程

1. 用户登陆 [已测试]

   POST: https://sampling.alphamj.cn/signin

   Payload: 

   ```json
   {"username":"用户名", "password":"密码"}   // 验证码？
   ```

   Response: 
   ```json
   {"result": "success", "uid": user.id}
   ```
   ```json
   {"result": "error", "msg": "相应的错误信息"}
   ```

   返回数据头包括COOKIE和SESSION，请求其他业务时应附带SESSION信息，作为身份验证。

2. 用户注册 [已测试]

   POST: https://sampling.alphamj.cn/signup

   Payload: 
   ```json
   {"username":"用户名", "password":"密码", "email": "邮箱"}
   ```

   Response: 
   ```json
   {"result": "success", "uid": user.id}
   ```
   ```json
   {"result": "error", "msg": "相应的错误信息"}
   ```

   返回数据头包括COOKIE和SESSION

3. 获取活动列表 [已测试]

   GET: https://sampling.alphamj.cn/get-activities

   Payload: 无

   Response: 

   ```json
   [
       {"id": 4, "name": "东北大学才明洋表彰大会", "start_time": "2019-02-30 08:20:18", "end_time": "2019-2-31 20:17:24"},
       {}
   ]
   ```

4. 创建新活动 [已测试]

   POST: https://sampling.alphamj.cn/append-activity

   Payload:

   开始和结束时间均为可选

   ```json
   {
       "name": "东北大学才明洋表彰大会"
       [,"start_time": "%Y-%m-%d %H:%M:%S"]
       [,"end_time": "结束时间"]
   }
   ```

   Response:

   ```json
   {
       "activity_id": 1
   }
   ```

5. 获取小程序码 [未测试：小程序未发布]

   GET: https://sampling.alphamj.cn/xcx/get-qr?activity_id=<activity_id>

   Response:

   图片的二进制数据或包含错误信息的json，用返回的Content-Type区分。

6. 建立连接 [已测试]

   wss://sampling.alphamj.cn/ws/[<活动id>]

   建立ws连接时必须附带Session信息，否则服务器会拒绝服务。

   活动id为可选项，若无此id，服务器自动选择最近的活动建立连接

   连接时可能出现的错误如下：

   ```json
   {"error":"unauthenticated"}
   ```
   ```json
   {"error":"invalid id"}
   ```

   以下为可能的数据包格式

   当成功连接时，服务器会回复“BLXDNZ”。

   1. 添加用户：云 -> 本地 [已测试]

      ```json
      {"action": "append-user", 
       "content": {
           "avatar": "头像地址", 
           "nickname": "Yeah...TT", 
           "language": "zh_CN", 
           "country": "China", 
           "province": "Jilin", 
           "gender": 1, 
           "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX", 
           "city": "Yanbian"
       }
      }
      ```

   2. 发送弹幕：云 -> 本地 [已测试]

      ```json
      {"action": "send-danmu", 
       "content": {"danmu": "kao", "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX"}}
      ```

   3. 修改活动设置信息：本地 -> 云 [已测试]

      ```json
      {"action": "modify-activity" , "content": {"要修改的信息字典":""}}
      ```

   4. 中奖：本地 -> 云  [已测试]

      ```json
      {"action": "lucky-dog", "content": {"uid": "uid", "award":  "奖项名称"}}
      ```

   5. 请求用户列表：本地->云 [已测试]

      ```json
      {"action": "get-participants"}
      ```

   6. 发送用户列表：云->本地 [已测试]

      ```json
      {"action": "participants", 
      "content": [
          {"avatar": "头像地址", "nickname": "Yeah...", "language": "zh_CN", "nickName": "Yeah...", "country": "China", "province": "Jilin", "gender": 1, "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX", "city": "Yanbian"},
          {}
      ]}
      ```

   7. 添加奖项：本地->云 [已测试]

      ```json
      {"action": "append-award",
       "content": {
           "name": "一等奖",
           "prize": "兰博基尼五元优惠券",
           "amount": 10
       }}
      ```

   8. 删除奖项：本地->云 [已测试]

      ```json
      {"action": "delete-award",
       "content": {
           "name": "一等奖"
       }}
      ```

   9. 获得奖项列表：本地->云 [已测试]

      ```json
      {"action": "get-awards"}
      ```

   10. 发送奖项列表：云->本地 [已测试]

     ```json
     {"action": "awards", "content": [{"id": 1, "award_name": "一等奖", "prize_name": "兰博基尼五元优惠券", "amount": 10, "activity_id": 1}]}
     ```

   11. 请求中奖人列表：本地->云 [已测试]

      ```json
      {"action": "get-lucky-dogs"}
      ```

   12. 请求活动信息：本地->云 [已测试]

       ```json
       {"action": "get-activity-info"}
       ```

   13. 发送活动信息：云->本地 [已测试]

      ```json
      {"action":"activity-info",
       "content": {
           "name": "才明洋表彰大会",
           "start_time": "2019-04-09 12:00:00",
           "end_time": "2019-04-09 22:00:00",
           "invite_code": "ABCDE"
      }}
      ```

