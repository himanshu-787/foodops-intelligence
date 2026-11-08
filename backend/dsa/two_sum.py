# Brute force: O(n²) time, O(1) space
def two_sum_slow(prices, target):
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            if prices[i] + prices[j] == target:
                return [i, j]
    return []


# Optimized with hashmap: O(n) time, O(n) space
def two_sum_fast(prices, target):
    seen = {}                          # price -> index
    for i, price in enumerate(prices):
        need = target - price
        if need in seen:
            return [seen[need], i]
        seen[price] = i
    return []


if __name__ == "__main__":
    prices = [250, 80, 120, 40, 180]
    print(two_sum_slow(prices, 300))   # [1, 4] ya [2, 4]
    print(two_sum_fast(prices, 300))