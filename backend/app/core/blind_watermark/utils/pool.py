"""
並行處理池模組

提供多種並行處理模式的統一介面
"""
import sys
import multiprocessing
import warnings
from typing import Callable, List, Any, TypeVar, Optional

from ..types import PoolMode

if sys.platform != 'win32':
    try:
        multiprocessing.set_start_method('fork')
    except RuntimeError:
        # 已經設定過，忽略
        pass

T = TypeVar('T')
R = TypeVar('R')


class CommonPool:
    """普通串行處理池"""
    
    def map(self, func: Callable[[T], R], args: List[T]) -> List[R]:
        """
        串行映射函數
        
        Args:
            func: 要應用的函數
            args: 參數列表
            
        Returns:
            結果列表
        """
        return list(map(func, args))


class AutoPool:
    """
    自動選擇並行處理模式的池
    
    支援模式：
    - common: 串行處理
    - multithreading: 多執行緒
    - multiprocessing: 多進程
    - vectorization: 向量化（預留）
    - cached: 快取模式（預留）
    """
    
    def __init__(self, mode: PoolMode = 'common', processes: Optional[int] = None):
        """
        初始化處理池
        
        Args:
            mode: 處理模式
            processes: 進程/執行緒數量
        """
        # Windows 不支援 multiprocessing fork 模式
        if mode == 'multiprocessing' and sys.platform == 'win32':
            warnings.warn(
                'Windows 不支援 multiprocessing，自動切換至 multithreading',
                RuntimeWarning
            )
            mode = 'multithreading'
        
        self.mode = mode
        self.processes = processes
        
        if mode == 'vectorization':
            self.pool = CommonPool()
        elif mode == 'cached':
            self.pool = CommonPool()
        elif mode == 'multithreading':
            from multiprocessing.dummy import Pool as ThreadPool
            self.pool = ThreadPool(processes=processes)
        elif mode == 'multiprocessing':
            from multiprocessing import Pool
            self.pool = Pool(processes=processes)
        else:  # common
            self.pool = CommonPool()
    
    def map(self, func: Callable[[T], R], args: List[T]) -> List[R]:
        """
        映射函數到參數列表
        
        Args:
            func: 要應用的函數
            args: 參數列表
            
        Returns:
            結果列表
        """
        return self.pool.map(func, args)
    
    def __enter__(self):
        """上下文管理器進入"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        if hasattr(self.pool, 'close'):
            self.pool.close()
        if hasattr(self.pool, 'join'):
            self.pool.join()

