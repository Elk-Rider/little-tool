import sys
from collections import Counter


def solve():
    # 读取所有输入数据
    # sys.stdin.read().split() 可以自动处理换行和空格，将输入解析为列表
    input_data = sys.stdin.read().split()

    if not input_data:
        return

    try:
        n = int(input_data[0])
        s = input_data[1]
        t = input_data[2]
    except IndexError:
        return

    # 步骤 1: 检查 S 和 T 是否由相同的字符组成
    # 如果字符统计不一致，说明无法通过重排变成 T
    if Counter(s) != Counter(t):
        print("-1")
        return

    # 步骤 2: 寻找 S 的最长前缀，使其为 T 的子序列
    # t_index 指向 T 中当前搜索的起始位置
    t_index = 0
    # max_prefix_len 记录成功匹配的前缀长度
    max_prefix_len = 0

    # 遍历 S 的每个字符
    for char_s in s:
        # 在 T 中从 t_index 开始寻找 char_s
        # 只要 t_index 小于 n 且当前字符不匹配，就向后移动
        while t_index < n and t[t_index] != char_s:
            t_index += 1

        # 如果找到匹配字符 (t_index < n)
        if t_index < n:
            max_prefix_len += 1
            # 匹配成功后，t_index 后移一位，准备匹配下一个字符
            t_index += 1
        else:
            # 如果在 T 的剩余部分找不到当前的 char_s，
            # 说明 S 的当前前缀无法作为 T 的子序列延伸下去，循环结束
            break

    # 步骤 3: 计算最少操作次数
    # 操作次数 = 总长度 - 不需要操作的前缀长度
    ans = n - max_prefix_len
    print(ans)


if __name__ == '__main__':
    solve()