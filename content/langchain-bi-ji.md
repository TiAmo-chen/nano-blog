---
title: LangChain 笔记
date: 2026-03-26
tags: [AI, LangChain, LLM, Transformer]
slug: langchain-bi-ji
---
# user 
[LangChain+LangGraph开发实战全套视频课程](https://www.bilibili.com/video/BV178w1z7EHQ?p=4)
# 大语言模型
## Transformer自注意力机制  
	实质上就是向量的加减法
![[Pasted image 20260326150023.png]]

##  Transformer流程
- 词向量化
- attention
- MLP:多层感知机,基于分析进一步调整向量值
- attention和MLP  多次重复

- softmax:向量转化为词汇  , 但是实际上是给出一个token以及对应token的概率分布
	- 采用随机采样的方式,为了具备多样性,也就是temperature参数

	早期的 Transformer模型确实是纯粹的概率分布的大预言模型,模型参数量的升级以及训练数据量的升级
- Transformer本来是作为翻译用的，但当模型规模和训练数据量增突破某个临界点时，模型像是突然拥有了智能，不仅可以理解人类语言，还能推理、分析。这种现象被称为“涌现”（EmergentAbilities）。这种超大规模的语言模型则被称为大语言模型

### 记忆丢失问题
- 因为是计算出来的,所以上下文长度如果太大的话,那么计算量就会很大,就算不过来了,所以模型就都会存在上下文的限制
- 
- Generative  Pre-trained  Transformer
- 大语言模型（Large Language Model，LLM）




































