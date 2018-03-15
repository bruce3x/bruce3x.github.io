---
title: EventBus 实现原理
date: 2018-03-15
category: Android
tags:
    - SourceCode
    - EventBus
---

[EventBus 项目地址](https://github.com/greenrobot/EventBus)

[EventBus 基本使用方式](http://greenrobot.org/eventbus/documentation/how-to-get-started/)

EventBus 是一个 Android 事件订阅/发布的事件总线。使用简单，事件发布和订阅充分解耦。

![](https://ws1.sinaimg.cn/large/006tNbRwly1fpdlrt6oqaj30zk0dbgmz.jpg)


## 1. EventBus 注册订阅流程

`EventBus#register(Object subscriber)` 方法用来将订阅者注册到 EventBus。

```java
public void register(Object subscriber) {
    Class<?> subscriberClass = subscriber.getClass();
    List<SubscriberMethod> subscriberMethods = subscriberMethodFinder.findSubscriberMethods(subscriberClass);
    synchronized (this) {
        for (SubscriberMethod subscriberMethod : subscriberMethods) {
            subscribe(subscriber, subscriberMethod);
        }
    }
}
```

其中主要有两步：

1. 查找订阅者内部订阅事件的方法 `SubscriberMethod`
2. 依次将订阅者和订阅方法绑定起来

查找订阅事件方法的实现在 `SubscriberMethodFinder#findSubscriberMethods(Class<?> subscriberClass)` 方法中。会优先从缓存中读取之前已经获取到的结果，如果缓存没有，就从预先指定的 Index 索引文件中查找，或者利用反射遍历订阅者类中的方法。

```java
List<SubscriberMethod> findSubscriberMethods(Class<?> subscriberClass) {
    List<SubscriberMethod> subscriberMethods = METHOD_CACHE.get(subscriberClass);
    if (subscriberMethods != null) return subscriberMethods;

    if (ignoreGeneratedIndex) {
        subscriberMethods = findUsingReflection(subscriberClass);
    } else {
        subscriberMethods = findUsingInfo(subscriberClass);
    }
    // ...
    METHOD_CACHE.put(subscriberClass, subscriberMethods);
    return subscriberMethods;
}
```

EventBus 可以通过 APT 注解处理器在编译器为订阅者和订阅方法生成 Index 索引文件，是 `SubscriberInfoIndex` 接口的实现类。其中包含了订阅方法名称、事件类型、订阅线程、优先级等信息，不需要运行时去逐次遍历订阅类的所有方法。

利用反射查找订阅方法，即获取订阅类的所有方法，逐个检查修饰符、参数个数、注解类型，然后将所有符合条件的订阅方法返回。

将订阅者和订阅方法绑定的过程，实质上是将前面获取到的订阅信息记录到集合中，供发布事件时查询使用。具体实现在 `EventBus#subscribe(Object subscriber, SubscriberMethod subscriberMethod)` 方法中。
1. 首先会获取 subscriberMethod 的事件类型，以及它对应的订阅列表，按照优先级(`priority`) 将该次订阅信息插入到列表中。
2. 记录 subscriber 订阅的事件类型。
3. 如果该方法订阅的是粘性事件，会去 `stickyEvents` 中查找有效的事件实例，然后发布给该订阅方法。

## 2. EventBus 事件发布流程

`EventBus#post(Object event)` 用来发布事件。

`EventBus#postSticky(Object event)` 方法发布粘性事件，先把事件类型和实例记录到 `stickyEvents` 集合中，然后执行正常的 `EventBus#post(Object event)` 流程。

`post()` 方法会从当前线程的 ThreadLocal 中获取到 `PostingThreadState` 实例，将事件对象添加到 PostingThreadState 的事件队列中，然后遍历事件队列，调用 `postSingleEvent(Object event, PostingThreadState postingState)` 方法依次发布事件。

`postSingleEvent()` 方法中，如果 EventBus 支持 `eventInheritance`，会去查找事件的父类和接口类型。然后循环每一个类型，调用 `postSingleEventForEventType(Object event, PostingThreadState postingState, Class<?> eventClass)` 方法将事件发布到每一个订阅者。如果没有人订阅这个事件，会默认发布一个 `NoSubscriberEvent` 事件。

`postSingleEventForEventType()` 方法会根据传入的事件类型，在 `subscriptionsByEventType` 集合中去查找订阅该事件类型的所有订阅信息(subsriptions)，然后遍历调用 `postToSubscription(Subscription subscription, Object event, boolean isMainThread)` 向订阅者发布事件。

`postToSubscription()` 方法中，会根据订阅方法的 `threadMode` 属性，来决定是直接调用订阅方法（`invokeSubscriber(Subscription subscription, Object event)`），或者交给响应的 Poster 切换线程然后再进行订阅方法的调用。

`invokeSubscriber()` 实质上就是反射调用了 `java.lang.reflect.Method#invoke` 方法，将事件对象传递给订阅者的响应事件的方法。


## 3. EventBus 事件线程切换的实现

EventBus 中的 ThreadMode 有五种：

- `POSTING`

直接在发布事件的线程，调用订阅者的响应方法。

- `MAIN`

如果发布事件的线程在主线程，直接调用订阅者的响应方法；否则将事件丢到主线程消息队列中，排队调用。

- `MAIN_ORDERED`

在主线程排队调用订阅者的响应方法。

- `BACKGROUND`

如果发布线程在非主线程，直接调用订阅者的响应方法；否则会将事件发到一个后台线程，去调用订阅者的响应方法。多个事件会在队列中依次执行，尽量避免耗时任务阻塞线程。

- `ASYNC`

直接在一个空闲线程中，进行调用。ASYNC 类的线程都是相互独立的，可以在响应方法中执行耗时任务，如网络请求。尽量避免同时触发大量的 ASYNC 类的事件，防止线程并发数量过大。


#### 主线程 `HandlerPoster`

`HandlerPoster` 自身继承了 Handler，创建于主线程，当它收到消息时，自然会回调在主线程。内部有一个队列 `PendingPostQueue`，用来存放排队的事件。

```java
public void enqueue(Subscription subscription, Object event) {
    PendingPost pendingPost = PendingPost.obtainPendingPost(subscription, event);
    synchronized (this) {
        queue.enqueue(pendingPost);
        if (!handlerActive) {
            handlerActive = true;
            if (!sendMessage(obtainMessage())) {
                throw new EventBusException("Could not send handler message");
            }
        }
    }
}
```

外部将订阅信息和事件实例，传给这个 Poster 之后。会先创建一个 PendingPost 对象，然后丢到队列中，再给自己发一个空消息。会在自身的 `handleMessage()` 方法中响应这个消息，**此时已经处于了主线程上**，遍历 PendingPostQueue，把里面的 PendingPost 对象交给 `EventBus#invokeSubscriber(PendingPost pendingPost)` 方法。内部实质上也是通过反射调用了订阅者的响应方法。


#### 后台线程 `BackgroundPoster`

`BackgroundPoster` 自身实现了 `Runnable` 接口，方便将自己丢到线程池中去执行。在 `enqueue(Subscription subscription, Object event)` 方法中，将订阅对象封装成 PendingPost 对象之后，添加到队列中。如果已有一个后台线程在运行，则会排队等待；否则会将自身交给 EventBus 的线程池，启动一个线程来执行。

实际执行时，会不断地从 PendingPostQueue 中取对象，然后调用 `invokeSubscriber()` 方法，直到队列中没有新的对象。

#### 异步线程 `AsyncPoster`

实现类似于 `BackgroundPoster`，将 PendingPost 对象添加到队列中后，会直接把自己交给线程池，在一个空闲线程中执行事件发布操作。

