import json
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, END
from tkinter import font as tkfont


JSON_FILE = "stores.json"
PROJECT_PATH = r"D:/phonestore"
BRANCH = "main"
COUNT_FILE = "commit_count.txt"

# 전역 데이터
stores = []
filtered_data = []
last_selected_index = None   # 🔸 마지막으로 선택한 인덱스 기억


# =========================
# Commit Count
# =========================
def load_commit_count():
    if not os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, "w") as f:
            f.write("1")
        return 1

    with open(COUNT_FILE, "r") as f:
        return int(f.read().strip())


def save_commit_count(n):
    with open(COUNT_FILE, "w") as f:
        f.write(str(n))


# =========================
# Git 실행
# =========================
def run_git_cmd(cmd):
    return subprocess.run(
        cmd,
        cwd=PROJECT_PATH,
        shell=True,
        text=True,
        capture_output=True
    )


# =========================
# JSON LOAD / SAVE
# =========================
def load_stores():
    if not os.path.exists(JSON_FILE):
        return []

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_stores(stores_data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(stores_data, f, ensure_ascii=False, indent=2)

    refresh_list()  # 리스트 새로고침


# =========================
# 목록 갱신
# =========================
def refresh_list(data=None):
    store_list.delete(0, END)

    global stores, filtered_data
    if data is None:
        stores = load_stores()
        data = stores

    filtered_data = data  # 🔸 현재 화면에 보이는 데이터 기준으로 유지

    for s in data:
        store_list.insert(END, f"{s['name']} / {s['region']}")


# =========================
# 리스트 클릭 시 입력값 로드
# =========================
def on_select(event):
    global last_selected_index

    sel = store_list.curselection()
    if not sel:
        return

    index = sel[0]
    last_selected_index = index  # 🔸 선택 인덱스 기억

    s = filtered_data[index]

    name_var.set(s["name"])
    region_var.set(s["region"])
    lat_var.set(s["lat"])
    lng_var.set(s["lng"])
    address_var.set(s["address"])
    chat_var.set(s["kakaoOpenChat"])
    phone_var.set(s["phoneNumber"])


# =========================
# 추가
# =========================
def add_store():
    global stores

    store = {
        "name": name_var.get().strip(),
        "region": region_var.get().strip(),
        "lat": lat_var.get().strip(),
        "lng": lng_var.get().strip(),
        "address": address_var.get().strip(),
        "kakaoOpenChat": chat_var.get().strip(),
        "phoneNumber": phone_var.get().strip()
    }

    if not store["name"] or not store["region"]:
        messagebox.showerror("입력 오류", "매장명과 지역은 필수입니다.")
        return

    stores.append(store)
    save_stores(stores)

    clear_inputs()
    refresh_list()


# =========================
# 수정 저장
# =========================
def update_store():
    global last_selected_index, stores

    # 🔸 화면에서 선택이 풀려도 last_selected_index 기준으로 수정
    if last_selected_index is None:
        messagebox.showwarning("선택 없음", "수정할 매장을 선택하세요.")
        return

    if last_selected_index < 0 or last_selected_index >= len(filtered_data):
        messagebox.showwarning("선택 오류", "선택한 매장을 찾을 수 없습니다.")
        return

    # 화면 기준 인덱스 → 실제 stores 인덱스
    target_obj = filtered_data[last_selected_index]
    try:
        global_idx = stores.index(target_obj)
    except ValueError:
        messagebox.showwarning("선택 오류", "선택한 매장이 목록에서 변경되었습니다.")
        return

    stores[global_idx] = {
        "name": name_var.get().strip(),
        "region": region_var.get().strip(),
        "lat": lat_var.get().strip(),
        "lng": lng_var.get().strip(),
        "address": address_var.get().strip(),
        "kakaoOpenChat": chat_var.get().strip(),
        "phoneNumber": phone_var.get().strip()
    }

    save_stores(stores)

    messagebox.showinfo("수정 완료", "매장 정보가 수정되었습니다.")
    last_selected_index = None
    clear_inputs()
    refresh_list()


# =========================
# 삭제
# =========================
def delete_store():
    global last_selected_index, stores

    if last_selected_index is None:
        messagebox.showwarning("선택 없음", "삭제할 매장을 선택하세요.")
        return

    if last_selected_index < 0 or last_selected_index >= len(filtered_data):
        messagebox.showwarning("선택 오류", "선택한 매장을 찾을 수 없습니다.")
        return

    s = filtered_data[last_selected_index]

    confirm = messagebox.askyesno(
        "삭제 확인",
        f"정말 삭제할까요?\n\n{s['name']} / {s['region']}"
    )

    if not confirm:
        return

    # 실제 stores 리스트에서 제거
    try:
        stores.remove(s)
    except ValueError:
        pass

    save_stores(stores)

    clear_inputs()
    last_selected_index = None
    refresh_list()


# =========================
# 입력 초기화
# =========================
def clear_inputs():
    global last_selected_index

    name_var.set("")
    region_var.set("")
    lat_var.set("")
    lng_var.set("")
    address_var.set("")
    chat_var.set("")
    phone_var.set("")

    last_selected_index = None


# =========================
# JSON 업로드 + Git Push
# =========================
def upload_and_push():
    try:
        save_stores(stores)
    except Exception:
        pass

    count = load_commit_count()
    commit_msg = f"{count}"

    r1 = run_git_cmd("git add .")
    if r1.returncode != 0:
        messagebox.showerror("Git 오류", r1.stderr)
        return

    r2 = run_git_cmd(f'git commit -m "{commit_msg}"')

    if "nothing to commit" in r2.stdout:
        messagebox.showinfo("알림", "변경사항이 없습니다.")
        return

    r3 = run_git_cmd(f"git push origin {BRANCH}")
    if r3.returncode != 0:
        messagebox.showerror("Push 실패", r3.stderr)
        return

    save_commit_count(count + 1)

    messagebox.showinfo("업로드 완료", f"commit: {commit_msg}")


# =========================
# 검색
# =========================
def search_store():
    keyword = search_var.get().strip()

    global filtered_data
    if not keyword:
        filtered_data = stores
    else:
        filtered_data = [
            s for s in stores
            if keyword in s["name"] or keyword in s["region"]
        ]

    refresh_list(filtered_data)


# ⭐ 엔터 검색 + 입력값 자동 초기화
def search_and_clear(event=None):
    global last_selected_index
    search_store()
    search_var.set("")
    last_selected_index = None


# =========================
# UI
# =========================
root = tk.Tk()
root.title("Store JSON Manager + Git Push")
root.geometry("760x540")
root.resizable(False, False)

# ⭐ 한글 폰트 통일 (돋보기 현상 방지)
default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(family="맑은 고딕", size=10)

stores = load_stores()
filtered_data = stores


# =========================
# LEFT Panel
# =========================
frame_left = tk.Frame(root)
frame_left.pack(side="left", fill="y", padx=10, pady=10)

tk.Label(frame_left, text="매장 검색").pack()

search_var = tk.StringVar()

entry_search = tk.Entry(frame_left, textvariable=search_var)
entry_search.pack(fill="x")

# ⭐ 엔터키 → 검색 + 입력창 자동 초기화
entry_search.bind("<Return>", search_and_clear)

tk.Button(frame_left, text="검색", command=search_and_clear)\
    .pack(fill="x", pady=5)

tk.Label(frame_left, text="매장 목록", font=("맑은 고딕", 12, "bold")).pack()

store_list = Listbox(frame_left, width=35, height=25)
store_list.pack()
store_list.bind("<<ListboxSelect>>", on_select)

refresh_list()


# =========================
# RIGHT Panel
# =========================
frame_right = tk.Frame(root)
frame_right.pack(side="right", fill="both", padx=10, pady=10)


def add_input(label, var):
    tk.Label(frame_right, text=label, anchor="w").pack(fill="x")
    tk.Entry(frame_right, textvariable=var).pack(fill="x", pady=2)


name_var = tk.StringVar()
region_var = tk.StringVar()
lat_var = tk.StringVar()
lng_var = tk.StringVar()
address_var = tk.StringVar()
chat_var = tk.StringVar()
phone_var = tk.StringVar()

add_input("매장명", name_var)
add_input("지역", region_var)
add_input("위도 (lat)", lat_var)
add_input("경도 (lng)", lng_var)
add_input("주소", address_var)
add_input("카카오 오픈채팅", chat_var)
add_input("전화번호", phone_var)


# =========================
# 버튼 2줄 배치
# =========================
btn_top = tk.Frame(frame_right)
btn_top.pack(fill="x", pady=6)

tk.Button(btn_top, text="추가", width=10, command=add_store)\
    .pack(side="left", padx=4)

tk.Button(btn_top, text="수정 저장", width=10, command=update_store)\
    .pack(side="left", padx=4)

tk.Button(btn_top, text="삭제", width=10, command=delete_store)\
    .pack(side="left", padx=4)


btn_bottom = tk.Frame(frame_right)
btn_bottom.pack(fill="x", pady=6)

tk.Button(btn_bottom, text="입력 초기화", width=10,
          command=clear_inputs)\
    .pack(side="left", padx=4)

tk.Button(btn_bottom, text="JSON 업로드", width=18,
          command=upload_and_push)\
    .pack(side="right", padx=4)


root.mainloop()
