import os
import io
import sys
import tabula
import requests
import datetime
import bs4 as bs
import pandas as pd
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
import isoweek

def extract_text_by_page(pdf_path):
    ''' Extracts text from each page of the 
    inputted pdf, and returns the text. '''
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                caching=True,
                                check_extractable=True):
            res_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(res_manager, fake_file_handle)
            page_interpreter = PDFPageInterpreter(res_manager, converter)
            page_interpreter.process_page(page)
            
            text = fake_file_handle.getvalue()
            yield text
            # close open handles
            converter.close()
            fake_file_handle.close()
    
def extract_text(pdf_path):
    ''' The search_str is the name of the table of interest, 
    albeit weirdly formatted by the text extraction. Function
    locates the page containing this string, and returns 
    the page number. '''
    for i, page in enumerate(extract_text_by_page(pdf_path)):
        search_str = 'AantaltestenuitgevoerddoordeGGD'
        if search_str in page:
            table_page_num = i + 1
            break
    return table_page_num
        
def extract_table(table_page_num, file_path):
    ''' Extracts the table data from the inputted page number,
    returning it as a dataframe.'''
    tables = tabula.read_pdf(file_path,
        pages = table_page_num,
        guess = False,
        columns  = (200, 340, 440),
        pandas_options = {'header':None}
    )
    if tables:
        return tables[0]
    else:
        print('something wrong....')
        sys.exit()

def get_rapport_date(rapport_name):
    ''' Parses the filename to extract the rapport date, 
    formats it, and returns it. '''
    split_arr = rapport_name.split('_')
    for item in split_arr:
        if len(item) == 8 and item.isdigit():
            raw_dt = item
    if raw_dt:
        date = datetime.datetime.strptime(raw_dt, '%Y%m%d')
        return date
    else:
        print('Rapport date could not be parsed.')
        sys.exit()

def remove_old_pdfs(pdf_files, pdf_folder):
    ''' Removes all other pdf rapports than the most recent one,
    and returns said pdfs date and name.'''
    pdf_list = []
    for pdf in pdf_files:
        pdf_i = {'name' : pdf , 'date' : get_rapport_date(pdf)}
        pdf_list.append(pdf_i)
    pdf_list.sort(key = lambda x:x['date'], reverse=True) 
    for pdf in pdf_list[1:]:
        pdf_fp = os.path.join(pdf_folder, pdf['name'])
        if os.path.exists(pdf_fp):
            os.remove(pdf_fp)
    return pdf_list[0]['date'], pdf_list[0]['name']

def retreive_current_rapport(pdf_folder):
    ''' Retreives information about the pdf 
    rapport currently in the pdf_rapport folder  '''
    pdf_files = os.listdir(pdf_folder)
    if len(pdf_files) == 1:
        pdf_name = pdf_files[0]
        date = get_rapport_date(pdf_name)
        return date, pdf_name
    elif len(pdf_files) > 1:
        date, pdf_name = remove_old_pdfs(pdf_files, pdf_folder)
        return date, pdf_name
    else:
        return None, None

def retreive_online_rapport():
    ''' Retreives information about the most recent pdf rapport
    from the RIVM website. Returns the file url, the file name,
    and the date of publication (by parsing the name). '''
    url = ('https://www.rivm.nl/coronavirus-covid-19/' \
        'actueel/wekelijkse-update-epidemiologische-' \
        'situatie-covid-19-in-nederland')
    response = requests.get(url)
    if response.raise_for_status() == None:
        soup = bs.BeautifulSoup (response.content, 'html.parser')
        link_soup = soup.find(class_='list-group-item icon-pijl-rechts')
        if link_soup:
            pdf_url = 'http://rivm.nl' + link_soup['href']
            rapport_name = link_soup['href'].split('/')[-1]
            file_date = get_rapport_date(rapport_name)
            return file_date, pdf_url, rapport_name
        else:
            print('Error retreiving pdf link from RIVM website.')
            sys.exit()
    else:
        print(response.raise_for_status())
        sys.exit()

