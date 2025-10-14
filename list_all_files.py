import os
import glob


def list_all_json_files():
    print("=== ВСЕ JSON ФАЙЛЫ В ПАПКЕ ===")

    json_files = glob.glob("*.json")

    if not json_files:
        print("❌ JSON файлы не найдены!")
        return []

    print("📂 Все JSON файлы:")
    for i, file in enumerate(json_files, 1):
        file_size = os.path.getsize(file)
        print(f"   {i}. {file} ({file_size} байт)")

    return json_files


if __name__ == '__main__':
    list_all_json_files()