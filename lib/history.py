import gspread
import time

class History:

    def __init__(self, params) -> None:
        
        self._config = params

        gc = gspread.service_account(
            filename=params['google_account'])

        self.re = gc.open(params['sheet_place']).worksheet(params['report_sheet'])
    
    def insert_gs(self, **data) :
        
        all_datas = list(data.values())

        all_index = self.re.get_values(f'A:{chr(len(all_datas)+65)}')
        
        all_datas.insert(0,len(all_index))
        
        # 시세 및 수량 데이터 단일 row 삽입
        self.re.update(f'A{len(all_index) + 1}:{chr(len(all_datas)+64)}{len(all_index) + 1}',
                       [
                           all_datas
                       ]
                  )