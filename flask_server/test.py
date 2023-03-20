def parse_statment(s):
    ret1 = s.split("\n")
    while len(ret1) != 0 and ret1[0] == '':
        del ret1[0]
    for i in range(len(ret1)):
        if '. ' in ret1[i]:
            ret1[i] = ret1[i].split('. ')[1]
    return ret1
s = "\n\n1. Attention 메커니즘이 어떻게 자연어 처리 작업에 사용되는지?\n" + \
"2. Attention 메커니즘은 어떤 기능을 가지고 있는가?\n" + \
"3. Attention 메커니즘을 사용하면 어떤 이점이 있는가?"

s = parse_statment(s)
print(s)