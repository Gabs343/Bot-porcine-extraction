import time
import sys

from logs import *
from settings import *
from exceptions import *
from processes.magyp import MagypProcess
from processes.pdf_extraction import PDFProcess
  
class Main:
    __settings_services_classes: tuple = ()
    __logs_services_classes: tuple = (LogTxt, LogXlsx, LogVideo)
    __settings_services: list[SettingService] = []
    __logs_services: list[LogService] = []
    __bot_name: str = "TEST"
    __status: str = "READY"
    __status_callback = None
    __had_error: bool = False
    
    def __init__(self) -> None:
        self.__settings_services = self.__get_settings_services()
        
    @property   
    def settings_services(self) -> list[SettingService]:
        return self.__settings_services
    
    @property   
    def logs_services(self) -> list[LogService]:
        return self.__logs_services
    
    @property   
    def bot_name(self) -> str:
        return self.__bot_name
    
    @property   
    def status(self) -> str:
        return self.__status
    
    @property   
    def status_callback(self) -> str:
        return self.__status_callback
    
    @status_callback.setter
    def status_callback(self, callback) -> None:
        self.__status_callback = callback
        
    def start(self, *args) -> None:
        try:
            self.__execution_begun()

            #Your code goes here
            self.do_magyp_process()
            ####################
            
            self.__execution_completed()
        except Exception as e:
            raise Exception(e)
        
    def do_magyp_process(self):
        try:
            logXlsx: LogXlsx = self.__execute_action(function=self.__get_log_service, log_type=LogXlsx)
            logTxt: LogTxt = self.__execute_action(function=self.__get_log_service, log_type=LogTxt)

            self.__execute_action(function=logTxt.write_info, message='Magyp process has begun')

            data: dict = {}
            data['magyp'] = dict.fromkeys(['minimo', 'maximo', 'promedio'], 'Error')
            
            page: MagypProcess = MagypProcess()
            self.__execute_action(function=page.open)
            self.__execute_action(function=page.click_current_year)
            self.__execute_action(function=self.__create_folders, folders=['web-output'])
            pdf_path: str = self.__execute_action(function=page.download_last_pdf, folder_output='web-output')
            
            self.do_pdf_extraction_process(path=pdf_path, data=data)
            
            self.__execute_action(function=logXlsx.write_info, message='Magyp Process')
            self.__execute_action(function=logTxt.write_info, message='Magyp process completed')
        except Exception as e:
            self.__execute_action(function=logXlsx.write_error, message='Magyp Process', detail='There was an error in the magyp page')
            self.__execute_action(function=logTxt.write_error, message='Magyp process not completed', detail=e)
            self.__had_error = True
            
    def do_pdf_extraction_process(self, path: str, data: dict):
        try:
            pdf = PDFProcess(path=path)
            text: str = self.__execute_action(function=pdf.extract_text_from_page, page=3)
            pdf_data: list[str] = (text.replace('*', '')
                        .replace('\n', ' ')
                        .replace('  ', ' ')
                        .strip().split(' '))
            
            pdf_data = pdf_data[3:]
            for i, key in enumerate(data['magyp'].keys()):
                data['magyp'][key] = pdf_data[i]
            os.remove(path)
        except Exception as e:
            raise Exception(e)
            
    def __create_folders(self, folders: list[str]) -> None:
        for folder in folders:
            if(not os.path.exists(folder)):
                os.makedirs(folder)
        
    def pause(self) -> None:
        self.__notify_status(new_status='PAUSED')
            
    def unpause(self) -> None:
        self.__notify_status(new_status='RUNNING')
        
    def stop(self) -> None:
        self.__notify_status(new_status='CLOSING BOT')
        
    def __execution_begun(self) -> None:
        log_name: str = datetime.now().strftime("%d.%m.%Y_%H%M%S")
        self.__logs_services = [log(name=log_name) for log in self.__logs_services_classes]
        logXlsx: LogXlsx = self.__get_log_service(log_type=LogXlsx)
        logXlsx.write_info(message=f'The Bot has begun')
        self.__notify_status(new_status="RUNNING")
             
    def __execution_completed(self):
        self.__notify_status(new_status="READY")
        logXlsx: LogXlsx = self.__get_log_service(log_type=LogXlsx)
        if(self.__had_error):
            logXlsx.write_error(message=f'The Bot has ended with errors')
        else:
            logXlsx.write_info(message=f'The Bot has ended without errors')
        self.__close_logs()
        
    def __notify_status(self, new_status: str) -> None:
        self.__status = new_status
        logTxt: LogTxt = self.__get_log_service(log_type=LogTxt)
        logTxt.write_info(message=f'Bot {new_status}')
        if self.__status_callback:
            self.__status_callback(new_status)
        
    def __get_log_service(self, log_type: LogService) -> LogService:
        try: return next(log for log in self.__logs_services if isinstance(log, log_type))
        except StopIteration:
            raise ServiceNotFound(f'The log service of type {log_type}, cannot be found')
    
    def __get_setting_service(self, setting_type: SettingService) -> SettingService:
        try: return next(service for service in self.__settings_services if isinstance(service, setting_type))
        except StopIteration:
            raise ServiceNotFound(f'The setting service of type {setting_type}, cannot be found')
        
    def __execute_action(self, function, **kwargs):
        logTxt: LogTxt = self.__get_log_service(log_type=LogTxt)
        while self.__status == 'PAUSED':
            if(self.__status=='RUNNING'):
                break
        return logTxt.write_and_execute(function, **kwargs)
    
    def __close_logs(self) -> None:
        for log in self.__logs_services:
            log.close()
    
    def __get_settings_services(self) -> list[SettingService]:
        return [service(bot_name=self.__bot_name) for service in self.__settings_services_classes]
                                
if __name__ == "__main__":
    st = time.time()
    main = Main()
    main.start(sys.argv[1:])
    et = time.time()
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
        
    
