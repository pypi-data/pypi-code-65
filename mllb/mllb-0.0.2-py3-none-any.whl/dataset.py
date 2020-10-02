"""
This class is initialized with a the name of a csv file. Specific 
columns can be selected and even edited.

"""



class dataset:

    def __init__(self, file_name):

        """
        Initializer of the dataset object.

        Attributes:
            __initial_header: (list) a list containing the name of each column in
                              the csv file.

                              Its values will be inputed in the __to_list method.

            __header: (list) a list contaning the header to be displayed when the 
                      dataset object is printed out with the __repr__ method.

                      Its values will be inputed in the __to_list method. The values
                      could either be the names of the header of each column in the csv
                      file, or the index values of each column (0 to n - 1).

            __show_header: (boolean) this attribute determines whether the headers of the
                           csv file will be shown when the csv_object is printed out
                           with the __repr__ method.

                           Its value can be updated with the show_header method.

            __header_type: (string) this attribute determines which of the headers is used
                           when the csv_object is printed out alongside the data when the 
                           __repr__ method is called.
                           
                           If its value is "string", the original header within the csv
                           file is printed out with the dataset as its header. If its
                           value is "number", the index values of each column is printed
                           out alongside the dataset.

            __data: (list) this is the attribute that holds the csv data as a two dimensional
                    list

            # dim: (string) this attribute holds the dimensions of the dataset. Its value is
            #      in the form of 'number of rows' x 'number of columns'.

            __dimy: (int) this attributes indicates the number of rows in the csv data.

                    The header row is not included in this number.

            __dimx: (int) this attribute indicates the number of columns in the csv data.

            print_range: (tuple) this attribute determines what rows are printed out
                         when the dataset is printed out with the __repr__ method.

                         It's default value is (0, 20) or (0, self.__n), depending on
                         the number of rows in the dataset.

            """

        self.__initial_header = []
        self.__header = []
        self.__show_header = True
        self.__header_type = "string"


        if isinstance(file_name, str):
            self.__data = self.__to_list(file_name)
        
        elif isinstance(file_name, list):
            self.__data = self.__custom_dataset(file_name)
        
        #self.dim = "{} x {}".format(len(self.__data), len(self.__data[0]))

        self.__dimy = len(self.__data)
        self.__dimx = len(self.__data[0])

        self.print_range =  (0, self.__m)
        if self.__m > 20:
            self.print_range = (0, 20)
        
        
    def __to_list(self, file_name):

        """
        Turns the file indicated by the file_name into a two dimensional list.
        It also tries to convert numbers within the list created into floats.

        Args:
            file_name: (str) name of csv file
        
        Return:
            as_list: (list) the data within the csv file as a two dimensional list

        """

        # imports csv module and converts the data to a two dimensional list

        import csv
        with open(file_name, mode='r') as file:
            csv_file = csv.reader(file)
            as_list = list(csv_file)

        # converts any number within the dataset to floats

        for i in range(len(as_list)):
            for j in range(len(as_list[0])):
                try:
                    float(as_list[i][j])
                except ValueError:
                    pass
                else:
                    as_list[i][j] = float(as_list[i][j])

        # checks for a header and intializes the __initial_header and __header attrtibutes

        if set([isinstance(j, str) for j in as_list[0]]) == {True}:
            from copy import deepcopy

            self.__initial_header = deepcopy(as_list[0])
            self.__header = deepcopy(as_list[0])
            as_list.pop(0)

        return as_list


    def __custom_dataset(self, file_name):

        """
        Sets the __data attribute the value passed in as 'file_name'.

        Args:
            file_name: (list) two dimensional list of data
        
        Return:
            as_list: (list) the data within the csv file as a two dimensional list

        """

        from copy import deepcopy

        as_list = file_name
        self.__initial_header = deepcopy(as_list[0])
        self.__header = deepcopy(as_list[0])
        as_list.pop(0)

        return as_list

    
    def __repr__(self):

        """
        Prints out the values of the dataset in an orderly form.

        Args:
            --

        Return:
            "": (string) it returns this to avoid errors arising from None ValueError

        """

        # checks for the maximum lenght of string text in each row

        transposed = [[len(str(self.__data[j][i])) for j in range(self.__dimy)] for i in range(self.__dimx)]

        if self.__show_header == True:
            for j in range(self.__dimx):
                transposed[j].insert(0, len(str(self.__header[j])))

        for j in range(self.__dimx):
            transposed[j] = max(transposed[j])
        
        # prints out the data

        output = ""

        if self.__show_header:
            output = "".join([str(self.__header[j]).rjust(transposed[j] + 3) for j in range(self.__dimx)])
            print(output)
            print("=" * len(output))
        
        start, stop = self.print_range

        for i in range(start, stop):
            string = ""

            for j in range(self.__dimx):
                string += f"{self.__data[i][j]}".rjust(transposed[j] + 3)

            print(string)

        return ""


    def __prepare_print_range(self):

        """
        This method checks, validates and prepares the print_range attribute whenever
        the __repr__ method is called. If it's value doesn't meet the requirements, an 
        error is thrown.

        """

        if not isinstance(self.print_range, tuple) or len(self.print_range) != 2:
            raise TypeError("print_range attribute must be a two element tuple")

        start, stop = self.print_range
        
        if 0 <= start < self.__m and 0 <= stop < self.__m:
            pass

        else:
            raise ValueError("print_start stop attribute values out of bounds")

        
    def header_type(self, type="string"):

        """
        This method updates the header type to be displayed when the dataset object
        is printed out.

        Args:
            type: (string) its value is either 'string' or 'number'

                  'string' prints out the original headers within the dataset, while 'numbers'
                  prints out the index values of each column

        Return:
            --

        """

        import warnings
        if self.__header_type == "number_stuck":
            warnings.warn("header type won't change from 'number' after spread method is called")
        
        else:
            if type == "number":
                self.__header = [j for j in range(self.__dimx)]
                self.__header_type = type

            elif type == "string":
                self.__header = self.__initial_header
                self.__header_type = type

            else:
                raise ValueError("invalid header type")


    def show_header(self, ans=True):

        """
        This method determines whether the header is printed out alongside the dataset when
        the print function is called.

        Args:
            ans: (boolean) True or False

        Return:
            --
        
        """

        self.__show_header = ans


    def __len__(self):

        """
        Returns the number of rows within the dataset. The header rows not included.

        Args:
            --

        Return:
            number_of_rows: (int) number of rows in the csv dataset

        """

        number_of_rows = self.__dimy
        return number_of_rows


    def __getitem__(self, *column_indicator):

        """
        This method returns a dataset object that only contains one column from the the self
        dataset.

        Args:
            column_indicator: (string or int) a string is used to indicate the name of the row as 
            seen in the csv dataset, or an int to just indicate its column index.

        Return:
            column_dataset: (dataset) created dataset object

        """

        column_data = [[] for i in range(self.__dimy + 1)]

        if isinstance(column_indicator[0], int) or isinstance(column_indicator[0], str) or isinstance(column_indicator[0], slice):

            col = column_indicator[0]

            if isinstance(col, str) and col in self.__initial_header:
                column_index = self.__initial_header.index(col)
                header_value = col

                column_data[0].append(header_value)
                for i in range(self.__dimy):
                    column_data[i + 1].append(self.__data[i][column_index])

            elif isinstance(col, int) and 0 <= col < self.__dimx:
                column_index = col
                header_value = self.__header[col]

                column_data[0].append(header_value)
                for i in range(self.__dimy):
                    column_data[i + 1].append(self.__data[i][column_index])

            elif isinstance(col, slice):
                if col.step == None:

                    for c in range(col.start, col.stop):
                        header_value = self.__header[c]

                        column_data[0].append(header_value)
                        for i in range(self.__dimy):
                            column_data[i + 1].append(self.__data[i][c])

                else:

                    for c in range(col.start, col.stop, col.step):
                        header_value = self.__header[c]

                        column_data[0].append(header_value)
                        for i in range(self.__dimy):
                            column_data[i + 1].append(self.__data[i][c])


            else:
                raise IndexError(col)


        else:

            for col in column_indicator[0]:
                
                if isinstance(col, str) and col in self.__initial_header:
                    column_index = self.__initial_header.index(col)
                    header_value = col

                    column_data[0].append(header_value)
                    for i in range(self.__dimy):
                        column_data[i + 1].append(self.__data[i][column_index])

                elif isinstance(col, int) and 0 <= col < self.__dimx:
                    column_index = col
                    header_value = self.__header[col]

                    column_data[0].append(header_value)
                    for i in range(self.__dimy):
                        column_data[i + 1].append(self.__data[i][column_index])

                elif isinstance(col, slice):
                    if col.step == None:

                        for c in range(col.start, col.stop):
                            header_value = self.__header[c]

                            column_data[0].append(header_value)
                            for i in range(self.__dimy):
                                column_data[i + 1].append(self.__data[i][c])

                    else:

                        for c in range(col.start, col.stop, col.step):
                            header_value = self.__header[c]

                            column_data[0].append(header_value)
                            for i in range(self.__dimy):
                                column_data[i + 1].append(self.__data[i][c])

                else:
                    raise IndexError(col)

        column_dataset = dataset(column_data)

        return column_dataset


    def __delitem__(self, *key):

        """
        This method deletes columns from the dataset given the indices of the columns.

        Args:
            key: (string or int) a string is used to indicate the name of the row as 
            seen in the csv dataset, or an int to just indicate its column index.

        Return:
            --

        """
        
        column_names = []
        #print(key)

        if isinstance(key[0], tuple):

            for k in key[0]:
                if isinstance(k, int) and 0 <= k < self.__dimx:
                    header_name = self.__initial_header[k]
                    column_names.append(header_name)

                elif isinstance(k, str) and k in self.__initial_header:
                    column_names.append(k)

                else:
                    raise IndexError(k)

            for col in column_names:
                index = self.__initial_header.index(col)

                for i in range(self.__dimy):
                    self.__data[i].pop(index)
                
                self.__header.pop(index)
                self.__initial_header.pop(index)

            self.__dimx -= len(column_names)
            
            if self.__header_type in ["number", "number_stuck"]:
                self.__header = [i for i in range(self.__dimx)]

        else:

            if isinstance(key[0], int) and 0 <= key[0] < self.__dimx:
                header_name = self.__initial_header[key[0]]

            elif isinstance(key[0], str) and key[0] in self.__initial_header:
                header_name = key[0]

            else:
                raise IndexError(key[0])

            index = self.__initial_header.index(header_name)

            for i in range(self.__dimy):
                self.__data[i].pop(index)
            
            self.__header.pop(index)
            self.__initial_header.pop(index)

            self.__dimx -= 1
            
            if self.__header_type in ["number", "number_stuck"]:
                self.__header = self.__header.pop(-1)


    def add(self, key, value):

        """
        This method adds to each of the numbers within the columns specified by the the key
        by the number specified as 'value'. If a number within the columns is a string, it
        is left out of the addition.

        Args:
            key: (int or str or list) key(s) of the columns where the values will be added

            value: (float or int) number to be added to the column

        Return:
            --

        """

        if isinstance(key, int) and 0 <= key < self.__dimx:
            for i in range(self.__dimy):
                if isinstance(self.__data[i][key], str) == False:
                    self.__data[i][key] += value

        elif isinstance(key, str) and key in self.__initial_header:
            index_value = self.__initial_header.index(key)
            
            for i in range(self.__dimy):
                if isinstance(self.__data[i][index_value], str) == False:
                    self.__data[i][index_value] += value

        elif isinstance(key, list):

            for k in key:
                if isinstance(k, int) and 0 <= k < self.__dimx:
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][k], str) == False:
                            self.__data[i][k] += value

                elif isinstance(k, str) and key in self.__initial_header:
                    index_value = self.__initial_header.index(k)
                    
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][index_value], str) == False:
                            self.__data[i][index_value] += value


    def sub(self, key, value):

        """
        This method subtracts from each of the numbers within the columns specified by the the key
        by the number specified as 'value'. If a number within the columns is a string, it
        is left out of the subtraction.

        Args:
            key: (int or str or list) key(s) of the columns where the values will be added

            value: (float or int) number to be added to the column

        Return:
            --

        """

        if isinstance(key, int) and 0 <= key < self.__dimx:
            for i in range(self.__dimy):
                if isinstance(self.__data[i][key], str) == False:
                    self.__data[i][key] -= value

        elif isinstance(key, str) and key in self.__initial_header:
            index_value = self.__initial_header.index(key)
            
            for i in range(self.__dimy):
                if isinstance(self.__data[i][index_value], str) == False:
                    self.__data[i][index_value] -= value

        elif isinstance(key, list):

            for k in key:
                if isinstance(k, int) and 0 <= k < self.__dimx:
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][k], str) == False:
                            self.__data[i][k] -= value

                elif isinstance(k, str) and key in self.__initial_header:
                    index_value = self.__initial_header.index(k)
                    
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][index_value], str) == False:
                            self.__data[i][index_value] -= value

    
    def mul(self, key, value):

        """
        This method multiplies each of the numbers within the columns specified by the the key
        by the number specified as 'value'. If a number within the columns is a string, it
        is left out of the multiplication.

        Args:
            key: (int or str or list) key(s) of the columns where the values will be added

            value: (float or int) number to be added to the column

        Return:
            --

        """

        if isinstance(key, int) and 0 <= key < self.__dimx:
            for i in range(self.__dimy):
                if isinstance(self.__data[i][key], str) == False:
                    self.__data[i][key] *= value

        elif isinstance(key, str) and key in self.__initial_header:
            index_value = self.__initial_header.index(key)
            
            for i in range(self.__dimy):
                if isinstance(self.__data[i][index_value], str) == False:
                    self.__data[i][index_value] *= value

        elif isinstance(key, list):

            for k in key:
                if isinstance(k, int) and 0 <= k < self.__dimx:
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][k], str) == False:
                            self.__data[i][k] *= value

                elif isinstance(k, str) and key in self.__initial_header:
                    index_value = self.__initial_header.index(k)
                    
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][index_value], str) == False:
                            self.__data[i][index_value] *= value


    def div(self, key, value):

        """
        This method divides each of the numbers within the columns specified by the the key
        by the number specified as 'value'. If a number within the columns is a string, it
        is left out of the division.

        Args:
            key: (int or str or list) key(s) of the columns where the values will be added

            value: (float or int) number to be added to the column

        Return:
            --

        """

        if isinstance(key, int) and 0 <= key < self.__dimx:
            for i in range(self.__dimy):
                if isinstance(self.__data[i][key], str) == False:
                    self.__data[i][key] *= value

        elif isinstance(key, str) and key in self.__initial_header:
            index_value = self.__initial_header.index(key)
            
            for i in range(self.__dimy):
                if isinstance(self.__data[i][index_value], str) == False:
                    self.__data[i][index_value] *= value

        elif isinstance(key, list):

            for k in key:
                if isinstance(k, int) and 0 <= k < self.__dimx:
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][k], str) == False:
                            self.__data[i][k] *= value

                elif isinstance(k, str) and key in self.__initial_header:
                    index_value = self.__initial_header.index(k)
                    
                    for i in range(self.__dimy):
                        if isinstance(self.__data[i][index_value], str) == False:
                            self.__data[i][index_value] *= value


    def data(self):
        
        """
        This method returns the data within the object as a two dimensional list. The
        header is not included in the return value.

        Args:
            --

        Return:
            data: (list) two dimensional list of the data within the object, exluding the
                  header

        """

        data = self.__data

        return data


    def spread(self, index, spreader):

        """
        This function replaces values in columns by spreading them into more columns with
        the new values as values contained in 'spreader'. Each value within the column
        must be represented by a key in the spreader.

        This function also deactivates the ability to select header type with the header_type
        method. The header will now only be numbers.

        Args:
            index: (int or str) index of column to be spread

            spreader: (dict) keys of values to 

        Return:
            --
        """

        import warnings
        warnings.warn("""calling the spread function also deactivates the ability to 
                         select 'string' header type with the 'header_type' method.
                         Only the 'number' header type will be availble.""")

        self.__header_type = "number_stuck"

        if isinstance(index, int) and 0 <= index < self.__dimx:
            pass

        elif isinstance(index, str) and index in self.__initial_header:
            index = self.__initial_header.index(index)

        else:
            raise IndexError(index)

        length_set = set([len(spreader[i]) for i in spreader])

        if len(length_set) != 1:
            raise ValueError("Unequal number of lists within each spreader item.")

        length = list(length_set)[0]
        
        for i in range(self.__dimy):

            try:
                spreader[self.__data[i][index]]
            except KeyError:
                raise Exception(str(self.__data[i][index]) + " not found in the spreader dictionary key")
            else:
                
                key = self.__data[i][index]

                for j in range(length):
                    self.__data[i].insert(index + j, spreader[key][j])

                self.__data[i].pop(index + length)

        self.__dimx += length - 1

        if self.__header_type == "string":
            for j in range(length):
                self.__header.insert(index + j, "")
        
        elif self.__header_type in ["number", "number_stuck"]:
            self.__header = [i for i in range(self.__dimx)]