from PyPDF2 import PdfReader, PageObject

class PDFProcess:
    def __init__(self, path: str) -> None:
        self.reader = PdfReader(path)
        self.parts = []
        
    def extract_text_from_page(self, page: str) -> str:
        page: PageObject = self.reader.pages[page-1]
        page.extract_text(visitor_text=self.__visitor_body)
        text_body = "".join(self.parts)
        return text_body
        
    def __visitor_body(self, text, cm, tm: list[float], fontDict, fontSize):
        x: float = tm[4]
        y: float = tm[5]
        if(y > 570 and y < 593):
            if(x < 200):
                self.parts.append(text)