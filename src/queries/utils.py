import csv

def data_to_csv(data, filename="default.csv"):
    file = open(filename, 'w+', newline ='')

    # writing the data into the file
    with file:
        write = csv.writer(file)
        write.writerows(data)

def reservation_sort(reservations, reverse=False):
    """Takes an array of dictionaries with the same structure and sorts"""
    reservations.sort(key = lambda res: res.date_started, reverse=reverse)
