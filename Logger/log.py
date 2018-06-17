class Logger:
    def __init__(self, name):
        print('start ' + name)

    def log(self, message):
        raise NotImplementedError("Subclass must implement abstract method")

    def set_expose_log(self, is_expose_log):
        raise NotImplementedError("Subclass must implement abstract method")

class LocalLogger(Logger):
    _is_expose_log = True

    def __init__(self):
        super(LocalLogger, self).__init__("LocalLogger")
    
    def log(self, message):
        if self._is_expose_log:
            print(message)
    
    def set_expose_log(self, is_expose_log):
        self._is_expose_log = is_expose_log