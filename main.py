import json
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, Listbox, END

# =========================
# 설정
# =========================
JSON_FILE = "stores.json"
PROJECT_PATH = r"D:/phonestore"
BRANCH = "main"
COUNT_FILE = "commit_count.txt"


# =========================
# Commit Count 관리
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
# Git 명령 실행 유틸
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


def save_stores(stores):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(stores, f, ensure_ascii=False, indent=2)

    messagebox.showinfo("저장 완료", "stores.json 저장되었습니다.")
    refresh_list()


# =========================
# UI 목록 갱신
# =========================
def refresh_list():
    store_list.delete(0, END)

    global stores
    stores = load_stores()

    for s in stores:
        store_list.insert(END, f"{s['name']} / {s['region']}")


# =========================
# 리스트 선택 시 입력창 로드
# =========================
def on_select(event):
    if not store_list.curselection():
        return

    index = store_list.curselection()[0]
    s = stores[index]

    name_var.set(s["name"])
    region_var.set(s["region"])
    lat_var.set(s["lat"])
    lng_var.set(s["lng"])
    address_var.set(s["address"])
    chat_var.set(s["kakaoOpenChat"])
    phone_var.set(s["phoneNumber"])


# =========================
# 매장 추가
# =========================
def add_store():
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
# 매장 삭제
# =========================
def delete_store():
    if not store_list.curselection():
        messagebox.showwarning("선택 없음", "삭제할 매장을 선택하세요.")
        return

    index = store_list.curselection()[0]
    s = stores[index]

    confirm = messagebox.askyesno(
        "삭제 확인",
        f"정말 삭제할까요?\n\n{s['name']} / {s['region']}"
    )

    if not confirm:
        return

    del stores[index]
    save_stores(stores)

    clear_inputs()
    refresh_list()


# =========================
# 입력칸 초기화
# =========================
def clear_inputs():
    name_var.set("")
    region_var.set("")
    lat_var.set("")
    lng_var.set("")
    address_var.set("")
    chat_var.set("")
    phone_var.set("")


# =========================
# JSON 업로드 + Git Push
# =========================
def upload_and_push():
    try:
        save_stores(stores)
    except:
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

    messagebox.showinfo("업로드 완료", f"JSON 업로드 & Git Push 완료\ncommit: {commit_msg}")


# =========================
# Tkinter UI
# =========================
root = tk.Tk()
root.title("Store JSON Manager + Git Push")
root.geometry("860x540")
root.resizable(False, False)

stores = load_stores()


# =========================
# Left List
# =========================
frame_left = tk.Frame(root)
frame_left.pack(side="left", fill="y", padx=10, pady=10)

tk.Label(frame_left, text="매장 목록", font=("맑은 고딕", 12, "bold")).pack()

store_list = Listbox(frame_left, width=35, height=27)
store_list.pack()
store_list.bind("<<ListboxSelect>>", on_select)

refresh_list()


# =========================
# Right Input Panel
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
# Button Row
# =========================
btn_frame = tk.Frame(frame_right)
btn_frame.pack(fill="x", pady=10)

tk.Button(btn_frame, text="추가", width=10, command=add_store)\
    .pack(side="left", padx=5)

tk.Button(btn_frame, text="삭제", width=10, command=delete_store)\
    .pack(side="left", padx=5)

tk.Button(btn_frame, text="입력 초기화", width=10, command=clear_inputs)\
    .pack(side="left", padx=5)

tk.Button(btn_frame, text="JSON 업로드 (Git Push)", width=18,
          command=upload_and_push)\
    .pack(side="right", padx=5)


root.mainloop()
