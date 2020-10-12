import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
# from PyVisualizer.CommonUtilities import CommonUtilities


# commonUtils = CommonUtilities()
# conn = commonUtils.connectAndAutorizeToServiceAccount("./service_account.json")
# sheet1 = commonUtils.read_google_sheet(clientConnectionObject=conn,sGoogleSheetFileName="Copy_of_Greendeck_SE_Assignment_Task_2", sWorkSheetName="Sheet1")
# sheet1_data = sheet1.get_all_records()
# print(sheet1_data)
# df = pd.DataFrame(sheet1_data)
class Visualizer():

    def barPlotSalesByYear(self, pandasDataframe, xColName, yColName, sSaveWithFileName):
        """
        Helps in plotting a bar plot, Avg Sales by year on y axis and year on x axis
        :param dataFrame: accepts a pandas dataframe
        :param xColName: Column name to be plotted on x axis
        :param yColName: Column name to be plotted on y axis
        :param sSaveWithFileName: It will save the file in present working directory with the mentioned file name
        """
        pandasDataframe['year'] = pandasDataframe[xColName].apply(lambda x: pd.Timestamp(x, unit='s').date().year)
        sns.barplot(x='year', y=yColName, data=pandasDataframe)
        plt.ticklabel_format(style='plain', axis='y')
        plt.title("Avg Sales per year")
        plt.xlabel("Year(s)", fontsize=10)
        plt.ylabel("Average_sales", fontsize=10)
        plt.xticks(rotation=45)
        plt.show()
        plt.savefig(sSaveWithFileName)

    def barPlotSalesByMonth(self, pandasDataframe, xColName, yColName, sSaveWithFileName):
        """
        Helps in plotting a bar plot, Avg Sales by month on y axis and year on x axis
        :param dataFrame: accepts a pandas dataframe
        :param xColName: Column name to be plotted on x axis
        :param yColName: Column name to be plotted on y axis
        :param sSaveWithFileName: It will save the file in present working directory with the mentioned file name
        """
        pandasDataframe['month'] = pandasDataframe[xColName].apply(
            lambda x: pd.Timestamp(x, unit='s').date().strftime("%B"))
        sns.barplot(x='month', y=yColName, data=pandasDataframe)
        plt.ticklabel_format(style='plain', axis='y')
        plt.title("Avg Sales by months")
        plt.xlabel("Months", fontsize=10)
        plt.ylabel("Average_sales", fontsize=10)
        plt.xticks(rotation=45)
        plt.show()
        plt.savefig(sSaveWithFileName)

    def getSalesByYearsAndMonths(self, pandasDataFrame):
        return pd.pivot_table(data=pandasDataFrame, values='average_sales', index=['year'], columns=['month'],
                              aggfunc='sum').T

# Visualizer().barPlotSalesByMonth(pandasDataframe=df,xColName="timestamp",yColName="average_sales",sSaveWithFileName="salesByMonth.png")