#!/usr/bin/env python
# coding: utf-8

# Import common EDA libraries
import pandas as pd
import numpy as np
# Import system interaction libraries
from sys import path
# Import interactive tools
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, interactive
# Import plotting tools
import seaborn as sns
import matplotlib.pyplot as plt
# Import Utils 
path.append(".")
from .utils import Utils as Utils 

class BDTK:
    """
    The Big Data Analysis Toolkit. 
    
    Author: Aurum Kathuria 
    (LinkedIn: https://linkedin.com/in/heyaurum, GitHub: https://github.com/aurumkathuria)
    
    This is the toolkit designed to optimize data anlysis for data scientists & data analysts.
    
    Read the BDTK Handbook for an in-depth explanation of the purpose and features of the Toolkit.
    """
    
    __version__ = "0.1.1"
    __author__ = 'Aurum Kathuria'
    
    def clean_name(self,name):
        Utils.type_check(name, str)
        return name[0].upper() + name[1:].lower()
    
    def __init__(self, df_in=None, **kwds):
        """ Creates a new BDTK Instance based off the pandas.DataFrame DF_IN, and uses the keyword args in **kwds.
        
        Parameters
        -------------------------------
        df_in: pandas.DataFrame object
            The dataframe on which to perform primary analysis
        **kwds: default None
            Optional keywords to pass in to this new BDTK object.
            
            Possible Keyword Arguments:
                filepath: str, path-like
                    Path to a stored csv file from which to extract a pandas DataFrame. 
                    'df_in' must be None for this to be used, otherwise df_in will be used and this will be ignored.
        
        Examples
        -------------------------------
        >>> BDTK(pd.DataFrame())
        DATAFRAME INFORMATION 
        SHAPE: (0, 0) 
        COLUMNS: Index([], dtype='object')
        >>>"""
        # Extract df_in from filepath if it doesn't exist, and ensure df_in is a pd.DataFrame
        if not Utils.type_check(df_in, pd.DataFrame, True):
            filepath = kwds.get("filepath", None)
            if not filepath:
                raise ValueError("No dataframe or filepath passed in. Each BDTK instance requires a dataframe to process. \
                                 Please pass in either a pandas.DataFrame obj or a path to a .csv file.")
            else: #filepath exists
                df_in = pd.read_csv(filepath)
        # df_in now exists for sure as a DataFrame, so let's add it to this object
        self.dataframe = df_in
        
        #initialize basic variables for the future
        self.data_types_dict = {}
        self.columns_to_figures = {}
        self.correlations = None
           
        # prep plotting aesthetics
        #set font size names
        SMALL_SIZE = 14
        MEDIUM_SIZE = 16
        BIGGER_SIZE = 22
        #set font sizes
        plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
        plt.rc('axes', titlesize=BIGGER_SIZE)    # fontsize of the axes title
        plt.rc('axes', labelsize=BIGGER_SIZE)    # fontsize of the x and y labels
        plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
        plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
        plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
        #set figure size
        plt.rcParams["figure.figsize"] = (14, 8) # size of the figure plotted
        #set color palettes
        self.qualitative_palette = sns.color_palette("husl")
        self.sequential_palette = sns.light_palette("#FDB515", 4)
        self.diverging_palette = sns.diverging_palette(h_neg=233, h_pos=52, s=95, l=75, center='light')
        sns.set_palette(self.qualitative_palette)#, color_codes=True)
        
        
    def data_types(self, sample_size=0.1, accuracy_threshold=0.5, display_unknowns=True):
        """Takes a random sample if sample_size values from each column, and tries
        to deduce the type of data stored in that column from the values.
        
        Parameters
        -------------------------------
        sample_size: int, float; default 0.1
            As an int: The number of random values to look at in each column to 
            identify the type of value. 
            As a float: The proportion of values to look at in each column to 
            identify the type of value.
        accuracy_threshold: float, >= 0 & <= 1
            The minimum proportion required to classify a column as of a specific type
        display_unknowns: boolean
            Whether to display the preset message when a column's data type is 
            unknown. Useful for debugging this function or your dataset when trying 
            to understand why a column received the 'unknown' type classification.
                
        
        Returns
        -------------------------------
        A dictionary of column names to the data types of those columns. This dictionary is also
            stored as an instance attribute under 'self.data_types_dict'.
        
        
        See Also
        -------------------------------
        BDTK.column_distribution()
        
        
        Examples
        -------------------------------
        bdtk = new BDTK(df)
        bdtk.data_types()
        """
        
        Utils.type_check(sample_size, [int, float])
        Utils.type_check(accuracy_threshold, [float, int])
        assert accuracy_threshold >= 0 and accuracy_threshold <= 1, "threshold must be between 0 and 1" 
        if type(sample_size) == float:
            sample_size = int(sample_size * self.dataframe.shape[0])
        
        columns_to_data_types = {}
        for col_name in self.dataframe.columns:
            column = self.dataframe.loc[:, col_name]
            if len(column.shape) != 1:
                columns_to_data_types[col_name] = 'unknown: column shape incorrect'
                continue
            random_n_indices = np.random.choice(self.dataframe.index, size=sample_size, replace=False)
            random_n_values = column.loc[random_n_indices]
            types = random_n_values.apply(type)
            type_freqs = types.value_counts()
            #Ensure enough non-null values exist in the sample
            na_count = np.sum(random_n_values.isna())
            if na_count > sample_size*(1-accuracy_threshold):
                columns_to_data_types[col_name] = 'unknown: too many NaNs'
                if display_unknowns:
                    print(f"{col_name} has too many null values to determine type")
                    print(f"{na_count} null values out of {sample_size} values is a {round(na_count/sample_size*100, 2)}% " +
                          f"null value rate. At threshold {accuracy_threshold}, up to {round(sample_size*(1-accuracy_threshold))} "
                          f"null values are allowed.")
                continue
            #Determine qual. vs quant. variable
            if str(type_freqs.index[0]) == "<class 'str'>":
                columns_to_data_types[col_name] = 'qualitative'
            else:
                columns_to_data_types[col_name] = 'quantitative'
        self.data_types_dict = columns_to_data_types
        return columns_to_data_types
    
    
    def change_data_type(self, column_name, new_data_type):
        """Takes a column name columns_name and changes its stored data type to be 
        new_data_type.
        
        This is useful if a column appears to be quantitative, but is instead ordinal.
        Changing this results in different graphs being displayed as a result of
        bdtk.column_distribution() or bdtk.interactive_col_dist().
        
        
        Parameters
        -------------------------------
        column_name: str
            A name of a column in the dataframe self.dataframe. If not a valid column, 
            throws a ValueError.
        new_data_type: str
            This is the data type stored for the column column_name.
            Possible values are:
                "quantitative"
                "quant"
                "qualitative"
                "qual"
            Note: the abbreviated versions are stored as the whole versions for consistency.
            The abbreviations are only available for convenience here.
        
        
        Returns
        -------------------------------
        The new data type of the column.
        
        
        See Also
        -------------------------------
        BDTK.data_types()
        
        
        Examples
        -------------------------------
        bdtk = new BDTK(df)
        bdtk.data_types()
        bdtk.change_data_type('col1', 'quant')
        """
        #Setup
        Utils.type_check(column_name, str)
        Utils.type_check(new_data_type, str)
        assert column_name in self.dataframe.columns, "column_name must be in the dataframe's columns"
        if new_data_type=='quant':
            new_data_type = 'quantitative'
        elif new_data_type=='qual':
            new_data_type = 'qualitative'
        if new_data_type not in ['quantitative', 'qualitative']:
            raise ValueError("new data_type must be either 'quantitative', 'qualitative', or their abbreviations")
           
        #Change Type
        old_type = self.data_types_dict[column_name]
        self.data_types_dict[column_name] = new_data_type
        
        #return
        return self.data_types_dict[column_name]
    
    
    def get_optimal_data_types(self, columns=None, float_thresh=0.001):
        """ Find the smallest data types for each numeric column while maintaining
        data granularity.
        
        Parameters
        -------------------------------
        columns: list; default None
            The columns for which to identify the optimal data types.
            If None, will go through all columns.
        float_thresh: float; default 0.001 (0.1%)
            For columns with decimal numbers, how much rounding error to 
            accept. Rounding error is to be expected here, since operations
            on floating-point numbers are inexact.
            (see: https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html#693)

        
        Returns
        -------------------------------
        A dictionary mapping column names to data types.
        
        
        See Also
        -------------------------------
        bdtk.data_types()
        numpy data types (link: https://numpy.org/devdocs/user/basics.types.html)
        
        
        Examples
        -------------------------------
        >>> bdtk = BDTK(sns.load_dataset('planets')) 
        >>> bdtk.get_optimal_data_types()
        {'method': str,
         'number': numpy.uint8,
         'orbital_period': numpy.float32,
         'mass': numpy.float16,
         'distance': numpy.float32,
         'year': numpy.uint16}
        
        """
        # Get quantitative columns vs. qualitative columns
        if not self.data_types_dict:
            self.data_types(display_unknowns=False)
        
        # Setup
        if not columns:
            columns = self.dataframe.columns
        columns_to_optimal_data_types = {}
        bits_to_dtypes = {'int': {'signed': {8: np.int8, 16: np.int16, 32: np.int32, 64: np.int64}, 
                                 'unsigned': {8: np.uint8, 16: np.uint16, 32: np.uint32, 64: np.uint64}
                                 },
                          'float': {16: np.half, 32: np.single, 64: np.double, 128: np.longdouble}
                         }
        
        # Main loop
        for col_name in self.dataframe.columns:
            # Filter out qualitative columns
            if 'qual' in self.data_types_dict[col_name]:
                columns_to_optimal_data_types[col_name] = self.dataframe[col_name].dtype
                continue;
            
            # Get column without noisy nulls
            column = self.dataframe[col_name]
            column = column[~column.isna()]
            has_floats = np.sum(np.abs(column - np.array(column, dtype=np.int64))) > float_thresh*len(column)
            
            # maybe replace existing loop with bit-wise manipulation?
            if not has_floats:
                # Determine whether column needs negative (signed) values
                min_val, max_val, unsigned = np.min(column), np.max(column), False
                if min_val >= 0:
                    unsigned = True
                    
                # int dtypes depend on the element w highest absolute value
                # We'll use that to identify the optimal data type 
                max_abs = np.max([np.abs(min_val), np.abs(max_val)])
                for i in np.arange(1, 4):
                    num_bits = int(((2**i) * (2**3)) / (unsigned+1))
                    if np.log2(max_abs) < num_bits:
                        break;
                columns_to_optimal_data_types[col_name] = bits_to_dtypes['int'][f'{"un"*unsigned}signed'][num_bits]
            else:
                # iterate through options til we find the best one with acceptable error
                for dtype in bits_to_dtypes['float'].values():
                    diff = np.sum(np.abs(column - np.array(column, dtype=dtype)))
                    if diff < float_thresh*len(column):
                        columns_to_optimal_data_types[col_name] = dtype
                        break;
        return columns_to_optimal_data_types
    
    def column_distribution(self, base_column, compare_column=None, **kwargs):
        """Returns and optionally displays a visualization of the distribution of a quantitative column,
        optionally against a qualitative column.
        
        Will call self.data_types if self.data_types_dict is None, as this function
        requires information on the data type of the column to determine the type
        of plot to display.
        
        Parameters
        -------------------------------
        base_column: str
            The name of the column whose distribution is to be visualized.
        compare_column: str, default None
            The name of the column to compare distributions with the base_column.
        **kwargs: some additional specifications 
            show_unknowns: boolean, default True
                Whether to show the value_counts of the column as a DataFrame when the 
                data type is unknown.
            1D:
            
            2D:
                Quant vs. Quant:
                    trendline: boolean, default False
                        Whether to include the regression line, along with r squared and 
                        regression line equation, on the plot displayed. 
        
        
        Returns
        -------------------------------
            The AxesSubplot object and Figure object on which this plot is displayed.
        
        See Also 
        -------------------------------
        seaborn.regplot()
        seaborn.scatterplot()
        seaborn.kdeplot()
        seaborn.rugplot()
        seaborn.distplot()
        
        
        Examples
        -------------------------------
        bdtk = BDTK(DataFrame)
        bdtk.column_distribution(col1)
        bdtk.column_distribution(col3, col4)
        """
        # Setup
        Utils.type_check(base_column, str)
        assert base_column in self.dataframe.columns
        base_vals = self.dataframe.loc[:, base_column]
        if compare_column:
            Utils.type_check(compare_column, str)
            assert compare_column in self.dataframe.columns
            compare_vals = self.dataframe.loc[:, compare_column]
        if not self.data_types_dict:
            self.data_types(display_unknowns=False)
        clean_name = self.clean_name
        
        #Handle special keyword arguments
        trendline = kwargs.get('trendline', True)
        ci = (lambda: None if not trendline else 95)()
        
        
        # Define 2D Distribution Methods
        def quant_v_quant(base_column, compare_column):
            """Displays a Scatterplot, optionally with a trendline, comparing
            the distributions of two quantitative variables"""
            r_sq = self.dataframe[base_column].corr(self.dataframe[compare_column])
            sns.set_palette(palette=self.diverging_palette)
            if trendline:
                ax = sns.regplot(x=base_column, y=compare_column, data=self.dataframe,
                             ci=ci, fit_reg=trendline, label=f"r^2: {round(r_sq, 4)}")
                plt.legend(fontsize='large', edgecolor='r')
            else: #no trendline
                ax = sns.regplot(x=base_column, y=compare_column, data=self.dataframe,
                             ci=ci)
            plt.title(f"Comparing The Distribution of Values in \"{base_column}\" Against \"{compare_column}\"")
            plt.xlabel(f"{base_column} Values") 
            plt.ylabel(f"{compare_column} Values")
            plt.grid(True)
            #if len(base_uniques) > len(plt.xticks()):
                #plt.xticks(base_uniques.index)
            #if len(compare_uniques) > len(plt.yticks()):
                #plt.yticks(compare_uniques.index)
            return ax, fig
            
        def quant_v_qual(quant_col, qual_col):
            """Displays a Segmented Violin Plot comparing the distribution of 
            a quantitiative variable and a qualitative variable"""
            ax = sns.violinplot(x=qual_col, y=quant_col, data=self.dataframe, orient='v',
                               palette=self.qualitative_palette)
            ax.set(
                title=f"Comparing the Distribution of \"{quant_col}\" Against the Values in \"{qual_col}\"", 
                xlabel=f"Unique Values of \"{qual_col}\"",
                ylabel=f"Values of \"{quant_col}\""
            )
            #ideally, we have ~0 deg rot with 3 elements, ~60 deg rot w 30 elements, max 90 deg rot
            xtick_rot = lambda num: 95/(1 + np.power(np.e, (-1 * 0.25 * (num - 15)))) - 5
            plt.xticks(rotation=xtick_rot(len(plt.xticks()[0])))
            print('rotation:', xtick_rot(len(plt.xticks()[0])))
            print('numticks:', len(plt.xticks()[0]))
            plt.grid(True)
            return ax, fig
        
        def qual_vs_qual(x_column, y_column):
            """Will use a Segmented Bar Plot to count the number of observations 
            in overlapping categories
            
            future version:
                use https://randyzwitch.com/creating-stacked-bar-chart-seaborn/ to create
                a seaborn implementation of this            
            """
            #the line below handles finding a column from which the final output can be collected.
            #it is a stopgap fix and should be updated in the future, and will error if len(df.columns) == 2
            last_column = [col for col in self.dataframe.columns if col not in [x_column, y_column]][0]
            self.dataframe.groupby([x_column, y_column]).count().reset_index().pivot(x_column, y_column, last_column)
            
            otu = minimal_df.groupby([x_column, y_column]).count().reset_index()
            otu = otu.pivot(x_column, y_column, last_column).fillna(0)
            prev_height = np.zeros(len(otu.index))
            i = 0
            for i in range(len(otu.columns)):
                height = np.array(otu.iloc[:, i])
                plt.bar(x=list(otu.index), height=height, bottom=prev_height, 
                        label=f"\"{y_column}\"={otu.columns[i]}")
                prev_height = [prev_height[i] + height[i] for i in np.arange(height.shape[0])]
            plt.legend()
            plt.ylim(top=max(prev_height)*1.1)

            plt.title(f"Comparing the Values of \"{x_column}\" Against the Values in \"{y_column}\"")
            plt.xlabel(f"Unique Values of \"{x_column}\"")
            plt.ylabel(f"Unique Values of \"{y_column}\"")
            return None, fig
        
        # Prep to Graph
        neat_basecol_name = clean_name(base_column)
        ax = None
        fig = plt.figure(figsize=(14, 8))
        base_data_type = self.data_types_dict[base_column]
        
        # 1D Distribution
        if not compare_column:
            base_vals = base_vals[~base_vals.isna()]
            if base_data_type == "quantitative":
                sns.set_palette(palette=self.diverging_palette)
                ax = sns.distplot(base_vals)
            if base_data_type == "qualitative":
                val_counts = base_vals.value_counts()
                ax = sns.barplot(x=val_counts.index, y=val_counts, palette=self.sequential_palette)
                plt.title("The Distribution of Values in " + base_column)
                plt.xlabel("Unique Values of " + base_column) 
                plt.ylabel("Counts")
            if ax == None and kwargs.get('show_unknowns', False):
                print("Data Type for Column Unknown. Displaying Value Counts.")
                display(pd.DataFrame(base_vals.value_counts()))           
        else:
            base_uniques = self.dataframe[base_column].value_counts()
            compare_uniques = self.dataframe[compare_column].value_counts()
            compare_data_type = self.data_types_dict[compare_column]
            if base_data_type == 'quantitative' and compare_data_type == 'quantitative':
                print("2D Quant vs. Quant => Scatterplot")
                return quant_v_quant(base_column, compare_column)
            if base_data_type == 'quantitative' and compare_data_type == 'qualitative':
                print("2D Quant vs. Qual => Violin Plot")
                return quant_v_qual(base_column, compare_column)
            if base_data_type == 'qualitative' and compare_data_type == 'quantitative':
                print("2D Qual vs. Quant => Violin Plot")
                return quant_v_qual(compare_column, base_column)
            if base_data_type == 'qualitative' and compare_data_type == 'qualitative':
                print("2D Qual vs. Qual => Stacked Bar Plot")
                return qual_vs_qual(base_column, compare_column)
            
        return ax, fig
        
    
    def interactive_col_dist(self, hide_plot=False):
        """Displays an interactive visualization of the distribution of a column, optionally 
        against another column. 
            
            Currently Supported Data Types:
                1D: 
                    - quant
                    - qual
                2D: 
                    - quant vs. quant
                    - quant vs. qual (same as qual vs. quant for displayed figure)
                    - qual vs. qual
        
        Will call self.data_types if self.data_types_dict is None, as this function
        requires information on the data type of the column to determine the type
        of plot to display.
        
        Parameters
        -------------------------------
        hide_plot: boolean, default False
            A way to hide the plot and save memory when the plot is no longer needed but 
            the code is desired to remain.  
        
        Returns
        -------------------------------
            The interactive object to visualize column relationships.
        
        See Also 
        -------------------------------
        BDTK.column_distribution()        
        
        Examples
        -------------------------------
        bdtk = BDTK(DataFrame)
        bdtk.interactive_col_dist()
        bdtk.interactive_col_dist(hide_plot=True)
        """
        #hide_plot functionality
        if hide_plot:
            return None
        
        # Create widgets
        base_column_widget = widgets.Dropdown(options=self.dataframe.columns)
        compare_column_widget = widgets.Dropdown(options=[None, *self.dataframe.columns[1:]])
        trendline_widget = widgets.Checkbox(value=False, indent=True, description="Show Trendline")

        # Updates the image options based on directory value
        def update_compare_options(*args):
            value = compare_column_widget.value
            options = [None, *self.dataframe.columns]
            base_col_value = args[0]['new']
            options.remove(base_col_value)
            compare_column_widget.options = options
            if value == base_col_value:
                compare_column_widget.value = None
            else: 
                compare_column_widget.value = value
            
        # Tie the compare_column options to base_column value
        base_column_widget.observe(update_compare_options, 'value')
        
        interacter = interact(self.column_distribution, 
                 base_column=base_column_widget, 
                 compare_column=compare_column_widget)

        return interacter
    
    
    def __repr__(self):
        return f"DATAFRAME INFORMATION \n" + \
            f"SHAPE: {self.dataframe.shape} \n" + \
            f"COLUMNS: {self.dataframe.columns}"

