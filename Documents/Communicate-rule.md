## 与云端通信流程

要不要csrf_token？

1. 用户登陆

   POST: https://sampling.alphamj.cn/signin

   DATA: {"username":"用户名", "password":"密码"}   // 验证码？

   RET: {"result": "success", "uid": user.id}

   ​         {"result": "error", "msg": "相应的错误信息"}

   返回数据头包括COOKIE和SESSION，请求其他业务时应附带SESSION信息，作为身份验证。

2. 用户注册

   POST: https://sampling.alphamj.cn/signup

   DATA: {"username":"用户名", "password":"密码", "email": "邮箱"}   // 验证码？

   RET: {"result": "success", "uid": user.id}

   ​         {"result": "error", "msg": "相应的错误信息"}

   返回数据头包括COOKIE和SESSION

3. 建立连接

   wss://sampling.alphamj.cn/ws

   建立ws连接时必须附带Session信息，否则服务器会拒绝服务。

   以下为可能的数据包格式

   1. 添加用户：云 -> 本地

      ```json
      {"action": "append-user", 
       "content": {"avatar": "头像地址", "nickname": "Yeah...", "language": "zh_CN", "nickName": "Yeah...", "country": "China", "province": "Jilin", "gender": 1, "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX", "city": "Yanbian"}
      }
      ```

   2. 发送弹幕：云 -> 本地

      ```json
      {"action": "send-danmu", 
       "content": {"danmu": "kao", "uid": "oxwbU5M0-CCKSRFknXXXXXXXXXXX"}}
      ```

   3. 获得历史活动： 云 -> 本地

      ```json
      {"action": "history-activities", 
      "content": [
          {"id": 1,
          "name": "jgbzdh",
          "start_time": "2019-01-06 08:30:41",
          "end_time": "2019-01-06 10:30:41"
          }, {}]
      }
      ```

   4. 获得正在进行的活动： 云 -> 本地

      ```json
      {"action": "running-activity" , "content": {"活动信息字典"}}
      ```

   5. 修改活动设置信息：本地 -> 云

      ```json
      {"action": "modify-activity" , "content": {"要修改的信息字典"}}
      ```

   6. 中奖：

      ```json
      {"action": "lucky-dog", "content": {"uid": "uid"}}
      ```
      
   7. 创建新活动：
      ```json
      {"action": "create-activity", "content": {}}
      ```


