from datetime import datetime


if __name__ == '__main__':
    a = datetime.now()
    b = datetime.strptime('2022_08_17', '%Y_%m_%d')
    print(a > b)
