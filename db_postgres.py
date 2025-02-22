import psycopg2
import pandas as pd

def get_connection():
# подключение к серверу БД, данные для входа прописываются здесь же
	try:
		return psycopg2.connect(
			database="postgres",
			user="postgres",
			password="123456",
			host="127.0.0.1",
			port=5432,
		)
	except:
		return False

def log_check_conn_to_db():
    conn = get_connection()
    '''
    if conn:
        print("Connection to the PostgreSQL established successfully.")
    else:
        print("Connection to the PostgreSQL encountered and error.")
    '''    
    # СОЗДАЙТЕ КУРСОР, ИСПОЛЬЗУЯ ОБЪЕКТ ПОДКЛЮЧЕНИЯ
    curr = conn.cursor()
    # ВЫПОЛНИТЕ SQL-ЗАПРОС
    db_name = 'kks_test_2'
    curr.execute(f"SELECT * FROM {db_name};")
    # ИЗВЛЕКИТЕ ВСЕ СТРОКИ ИЗ КУРСОРА
    data = curr.fetchall()
    
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{db_name}' ORDER BY ordinal_position;"
    curr.execute(query)
    
    columns = []
    for row in curr.fetchall():
        columns.append(row[0])
    
    # РАСПЕЧАТАЙТЕ ЗАПИСИ
    # for row in data:
    #     print(row)
    # ЗАКРОЙТЕ СОЕДИНЕНИЕ
    conn.close()
    
    return data, columns

# l = ['10LBA12CP001', '10LBA11CP001', '10LBA22CP001', '10LBA21CP001', '10LAB81CF901', '10LAB83CF901', '10LAB80CF901', '10LAB82CF901',
#      '10JRB10CP001', '10JRB10CP001', '10JRB10CP003', '10JRB10CP\n', '10JRB10CP002', '10JRB10CP002', '10JRB10CP006', '10JRB10CP007',
#      '10JRB10CP\n', '10JRB10CP007', '10JRB10CR001', '10JRB10CQ001', '10JRB10CR001', '10JRB10CQ001', '10JRB10CT001', '10JRB10CT001',
#      '10JRB10CT000', '10JRB10CP004', '10JRB10CT002', '10JRB10CP004', '10JRB10CP009', '10JRB10CP008', '10JRB10CP009', '']



def main():
    # preprocessed_data: pd.DataFrame)-> pd.DataFrame:
    selected_data_from_db, columns_of_db = log_check_conn_to_db() #List[Tuple]
    # g = database_kks_search(preprocessed_data, selected_data_from_db)
    return selected_data_from_db, columns_of_db

def zalupa():
    # Загрузка CSV файла с указанием разделителя и кодировки
    import csv
    df = pd.read_csv(r'C:\Users\user\Desktop\ss.csv', sep=';')

    # подключение к БД с данными о ККS
    # result = main()

    # columns_of_db - список строк названий столбцов из бд
    selected_data_from_db, columns_of_db = main()[:2]

    # цикл по добавлению столбцов, заполненных символом #, из списка строк названий столбцов бд
    # не считая значения kks, который уже есть в исходной таблице
    for i in columns_of_db[1:]:
        df[f'{i}'] = '#'


    column_names = columns_of_db[1:]
    kks_data = [x[0]  for x in selected_data_from_db]

    index_count = 0
    for i in df['KKS']:
        index_count +=1
        if i in kks_data: 
            index_kks_df = index_count
            index_kks_db= kks_data.index(i)
            print(True, ' - ', index_kks_df, ' - ',i, ' - ', list(selected_data_from_db[index_kks_db][1:]))
            df.loc[index_kks_df, column_names] = list(selected_data_from_db[index_kks_db][1:])
    print(df)
    pass