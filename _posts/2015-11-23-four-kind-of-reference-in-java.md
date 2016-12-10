---
title: 强引用、弱引用、软引用、虚引用
date: 2015-11-23
category: Java
tags:
    - Java
    - Reference
---


**目录**

<!-- MarkdownTOC -->

- [1.强引用（StrongReference）](#1强引用（strongreference）)
- [2.软引用（SoftReference）](#2软引用（softreference）)
- [3.弱引用（WeakReference）](#3弱引用（weakreference）)
- [4.虚引用（PhantomReference）](#4虚引用（phantomreference）)

<!-- /MarkdownTOC -->

---

最近听小伙伴聊到弱引用、软引用，原来只是听说过，不知道怎么用，特此查阅了一些资料，学习一下。

从JDK1.2版本开始，把对象的引用分为四种级别，这四种级别由高到低依次为：**强引用、软引用、弱引用、虚引用。**

<a name="1强引用（strongreference）"></a>
## 1.强引用（StrongReference）

强引用是最常用的引用方式，如果一个对象具有强引用，那么垃圾回收器绝不会回收它。

```Java
/**
 * Created by zero on 2015/11/23.
 * SimpleCodeDemo
 */
public class StrongReferenceDemo {
    public static void main(String[] args) {
        String ref = new String("StrongReference");//强引用
        System.gc();
        System.runFinalization();
        System.out.println(ref);//对象并没有被回收
    }
}

```

当内存不足时，Java虚拟器宁愿跑出`OutOfMemoryError`错误，终止程序，也不会靠随意回收强引用对象来解决内存不足的问题。

```Java
Object o = new Object();//强引用
o = null;//显式置为null
```

显式设置为`null`，或者超出对象的生命周期范围，该对象不存在强引用，这个时候就可以被回收了。

<a name="2软引用（softreference）"></a>
## 2.软引用（SoftReference）

如果一个对象具有软引用，内存足够时，gc不会回收它；内存不足时，gc就会回收这个对象的内存。只要垃圾回收器没有回收它，该对象就可以被程序使用。**软引用可用来实现内存敏感的高速缓存。**

```Java
/**
 * Created by zero on 2015/11/23.
 * SimpleCodeDemo
 */
public class SoftReferenceDemo {
    public static void main(String[] args) {
        String ref = new String("SoftReference");//强引用
        SoftReference<String> softRef = new SoftReference<>(ref);//软引用

        ref = null;//强引用置为null,由于软引用存在，对象并不会被回收，直到内存不足

    }
}

```

在Android开发中，经常会用到大量图片，如果每次都读取图片，涉及IO操作速度慢。将图片缓存到内存里，需要的时候直接拿来用。

由于图片占用内存较大，缓存图片很多的话容易发生OOM，可以用软引用来避免这一问题。

```Java
/**
 * Created by zero on 2015/11/23.
 * SimpleCodeDemo
 */
public class ImageCacheDemo {

	//用HashMap来保存软引用对象
    private Map<String, SoftReference<Bitmap>> imageCache = new HashMap<>();

    public void addBitmapToCache(String path) {
        Bitmap bitmap = BitmapFactory.decodeFile(path);//强引用
        SoftReference<Bitmap> softBitmap = new SoftReference<Bitmap>(bitmap);//软引用

        imageCache.put(path, softBitmap);//添加到map里缓存
    }

    public Bitmap getBitmapByPath(String path) {
        //从map缓存中取出软引用对象
        SoftReference<Bitmap> softBitmap = imageCache.get(path);
        //判断是否存在软引用
        if (softBitmap == null) return null;
        //若内存不足Bitmap被回收，会取得null
        return softBitmap.get();
    }
}

```

使用了软引用，在OOM发生之前，这些缓存的图片资源占用的内存会被释放掉，避免Crash。

值得注意的地方:

> 在gc之前，`SoftReference`类的`get()`方法会返回对象的强引用，一旦gc回收该对象之后，`get()`方法会返回`null`。所以，在获取软引用对象的时候，要判断是否为`null`，防止`NullPointerException`异常导致应用挂掉。


<a name="3弱引用（weakreference）"></a>
## 3.弱引用（WeakReference）

在垃圾回收器线程扫描它所管辖的内存区域的过程中，一旦发现了只具有弱引用的对象，**不管当前内存空间足够与否，都会回收它的内存**。

相比于软引用，只具有弱引用的对象拥有更短暂的生命周期。

由于垃圾回收器是一个优先级很低的线程，因此不一定会很快发现那些只具有弱引用的对象。

```Java

/**
 * Created by zero on 2015/11/23.
 * SimpleCodeDemo
 */
public class WeakReferenceDemo {
    public static void main(String[] args) {
        String ref = new String("WeakReference");//强引用
        WeakReference<String> weakRef = new WeakReference<String>(ref);//弱引用
        ref = null;

        System.out.println(weakRef.get());//WeakReference
        System.gc();//强制gc
        System.out.println(weakRef.get());//null
    }
}


```

输出结果：

```
WeakReference
null

```

<a name="4虚引用（phantomreference）"></a>
## 4.虚引用（PhantomReference）

“虚引用”顾名思义，就是形同虚设，与其他几种引用都不同，虚引用并不会决定对象的生命周期。如果一个对象仅持有虚引用，那么它就和没有任何引用一样，在任何时候都可能被垃圾回收器回收。

虚引用主要用来跟踪对象被垃圾回收器回收的活动。虚引用与软引用和弱引用的一个区别在于：虚引用必须和引用队列 （`ReferenceQueue`）联合使用。当垃圾回收器准备回收一个对象时，如果发现它还有虚引用，就会在回收对象的内存之前，把这个虚引用加入到与之 关联的引用队列中。
