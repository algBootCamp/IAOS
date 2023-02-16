import numpy as np

a = np.array([1, 2, 3])
print(a)
b = np.array([[1, 2], [3, 4]])
print(b)
a = np.array([1, 2, 3, 4, 5], ndmin=2)
print(a)
a = np.array([1, 2, 3], dtype=complex)
print(a)

x = [1, 2, 3]
a = np.asarray(x)
print(a)
x = (1, 2, 3)
a = np.asarray(x)
print(a)

# y = [(1, 2, 3), (4, 5)]
# c = np.asarray(y)
# print(c)

a=np.random.rand(3,4)      #创建指定为3行4列)的数组(范围在0至1之间)
b=np.random.uniform(0,100) #创建指定范围内的一个数
c=np.random.randint(0,100) #创建指定范围内的一个整数
print("创建指定为3行4列)的数组：\n",a)   #\n 表示换行
print("创建指定范围内的一个数：%.2f" %b) #%.2f 表示结果保留2位小数
print("创建指定范围内的一个整数：",c)


#正态生成3行4列的二维数组
a= np.random.normal(1.5, 3, (3, 4))  #均值为1.5，标准差为3
print(a)
# 截取第1至2行的第2至3列(从第0行、0列算起算起)
b = a[1:3, 2:4]
print("截取第1至2行的第2至3列: \n",b)


a=np.arange(20).reshape(4,5)
print("原数组a:\n",a)
print("a全部元素和: ", a.sum())
print("a的最大值: ", a.max())
print("a的最小值: ", a.min())
print("a每行的最大值: ", a.max(axis=1))  #axis=1代表行
print("a每列的最大值: ", a.min(axis=0))  #axis=0代表列
print("a每行元素的求和: ", a.sum(axis=1))
print("a每行元素的均值：",np.mean(a,axis=1))
print("a每行元素的标准差：",np.std(a,axis=1))


A = np.array([[0,1], [1,2]])  #数组
B = np.array([[2,5],[3,4]])   #数组
print("A：\n",A)
print("B：\n",B)

print("对应元素相乘：\n",A*B)
print("矩阵点乘：\n",A.dot(B))
print("矩阵点乘：\n",np.dot(A,B))  #(M行, N列) * (N行, Z列) = (M行, Z列)
print("横向相加：\n",np.hstack((A,B)))
print("纵向相加：\n",np.vstack((A,B)))