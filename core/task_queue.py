import queue
import threading
import uuid
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Any, Dict, Optional, List, Tuple
import time

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()

class Priority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

    def __lt__(self, other):
        return self.value < other.value

@dataclass(order=True)
class Task:
    priority: Priority
    id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    func: Callable = field(compare=False, default=None)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: dict = field(default_factory=dict, compare=False)
    callbacks: Dict[str, Callable] = field(default_factory=dict, compare=False)
    cancellable: bool = field(default=True, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    progress: float = field(default=0.0, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    result: Any = field(default=None, compare=False)

class TaskQueueService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TaskQueueService, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.queue = queue.PriorityQueue()
        self.active_tasks: Dict[str, Task] = {}
        self.running_task: Optional[Task] = None
        self.stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        self._initialized = True
        logger.info("TaskQueueService iniciado.")

    def add_task(self, func, args=(), kwargs=None, priority=Priority.NORMAL, 
                 callbacks=None, cancellable=True) -> str:
        if kwargs is None: kwargs = {}
        if callbacks is None: callbacks = {}
        
        task = Task(
            priority=priority,
            func=func,
            args=args,
            kwargs=kwargs,
            callbacks=callbacks,
            cancellable=cancellable
        )
        
        self.active_tasks[task.id] = task
        # Usamos o valor negativo da prioridade porque PriorityQueue é um min-heap
        self.queue.put((-priority.value, time.time(), task))
        logger.debug(f"Tarefa {task.id} adicionada à fila com prioridade {priority.name}.")
        return task.id

    def cancel_task(self, task_id: str) -> bool:
        if task_id not in self.active_tasks:
            return False
        
        task = self.active_tasks[task_id]
        if not task.cancellable:
            return False
        
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            # A tarefa ainda está na fila, o worker irá ignorá-la
            return True
        elif task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.CANCELLED
            # Aqui dependeria da função monitorar o status, 
            # mas marcamos como cancelado para o callback final
            return True
        
        return False

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                # Timeout curto para verificar stop_event periodicamente
                _, _, task = self.queue.get(timeout=1.0)
                
                if task.status == TaskStatus.CANCELLED:
                    self._handle_callback(task, 'on_cancel')
                    continue
                
                self.running_task = task
                task.status = TaskStatus.RUNNING
                self._handle_callback(task, 'on_start')
                
                try:
                    logger.info(f"Executando tarefa {task.id}...")
                    # Injeta o próprio objeto task nos kwargs se a função aceitar progress_callback
                    # Isso permite que a função reporte progresso
                    task.result = task.func(*task.args, **task.kwargs)
                    task.status = TaskStatus.COMPLETED
                    self._handle_callback(task, 'on_complete', task.result)
                except Exception as e:
                    logger.exception(f"Erro ao executar tarefa {task.id}: {e}")
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    self._handle_callback(task, 'on_error', task.error)
                finally:
                    self.running_task = None
                    self.queue.task_done()
                    
            except queue.Empty:
                continue

    def _handle_callback(self, task: Task, name: str, *args):
        callback = task.callbacks.get(name)
        if callback:
            # Callbacks devem ser agendados na thread principal pelo chamador (ex: app.after)
            # ou o callback deve lidar com thread safety.
            try:
                callback(*args)
            except Exception as e:
                logger.error(f"Erro no callback {name} da tarefa {task.id}: {e}")

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        task = self.active_tasks.get(task_id)
        return task.status if task else None

    def get_queue_size(self) -> int:
        return self.queue.qsize()

    def is_processing(self) -> bool:
        return self.running_task is not None or not self.queue.empty()

    def shutdown(self):
        self.stop_event.set()
        logger.info("TaskQueueService encerrando...")

def get_task_queue() -> TaskQueueService:
    return TaskQueueService()
