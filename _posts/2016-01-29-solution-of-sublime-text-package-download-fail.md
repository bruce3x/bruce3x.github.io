---
title: Sublime Text 3 插件下载失败的解决方案
date: 2016-01-29T00:00:00.000Z
category: Tool
tags:
  - Sublime Text
---

前两天瞎折腾，把日常使用的 Ubuntu 系统玩坏了，后果就是重装系统。。。

Sublime Text 这款文本编辑器也得重装，安装插件的时候发现了一个头疼的问题：提供 Sublime Text 插件下载的网站 [packagecontrol.io](https://packagecontrol.io/) 被墙了！墙了！了！

它的包管理器(Package Control) 也下载不下来，即使手动下载回来，然后丢到相应的文件夹，也不会从服务器成功地获取到有效的插件列表，一直会提示

> There are no packages available for installation.

> Package Control: Error downloading channel. curl: (56) Proxy CONNECT aborted downloading <https://packagecontrol.io/channel_v3.json>.

解决方案就是：**设置代理！**

官网给出的安装 Package Control 的最快捷的方法，就是在 Console 输入一段代码，如下（实际使用的时候不换行）：

```python
import urllib.request,os,hashlib;
h = '2915d1851351e5ee549c20394736b442' + '8bc59f460fa1548d1514676163dafc88';
pf = 'Package Control.sublime-package';
ipp = sublime.installed_packages_path(); urllib.request.install_opener( urllib.request.build_opener( urllib.request.ProxyHandler()) );
by = urllib.request.urlopen( 'http://packagecontrol.io/' + pf.replace(' ', '%20')).read();
dh = hashlib.sha256(by).hexdigest();
print('Error validating download (got %s instead of %s), please try manual install' % (dh, h)) if dh != h else open(os.path.join( ipp, pf), 'wb' ).write(by)
```

学过 Python 的话，很容易就看懂了，从服务器下载需要的包到指定路径，并判断 hash 值是否有效。

其中有一句 `urllib.request.ProxyHandler()`，这里使用了代理，我们可以在这里填入自己的代理地址，比如：

```python
urllib.request.ProxyHandler({
    'http':'127.0.0.1:1080',
    'https':'127.0.0.1:1080',
})
```

加入代理之后，把那一大串代码输入到 Sublime Text 的 Console 里，就会自动下载安装 Package Control 了。

然后打开 `Menu -> Package Settings -> Package Control -> Settings - User`

在里面设置代理，输入如下：

```json
{
    "http_proxy": "127.0.0.1:1080",
    "https_proxy": "127.0.0.1:1080",
}
```

这样设置完成之后，就能顺利访问 [packagecontrol.io](https://packagecontrol.io/) ，`Ctrl + Shift + P -> Package Control: Install Package` 就可以安装插件啦。

另外还有种安装插件的方法，从 Github 仓库安装，一般情况下都能直接访问 Github，所以这种方法不用设置代理 。

1. `Ctrl + Shift + P -> Package Control: Add Repository` 添加 Github 仓库
2. 输入 `https://github.com/<username>/<repo>`, 如`https://github.com/wakatime/sublime-wakatime`
3. `Ctrl + Shift + P -> Package Control: Install Package` 获取插件列表，就能看到刚刚添加的插件了，按 `Enter` 下载就 OK 了。

╮(╯▽╰)╭，我用的插件不多，就 `wakatime`, `git`, `convertToUTF8`, etc.

另另外，Ubuntu 系统 Sublime Text 不能输入中文问题，解决方案在这里 -> [lyfeyaj/sublime-text-imfix](https://github.com/lyfeyaj/sublime-text-imfix)

输入框不跟随问题，目前好像还无能为力。。。 ╮(╯▽╰)╭
