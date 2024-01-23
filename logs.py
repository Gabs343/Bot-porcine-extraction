import os
import logging
import pandas as pd
import time
import pyscreenrec
import subprocess
from datetime import datetime

class LogService:
    
    def __init__(self, name: str) -> None:
        self.path = f'{os.path.dirname(os.path.abspath(__file__))}\\logs\\{name}'
    
    def create() -> None: raise NotImplementedError
    def write_info(message: str) -> None: raise NotImplementedError
    def write_error() -> None: raise NotImplementedError
    def close() -> None: raise NotImplementedError
    
    def create_folder(self, path: str) -> None:
        if(not os.path.exists(path)):
            os.makedirs(path)
    
class LogTxt(LogService):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.__name: str = f'{name}.txt'
        self.__logger: logging.Logger = None
        self.create_folder(path=self.path)
        self.create()
        
    @property
    def file_path(self) -> str:
        return f'{self.path}\\{self.__name}'
            
    def create(self) -> None:
        logger_file: str = self.file_path
        formatter: logging.Formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler: logging.FileHandler = logging.FileHandler(logger_file)
        
        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        self.__logger.addHandler(handler)
        
    def write_info(self, message: str) -> None:
        self.__logger.info(message)
        
    def write_and_execute(self, function, **kwargs):
        some_data = None
        self.write_info(message=f'executing function: "{function.__name__}" with keyword arguments: {kwargs}')
        function_start : float = time.time()
        some_data = function(**kwargs)
        function_end: float = time.time()
        elapsed_time: float = function_end - function_start
        self.write_info(message=f'function: "{function.__name__}" finished in {elapsed_time} seconds')
        return some_data
        
    def write_error(self, message: str, detail: str = None) -> None:
        self.__logger.critical(f'{message} - {detail}')

    def close(self) -> None:
        for handler in self.__logger.handlers[:]:
            self.__logger.removeHandler(handler)
            handler.close()
            
    def __str__(self) -> str:
        return type(self).__name__
            
class LogXlsx(LogService):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.__name: str = f'{name}.xlsx'
        self.__row: int = 1
        self.__log: dict = {}
        self.create_folder(path=self.path)
        self.create()
        
    @property
    def file_path(self) -> str:
        return f'{self.path}\\{self.__name}'
            
    def create(self, columns: list[str] = None) -> None:
        log_columns: list[str] = ["Time", "Title", "Status", "Detail"]
        if(columns):
            log_columns.extend(columns)
        self.__log = dict.fromkeys(log_columns)
        
        for key in self.__log.keys():
            self.__log[key] = {}
        
    def write_info(self, message: str) -> None:
        self.__log["Time"][self.__row] = datetime.now().strftime("%H:%M:%S")
        self.__log["Title"][self.__row] = message
        self.__log["Status"][self.__row] = "OK"
        self.__row += 1
        
    def write_error(self, message: str, detail: str = None) -> None:
        self.__log["Time"][self.__row] = datetime.now().strftime("%H:%M:%S")
        self.__log["Title"][self.__row] = message
        self.__log["Detail"][self.__row] = detail
        self.__log["Status"][self.__row] = "ERROR"
        self.__row += 1
        
    def write_in_column(self, column: str, message: str) -> None:
        self.__log[column][self.__row] = message
        
    def close(self) -> None:
        dataframe: pd.DataFrame = pd.DataFrame.from_dict(self.__log, orient="index").T
        dataframe = dataframe.style.apply(self.__style_status, subset='Status')
        dataframe.to_excel(self.file_path, engine='openpyxl')
        
    def __style_status(self, value: str) -> list[str]:
        colors = {'OK': 'green', 'ERROR': 'red'}
        return [f'background-color: {colors[val]}; color:white' for val in value]
        
    def __str__(self) -> str:
        return type(self).__name__
    
class LogVideo(LogService):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self.__name: str = f'{name}.mp4'
        self.__recorder = pyscreenrec.ScreenRecorder()
        self.create_folder(path=self.path)
        self.create()
    
    @property
    def file_path(self) -> str:
        return f'{self.path}\\{self.__name}'
    
    def create(self) -> None:
        self.__recorder.start_recording(self.file_path, 10)
    
    def close(self) -> None:
        self.__recorder.stop_recording()
        self.__convert_to_mkv()
        
    def __convert_to_mkv(self):
        if(os.path.exists(self.file_path)):
            output = self.file_path.replace('.mp4', '.mkv')
            subprocess.run(f'ffmpeg -i "{self.file_path}" -f matroska "{output}"', shell=True)
            os.remove(self.file_path)
            self.__name = self.__name.replace('.mp4', '.mkv')  