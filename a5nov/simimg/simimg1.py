# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import cv2
import numpy as np
from PIL import Image
import imagehash
from skimage.metrics import structural_similarity as ssim
import albumentations as A
from multiprocessing import Pool, Manager

input_folder = 'photos'
output_folder = 'organized_photos'

transform = A.Compose([A.Resize(256, 256)])


def preprocess_image(image_path):
    image = Image.open(image_path).convert('RGB')
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    augmented = transform(image=img_cv)
    return Image.fromarray(cv2.cvtColor(augmented['image'], cv2.COLOR_BGR2RGB))


def get_hash(image):
    return imagehash.phash(image)


def calculate_ssim(img1, img2):
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    score, _ = ssim(img1_gray, img2_gray, full=True)
    return score


def process_image(args):
    filename, input_folder, groups, lock = args
    path = os.path.join(input_folder, filename)
    image = preprocess_image(path)
    img_hash = get_hash(image)
    img_array = np.array(image)

    with lock:
        matched_group = None
        for group in groups:
            hamming_dist = img_hash - group['hash']
            if hamming_dist <= 6:
                similarity = calculate_ssim(img_array, group['image_array'])
                if similarity >= 0.95:
                    matched_group = group
                    break

        if matched_group is None:
            group_name = f'group_{len(groups) + 1}'
            group_folder = os.path.join(output_folder, group_name)
            os.makedirs(group_folder, exist_ok=True)
            groups.append(
                {
                    'hash': img_hash,
                    'image_array': img_array,
                    'folder': group_folder,
                }
            )
            matched_group = groups[-1]

    dest_path = os.path.join(matched_group['folder'], filename)
    os.rename(path, dest_path)
    return f"Moved '{filename}' to '{matched_group['folder']}'"


def folderize_similar_images(folder):
    os.makedirs(output_folder, exist_ok=True)
    manager = Manager()
    groups = manager.list()
    lock = manager.Lock()
    args = [
        (f, folder, groups, lock)
        for f in os.listdir(folder)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]

    with Pool() as pool:
        results = pool.map(process_image, args)

    for r in results:
        print(r)


if __name__ == '__main__':
    folderize_similar_images(input_folder)
