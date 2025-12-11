# algorithms.py

# --- HELPER ---
def get_val(item, key):
    val = item.get(key, '')
    return float(val) if key == 'ipk' and val else str(val).lower()

def should_swap(val_a, val_b, key):
    return val_a < val_b if key == 'ipk' else val_a > val_b

# --- SEARCHING ---
def algo_linear_search(data, q):
    return [i for i in data if q.lower() in i['nama'].lower() or q.lower() in i['nim'].lower()]

def algo_sequential_search(data, q):
    res = []; i = 0; n = len(data); q = q.lower()
    while i < n:
        if q in data[i]['nama'].lower() or q in data[i]['nim'].lower(): res.append(data[i])
        i += 1
    return res

def algo_binary_search(data, q):
    sorted_data = sorted(data, key=lambda x: x['nama'].lower())
    q = q.lower(); low = 0; high = len(sorted_data) - 1; found = -1
    while low <= high:
        mid = (low + high) // 2
        val = sorted_data[mid]['nama'].lower()
        if val.startswith(q): found = mid; break
        elif val < q: low = mid + 1
        else: high = mid - 1
    if found != -1:
        l = found
        while l >= 0 and sorted_data[l]['nama'].lower().startswith(q): l -= 1
        r = found
        while r < len(sorted_data) and sorted_data[r]['nama'].lower().startswith(q): r += 1
        return sorted_data[l+1 : r]
    return []

# --- SORTING ---
def algo_bubble_sort(data, key):
    n = len(data); arr = data.copy()
    for i in range(n):
        for j in range(0, n - i - 1):
            if should_swap(get_val(arr[j], key), get_val(arr[j+1], key), key):
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def algo_selection_sort(data, key):
    arr = data.copy(); n = len(arr)
    for i in range(n):
        idx = i
        for j in range(i + 1, n):
            val_j = get_val(arr[j], key); val_idx = get_val(arr[idx], key)
            swap = val_j > val_idx if key == 'ipk' else val_j < val_idx
            if swap: idx = j
        arr[i], arr[idx] = arr[idx], arr[i]
    return arr

def algo_insertion_sort(data, key):
    arr = data.copy()
    for i in range(1, len(arr)):
        key_item = arr[i]; key_val = get_val(key_item, key); j = i - 1
        while j >= 0:
            compare = get_val(arr[j], key)
            swap = key_val > compare if key == 'ipk' else key_val < compare
            if swap: arr[j+1] = arr[j]; j -= 1
            else: break
        arr[j+1] = key_item
    return arr

def algo_shell_sort(data, key):
    arr = data.copy(); n = len(arr); gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]; temp_val = get_val(temp, key); j = i
            while j >= gap:
                compare = get_val(arr[j-gap], key)
                swap = compare < temp_val if key == 'ipk' else compare > temp_val
                if swap: arr[j] = arr[j-gap]; j -= gap
                else: break
            arr[j] = temp
        gap //= 2
    return arr

def algo_merge_sort(data, key):
    if len(data) <= 1: return data
    mid = len(data) // 2
    left = algo_merge_sort(data[:mid], key)
    right = algo_merge_sort(data[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    res = []; i = j = 0
    while i < len(left) and j < len(right):
        vl = get_val(left[i], key); vr = get_val(right[j], key)
        pick_l = vl > vr if key == 'ipk' else vl < vr
        if pick_l: res.append(left[i]); i += 1
        else: res.append(right[j]); j += 1
    res.extend(left[i:]); res.extend(right[j:])
    return res