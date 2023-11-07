from pathlib import Path
import shutil
import sys
import re
##normalize
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ" + "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ".upper()
TRANSLATION = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k",
    "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "ts",
    "ch", "sh", "sch", "", "y", "", "e", "yu", "ja", "je", "i", "ji", "g"
) + (
    "A", "B", "V", "G", "D", "E", "E", "J", "Z", "I", "J", "K",
    "L", "M", "N", "O", "P", "R", "S", "T", "U", "F", "H", "TS",
    "CH", "SH", "SCH", "", "Y", "", "E", "YU", "JA", "JE", "I", "JI", "G"
)

TRANS = dict(zip(CYRILLIC_SYMBOLS, TRANSLATION))

def normalize(name: str) -> str:
    t_name = name.translate(TRANS)
    t_name = re.sub(r'[^a-zA-Z0-9]', '_', t_name)  # This regex replaces all characters except letters and numbers
    return t_name

##parser

FILE_CATEGORIES = {
    'JPEG': [],
    'PNG': [],
    'JPG': [],
    'SVG': [],
    'MP3': [],
    'OGG': [],
    'WAV': [],
    'AMR': [],
    'AVI': [],
    'MP4': [],
    'MOV': [],
    'MKV': [],
    'DOC': [],
    'DOCX': [],
    'TXT': [],
    'PDF': [],
    'XLSX': [],
    'PPTX': [],
    'ZIP': [],
    'GZ': [],
    'TAR': []
}

OTHER_FILES = []
FOLDERS = []
EXTENSIONS = set()
UNKNOWN = set()


def get_extension(filename: str) -> str:
    """Returns the file extension in uppercase, without the dot."""
    return Path(filename).suffix[1:].upper()


def scan(folder: Path) -> None:
    for item in folder.iterdir():
        if item.is_dir():
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'other_files'):
                FOLDERS.append(item)
                scan(item)
            continue

        ext = get_extension(item.name)
        fullname = folder / item.name

        if not ext:
            OTHER_FILES.append(fullname)
        else:
            container = FILE_CATEGORIES.get(ext)
            if container is not None:
                EXTENSIONS.add(ext)
                container.append(fullname)
            else:
                UNKNOWN.add(ext)
                OTHER_FILES.append(fullname)


    if len(sys.argv) < 2:
        print("Please provide a folder path to scan.")
        sys.exit(1)

    folder_for_scan = sys.argv[1]
    print(f'Start in folder {folder_for_scan}')

    scan(Path(folder_for_scan))

    for ext, files in FILE_CATEGORIES.items():
        print(f'{ext} files: {files}')

    print(f'Other files: {OTHER_FILES}')
    print(f'Types of files in folder: {EXTENSIONS}')
    print(f'Unknown types of files: {UNKNOWN}')
    print(FOLDERS[::-1])


def handle_media(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    shutil.move(str(filename), str(target_folder / normalize(filename.name)))

def handle_other(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    shutil.move(str(filename), str(target_folder / normalize(filename.name)))

def handle_archive(filename: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(filename.resolve()), str(folder_for_file.resolve()))
    except shutil.ReadError:
        print(f'{filename} is not an archive!')
        folder_for_file.rmdir()
        return None
    filename.unlink()

def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f'Failed to delete folder {folder}')

def main(folder: Path):
    print(f'Start in folder {folder.resolve()}')
    scan(folder)

    for file in FILE_CATEGORIES['JPEG']:
        handle_media(file, folder / 'images' / 'JPEG')
    # ... [similar lines for other file types]

    for file in FILE_CATEGORIES['ZIP']:
        handle_archive(file, folder / 'archives')

    for folder_item in FOLDERS[::-1]:
        handle_folder(folder_item)


def parse_and_scan_folder():
    if len(sys.argv) > 1:
        folder_for_scan = Path(sys.argv[1])
        if folder_for_scan.exists() and folder_for_scan.is_dir():
            main(folder_for_scan.resolve())
        else:
            print(f"'{folder_for_scan}' is not a valid directory.")
    else:
        print("Please provide the folder to be scanned as an argument.")

if __name__ == '__main__':
    parse_and_scan_folder()
