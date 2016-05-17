import os


# this allows me to create a data sheet that can easily be used in excel, or go
# straight to my favorite data analysis software, JASP
class DataSheet:
    def __init__(self, col_names, participant, file_name):
        self.col_names = col_names
        self.file_name = "P" + str(file_name) + ".csv"
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.file_n = os.path.join(script_directory, "data", self.file_name)
        with open(self.file_n, 'w') as data_sheet:
            for col in col_names:
                data_sheet.write(col + ',')
            data_sheet.write("\n")

    def writeSection(self, data_dict):
        # From a dict passed by the user, this creates a list of the data, in order based on self.col_names, defined
        # when the object is created
        current_line = []
        for col in self.col_names:
            current_line.append(data_dict[col])
        self.writeRow(current_line)

    def writeRow(self, cols):
        with open(self.file_n, 'a')as data_sheet:
            for col in cols:
                s = str(col)
                data_sheet.write(s + ',')
            data_sheet.write('\n')


    def experimentSheet(self):
        # This will copy all of the data into an experiment sheet.
        pass
