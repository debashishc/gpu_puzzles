import torch
import triton
import triton.language as tl

@triton.jit
def matrix_multiplication_kernel(
    a, b, c, 
    M, N, K,
    stride_am, stride_an, 
    stride_bn, stride_bk, 
    stride_cm, stride_ck
):
    i = tl.program_id(0)  
    j = tl.program_id(1)  
    
    acc = 0.0
    
    for k in range(N):
        a_idx = i * stride_am + k * stride_an
        a_val = tl.load(a + a_idx)
        
        b_idx = k * stride_bn + j * stride_bk
        b_val = tl.load(b + b_idx)
        
        acc += a_val * b_val
    
    c_idx = i * stride_cm + j * stride_ck
    tl.store(c + c_idx, acc)
    

# a, b, c are tensors on the GPU
def solve(a: torch.Tensor, b: torch.Tensor, c: torch.Tensor, M: int, N: int, K: int):
    stride_am, stride_an = N, 1 
    stride_bn, stride_bk = K, 1  
    stride_cm, stride_ck = K, 1
    
    grid = (M, K) 
    matrix_multiplication_kernel[grid](
        a, b, c,
        M, N, K,
        stride_am, stride_an,
        stride_bn, stride_bk,
        stride_cm, stride_ck
    )