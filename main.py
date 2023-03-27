import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import datetime
from datetime import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import sys

def main():
    if(sys.argv[1] == "update"):
        if(len(sys.argv) == 3):
            update_data(int(sys.argv[2]))
        else:
            update_data(int(datetime.date.today().year))
        
        #DO POPRAWY BO ROK
    elif(sys.argv[1] == "read_days"):
        try:
            read_data_from_database_from_last_days(sys.argv[2], int(sys.argv[3]))
        except:
            print("Error, cannot read data")

    elif(sys.argv[1] == "read_year"):
        if(len(sys.argv) == 4):
            try:
                read_data_from_database_from_year(sys.argv[2], int(sys.argv[3]))
            except:
                print("Error, cannot read data")
        else:
            try:
                read_data_from_database_from_year(sys.argv[2], int(datetime.date.today().year))
            except:
                print("Error, cannot read data")
        
    elif(sys.argv[1] == "help"):
        print("Avaiable argument: update, read_days, read_year")
    else:
        print("Argument error, use argument help")

    #update_data(2022)
    #print(type(read_data_from_database_from_last_days("EUR", 15)))
    #data_list = read_data_from_database_from_last_days("EUR", 180)
    #data_list = read_data_from_database_from_year("USD", 2022)
    #read_data_from_database_from_year("USD", 2022)
    #read_data_from_database_from_last_days("EUR", 180)

    #df['date'] = df['date'].astype(datetime)

    #df["value"].plot(kind='line')
    #df.plot(kind = 'line', x = 'value', y = 'date')
    #df.plot(df['value'], df['date'])
    #df.plot(x=df['date'], y=df['value'])
    #plt.show()

    #DZIALA
    #res = cur.execute("SELECT * FROM currency_rates WHERE currency = 'HUF'")
    #print(res.fetchall())
    return

def read_data_one_day(link, year, month, day):
    odpowiedz = requests.get(link)

    soup = BeautifulSoup(odpowiedz.content, 'html.parser')
    table = soup.find("tbody")
    #print(len(table.find_all("tr")))
    for row in table.find_all("tr"):
        if(len(row.find_all("td")) == 3):
            if(row.find("th") is None):
                #print("No data available in selected day") #######
                return 1
            currency = row.find("th").string
            column = row.find_all("td")
            name = column[0].string
            value = column[1].string
            dotPos = value.find(".")
            value = value[:dotPos+5]
            data = (year, month, day, currency, value)
            #print(data)
            add_data_to_database(data)
    return 0

def read_data_many_days(year):
    #id = 1
    errors = 0
    success = 0
    current_day = dt.now().strftime("%Y-%m-%d")
    #print("date and time =", current_day)	
    for month in range(12):
        for day in range(31):
            dayStr = str(day+1)
            if(len(dayStr) == 1):
                dayStr = "0" + dayStr
            monthStr = str(month+1)
            if(len(monthStr) == 1):
                monthStr = "0" + monthStr
            #idStr = str(id)
            #if(len(idStr) == 1):
                #monthStr = "00" + idStr
            #elif(len(idStr) == 2):
                #monthStr = "0" + idStr
            correctDate = None
            try:
                newDate = datetime.datetime(year,month+1,day+1)
                correctDate = True
            except ValueError:
                correctDate = False
            if(correctDate):
                print(str(year) + "-" + monthStr + "-" + dayStr) ######
                if(check_data_in_day(year, month+1, day+1) == 0):
                    result = read_data_one_day("https://www.xe.com/currencytables/?from=PLN&date=" + str(year) + "-" + monthStr + "-" + dayStr, year, month+1, day+1)
                    if(result == 0):
                        errors = 0
                        success = success + 1
                    else:
                        errors = errors + 1

                    #print(errors)
                    #print("Data successully added to database")

                    if(errors >= 5):
                        #print("Over 5 days in a row withous data available") #######
                        return

                    if(str(year) + "-" + monthStr + "-" + dayStr == current_day):
                        #print("Current day has been reached") ######
                        if(success > 1):
                            print("Data of new " + str(success) + " days has been added to database")
                        elif(success == 1):
                            print("Data of new " + str(success) + " day has been added to database")
                        else:
                            print("No new data has been added to database")
                        return

                    time.sleep(1.0)
                else:
                    #print("Data already exists in database") ########
                    errors = 0
            #else:
                #print("Day do not exist")

    return

def add_data_to_database(data):
    path = 'database.db'
    con = sqlite3.connect(path)
    cur = con.cursor()
    #cur.execute("INSERT INTO currency_rates VALUES(1, 22, 11, 16, 'currency', 'value')")
    sql = ''' INSERT INTO currency_rates
              VALUES(?,?,?,?,?) '''
    cur.execute(sql, data)
    con.commit()
    #print("Data successully added to database") #######

def check_data_in_day(year, month, day):
    data = (year, month, day)
    path = 'database.db'
    con = sqlite3.connect(path)
    cur = con.cursor()
    #cur.execute("INSERT INTO currency_rates VALUES(1, 22, 11, 16, 'currency', 'value')")
    sql = ''' SELECT COUNT(1)
              FROM currency_rates
              WHERE year = ?
              AND month = ?
              AND day = ?'''
    res = cur.execute(sql, data)
    #print(res.fetchone()[0])
    return res.fetchone()[0]

def create_database():
    path = 'database.db'
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("CREATE TABLE currency_rates(year, month, day, currency, value)")

def update_data(year):
    try:
        read_data_many_days(year)
    except:
        print("Database does not exists, I am creating new one")
        create_database()
        read_data_many_days(year)

def read_data_from_database_from_last_days(currency, days):
    data = (currency, days)
    path = 'database.db'
    con = sqlite3.connect(path)
    cur = con.cursor()
    #cur.execute("INSERT INTO currency_rates VALUES(1, 22, 11, 16, 'currency', 'value')")
    sql = ''' SELECT *
              FROM currency_rates
              WHERE currency = ? 
              ORDER BY year DESC, month DESC, day DESC
              LIMIT ?'''
    res = cur.execute(sql, data)
    #print(res.fetchone()[0])
    dataframe_operations(res.fetchall())
    #return res.fetchall()

def read_data_from_database_from_year(currency, year):
    data = (currency, year)
    path = 'database.db'
    con = sqlite3.connect(path)
    cur = con.cursor()
    #cur.execute("INSERT INTO currency_rates VALUES(1, 22, 11, 16, 'currency', 'value')")
    sql = ''' SELECT *
              FROM currency_rates
              WHERE currency = ?
              AND year = ?
              ORDER BY year DESC, month DESC, day DESC'''
    res = cur.execute(sql, data)
    #print(res.fetchone()[0])
    dataframe_operations(res.fetchall())
    #return res.fetchall()

def dataframe_operations(data_list):
    df = pd.DataFrame (data_list, columns = ['year', 'month', 'day', 'currency', 'value'])
    #print(df['currency'].values[0])
    df['value'] = df['value'].astype(float)
    df['value'] = round(1/df['value'],4)
    df.rename(columns = {'value':df['currency'].values[0]}, inplace = True)
    df['date'] = df['year'].astype(str) + "-" + df['month'].astype(str) + "-" + df['day'].astype(str)
    del df['year']
    del df['month']
    del df['day']
    df.date = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df.set_index(['date'],inplace=True)
    df.plot()
    #print(df)
    plt.show()

if __name__ == '__main__':
    main()