---
title: Docker 优雅地终止容器中的 Python 程序
date: 2018-04-21
category: Tech
tags:
    - Docker
---

自从接触了 Docker 之后，在服务器上跑的 Python 程序，我基本上都是使用 Docker 进行部署，利用 Docker 镜像可以规避一些环境差异带来的坑。

Docker 可以通过启动、停止容器来控制程序的运行状态。那停止容器的时候，里面运行程序是如何停下来的呢？程序有没有正常退出呢？可以通过一个 Demo 程序来实验一下。

下面是一个简易版的程序：

![](https://ws3.sinaimg.cn/bmiddle/006tKfTcgy1fqkefg7chvj30l00pimz7.jpg)

本地构建镜像，然后启动一个容器跑起来，稍等一会，然后停止容器。可以看到容器的 Exit code 并不为 0，也就是说程序并没有正常退出。
![](https://ws2.sinaimg.cn/large/006tKfTcgy1fqkebyx20xj31kw0bwdi0.jpg)

根据 [Docker 官方文档](https://docs.docker.com/engine/reference/commandline/stop/#extended-description) 的说明，停止容器时，会先给容器发一个 `SIGTERM` 信号，等待超时后，会再给容器发一个 `SIGKILL` 信号，强行停止程序。

**前面的程序并没有在接收 `SIGTERM` 信号时，并没有及时停止，最终被强制杀掉。**为了保证程序能够正常收尾退出，需要处理 `SIGTERM` 信号，利用 Python 中的 signal 模块可以轻松实现。

> 关于 Python signal 模块的使用，可以看一下 [文档](https://docs.python.org/3/library/signal.html#signal.signal) 和 [example](https://pymotw.com/3/signal/index.html) 。

![](https://ws1.sinaimg.cn/large/006tKfTcgy1fqkeg3ys0aj30xo12iq7w.jpg)

具体实现很简单，添加 `SIGTERM`信号的回调，然后在循环的时候判断下退出条件就好了。

此时重新走一遍流程，构建镜像、启动、停止容器，再查看一下状态。此时程序 Exit code 为 0，说明它正常退出。

![](https://ws4.sinaimg.cn/large/006tKfTcly1fqkejn77ioj31kw0bwwgp.jpg)

查看日志，可以看到程序循环结束之后，后面的收尾工作也执行了。

![](https://ws3.sinaimg.cn/bmiddle/006tKfTcly1fqkepzvphij30fc0gimyg.jpg)



实际使用中，可以在接到 `SIGTERM` 信号之后，把内存数据进行持久化，防止数据、状态丢失；
如果不处理的话，可能会导致资源不能正常释放，数据丢失等状况。



>  文中代码预览图生成工具 [Carbon](https://carbon.now.sh/)

