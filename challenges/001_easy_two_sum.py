

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Easy Two Sum — 經典演算法挑戰題

題目描述：
    給定一個整數陣列 nums 和一個整數目標值 target，
    找出陣列中兩個數字的索引，使得它們的和等於 target。
    假設每組輸入恰好有一個解，且同一個元素不能使用兩次。

範例：
    輸入: nums = [2, 7, 11, 15], target = 9
    輸出: [0, 1]
    解釋: nums[0] + nums[1] = 2 + 7 = 9

解題思路：
    1. 暴力法 O(n²)：雙重迴圈檢查所有配對
    2. 雜湊表法 O(n)：用字典記錄已遍歷的數字與索引，
       對每個數字查找「target - 當前數字」是否已存在於字典中
"""

from typing import List, Tuple, Optional


# ============================================================
# 解法一：暴力法（Brute Force）
# 時間複雜度：O(n²) — 兩層巢狀迴圈
# 空間複雜度：O(1) — 只用常數額外空間
# ============================================================
def two_sum_brute_force(nums: List[int], target: int) -> Optional[List[int]]:
    """暴力法：逐一檢查所有可能的兩數組合"""
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None


# ============================================================
# 解法二：雜湊表法（Hash Map）— 最佳解法
# 時間複雜度：O(n) — 只需遍歷陣列一次
# 空間複雜度：O(n) — 字典最多存 n 個元素
#
# 核心概念：
#   遍歷陣列時，對於當前數字 num，我們需要的配對數字是
#   complement = target - num。若 complement 已經在字典中，
#   代表我們找到了答案；否則把 num 存入字典供後續查找。
# ============================================================
def two_sum(nums: List[int], target: int) -> Optional[List[int]]:
    """雜湊表法：一次遍歷，用字典快速查找互補數"""
    # seen 字典：key = 數值, value = 該數值的索引
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num  # 計算需要的互補數
        if complement in seen:     # 互補數已存在 → 找到答案
            return [seen[complement], i]
        seen[num] = i              # 記錄當前數字與索引
    return None


# ============================================================
# 測試框架
# ============================================================
def run_tests() -> None:
    """執行所有測試案例，驗證兩種解法的正確性"""

    # 測試案例格式：(輸入陣列, 目標值, 預期輸出)
    test_cases: List[Tuple[List[int], int, List[int]]] = [
        # 基本案例
        ([2, 7, 11, 15], 9, [0, 1]),
        # 目標值較大
        ([3, 2, 4], 6, [1, 2]),
        # 相同數字配對
        ([3, 3], 6, [0, 1]),
        # 含負數
        ([-1, -2, -3, -4, -5], -8, [2, 4]),
        # 正負數混合
        ([-3, 4, 3, 90], 0, [0, 2]),
        # 較長陣列
        ([1, 5, 8, 3, 9, 2], 11, [2, 3]),
        # 首尾配對
        ([10, 20, 30, 40, 50], 60, [1, 3]),
        # 含零
        ([0, 4, 3, 0], 0, [0, 3]),
    ]

    solvers = [
        ("暴力法 O(n²)", two_sum_brute_force),
        ("雜湊表法 O(n)", two_sum),
    ]

    print("=" * 60)
    print("  Two Sum 演算法挑戰 — 測試結果")
    print("=" * 60)

    all_passed = True

    for solver_name, solver_func in solvers:
        print(f"\n【{solver_name}】")
        print("-" * 50)

        for i, (nums, target, expected) in enumerate(test_cases, 1):
            result = solver_func(nums[:], target)  # 傳入副本避免修改原陣列

            # 驗證結果：索引對應的兩數之和必須等於 target
            if result is not None and len(result) == 2:
                a, b = result
                actual_sum = nums[a] + nums[b]
                passed = (actual_sum == target and set(result) == set(expected))
            else:
                passed = False

            status = "✓ 通過" if passed else "✗ 失敗"
            if not passed:
                all_passed = False

            print(f"  測試 {i}: nums={nums}, target={target}")
            print(f"         預期={expected}, 實際={result}  [{status}]")

    print("\n" + "=" * 60)
    if all_passed:
        print("  所有測試皆通過！")
    else:
        print("  有測試未通過，請檢查程式邏輯。")
    print("=" * 60)

    # 示範雜湊表法的逐步執行過程
    print("\n\n【逐步解題示範】")
    print("-" * 50)
    demo_nums = [2, 7, 11, 15]
    demo_target = 9
    print(f"輸入: nums = {demo_nums}, target = {demo_target}\n")

    seen = {}
    for i, num in enumerate(demo_nums):
        complement = demo_target - num
        print(f"  步驟 {i + 1}: 檢查 nums[{i}] = {num}")
        print(f"           需要的互補數 = {demo_target} - {num} = {complement}")

        if complement in seen:
            print(f"           → 互補數 {complement} 在字典中（索引 {seen[complement]}）")
            print(f"           → 答案: [{seen[complement]}, {i}]")
            break
        else:
            seen[num] = i
            print(f"           → 互補數不在字典中，記錄 {{{num}: {i}}}")
            print(f"           → 目前字典: {seen}")


if __name__ == "__main__":
    run_tests()
