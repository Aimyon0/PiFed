# download_mnist.py
import os
import urllib.request
import gzip
import numpy as np

def download_and_save_mnist():
    base_url = "https://ossci-datasets.s3.amazonaws.com/mnist/"
    # 如果官方源慢，可以使用国内镜像源
    # base_url = "https://ossci-datasets.s3.amazonaws.com/mnist/"
    
    files = {
        "X_train": "train-images-idx3-ubyte.gz",
        "y_train": "train-labels-idx1-ubyte.gz",
        "X_test": "t10k-images-idx3-ubyte.gz",
        "y_test": "t10k-labels-idx1-ubyte.gz"
    }

    os.makedirs("mnist_data", exist_ok=True)
    
    for key, filename in files.items():
        filepath = os.path.join("mnist_data", filename)
        if not os.path.exists(filepath):
            print(f"正在下载 {filename}...")
            urllib.request.urlretrieve(base_url + filename, filepath)
        
        # 解压并转换为 numpy 数组
        with gzip.open(filepath, 'rb') as f:
            if "images" in filename:
                # 跳过前16个字节的头部信息
                data = np.frombuffer(f.read(), np.uint8, offset=16)
                # 归一化到 0~1 之间
                data = data.reshape(-1, 784).astype(np.float32) / 255.0
            else:
                # 跳过前8个字节的头部信息
                data = np.frombuffer(f.read(), np.uint8, offset=8)
            
            np.save(os.path.join("mnist_data", f"{key}.npy"), data)
            print(f"成功保存 {key}.npy, 形状: {data.shape}")

if __name__ == "__main__":
    download_and_save_mnist()