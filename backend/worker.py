from PySide6.QtCore import QObject, Signal, Slot

class InferenceWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, backend_func, question):
        super().__init__()
        self.backend_func = backend_func
        self.question = question

    @Slot()
    def run(self):
        try:
            result = self.backend_func(self.question)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