def dowload_rapport(url, pdf_name, target_dir):
    ''' Downloads rapport pdf and saves it
    to the pdf_rapport directory '''
    target_fp = os.path.join(target_dir, pdf_name)
    response = requests.get(url)
    with open(target_fp, 'wb') as f:
        f.write(response.content)
    print('New rapport downloaded')

def diagnose_table(dframe):
    ''' Checks if amount of columns in extraced data table
    is equal to 4. If not, exit program. (Would indicate
    a change in the table format/ column width). '''
    if dframe.shape[1] != 4:
        print('Parsing error: Unexpected amount of columns.')
        sys.exit()
    else:
        print('Parsing succesfull.')

def calculate_week_numer(row):
    ''' Function using the Isoweek module to calculate the week number
    corresponsing with a given date. '''
    return isoweek.Week.withdate(row['start_dt']).isoformat()

def process_test_data_df(dframe):
    ''' Parses dataframe with GGD testing data. First removes all
    redundant rows based on numerical values in column 2, and drops
    the totals row. Next, caculates the week numbers of the
    date ranges. Finally, exports the data to a csv files. '''
    diagnose_table(dframe)   
    dframe = dframe[pd.to_numeric(dframe.iloc[:, 2], 
        errors='coerce').notnull()]
    dframe = dframe[dframe.iloc[:, 0] != 'Totaal']
    dframe = dframe.rename(columns={
        0 : 'date',
        1 : 'aantal_testen',
        2 : 'aantal_positief',
        3 : 'perentage_positief'
        }
    )
    dframe[['start_dt', 'end_dt']] = dframe.date.str.split(
        pat=' - ', n=1, expand=True)
    dframe['start_dt'] = pd.to_datetime(dframe.start_dt, format='%d-%m-%Y')
    dframe['end_dt'] = pd.to_datetime(dframe.end_dt, format='%d-%m-%Y')
    dframe['week_number'] = dframe.apply(calculate_week_numer, axis=1)
    dframe['aantal_testen'] = pd.to_numeric(dframe['aantal_testen'])
    dframe['perentage_positief'] = pd.to_numeric(dframe['perentage_positief'])
    dframe = dframe.drop(columns= ['date'])
    target_dir = os.path.join(os.getcwd(), 'data')
    target_fp = os.path.join(target_dir, 'ggd_test_data.csv')
    dframe.to_csv(target_fp, index=False, header=True)
    print('CSV data file created')
    return dframe

def main():
    ''' First checks if the RIVM pdf rapport in the pdf_rapports
    folder is the most current one compared to the one on the 
    RIVM website. If not, the new pdf is downloaded, parsed,
    and the data table of interest is extracted.  '''
    pdf_folder = os.path.join(os.getcwd(), 'pdf_rapport')
    data_folder = os.path.join(os.getcwd(), 'data')
    cur_rap_date, cur_pdf_name = retreive_current_rapport(pdf_folder)
    online_rap_date, rap_url, online_pdf_name = retreive_online_rapport()
    if cur_rap_date != online_rap_date or cur_rap_date == None:
        if cur_rap_date != None:
            if os.path.exists(os.path.join(pdf_folder, cur_pdf_name)):
                os.remove(os.path.join(pdf_folder,cur_pdf_name))
        dowload_rapport(rap_url, online_pdf_name, pdf_folder)
        pdf_path = os.path.join(pdf_folder, online_pdf_name)
        table_page_num = extract_text(pdf_path)
        if table_page_num:
            test_data_df = extract_table(table_page_num, pdf_path)
            dframe = process_test_data_df(test_data_df)
            return dframe, online_pdf_name
    else:
        print('Online rapport is same as downloaded one.')
        target_fp = os.path.join(data_folder, 'ggd_test_data.csv' )
        if not os.path.exists(target_fp):
            pdf_path = os.path.join(pdf_folder, cur_pdf_name)
            table_page_num = extract_text(pdf_path)
            if table_page_num:
                test_data_df = extract_table(table_page_num, pdf_path)
                dframe = process_test_data_df(test_data_df)
        dframe = pd.read_csv(target_fp)
        return dframe, cur_pdf_name

if __name__ == '__main__':
    main()