---
title: Python 笔记
date: 2026-04-20
tags: [编程, Python, 装饰器, 异常处理, 生成器]
slug: python-bi-ji
---
# Python 笔记

#代码 #Python #学习 #已完成

## isinstance VS type
isinstance 和 type 的区别在于：

	-   type()不会认为子类是一种父类类型。
			`type(A()) == A`
	-   isinstance()会认为子类是一种父类类型。
			`isinstance(A(), A)`


## 装饰器decorator
```python

def dec(f):
	pass

@dec
def double(x):
	return x * 2
```

***decorator含义就是将下面的函数作为参数传递给@后面的函数***
## 异常
[(Python内置标准异常及其解析)](https://blog.csdn.net/m0_58477260/article/details/128311987)
[Python 标准异常总结](http://t.csdn.cn/k7vAg)

| 异常名称            | 描述                                                                                               |
| ------------------- | -------------------------------------------------------------------------------------------------- |
| Exception           | 所有异常的基类                                                                                     |
| StopIteration       | 当一个迭代器的 next()方法不指向任何对象时引发                                                      |
| SystemExit          | 由 sys.exit()函数引发                                                                              |
| StandardError       | 除了StopIteration异常和SystemExit，所有内置异常的基类                                              |
| ArithmeticError     | 数值计算所发生的所有错误的基类                                                                     |
| OverflowError       | 当数字类型计算超过最高限额引发                                                                     |
| FloatingPointError  | 当一个浮点运算失败时触发                                                                           |
| ZeroDivisonError    | 当除运算或模零在所有数值类型运算时引发                                                             |
| AssertionError      | 断言语句失败的情况下引发                                                                           |
| AttributeError      | 属性引用或赋值失败的情况下引发                                                                     |
| EOFError            | 当从 input() 函数输入，到达文件末尾时触发                                                          |
| ImportError         | 当一个 import 语句失败时触发                                                                       |
| KeyboardInterrupt   | 当用户中断程序执行，通常是通过按 Ctrl+c 引发                                                       |
| LookupError         | 所有查找错误基类                                                                                   |
| IndexError \n       | 当在一个序列中没有找到一个索引时引发                                                               |
| KeyError            | 当指定的键没有在字典中找到引发                                                                     |
| NameError           | 当在局部或全局命名空间中找不到的标识引发                                                           |
| UnboundLocalError   | 试图访问在函数或方法的局部变量时引发，但没有值分配给它。                                           |
| EnvironmentError    | Python环境之外发生的所有异常的基类。                                                               |
| IOError             | 当一个输入/输出操作失败，如打印语句或 open()函数试图打开不存在的文件时引发操作系统相关的错误时引发 |
| SyntaxError         | 当在Python语法错误引发；                                                                           |
| IndentationError    | 没有正确指定缩进引发。                                                                             |
| SystemError         | 当解释器发现一个内部问题，但遇到此错误时，Python解释器不退出引发                                   |
| SystemExit          | 当Python解释器不使用sys.exit()函数引发。如果代码没有被处理，解释器会退出。                         |
|                     | 当操作或函数在指定数据类型无效时引发                                                               |
| ValueError          | 在内置函数对于数据类型，参数的有效类型时引发，但是参数指定了无效值                                 |
| RuntimeError        | 当生成的错误不属于任何类别时引发                                                                   |
| NotImplementedError | 当要在继承的类来实现，抽象方法实际上没有实现时引发此异常                                           |


## 生成器
[python中yield的用法详解](https://blog.csdn.net/mieleizhi0522/article/details/82142856/)
![[python中yield的用法详解——最简单，最清晰的解释_python yield_冯爽朗的博客-CSDN博客.pdf]]

**********

- python 利用生成器可以实现函数运行一半继续运行，并且可以在这个中间塞数据进去

- 可以被next (函数调用并不断返回下一个值的对象称为迭代器：Iterator















































