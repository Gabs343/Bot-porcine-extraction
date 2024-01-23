import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class MagypProcess:
    def __init__(self) -> None:
        self.__url: str = 'https://www.magyp.gob.ar/sitio/areas/porcinos/informes/'
    
    def open(self) -> None:
        self.driver = webdriver.Edge()
        self.driver.maximize_window()
        self.driver.get(self.__url)
        self.driver.implicitly_wait(0.5)
        
    def close(self) -> None:
        self.driver.quit()
           
    def click_current_year(self) -> None:
        self.driver.find_element(by=By.XPATH, value=f'//p[contains(text(),"{self.__get_current_year()}")]/parent::a').click()
        
    def download_last_pdf(self, folder_output: str) -> str:
        pdf_file: str = f'Precio Porcino {self.__get_current_year()}_{self.__get_number_of_week()}'
        pdf_a_tag: WebElement = self.driver.find_element(by=By.XPATH, value=f'//a[contains(text(),"{pdf_file}")]')
        response = requests.get(pdf_a_tag.get_property('href'))
        with open(f'{folder_output}\\{pdf_file}.pdf', 'wb') as f:
            f.write(response.content)
        return f'{folder_output}\\{pdf_file}.pdf'
    
    def __get_current_year(self) -> str:
        return str(datetime.now().year)
    
    def __get_number_of_week(self) -> str:
        weekday: int = datetime.now().isoweekday()
        week: int = datetime.now().isocalendar().week
        if(weekday < 3): week -= 2
        else: week -= 1
        return f'{week:02d}'
        