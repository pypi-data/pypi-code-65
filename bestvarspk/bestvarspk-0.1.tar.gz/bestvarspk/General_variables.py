class Best_variables:
    def __init__(self, df, target, rgr=False):
        """ Generic dataset class for create object based 
        on prediction type inteded
        
        Attributes:
            df (dataframe) representing the data in pandas format
            target (string) representing target column
            rgr (boolean) representing target column as Regression(True) or Classification(False)
        """
        self.df = df
        self.target = target
        self.rgr = rgr
        self.x, self.y = self.separe_dataset()

    def separe_dataset(self):

        """Function to read data from a dataset and separe features and label   
        """
        lista = list(self.df.columns)
        lista.remove(self.target)

        x = self.df[lista].copy()  # independent columns
        y = self.df[self.target].copy()  # target column
        return x, y