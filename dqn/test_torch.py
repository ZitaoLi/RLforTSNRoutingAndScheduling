from tqdm import tqdm
import torch

@torch.jit.script
def foo():
    x = torch.ones((1024 * 12, 1024 * 12), dtype=torch.float32)
    y = torch.ones((1024 * 12, 1024 * 12), dtype=torch.float32)
    z = x + y
    return z


if __name__ == '__main__':
    z0 = None
    for _ in tqdm(range(100000)):
        zz = foo()
        if z0 is None:
            z0 = zz
        else:
            z0 += zz