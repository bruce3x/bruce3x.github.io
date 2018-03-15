---
title: Android 启动模式
date: 2018-03-14
category: Android
tags:
    - LaunchMode
---

Andoird 开发中天天都与 Activity 打交道，为了满足项目中的特殊需求，会使用到 Activity 的启动模式。

Android 中的启动模式共有四种：

- standard 标准模式
- singleTop 栈顶复用模式
- singleTask 栈内复用模式
- singleInstance 单实例模式

### standard

Activity 的默认启动模式。每次启动 Activity 都会去创建一个新的实例，添加到活动任务栈中，是最常用的一种模式。

### singleTop

启动 Activity 时，如果当前栈顶实例与目标 Activity 相同，则不创建新的实例，然后回调 `Activity#onNewIntent(Intent intent)` 方法；如果目标 Activity 不在栈顶，会创建一个新的实例。

假设任务栈为 `A > B > C`，其中 C 是 singleTop 模式，此时再启动一个 C，不会创建新的实例，任务栈还是 `A > B > C`。

任务栈 `A > B > C`，其中 B 是 singleTop 模式，此时再启动一个 B，由于它不在栈顶，会新创建一个实例，任务栈变为 `A > B > C > B`。

任务栈 `A > B > C`，其中 D 是 singleTop 模式，此时启动一个 D，任务栈会变为 `A > B > C > D`。

### singleTask

启动 Activity 时，会先查看已存在的任务栈 `taskAffinity` 属性值是否存在和该 Activity 的属性（默认值是**应用包名**）值一致的。如果不存在这样的任务栈，便会创建一个新的任务栈，并且启动该 Activity；如果存在这样的任务栈，会确认栈中是否存在该 Activity 的实例，如果不存在，会创建一个新的实例，添加到任务栈中，否则会销毁掉该实例之前的所有 Activity，使其重回栈顶，然后回调它的 `Activity#onNewIntent(Intent intent)` 方法。

任务栈为 `A > B > C`，其中 B 是 singleTask 模式，此时再启动一个 B，它的实例将重回栈顶，任务栈变为 `A > B`。

任务栈为 `A > B > C`，其中 D 是 singleTask 模式，此时启动一个 D，任务栈变为 `A > B > C > D`。

> 还可能有通过指定 taskAffinity 在别的栈中启动 singleTask 模式的 Activity 的情况

### singleInstance

启动 Activity 时，会直接创建一个新的任务栈，并且创建一个该 Activity 的实例添加到新任务栈中。如果在某个栈中已存在该 Activity 的实例，则不会创建新的栈和实例，而是直接复用该实例，并且回调 `Activity#onNewIntent(Intent intent)` 方法。

### 常用的 Intent flag

- `Intent#FLAG_ACTIVITY_SINGLE_TOP`

  为 Activity 指定 singleTop 启动模式，与 XML 中指定作用相同
  
- `Intent#FLAG_ACTIVITY_NEW_TASK` 

  为 Activity 指定 singleTask 启动模式，与 XML 中指定作用相同
  
- `Intent#FLAG_ACTIVITY_CLEAR_TOP` 

  通常和 singleTask 模式一起使用，可以使目标 Activity 之上的 Activity 都出栈；如果目标 Activity 是 standard 启动模式，则它自身的实例也会被销毁然后重建；如果是 singleTop 模式，则不会被销毁，而是回调 `Activity#onNewIntent(Intent intent)` 方法。

### 注意事项

采用**非 Activity 的 Context 实例**启动 Activity 时，会报异常。

> Caused by: android.util.AndroidRuntimeException: Calling startActivity() from outside of an Activity  context requires the FLAG_ACTIVITY_NEW_TASK flag. Is this really what you want?

是由于该 Context 实例并没有一个任务栈，需要指定 `Intent#FLAG_ACTIVITY_NEW_TASK`，实际上是采用了 singleTask 模式启动。

---

### 对 Android 官网文档的两点疑问

#### 1. 启动 singleTask 模式的 Activity 是否会直接创建新的任务栈

根据官方文档（[这里](https://developer.android.com/guide/components/activities/tasks-and-back-stack.html#ManifestForTasks)）：

> "singleTask"
> <br/>
> The system creates a new task and instantiates the activity at the root of the new task.  However, if an instance of the activity already exists in a separate task, the system routes the intent to the existing instance through a call to its onNewIntent() method, rather than creating a new instance. Only one instance of the activity can exist at a time.

根据实际测试，只有在该 Activity 的 `taskAffinity` 值对应的任务栈不存在时，才会去创建新的任务栈（create a new task）。

#### 2. 关于后台栈中 singleTask 模式的 Activity 被启动后，任务栈的变化情况 

官方文档配图：

![](https://ws4.sinaimg.cn/large/006tNbRwgy1fpcvs2e83dj30fa08lq3z.jpg)

> A representation of how an activity with launch mode "singleTask" is added to the back stack. If the activity is already a part of a background task with its own back stack, then the entire back stack also comes forward, on top of the current task.

按照图中描述，后台栈中的 singleTask 模式的 Y 在被启动之后，后台栈被合并到前台栈中了，也就是任务栈变成了 `1 > 2 > X > Y`。

根据我实际测试情况，结果并不是这样。

首先先构造出两个栈的初始情况，前台栈 `1 > 2`，后台栈 `X > Y`，其中 X / Y 都是 singleTask 模式。

![](https://ws2.sinaimg.cn/large/006tNbRwgy1fpcw16ul6dj313c06sn58.jpg)

然后再次启动 Y，看下任务栈的变化。

![](https://ws2.sinaimg.cn/large/006tNbRwly1fpcw3huvwij312207on66.jpg)

这时 Y 已经切换到前台，X / Y 还是在一个栈中（TaskRecord #121），1 / 2 在另一个栈中（TaskRecord #122）。

明显结果不像官方文档图中描述的那样，**两个任务栈没有合并到一起**！

然后依次按返回键退出 Activity，展示结果依次是 `Y -> X -> 2 -> 1`。但是在 X 切换到 2 的过程中，明显有一个任务栈的切换动画，和普通的同一个栈内切换 Activity 的效果不太一样。

> 查看当前运行的任务栈，使用的 adb 命令
>
> `adb shell dumpsys activity activities | sed -En -e '/Running activities/,/Run #0/p'`

