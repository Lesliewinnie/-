# 2个判断
'''
2, 3 a,d
1, 2 b,c
0, 2 b,d
a,c不可达
输入x, y
if y > 1:
    x = y a
else:
    x = 2 b
if x == 1:
    y = 1 c
else:
    y = x d
输出y
'''

'''
b = false
temp = a & b
return temp || c
 
a false b false c true return true 通过
a false b true c true return true 有fault无error无failure
a true b true c true return true 有fault有error无failure
a true b true c true return true 有fault有error有failure
'''
