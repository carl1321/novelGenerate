"""
通用异步队列模块
"""
import asyncio
import threading
import uuid
from queue import Queue
from typing import Dict, Any, Callable, Optional
from enum import Enum
import time


class TaskStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AsyncTaskQueue:
    """通用异步任务队列"""
    
    def __init__(self):
        self.task_queue = Queue()
        self.task_states: Dict[str, Dict[str, Any]] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.running = False
        self.queue_thread: Optional[threading.Thread] = None
        
    def register_handler(self, task_type: str, handler: Callable):
        """注册任务处理器"""
        self.task_handlers[task_type] = handler
        
    def start(self):
        """启动队列处理器"""
        if self.running:
            return
            
        self.running = True
        self.queue_thread = threading.Thread(target=self._queue_processor, daemon=True)
        self.queue_thread.start()
        print("✅ 异步队列处理器已启动")
        
    def stop(self):
        """停止队列处理器"""
        self.running = False
        if self.queue_thread:
            self.queue_thread.join()
        print("✅ 异步队列处理器已停止")
        
    def submit_task(self, task_type: str, data: Dict[str, Any]) -> str:
        """提交任务到队列"""
        task_id = str(uuid.uuid4())
        
        # 创建任务
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'data': data,
            'created_at': time.time()
        }
        
        # 添加到队列
        self.task_queue.put(task)
        
        # 初始化任务状态
        self.task_states[task_id] = {
            'status': TaskStatus.QUEUED.value,
            'progress': 0,
            'created_at': task['created_at'],
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None
        }
        
        print(f"📝 任务 {task_id} 已加入队列，类型: {task_type}")
        return task_id
        
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        return self.task_states.get(task_id)
        
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        queued_count = len([t for t in self.task_states.values() if t['status'] == TaskStatus.QUEUED.value])
        processing_count = len([t for t in self.task_states.values() if t['status'] == TaskStatus.PROCESSING.value])
        completed_count = len([t for t in self.task_states.values() if t['status'] == TaskStatus.COMPLETED.value])
        failed_count = len([t for t in self.task_states.values() if t['status'] == TaskStatus.FAILED.value])
        
        return {
            'queue_size': self.task_queue.qsize(),
            'queued_tasks': queued_count,
            'processing_tasks': processing_count,
            'completed_tasks': completed_count,
            'failed_tasks': failed_count,
            'total_tasks': len(self.task_states)
        }
        
    def _queue_processor(self):
        """队列处理器（在后台线程中运行）"""
        print("🔄 队列处理器启动")
        
        while self.running:
            try:
                # 获取任务（阻塞等待）
                task = self.task_queue.get(timeout=1)
                if task is None:
                    continue
                    
                task_id = task['task_id']
                task_type = task['task_type']
                task_data = task['data']
                
                print(f"🚀 开始处理任务 {task_id}，类型: {task_type}")
                
                # 更新任务状态为处理中
                self.task_states[task_id].update({
                    'status': TaskStatus.PROCESSING.value,
                    'progress': 10,
                    'started_at': time.time()
                })
                
                # 获取处理器
                handler = self.task_handlers.get(task_type)
                if not handler:
                    self._mark_task_failed(task_id, f"未找到任务类型 {task_type} 的处理器")
                    continue
                
                # 执行任务
                try:
                    # 在新的事件循环中运行异步任务
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(handler(task_id, task_data))
                    
                    # 更新任务状态为完成
                    self.task_states[task_id].update({
                        'status': TaskStatus.COMPLETED.value,
                        'progress': 100,
                        'completed_at': time.time(),
                        'result': result
                    })
                    
                    print(f"✅ 任务 {task_id} 处理完成")
                    
                except Exception as e:
                    self._mark_task_failed(task_id, str(e))
                    
                finally:
                    loop.close()
                    
                # 标记任务完成
                self.task_queue.task_done()
                
            except Exception as e:
                if self.running:  # 只有在运行状态下才打印错误
                    print(f"❌ 队列处理错误: {e}")
                    
        print("🔄 队列处理器停止")
        
    def _mark_task_failed(self, task_id: str, error: str):
        """标记任务失败"""
        self.task_states[task_id].update({
            'status': TaskStatus.FAILED.value,
            'progress': 0,
            'completed_at': time.time(),
            'error': error
        })
        print(f"❌ 任务 {task_id} 处理失败: {error}")


# 全局队列实例
task_queue = AsyncTaskQueue()
