

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合併排序（Merge Sort）演算法實作

演算法說明：
    合併排序是一種基於「分治法（Divide and Conquer）」的排序演算法。
    其核心思想是將陣列不斷地對半拆分，直到每個子陣列只剩一個元素，
    再將這些子陣列兩兩合併，合併過程中進行排序，最終得到完整的有序陣列。

    步驟：
    1. 分割（Divide）：將陣列從中間分成左右兩半
    2. 遞迴（Conquer）：對左右兩半分別遞迴執行合併排序
    3. 合併（Merge）：將兩個已排序的子陣列合併成一個有序陣列

時間複雜度：
    - 最佳情況：O(n log n)
    - 平均情況：O(n log n)
    - 最差情況：O(n log n)
    無論資料分布如何，時間複雜度始終為 O(n log n)，這是合併排序的一大優勢。

空間複雜度：
    - O(n)：需要額外的暫存空間來存放合併過程中的臨時陣列

穩定性：
    - 合併排序是「穩定排序」，相同值的元素在排序後會維持原本的相對順序。
"""

from typing import List


def merge_sort(arr: List[int]) -> List[int]:
    """
    合併排序 — 遞迴版本（回傳新陣列，不修改原陣列）

    參數：
        arr: 待排序的整數陣列

    回傳：
        排序後的新陣列
    """
    # 基底條件：長度為 0 或 1 的陣列已經是排序好的
    if len(arr) <= 1:
        return arr[:]

    # 步驟一：找到中間點，將陣列分成左右兩半
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    # 步驟二：遞迴排序左右兩半
    sorted_left = merge_sort(left_half)
    sorted_right = merge_sort(right_half)

    # 步驟三：合併兩個已排序的子陣列
    return _merge(sorted_left, sorted_right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    """
    合併兩個已排序的陣列為一個有序陣列。

    使用雙指標法：分別指向左右陣列的開頭，
    每次取較小的元素放入結果陣列，直到其中一邊用完，
    再把剩餘的元素全部接上。
    """
    result = []
    i = 0  # 左陣列的指標
    j = 0  # 右陣列的指標

    # 逐一比較左右兩邊的元素，取較小者放入結果
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            # 使用 <= 而非 < 以保持排序的穩定性
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    # 將左邊剩餘的元素加入結果
    result.extend(left[i:])
    # 將右邊剩餘的元素加入結果
    result.extend(right[j:])

    return result


def merge_sort_inplace(arr: List[int], left: int = 0, right: int = -1) -> None:
    """
    合併排序 — 原地排序版本（直接修改原陣列）

    參數：
        arr:   待排序的陣列
        left:  排序範圍的左邊界（含）
        right: 排序範圍的右邊界（含）
    """
    if right == -1:
        right = len(arr) - 1

    # 基底條件：子陣列長度小於等於 1
    if left >= right:
        return

    mid = (left + right) // 2

    # 遞迴排序左右兩半
    merge_sort_inplace(arr, left, mid)
    merge_sort_inplace(arr, mid + 1, right)

    # 合併已排序的兩半（使用暫存空間）
    _merge_inplace(arr, left, mid, right)


def _merge_inplace(arr: List[int], left: int, mid: int, right: int) -> None:
    """
    將 arr[left..mid] 和 arr[mid+1..right] 這兩段已排序的區間合併。
    需要 O(n) 的暫存空間。
    """
    # 建立左右兩段的暫存副本
    left_copy = arr[left:mid + 1]
    right_copy = arr[mid + 1:right + 1]

    i = 0  # 左暫存的指標
    j = 0  # 右暫存的指標
    k = left  # 原陣列的寫入位置

    while i < len(left_copy) and j < len(right_copy):
        if left_copy[i] <= right_copy[j]:
            arr[k] = left_copy[i]
            i += 1
        else:
            arr[k] = right_copy[j]
            j += 1
        k += 1

    # 把剩餘元素寫回
    while i < len(left_copy):
        arr[k] = left_copy[i]
        i += 1
        k += 1

    while j < len(right_copy):
        arr[k] = right_copy[j]
        j += 1
        k += 1


def merge_sort_bottom_up(arr: List[int]) -> List[int]:
    """
    合併排序 — 迭代版本（由下而上，Bottom-Up）

    不使用遞迴，改用迭代方式：
    先以大小 1 的區塊兩兩合併，再以大小 2 的區塊兩兩合併，
    依此類推，直到整個陣列排序完成。

    這個版本避免了遞迴的函式呼叫堆疊開銷。
    """
    result = arr[:]
    n = len(result)

    # 子陣列的大小從 1 開始，每次翻倍
    size = 1
    while size < n:
        # 對每一對相鄰的子陣列進行合併
        for start in range(0, n, size * 2):
            mid = min(start + size, n)
            end = min(start + size * 2, n)

            # 合併 result[start:mid] 和 result[mid:end]
            merged = _merge(result[start:mid], result[mid:end])
            result[start:start + len(merged)] = merged

        size *= 2

    return result


# ============================================================
# 使用範例與測試
# ============================================================

if __name__ == '__main__':
    import random
    import time

    print("=" * 60)
    print("  合併排序（Merge Sort）演算法示範")
    print("=" * 60)

    # --- 基本範例 ---
    print("\n【範例 1】基本排序")
    data = [38, 27, 43, 3, 9, 82, 10]
    print(f"  原始陣列：{data}")
    sorted_data = merge_sort(data)
    print(f"  排序結果：{sorted_data}")
    print(f"  原始陣列未被修改：{data}")

    # --- 原地排序版本 ---
    print("\n【範例 2】原地排序版本")
    data2 = [38, 27, 43, 3, 9, 82, 10]
    print(f"  排序前：{data2}")
    merge_sort_inplace(data2)
    print(f"  排序後：{data2}")

    # --- 迭代版本（由下而上） ---
    print("\n【範例 3】迭代版本（Bottom-Up）")
    data3 = [5, 1, 4, 2, 8, 0, 7, 3, 6, 9]
    print(f"  排序前：{data3}")
    print(f"  排序後：{merge_sort_bottom_up(data3)}")

    # --- 穩定性驗證 ---
    print("\n【範例 4】穩定性驗證")
    # 使用 (值, 原始索引) 的元組來驗證穩定性
    pairs = [(3, 'a'), (1, 'b'), (3, 'c'), (2, 'd'), (1, 'e')]
    print(f"  原始資料：{pairs}")
    # 只依據第一個元素（數值）排序
    sorted_pairs = merge_sort([p[0] for p in pairs])
    # 用完整的穩定排序示範
    stable_sorted = sorted(pairs, key=lambda x: x[0])  # Python 內建排序也是穩定的
    print(f"  穩定排序後：{stable_sorted}")
    print("  → 相同值的元素（如兩個 3、兩個 1）維持原本的相對順序")

    # --- 邊界情況測試 ---
    print("\n【範例 5】邊界情況")
    test_cases = [
        ([], "空陣列"),
        ([42], "單一元素"),
        ([1, 2, 3, 4, 5], "已排序陣列"),
        ([5, 4, 3, 2, 1], "反序陣列"),
        ([7, 7, 7, 7], "全部相同"),
        ([-3, 0, -1, 5, -2, 4], "含負數"),
    ]

    for test_arr, description in test_cases:
        result = merge_sort(test_arr)
        status = "✓" if result == sorted(test_arr) else "✗"
        print(f"  {status} {description:　<8}：{test_arr} → {result}")

    # --- 效能測試 ---
    print("\n【範例 6】效能比較")
    sizes = [1000, 5000, 10000, 50000]

    for n in sizes:
        random_data = [random.randint(0, 100000) for _ in range(n)]

        # 測試遞迴版本
        data_copy = random_data[:]
        start = time.perf_counter()
        merge_sort(data_copy)
        recursive_time = time.perf_counter() - start

        # 測試迭代版本
        data_copy = random_data[:]
        start = time.perf_counter()
        merge_sort_bottom_up(data_copy)
        iterative_time = time.perf_counter() - start

        # 測試原地排序版本
        data_copy = random_data[:]
        start = time.perf_counter()
        merge_sort_inplace(data_copy)
        inplace_time = time.perf_counter() - start

        print(f"  n={n:>6} | 遞迴: {recursive_time:.4f}s | "
              f"迭代: {iterative_time:.4f}s | 原地: {inplace_time:.4f}s")

    # --- 正確性驗證 ---
    print("\n【正確性驗證】以 1000 組隨機陣列進行測試...")
    all_passed = True
    for _ in range(1000):
        test = [random.randint(-1000, 1000) for _ in range(random.randint(0, 100))]
        expected = sorted(test)

        if merge_sort(test) != expected:
            all_passed = False
            break

        test_copy = test[:]
        merge_sort_inplace(test_copy)
        if test_copy != expected:
            all_passed = False
            break

        if merge_sort_bottom_up(test) != expected:
            all_passed = False
            break

    print(f"  結果：{'全部通過 ✓' if all_passed else '有測試失敗 ✗'}")

    print("\n" + "=" * 60)
    print("  複雜度總結")
    print("=" * 60)
    print("  時間複雜度：O(n log n) — 最佳、平均、最差皆相同")
    print("  空間複雜度：O(n) — 需要額外的暫存陣列")
    print("  穩　定　性：穩定排序")
    print("  適用場景：大量資料排序、需要穩定排序、外部排序（磁碟）")
    print("=" * 60)
