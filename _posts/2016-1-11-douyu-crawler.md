---
title: 抓取斗鱼直播弹幕
Date: 2016-1-11
category: Java
tags:
    - Java
    - Spider
---

前几天看了知乎的一个问题（[如何获取斗鱼直播间的弹幕信息？](https://www.zhihu.com/question/29027665)）之后，才有了这个想法。一直对抓取信息比较感兴趣，这次也不会错过咯，尝试一下 →.→

抓取数据的基本思路就是： 抓包 → 分析请求信息 → 模拟发送请求 → 获得数据

> 知乎回答地址：[如何获取斗鱼直播间的弹幕信息？ - Brucezz 的回答 - 知乎](https://www.zhihu.com/question/29027665/answer/80169234)


> Github 项目代码地址：[brucezz/DouyuCrawler](https://github.com/brucezz/DouyuCrawler)

最常见的就是用 Chrome 的开发者工具(F12)，然后看 Network 栏，有什么相关的 GET/POST 请求，然后构造相应的参数，用同样的方法发送给服务器，就能得到相应数据了，一般静态网页里的数据用这种方法就能搞定。当然，如果就这个简单的话，这篇博客也没有记录的必要啦，哈哈哈。

另外一个工具 Fiddler，可以捕获 HTTP/HTTPS 协议的流量。

还有一个开源的网络数据包分析软件 Wireshark，这款软件功能更为强大，支持多种协议，能够显示出最为详细的网络数据包数据。



## 0x01 初探

在直播页面的 HTML 源码里随便翻翻，发现了几点相关的 js 代码：

- `var $ROOM ={ ... }`
- `var room_args = { ... }`

这是定义了两个 js 的字典对象，也就是 JSON 格式的数据咯。用个工具格式化（[JSON在线编辑](http://www.kjson.com/jsoneditor/)）一下，看起来就很清晰啦。(省略了一些list里面的数据)

```json
{
  "room_id": 16101,
  "room_name": "微笑：  新年快乐啦啦啦~(≧▽≦)",
  "room_gg": {  },
  "room_pic": "http://staticlive.douyutv.com/upload/web_pic/201601/1/16101_1601111612_thumb.jpg",
  "owner_uid": 391270,
  "owner_name": "微笑",
  "show_status": 1,
  "room_url": "http://www.douyutv.com/weixiao",
  "show_id": 8557130,
  "room_pwd": 0,
  "cate_id": 1,
  "cate_name": "英雄联盟",
  "cate_url": "/directory/game/LOL",
  "near_show_time": 0,
  "game_cate_list": {  },
  "all_tag_list": {  },
  "room_tag_list": [  ],
  "show_time": 1452496988,
  "widgetType": 0,
  "widgetPosition": 0
}
```

其中，一些参数的含义：

- room_id：房间id
- owner_name：主播名
- show_status：当前直播状态，正在直播为1
- room_url：房间地址

```json
{
  "rpc_switch": 1,
  "leve_json": {  },
  "exp_level": {  },
  "no_home": 0,
  "no_home_time": "",
  "live_url": 0,
  "res_path": "/common/",
  "swf_url": "http://staticlive.douyutv.com/common/simplayer/WebRoom.swf?v21680",
  "server_config": [
    {
      "ip": "119.90.49.109",
      "port": "8044"
    },
    {
      "ip": "119.90.49.104",
      "port": "8017"
    }
  ],
  "def_disp_gg": 0
}
```

其中，`server_config` 字段的数据需要 UrlDecode 解码一下([UrlEncode编码/UrlDecode解码](http://tool.chinaz.com/tools/urlencode.aspx))，才能看到原本的面目。(省略了其他几个服务器地址)

参数：

- leve_json：定义了一些房间粉丝等级的标签
- server_config：一组服务器地址 ip:port ，后面会用到

页面里还输出了其他几个JSON数据`effectConfig`，`giftBatterConfig`，分别是定义了一些礼物的前端效果和对应代码，有需要的时候再去分析。


## 0x02 抓包分析

既然上面拿到的服务器的地址，就尝试监听一下这几个端口吧，看看有些什么数据发送到服务器了。

用 Wireshark 监听当前网络，过滤条件设置为

`tcp.port==8046||tcp.port==8044||tcp.port==8071||tcp.port==8068||
tcp.port==8058||tcp.port==8059||tcp.port==8054||tcp.port==8045||tcp.port==8061&&tcp.flags.push==1`

就是过滤监听相应的几个端口，然后我们就能看到本地和服务器通信的数据包啦。

这里有个小插曲，上面这段过滤条件很长嘛，我每次调试的时候它都会变，就得重新拼接这么长个字符串。我实在忍不了了，就写了个 [Python 小脚本](https://gist.github.com/brucezz/aa6cb1f144703287081e0543af32753b)，自动生成过滤字符串！用法如下：

- 启动脚本，输入从直播房间 HTML 上复制下来的源代码
- 复制出生成的过滤条件字符串
- 粘贴到 Wireshark 里就OK啦！

注：不用刻意去复制对称的引号/括号等等，只要包含整个 `server_config` 字段就好了，如图

效果图 Here～

![prot_filter.py效果图](/images/douyu-crawler-port-filter.png)

好了，先看第一个包，长得就是下面这样了。

![登录服务器抓包](/images/douyu-crawler-1.png)


前面是tcp三次握手的数据包，就不详写了。从蓝色框框位置开始，是正文内容。

正文包含五个部分：

1. 数据长度，大小为后四部分的字节长度，占4个字节
2. 内容和第一部分一样，4字节
3. 斗鱼固定的请求码，本地->服务器是 `0xb1,0x02,0x00,0x00`，服务器->本地是 `0xb2,0x02,0x00,0x00`，4字节
4. 消息内容
5. 尾部一个空字节 `0x00`

消息内容：

```
type@=loginreq/ # 请求类型
username@=/ # 用户名，匿名为空
ct@=0/ # 未知，设为0即可
password@=/ # 密码
roomid@=16101/ # 直播房间id
devid@=1C01371705D8B13361396AE2FAD50D6F/ # 设备id 32位大写16进制
rt@=1452508198/ # 请求时间戳 秒
vk@=2dcf0e6f1d16e45932a343bb71d5d0ad/ # 某一种key 32位
ver@=20150929/. # 版本号
```

然后，看服务器返回了什么东西。

![登录服务器返回数据](/images/douyu-crawler-2.png)

这张图片就证实了，前面说的斗鱼固定的请求码，服务器返回的是 `0xb2,0x02,0x00,0x00` 四个字节。然后返回了匿名用户的用户名，基本上没什么用。

紧接着，服务器又返回了一条数据。

![登录服务器返回数据2](/images/douyu-crawler-3.png)

这条包大概是多条返回数据合并到一起了，没关系，一个一个来看。

消息类型为 `msgrepeaterlist`, 里面包含了一组可用的弹幕服务器地址，数据看起来包含了一堆@符号，是因为用了js代码进行编码。

我用 Chrome 找到了相应的js文件，然后把代码转化为 Java 代码，大概就长下面这个样子：

```java
 public static String deFilterStr(String str) {
      if (str == null) return null;
      return str.trim().replace("@A", "@").replace("@S", "/");
  }

  public static String filterStr(String str) {
      if (str == null) return null;
      return str.trim().replace("@", "@A").replace("/", "@S");
  }
```

解码出来，通过 `/` 字符可以把字符串分割成多个以 `@=` 连接的键值对。其实这个操作也可以用正则来完成。

这样就能得到弹幕服务器的地址了，总共就四个：

```
danmu.douyutv.com:8061
danmu.douyutv.com:8062
danmu.douyutv.com:12601
danmu.douyutv.com:12602
```

后面一条消息，类型为 `setmsggroup`， 里面包含了房间编号即 `rid` 和弹幕群组编号即 `gid` 。

其余的消息，暂时没发现有什么用途。

然后来监听下弹幕服务器的端口，看看有什么数据。
设置下过滤条件： `tcp.port==8061||tcp.port==8062||tcp.port==12601||tcp.port==12602&&tcp.flags.push==1`

一来就发现了要找的数据包。

![弹幕服务器请求数据](/images/douyu-crawler-4.png)

向弹幕服务器发送了一条类型为 `loginreq` 的消息，消息格式如下：

```
type@=loginreq/
username@=visitor503535/
password@=1234567890123456/
roomid@=16101/.
```

这个包的格式比较简单，匿名登陆的话，用户名和密码随意就好，`roomid` 就是目标房间的id。

此时，服务器对应返回了一条没有价值的消息，忽略掉。

然后本地又发送了一条请求加入弹幕群组的消息。

![弹幕服务器请求数据2](/images/douyu-crawler-5.png)

```
type@=joingroup/
rid@=16101/
gid@=27/.
```

其中，`rid` 就是房间id，`gid` 是前面从服务器拿到的弹幕群组编号。

这两条消息发送完之后，就是登陆成功了。服务器不断向本地发送弹幕数据，以及鱼丸礼物信息等等。

我这里只简单地解析下弹幕的数据包，对于其他数据包方法一样。

![弹幕服务器返回数据](/images/douyu-crawler-6.png)

消息类型为 `chatmessage` , 其中：

- sender大概和用户id类似
- content为弹幕内容，由于是非 ASCII 字符，在 Wireshark 里没有显示出来
- snick为用户昵称
- chatmsgid为弹幕唯一id

可以直接用正则表达式提取出来。

另外，根据[心跳包机制](http://baike.baidu.com/view/1491229.htm)，我们要不断向服务器发送心跳包，以保持连接。

通过抓包能看到心跳包的样子：

![心跳包数据](/images/douyu-crawler-7.png)

一条类型为 `mrkl`(mark keep live ?) 的消息。

至此，抓包分析基本上就搞定了，每一个包的格式也搞明白了，接下来就是模拟发送相同的包，去请求服务器了。

## 0x03 模拟请求

根据前面抓包分析的结果，模拟过程大概是这样子的：

1. 获取直播房间 HTML 页面，提取出服务器地址和房间ID号
2. 选择一个服务器，发送登陆消息
3. 接收服务器返回的弹幕群组编号 `gid` 和弹幕服务器地址
4. 选择一个弹幕服务器，发送登陆请求和加入群组的请求
5. 读取服务器返回的弹幕数据
6. 定时发送心跳包


这里主要写一下第三步，向服务器发送请求，获取 `gid` , 数据格式如下：

```
type@=loginreq/ # 请求类型
username@=/ # 用户名，匿名为空
ct@=0/ # 未知，设为0即可
password@=/ # 密码
roomid@=16101/ # 直播房间id
devid@=1C01371705D8B13361396AE2FAD50D6F/ # 设备id 32位大写16进制
rt@=1452508198/ # 请求时间戳 秒
vk@=2dcf0e6f1d16e45932a343bb71d5d0ad/ # 某一种key 32位
ver@=20150929/. # 版本号
```

对应的 Java 请求代码

```java
    socket = new Socket(server.getHost(), server.getPort());//Socket连接服务器

    String timestamp = String.valueOf(System.currentTimeMillis() / 1000);//获取当前时间戳
    String uuid = UUID.randomUUID().toString().replace("-", "").toUpperCase();//构造uuid作为devid参数
    String vk = MD5Util.MD5(timestamp + "7oE9nPEG9xXV69phU31FYCLUagKeYtsF" + uuid);//vk参数
    //发送登陆请求
    MessageHandler.send(socket, Request.gid(rid, uuid, timestamp, vk));
    //等待接收
    MessageHandler.receive(socket, loginListener);
```

> 其中vk参数的算法， `vk = MD5(timestamp + "7oE9nPEG9xXV69phU31FYCLUagKeYtsF" + devid)` ，
> 我还不是很明白，在 Github 上看到的。[reusu/DouyuAssistant - Github](https://github.com/reusu/DouyuAssistant)



最终在控制台的效果，就是这样啦，当然也可以顺便保存到数据库里，可以积累数据然后进行分析。

![控制台效果图](/images/douyu-crawler-final.png)


## 0x04 后记

这次抓取斗鱼弹幕，涨了不少姿势呢。

- Wireshark 过滤数据包技巧
- 从抓取 HTTP 数据到抓取 TCP 数据
- Java Socket / IO / Thread coding （虽然依然很low）

---


> 知乎回答地址：[如何获取斗鱼直播间的弹幕信息？ - Brucezz 的回答 - 知乎](https://www.zhihu.com/question/29027665/answer/80169234)


> Github 项目代码地址：[brucezz/DouyuCrawler](https://github.com/brucezz/DouyuCrawler)

---

参考：

1. [如何获取斗鱼直播间的弹幕信息？ - 天白才痴 的回答](https://www.zhihu.com/question/29027665/answer/75117632)
2. [斗鱼弹幕抓取 | 霹雳啪啦程序汪](http://ndrlslz.github.io/2015/12/26/%E6%96%97%E9%B1%BC%E5%BC%B9%E5%B9%95%E6%8A%93%E5%8F%96/)
3. [reusu/DouyuAssistant - Github](https://github.com/reusu/DouyuAssistant)
