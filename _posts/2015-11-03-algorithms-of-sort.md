---
title: 常用排序算法整理
date: 2015-11-03
category: Algorithms
---

**目录**

<!-- MarkdownTOC -->

- [冒泡排序(稳定)](#冒泡排序稳定)
- [选择排序](#选择排序)
- [插入排序(稳定)](#插入排序稳定)
- [快速排序](#快速排序)
- [归并排序(稳定)](#归并排序稳定)
- [堆排序](#堆排序)

<!-- /MarkdownTOC -->

---

最近又复习了一下算法的内容，回顾了排序算法，争取徒手能撸出来，顺带写到博客里，方便查阅。

常见排序算法：冒泡排序，选择排序，插入排序，快速排序，归并排序，堆排序。

数据可视化：[http://www.sorting-algorithms.com/](http://www.sorting-algorithms.com/)

---

<a name="冒泡排序稳定"/>

# 冒泡排序(稳定)

### 基本思想

依次比较相邻的两个数，将小数放在前面，大数放在后面。

由于在排序过程中总是小数往前放，大数往后放，相当于气泡往上升，所以称作冒泡排序。主要通过两层循环来实现。

### 动态图

![选择排序](/images/bubble-sort.gif)

### 实现

```java

/**
 * Created by zero on 2015/11/03.
 * SimpleCodeDemo
 */
public class Bubble {

    public static void sort(int[] a) {
        for (int i = 0; i < a.length; i++) {
            boolean swaped = false;
            for (int j = a.length - 1; j > i; j--) {
                if (a[j] < a[j - 1]) {
                    swap(a, j, j - 1);
                    swaped = true;
                }
            }
            if (!swaped) break;
        }
    }

    private static void swap(int[] a, int i, int j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }
}

```

### 性能

- 空间复杂度O(1)
- 时间复杂度O(N^2)


---

<a name="选择排序"/>

# 选择排序

### 基本思想：

1. 找到数组里最小的元素
2. 让它和数组的第一个元素交换
3. 在剩下元素中找到最小值，与数组的第二个元素交换
4. 如此往复，直到将整个数组排序

通过不断地选择剩余元素之中的最小值来排序。

### 动态图

![选择排序](/images/selection-sort.gif)

### 实现

```java
/**
 * Created by zero on 2015/11/03.
 * SimpleCodeDemo
 */
public class Selection {

    public static void sort(int[] a) {
        for (int i = 0; i < a.length; i++) {
            int min = i;
            for (int j = i; j < a.length; j++) {
                if (a[min] > a[j]) min = j;
            }
            swap(a, i, min);
        }
    }

    //交换第i和j个元素的值
    private static void swap(int[] a, int i, int j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }
}

```



### 性能

- 时间复杂度O(N^2)，空间复杂度O(1)
- 运行时间和输入无关，无论输入元素排序怎样，比较和交换次数都不变
- 数据移动最少，交换次数仅与数据规模N呈线性关系




---


<a name="插入排序稳定"/>

# 插入排序(稳定)

### 基本思想：

1. 当前索引遍历数组
2. 当前索引左边为有序数组
3. 将索引位置所在的元素插入到左边有序数组中

### 动态图

![选择排序](/images/insertion-sort.gif)

### 实现

```java

/**
 * Created by zero on 2015/11/03.
 * SimpleCodeDemo
 */
public class Insertion {

    public static void sort(int[] a) {
        for (int i = 1; i < a.length; i++) {
            int t = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > t) {
                //将大于a[i]的值都后移
                a[j + 1] = a[j];
                j--;
            }
            a[j] = t;//插入
        }
    }
}
```

### 性能

插入排序对于部分有序的数组十分高效，也很适合小规模数组。

排序效率受输入元素初始顺序影响很大。

---


<a name="快速排序"/>

# 快速排序

### 基本思想：

1. 先对输入的数据进行洗牌
2. 以数据a[j]为中心进行分区，使得a[j]左侧的数据都小于等于a[j]，a[j]右侧的数据都大于等于a[j]
3. 分区完后递归排序

### 动态图

![选择排序](/images/quick-sort.gif)

### 实现

```java

/**
 * Created by zero on 2015/11/03.
 * SimpleCodeDemo
 */
public class Quick {

    public static void sort(int[] a) {
        //为了保障快速排序的性能, 在排序之前进行打乱操作
        //另外一种方法是在partition()方法中随机选择一个切分元素
        shuffle(a);
        sort(a, 0, a.length - 1);
    }

    private static void sort(int[] a, int lo, int hi) {
        if (hi <= lo) return;

        //切分
        int i = partition(a, lo, hi);

        //左子数组排序
        sort(a, lo, i - 1);
        //右子数组排序
        sort(a, i + 1, hi);
    }

    private static int partition(int[] a, int lo, int hi) {
        int i = lo, j = hi + 1;
        //选取第一个元素为切分元素，a[lo]
        while (true) {
            //从左扫描出第一个大于a[lo]的元素
            while (a[++i] < a[lo]) if (i == hi) break;
            //从右扫描出第一个小于a[lo]的元素
            while (a[--j] > a[lo]) if (j == lo) break;

            //上述元素不存在
            if (i >= j) break;
            //将较小元素移至a[lo]左边,较大元素移至右边
            swap(a, i, j);
        }

        //将a[lo]移至中间
        swap(a, lo, j);
        return j;
    }

    private static void swap(int[] a, int i, int j) {
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }

    private static void shuffle(int[] a) {
        Random random = new Random();
        for (int i = 0; i < a.length; i++) {
            int j = random.nextInt(a.length);
            swap(a, i, j);
        }
    }
}

```

### 性能

- 切分方法的内循环很简洁，速度快
- 比较次数很少

---


<a name="归并排序稳定"/>

# 归并排序(稳定)

### 基本思想：

要将一个数组排序，可以先（递归地）将它分成两半进行排序，然后将结果归并起来。

### 动态图

![选择排序](/images/merge-sort.gif)

### 实现

```java

/**
 * Created by zero on 2015/11/03.
 * SimpleCodeDemo
 */
public class Merge {

    private static int[] aux;//辅助数

    public static void sort(int[] a) {
        aux = new int[a.length];
        sort(a, 0, a.length - 1);
    }

    private static void sort(int[] a, int lo, int hi) {
        if (lo >= hi) return;
        int mid = (lo + hi) / 2;

        sort(a, lo, mid); //左子数组排序
        sort(a, mid + 1, hi);//右子数组排序
        merge(a, lo, mid, hi);//合并起来
    }

    private static void merge(int[] a, int lo, int mid, int hi) {
	    if (a[mid] <= a[mid + 1]) return;//认为数组有序，跳过merge()

        int i = lo, j = mid + 1;

        for (int k = lo; k <= hi; k++) {
            //将数据复制到辅助数组中
            aux[k] = a[k];
        }

        for (int k = lo; k <= hi; k++) {
            if (i > mid) a[k] = aux[j++];//左子数组已合并完
            else if (j > hi) a[k] = aux[i++];//右子数组已合并完
            else if (aux[i] > aux[j]) a[k] = aux[j++];
            else a[k] = aux[i++];
        }
    }
}

```

### 性能

归并排序时间复杂度O(NlgN), 空间复杂度O(N)

---


<a name="堆排序"/>

# 堆排序

### 基本思想：

1. 构造二叉堆
2. 利用堆的特性(堆顶为元素最大值)获取到最大值，插入到尾部
3. 将交换到堆顶的元素下沉到合适位置，在剩余元素中产生新的最大项
4. 插入到尾部，依次循环

### 动态图

![选择排序](/images/heap-sort.gif)

### 实现

```java

/**
 * Created by zero on 2015/11/03.
 * SimpleCodeDemo
 */
public class Heap {

    //二叉堆：每个结点都小于等于它的父结点
    //第k个结点，左子结点为2k，右子结点为2k+1

    //由于堆中索引从1开始，访问数组时索引值相应减1

    public static void sort(int[] a) {
        int N = a.length;

        for (int k = N / 2; k >= 1; k--) {
            //构造堆
            sink(a, k, N);
        }
        while (N > 1) {
            //修复堆，直到堆有序
            swap(a, 1, N--); //将最大项(堆顶元素)交换至最后面
            sink(a, 1, N);//下沉交换过来的元素
        }
    }

    // 下沉操作
    private static void sink(int[] a, int k, int N) {
        while (2 * k <= N) {
            int j = 2 * k;//指向左子结点
            if (j < N && a[j - 1] < a[j]) j++;//指向较大的子结点
            if (a[k - 1] >= a[j - 1]) break;//父结点大于子结点，则跳过

            swap(a, k, j);//父结点小于子结点，下沉，交换位置
            k = j;
        }
    }

    private static void swap(int[] a, int i, int j) {
        int t = a[i - 1];
        a[i - 1] = a[j - 1];
        a[j - 1] = t;
    }
}

```

### 性能

时间复杂度 O(NlgN), 空间复杂度 O(1)。
