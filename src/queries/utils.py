import csv

def data_to_csv(data, filename="default.csv"):
    file = open(filename, 'w+', newline ='')

    # writing the data into the file
    with file:
        write = csv.writer(file)
        write.writerows(data)
