# process performance analysis
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import bluebelt.helpers.defaults as defaults
import bluebelt.helpers.mpl_format as mpl_format
 

# process performance analysis

class ControlChart():
    
    def __init__(self, series, **kwargs):
        
        self.series = series
        
        self.calculate()
        
    def __str__(self):
        
        return 


    def __repr__(self):
        return (f'{self.__class__.__name__}(mean={self.mean:1.1f}, std={self.std:1.1f}, UCL={self.ucl:1.1f}, LCL={self.lcl:1.1f}, outlier_count={self.outlier_count:1.0f})')
    
    def calculate(self):
        mean = self.series.mean()
        std = self.series.std()
        ucl = mean + std * 3
        lcl = mean - std * 3
        outliers = self.series[(self.series > ucl) | (self.series < lcl)]
        
        self.mean = mean
        self.std = std
        self.ucl = ucl
        self.lcl = lcl
        self.outliers = outliers
        self.outlier_count = outliers.shape[0]
        
    def plot(self, **kwargs):
        
        fig, ax = plt.subplots(**kwargs)

        # outliers
        ax.plot(self.outliers, ls=None, marker='o', markersize=21, markerfacecolor=defaults.red+(0.4,), zorder=10)
        
        # observations
        ax.plot(self.series, marker='o', mfc=defaults.blue, color=defaults.light_blue, zorder=20)

        # mean
        ax.axhline(self.mean, color=defaults.grey, linestyle='--')
        ax.text(self.series.index.max(), self.mean, f'mean = {self.mean:1.2f}', ha='right', va='bottom', zorder=50, backgroundcolor=defaults.white+(0.5,))

        # control limits
        ax.axhline(self.ucl, color=defaults.grey, linestyle='--', zorder=1)
        ax.axhline(self.lcl, color=defaults.grey, linestyle='--', zorder=1)

        ax.text(self.series.index.max(), self.ucl, f'UCL = {self.ucl:1.2f}', ha='right', va='bottom', zorder=50, backgroundcolor=defaults.white+(0.5,))
        ax.text(self.series.index.max(), self.lcl, f'LCL = {self.lcl:1.2f}', ha='right', va='bottom', zorder=50, backgroundcolor=defaults.white+(0.5,))

        # labels
        ax.set_title(f'control chart of {self.series.name}', loc='left')
        ax.set_xlabel(self.series.index.name)
        ax.set_ylabel('value')

        # set x axis locator
        mpl_format.axisformat(ax, self.series)

        plt.close()

        return fig
    
    def plotly(self, **kwargs):
        
        config = dict({
            'scrollZoom': False,
            'displayModeBar': True,
            'editable': True
        })
        
        
        layout = go.Layout(
            title=f'control chart of {self.series.name}',    
            plot_bgcolor=f'rgba{defaults.white+(1,)}',
            hovermode="closest",
            xaxis=dict(
                title=self.series.index.name,
                linecolor=f'rgba{defaults.light_grey+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.light_grey+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.light_grey+(1,)}',
            ),
            yaxis=dict(
                title="value",
                linecolor=f'rgba{defaults.light_grey+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.light_grey+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.light_grey+(1,)}',
            ),
        )
        
        data = [go.Scatter(
                        x=self.outliers.index,
                        y=self.outliers.values,
                        marker=dict(
                            color=f'rgba{defaults.red+(0.4,)}',
                            size=21,
                        ),
                        mode='markers',
                        showlegend=False,
                        name='outliers'
                    ),
                go.Scatter(
                        x=self.series.index,
                        y=self.series.values,
                        line=dict(
                                width=3,
                                color=f'rgba{defaults.light_blue+(1,)}',
                            ),
                        marker=dict(
                            color=f'rgba{defaults.blue+(1,)}',
                            size=9,
                        ),
                        mode='lines+markers',
                        showlegend=False,
                        name=self.series.name,
                    ),
               ]
    
        fig = go.Figure(data=data, layout=layout)
    
    
        # add mean, UCL and LCL line
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.mean,
                x1=1,
                y1=self.mean,
                line=dict(
                    color=f'rgba{defaults.grey+(1,)}',
                    width=3,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.mean,
                text=f'mean = {self.mean:1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.ucl,
                x1=1,
                y1=self.ucl,
                line=dict(
                    color=f'rgba{defaults.grey+(1,)}',
                    width=3,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.ucl,
                text=f'UCL = {self.ucl:1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.lcl,
                x1=1,
                y1=self.lcl,
                line=dict(
                    color=f'rgba{defaults.grey+(1,)}',
                    width=3,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.lcl,
                text=f'LCL = {self.lcl:1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        # x-ticks to nice datetime format
        if isinstance(self.series.index, pd.DatetimeIndex):
            fig.update_layout(xaxis_tickformat = '%d-%m-%Y')
        
        # set width en height if any

        if 'width' in kwargs and 'height' in kwargs:
            fig.update_layout(width=kwargs.get('width'), height=kwargs.get('height'))

        return fig.show(config=config)


class RunChart():
    def __init__(self,
                 series,
                 alpha=0.05
                ):
        
        self.series = series
        self.alpha = alpha
        
        self.calculate()
        
    def __str__(self):
        
        str_runs_about="runs about the median:"
        str_expected_runs_about="expected runs about the median:"
        str_longest_run_about="longest run about the median:"
        str_clustering=f"clustering (p ≈ {self.p_value_clustering:1.2f}):"
        str_mixtures=f"mixtures (p ≈ {self.p_value_mixtures:1.2f}):"
        
        str_runs_up_or_down="runs up or down:"
        str_expected_runs_up_or_down="expected runs up or down:"
        str_longest_run_up_or_down="longest run up or down:"
        str_trends=f"trends (p ≈ {self.p_value_trends:1.2f}):"
        str_oscillation=f"oscillation (p ≈ {self.p_value_oscillation:1.2f}):"

        fill = 32
        return (f'{str_runs_about:{fill}}{self.runs_about:1.0f}\n' +
                f'{str_expected_runs_about:{fill}}{self.expected_runs_about:1.0f}\n' +
                f'{str_longest_run_about:{fill}}{self.longest_run_about:1.0f}\n' +
                f'{str_clustering:{fill}}{self.clustering}\n' +
                f'{str_mixtures:{fill}}{self.mixtures}\n' +
                f'\n' +
                f'{str_runs_up_or_down:{fill}}{self.runs_up_or_down:1.0f}\n' +
                f'{str_expected_runs_up_or_down:{fill}}{self.expected_runs_up_or_down:1.0f}\n' +
                f'{str_longest_run_up_or_down:{fill}}{self.longest_run_up_or_down:1.0f}\n' +
                f'{str_trends:{fill}}{self.trends}\n' +
                f'{str_oscillation:{fill}}{self.oscillation}')


    def __repr__(self):
        return (f'{self.__class__.__name__}(runs_about={self.runs_about:1.0f}, expected_runs_about={self.expected_runs_about:1.0f}, longest_run_about={self.longest_run_about:1.0f}, runs_up_or_down={self.runs_up_or_down:1.0f}, expected_runs_up_or_down={self.expected_runs_up_or_down:1.0f}, longest_run_up_or_down={self.longest_run_up_or_down:1.0f}, p_value_clustering={self.p_value_clustering:1.2f}, p_value_mixtures={self.p_value_mixtures:1.2f}, p_value_trends={self.p_value_trends:1.2f}, p_value_oscillation={self.p_value_oscillation:1.2f}, clustering={self.clustering}, mixtures={self.mixtures}, trends={self.trends}, oscillation={self.oscillation})')

    def metrics(self):
        str_runs_about="runs about the median:"
        str_expected_runs_about="expected runs about the median:"
        str_longest_run_about="longest run about the median:"
        str_clustering=f"clustering (p ≈ {self.p_value_clustering:1.2f}):"
        str_mixtures=f"mixtures (p ≈ {self.p_value_mixtures:1.2f}):"
        
        str_runs_up_or_down="runs up or down:"
        str_expected_runs_up_or_down="expected runs up or down:"
        str_longest_run_up_or_down="longest run up or down:"
        str_trends=f"trends (p ≈ {self.p_value_trends:1.2f}):"
        str_oscillation=f"oscillation (p ≈ {self.p_value_oscillation:1.2f}):"

        fill = 32
        print( (f'{str_runs_about:{fill}}{self.runs_about:1.0f}\n' +
                f'{str_expected_runs_about:{fill}}{self.expected_runs_about:1.0f}\n' +
                f'{str_longest_run_about:{fill}}{self.longest_run_about:1.0f}\n' +
                f'{str_clustering:{fill}}{self.clustering}\n' +
                f'{str_mixtures:{fill}}{self.mixtures}\n' +
                f'\n' +
                f'{str_runs_up_or_down:{fill}}{self.runs_up_or_down:1.0f}\n' +
                f'{str_expected_runs_up_or_down:{fill}}{self.expected_runs_up_or_down:1.0f}\n' +
                f'{str_longest_run_up_or_down:{fill}}{self.longest_run_up_or_down:1.0f}\n' +
                f'{str_trends:{fill}}{self.trends}\n' +
                f'{str_oscillation:{fill}}{self.oscillation}'))
    
    def calculate(self):
        '''
        The number of runs about the median is the total number of runs above the median and 
        the total number of runs below the median.
        A run about the median is one or more consecutive points on the same side of the center line.
        A run ends when the line that connects the points crosses the center line.
        A new run begins with the next plotted point. 
        A data point equal to the median belongs to the run below the median.

        The number of runs up or down is the total count of upward and downward runs in the series.
        A run up or down ends when the direction changes.


        Clustering, mixtures, trends and oscillation
        A p-value that is less than the specified level of significance indicates clustering, mixtures, trends and/or oscillation
        '''

        median = self.series.median()

        longest_runs_about = [] #pd.Series(dtype=object)[
        longest_runs_up_or_down = [] #pd.Series(dtype=object)

        # runs

        for index, value in self.series.iteritems():

            # runs about the median
            if index == self.series.index[0]: # set above and start the first run
                above = True if value > median else False
                longest_run_about = 1
                run_about_length = 1
                runs_about = 0
            elif (value > median and not above) or (value <= median and above): # new run about
                runs_about += 1 # add an extra run
                above = not above # toggle the above value
                if run_about_length > longest_run_about:
                    longest_run_about = run_about_length
                    longest_runs_about = [self.series.loc[:index].iloc[-(longest_run_about+1):-1]]
                elif run_about_length == longest_run_about:
                    longest_runs_about += [self.series.loc[:index].iloc[-(longest_run_about+1):-1]]
                #longest_run_about = max(longest_run_about, run_about_length)
                run_about_length = 1
            elif index == self.series.index[-1]: # the last value might bring a longest run
                run_about_length += 1
                if run_about_length > longest_run_about:
                    longest_run_about = run_about_length
                    longest_runs_about = [self.series.loc[:index].iloc[-(longest_run_about):]]
                elif run_about_length == longest_run_about:
                    longest_runs_about += [self.series.loc[:index].iloc[-(longest_run_about):]]
            else:
                run_about_length += 1

            # runs up or down
            if index == self.series.index[0]: # set the first value
                previous_value = value
            elif index == self.series.index[1]: # set up and start first run
                up = True if value > previous_value else False
                longest_run_up_or_down = 1
                run_up_or_down_length = 1
                runs_up_or_down = 1
                previous_value = value

            elif (value > previous_value and not up) or (value <= previous_value and up): # new run up or down
                runs_up_or_down += 1 # add an extra run
                up = not up # toggle up
                if run_up_or_down_length > longest_run_up_or_down:
                    longest_run_up_or_down = run_up_or_down_length
                    longest_runs_up_or_down = [self.series.loc[:index][-(longest_run_up_or_down+1):-1]]
                elif run_up_or_down_length == longest_run_up_or_down:
                    longest_runs_up_or_down += [self.series.loc[:index][-(longest_run_up_or_down+1):-1]]   
                run_up_or_down_length = 1
                previous_value = value

            elif index == self.series.index[-1]: # the last value might bring a longest run
                run_up_or_down_length += 1
                if run_up_or_down_length > longest_run_up_or_down:
                    longest_run_up_or_down = run_up_or_down_length
                    longest_runs_up_or_down = [self.series.loc[:index].iloc[-(longest_run_up_or_down):]]
                elif run_up_or_down_length == longest_run_up_or_down:
                    longest_runs_up_or_down += [self.series.loc[:index].iloc[-(longest_run_up_or_down):]]

            else:
                run_up_or_down_length += 1
                previous_value = value



        # expected runs
        m = self.series[self.series > self.series.median()].count()
        n = self.series[self.series <= self.series.median()].count()
        N = self.series.count()

        expected_runs_about = 1 + (2 * m * n) / N

        expected_runs_up_or_down = (2 * (m + n) - 1) / 3

        # clustering and mixtures
        p_value_clustering = stats.norm.cdf((runs_about - 1 - ((2 * m * n) / N)) / (((2 * m * n * (2 * m * n - N)) / (N**2 * (N - 1)))**0.5))
        p_value_mixtures = 1 - p_value_clustering

        clustering = True if p_value_clustering < self.alpha else False
        mixtures = True if p_value_mixtures < self.alpha else False

        # trends and oscillation
        p_value_trends = stats.norm.cdf((runs_up_or_down - (2 * N - 1) / 3) / ((16 * N - 29) / 90)**0.5)
        p_value_oscillation = 1 - p_value_trends

        trends = True if p_value_trends < self.alpha else False
        oscillation = True if p_value_oscillation < self.alpha else False
        
        self.runs_about = runs_about
        self.expected_runs_about = expected_runs_about
        self.longest_run_about = longest_run_about
        self.runs_up_or_down = runs_up_or_down
        self.expected_runs_up_or_down = expected_runs_up_or_down
        self.longest_run_up_or_down = longest_run_up_or_down
        self.p_value_clustering = p_value_clustering
        self.p_value_mixtures = p_value_mixtures
        self.p_value_trends = p_value_trends
        self.p_value_oscillation = p_value_oscillation
        self.clustering = clustering
        self.mixtures = mixtures
        self.trends = trends
        self.oscillation = oscillation
        self.longest_runs_about = longest_runs_about
        self.longest_runs_up_or_down = longest_runs_up_or_down
        
    def plot(self, **kwargs):
        
        fig, ax = plt.subplots(nrows=1, ncols=1, **kwargs)

        # observations
        for run in self.longest_runs_about:
            ax.plot(run, lw=21, color=defaults.red, alpha=0.4, zorder=10)

        for run in self.longest_runs_up_or_down:
            ax.plot(run, lw=21, color=defaults.blue, alpha=0.4, zorder=10)

        ax.plot(self.series, marker='o', color=defaults.light_blue, zorder=20)

        # mean
        ax.axhline(self.series.median(), color=defaults.grey, linestyle='--', zorder=1)
        ax.text(self.series.index.max(), self.series.median(), f'median = {self.series.median():1.2f}', ha='right', va='bottom', zorder=50, backgroundcolor=defaults.white+(0.5,))

        # labels
        ax.set_title(f'run chart of {self.series.name}', loc='left')
        ax.set_xlabel(self.series.index.name)
        ax.set_ylabel('value')

        # set x axis locator
        mpl_format.axisformat(ax, self.series)

        
    def plotly(self, **kwargs):
        
        config = dict({
            'scrollZoom': False,
            'displayModeBar': True,
            'editable': True
        })
        
        
        layout = go.Layout(
            title=f'run chart of {self.series.name}',    
            plot_bgcolor=f'rgba{defaults.white+(1,)}',
            hovermode="closest",
            xaxis=dict(
                title=self.series.index.name,
                linecolor=f'rgba{defaults.grey+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.grey+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.grey+(0.2,)}',
            ),
            yaxis=dict(
                title="value",
                linecolor=f'rgba{defaults.grey+(1,)}',
                zeroline=False,
                ticks="outside",
                tickwidth=1,
                tickcolor=f'rgba{defaults.grey+(1,)}',
                ticklen=5,
                showgrid=True,
                gridwidth=0.5,
                gridcolor=f'rgba{defaults.grey+(1,)}',
            ),
        )
        
        data = []
        
        runs = 'run' if len(self.longest_runs_about)==1 else 'runs'
        for idx, trace in enumerate(self.longest_runs_about):
            data.append(go.Scatter(
                x=trace.index,
                y=trace.values,
                line=dict(
                    width=21,
                    color=f'rgba{defaults.red+(0.4,)}',
                ),
                mode='lines',
                name=f'longest {runs} about the median',
                legendgroup="runs_about",
                showlegend=True if idx==0 else False,
            ))

        runs = 'run' if len(self.longest_runs_up_or_down)==1 else 'runs'
        for idx, trace in enumerate(self.longest_runs_up_or_down):
            data.append(go.Scatter(
                x=trace.index,
                y=trace.values,
                line=dict(
                    width=21,
                    color=f'rgba{defaults.blue+(0.4,)}',
                ),
                mode='lines',
                name=f'longest {runs} up or down',
                legendgroup="runs_up_down",
                showlegend=True if idx==0 else False,
            ))


        data.append(go.Scatter(
            x=self.series.index,
            y=self.series.values,
            line=dict(
                    width=3,
                    color=f'rgba{defaults.light_blue+(1,)}',
                ),
            marker=dict(
                color=f'rgba{defaults.blue+(1,)}',
                size=9,
            ),
            mode='lines+markers',
            showlegend=False,
        ))
    
        fig = go.Figure(data=data, layout=layout)
    
    
        # add median line
        fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                y0=self.series.median(),
                x1=1,
                y1=self.series.median(),
                line=dict(
                    color=f'rgba{defaults.grey+(1,)}',
                    width=3,
                    dash='dash'
                ),
            )
        fig.add_annotation(
            dict(
                xref="paper",
                yref="y",
                x=1,
                y=self.series.median(),
                text=f'median = {self.series.median():1.2f}',
                showarrow=False,
                align='right',
                bgcolor=f'rgba{defaults.white+(0.5,)}',
            )
        )
        
        # x-ticks to nice datetime format
        if isinstance(self.series.index, pd.DatetimeIndex):
            fig.update_layout(xaxis_tickformat = '%d-%m-%Y')
        
        # set width en height if any
        if 'width' in kwargs and 'height' in kwargs:
            fig.update_layout(width=kwargs.get('width'), height=kwargs.get('height'))

        return fig.show(config=config)

