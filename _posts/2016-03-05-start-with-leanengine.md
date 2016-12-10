---
title: LeanCloud 云引擎初体验
date: 2016-03-05T00:00:00.000Z
category: Tool
tags:
  - LeanCloud
  - API
---

之前接触过 [LeanCloud](https://leancloud.cn)，一直把它当做是为移动端程序员提供的一种后端支持服务，让我们免去了繁琐的后台开发工作，通过集成 SDK 就可以直接实现云端数据存储等功能。比如，我在本地用 Python 写了一个爬虫，然后获取到一系列的数据，保存到 Leancloud 云端，再从 App 上获取云端数据，实现数据的获取与展示。

这几天我又有一个新的想法，之前云端数据仅仅是提供给自己的 App 使用，并且还需要配置 App ID/Key 和集成 SDK。如果我想把数据提供给别人使用的话，这样操作实在是不方便，而且提供 App ID 给别人会使得自己的数据也不安全 。然后就发现了 LeanCloud 有一项功能----云引擎，[官网介绍](https://leancloud.cn/docs/leanengine_guide-python.html)如下：

> 云引擎允许你编写 JavaScript 或者 Python 代码，并部署到我们的云端，通过拦截 save 请求，在保存对象之前或之后做一些事情；你可以自定义业务函数，并通过 SDK 调用；你还可以调用部分第三方库来实现自己的业务逻辑，甚至还可以将整个网站架设在云引擎之上，我们提供了网站托管服务。

也就是说我们可以在 LeanCloud 云端部署我自己的 Python 代码，那就可以在云端跑一个 Web 程序提供我们自定义的 API 服务，简单易用的 [Flask](http://flask.pocoo.org/) 框架再好不过啦 :)

下面就照着 LeanCloud 提供的文档流程走：

# 安装命令行工具

命令行工具 avoscloud 是 LeanCloud 提供的用来管理、部署云引擎项目的工具，通过简单的命令就可以部署、发布云引擎代码了。

[文档看这里](https://leancloud.cn/docs/cloud_code_commandline.html#使用)， Linux 和 Mac OSX 上都需要先安装 nodejs，然后通过 npm 安装命令行工具 avoscloud，Windows 平台就参考文档吧，我也没试过。

# 运行示例程序

文档提供了一个 Demo 程序（[python-getting-started](https://github.com/leancloud/python-getting-started)）以供参考，我们可以先按照文档的流程走一遍：

> 克隆项目 -> 添加 App ID 等信息 -> 安装项目依赖 -> avoscloud 命令启动项目。

这样就可以在本地 <http://localhost:3000> 看到效果了，同时 `avoscloud deploy` 和 `avoscloud publish` 命令分别可以把项目部署到测试环境和生产环境去。

> PS: APP_ID/APP_KEY 等信息，可以在 `你的 App 界面 -> 设置 -> 应用 Key` 找到 :)

# 改写代码，实现功能

## 1\. 返回自定义内容

打开项目可以看到，在 `wsgi.py` 里初始化了 leancloud 组件，并且获取到环境变量中的 App ID 等参数。在 `app.py` 中定义了几个路由函数：

```python
# 访问根目录 / ，会渲染 index.html 并返回
@app.route('/')
def index():
    return render_template('index.html')
```

我们可以模仿写一个自定义 API，比如访问 ['/brucezz'](http://brucezz.leanapp.cn/brucezz)，会返回相应的欢迎信息，并且格式为 JSON。

```python
# /<name> 表示，访问这样格式的url, 会映射到此函数，并返回响应结果
@app.route('/<name>')
def user(name):
    # flask.jsonify() 可以返回 JSON 字符串
    return jsonify(code=200, message='Hello, {0}~'.format(name))
```

返回结果如下：

```json
{
  "code": 200,
  "message": "Hello, brucezz~"
}
```

当然这个 API 也太简单了，实际使用肯定会有更多的逻辑处理。

## 2\. 从 LeanCloud 云端数据返回

这个 Web 程序当然也可以通过集成 leancloud-sdk ，来实现对 LeanCloud 云端数据的访问。

先写一个类 Skill 继承自 leancloud.Object，然后用装饰器设置几个属性。

```python
import leancloud

class Skill(leancloud.Object):
    @property
    def name(self):
        return self.get('name')

    @property
    def rank(self):
        return self.get('rank')

if __name__ == '__main__':
    # 添加几组数据供测试
    APP_ID = '你的APP_ID'
    MASTER_KEY = '你的MASTER_KEY'

    leancloud.init(APP_ID, master_key=MASTER_KEY)
    Skill(name='Python',rank=1).save()
    Skill(name='Java',rank=2).save()
    Skill(name='Swift',rank=3).save()
    Skill(name='C#',rank=4).save()
    Skill(name='Ruby',rank=5).save()
```

然后在 `app.py` 中编写路由函数：

```python
@app.route('/skill')
def all_skill():
    return jsonify(code=200, skills=get_all_skill())

def get_all_skill():
    query = Query(Skill).ascending('rank')
    return [{'name':skill.name,'rank':skill.rank} for skill in query.find()]
```

访问 ['/skill'](http://brucezz.leanapp.cn/skill) 返回结果如下：

```json
{
    "code": 200,
    "skills": [
        {
            "name": "Python",
            "rank": 1
        },
        {
            "name": "Java",
            "rank": 2
        },
        {
            "name": "Swift",
            "rank": 3
        },
        {
            "name": "C#",
            "rank": 4
        },
        {
            "name": "Ruby",
            "rank": 5
        }
    ]
}
```

这样就实现了从 LeanCloud 云端读取数据并返回。

## 3\. 通过网络访问，获取其他站点的数据，再返回

比如， 获取 [Gank.io 的 API](http://gank.io/api) 然后处理成自己想要的格式。

继续写路由函数：

```python
@app.route('/android')
def get_android():
    # 随机获取10条 Android 的推荐
    results = requests.get('http://gank.io/api/random/data/Android/10').json().get('results')
    # 仅需要标题和 url
    data = [{'desc': result.get('desc'), 'url': result.get('url')} for result in results]
    # 渲染 HTML 模板
    return render_template('android.html', datas=data)
```

HTML 模板

```html
<!DOCTYPE HTML>
<html>
<head>
    <title>Android 推荐！</title>
    <link rel="stylesheet" href="/static/style.css" type="text/css">
</head>
<body>
<div id="container">
    <h1>Android :)</h1>
    <p><a href="/android">点我换内容哟 ～</a></p>
    {% for data in datas %}
        <ul>
            <li><a href="{{ data.url }} ">{{ data.desc }}</a></li>
        </ul>
    {% endfor %}
</div>
</body>
</html>
```

访问 ['/android'](http://brucezz.leanapp.cn/android) 看看效果图！

![demo](/images/leancloud-engine-demo1.png)

# 发布

发布的项目可以设置一个二级域名，位置在 `你的 App 界面 -> 存储 -> 云引擎 -> 设置 -> Web 主机域名`

使用命令行工具

- `avoscloud deploy` 将项目部署到云端测试环境，访问 `http://stg-${your_app_domain}.leanapp.cn`
- `avoscloud publish` 将项目部署到云端生产环境，访问 `http://${your_app_domain}.leanapp.cn`

# 待续

这次体验 LeanCloud 云引擎仅仅是一个开始，还有云函数以及定时函数可以使用，以后会更加深入地研究。

另外 LeanCloud 云引擎还能使用 Python Web 框架，部署自己的小站，免去自己架设服务器的麻烦。

更多的技巧姿势，需参考 [LeanCloud 文档](https://leancloud.cn/docs/index.html)，以及 [Flask 文档](http://docs.jinkan.org/docs/flask/)。
