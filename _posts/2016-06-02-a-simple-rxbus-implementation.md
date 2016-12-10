---
title: RxBus 的简单实现
date: 2016-06-02
category: Android
tags:
    - RxJava
    - RxBus
---

今天写代码正好想到要用事件总线，先前都是使用 Square 的 Otto 或者 GreenRobot 的 EventBus ，听说 RxJava 能够轻易实现一个 Bus，所以就来研究研究这个车怎么开~

![没时间解释了，快上车！](/images/no-time-to-explain.jpg)

这辆车需要有一下功能：

- 订阅者能够订阅某种事件 Event
- 发布某种 Event 时，该事件的订阅者们能够及时响应

在 RxJava 里有一个对象 Subject，既是 Observable 又是 Observer，可以把 Subject 理解成一个管道或者转发器，数据从一端输入，然后从另一端输出。

Subject 有好几种，这里可以使用最简单的 `PublishSubject`。一旦数据从一端传入，结果会里立刻从另一端输出。

由于允许订阅者订阅某一种类型的 Event，所以注册订阅的时候需要一个 Class 对象对事件进行过滤。

### 简单实现

```java
public class RxBus {
    private static volatile RxBus instance;
    private final Subject<Object, Object> BUS;

    private RxBus() {
        BUS = new SerializedSubject<>(PublishSubject.create());
    }

    public static RxBus getDefault() {
        if (instance == null) {
            synchronized (RxBus.class) {
                if (instance == null) {
                    instance = new RxBus();
                }
            }
        }
        return instance;
    }

    public void post(Object event) {
        BUS.onNext(event);
    }

    public <T> Observable<T> toObserverable(Class<T> eventType) {
        // ofType = filter + cast
        return BUS.ofType(eventType);
    }
}
```



其中，RxBus 使用了单例模式，确保应用中只有一辆车。

`post` 方法发布一个 Event 对象给 bus，然后由 bus 转发给订阅者们。

`toObserverable` 方法能够获得一个包含目标事件的 Observable，订阅者对其订阅即可响应。

`bus.ofType()` 等效于  `bus.filter(eventType::isInstance).cast(eventType)` ，即先过滤事件类型，然后发射给订阅者。



### 开车啦

```java
public class RxBusActivity extends AppCompatActivity {
    private CompositeSubscription allSubscription = new CompositeSubscription();
    Button send;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        send = (Button) findViewById(R.id.send);
        send.setOnClickListener(
                v -> RxBus.getDefault().post(new OneEvent("hello bus")));
        allSubscription.add(RxBus.getDefault()
                .toObserverable(OneEvent.class).subscribe(this::response));
    }

    private void response(OneEvent event) {
        ToastUtil.show(event.msg);
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (allSubscription != null && !allSubscription.isUnsubscribed())
            allSubscription.unsubscribe();
    }

    class OneEvent {
        // some data you need ...
        String msg;

        public OneEvent(String msg) {
            this.msg = msg;
        }
    }
}
```

点击按钮，发送  `OneEvent` 事件，然后响应此事件，发出 Toast ~

通过多次调用 `toObserverable()` 方法可以订阅多种事件。

**小 tip** : `CompositeSubscription` 可以把 Subscription 收集到一起，方便 Activity 销毁时取消订阅，防止内存泄漏。



### Reference

- [翻译：通过 RxJava 实现一个 Event Bus – RxBus \| Drakeet的个人博客](https://drakeet.me/rxbus)
- [用RxJava实现事件总线(Event Bus) - 简书](http://www.jianshu.com/p/ca090f6e2fe2/)
