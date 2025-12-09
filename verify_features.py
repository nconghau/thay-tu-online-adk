from agent.feature_life_path import tinh_con_so_chu_dao
from agent.feature_zodiac import xem_cung_hoang_dao
from agent.feature_numerology import luan_giai_than_so_hoc

dob = "20/11/1995"
print(f"--- TEST DATA FOR: {dob} ---\n")

print("[1] LIFE PATH")
print(tinh_con_so_chu_dao(dob)['message'])
print("\n" + "="*50 + "\n")

print("[2] ZODIAC")
print(xem_cung_hoang_dao(dob)['message'])
print("\n" + "="*50 + "\n")

print("[3] NUMEROLOGY")
print(luan_giai_than_so_hoc(dob)['message'])
print("\n" + "="*50 + "\n")
