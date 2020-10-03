import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class WaterfallChart():
    
    '''
    This class creates flexible waterfall charts based on matplotlib. 
    The plot_waterfall() function returns an Axes object. So it’s very flexible to use the object outside the class for further editing.
    '''

    def __init__(self, step_values, step_names=[], metric_name='', last_step_label=''):
        '''
        step_values [list]: the cumulative values for each step.
        step_names [list]: (optional) the corresponding labels for each step. Default is []. If [], Labels will be assigned as 'Step_i' based on the order of step_values.
        metric_name [str]: (optional)  the metric label. Default is ''. If '', a label 'Value' will be assigned as metric name.
        last_step_label [str]: (optional) In the data pre-processing, an additional data point will be appended to reflect the final cumulative value. 
                               This is the label for that value. Default is ''. If '', the label will be assigned as 'Final Value'.
        '''
        self.step_values = step_values
        self.step_names = step_names if len(step_names)>0 else ['Step_{0}'.format(x+1) for x in range(len(step_values))] 
        self.metric_col = metric_name if metric_name!='' else 'Value'
        self.delta_col = 'delta'
        self.base_col = 'base'        
        self.last_step_label = last_step_label if last_step_label!='' else 'Final Value'
        
    def plot_waterfall(self, ax=None, figsize=(10, 5), title='', bar_labels=True,
                       color_kwargs={}, bar_kwargs={}, line_kwargs={}):
        '''
        Generate the waterfall chart and return the Axes object. 
        Parameters:
            ax [Axes]: (optional) existing axes. Default is None. If None, create a new one.
            figsize [tuple]: (optional) figure size. Default is (10, 5).
            title [string]: (optional) title of the Axes. Default is ''.
            bar_labels [bool|list|str]: (optional) what to show as bar labels on the plot. Refer to check_label_type() for details. 
                                        Default is True. If True, the metric values (deltas and final value) will be shown as labels.
            color_kwargs [dict]: (optional) arguments to control the colors of the plot. Refer to get_colors() function for details. Default is {}.
            bar_kwargs [dict]: (optional) arguments to control the bars on the plot. Valid values are any kwargs for matplotlib.pyplot.bar. Default is {}. 
            line_kwargs [dict]: (optional) arguments to control the lines on the plot. Valid values are any kwargs for matplotlib.axes.Axes.plot. Default is {}.
        '''
        # Prep data for plotting
        df_plot = self.prep_plot()
        # Plot
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)
        ax = self.plot_bars(ax, df_plot, color_kwargs, bar_kwargs)
        ax = self.plot_link_lines(ax, df_plot, line_kwargs)
        # Label
        if bar_labels:
            ax = self.add_labels(ax, df_plot, bar_labels, color_kwargs)
        # Format
        ax.set_xlim(-0.5, len(df_plot)-0.5)
        ax.set_ylim(0, df_plot[self.metric_col].max()*1.1)
        ax.set_ylabel(self.metric_col)
        ax.set_title(title, fontsize=16)
        return ax

    def prep_plot(self):
        '''
        Take the input values and create a dataframe for plotting
        '''
        # Create a table for plotting
        step_deltas = list(pd.Series(self.step_values).diff().fillna(pd.Series(self.step_values)).values)
        df_plot = pd.DataFrame(
            [self.step_values+[self.step_values[-1]], step_deltas+[self.step_values[-1]]],
            columns = self.step_names + [self.last_step_label], 
            index = [self.metric_col, self.delta_col]).transpose()
        # Add base values
        df_plot[self.base_col] = df_plot[self.metric_col].shift(1).fillna(0)
        df_plot[self.base_col] = list(df_plot[self.base_col].values[0:-1]) + [0]  
        return df_plot
    
    def plot_bars(self, ax, df_plot, color_kwargs={}, bar_kwargs={}):
        '''
        Plot the bar elements of the waterfall chart 
        Parameters:
            ax [Axes]: existing axes.
            df_plot [DataFrame]: data to plot.
            color_kwargs [dict]: (optional) arguments to control the colors of the plot. Default is {}
            bar_kwargs [dict]: (optional) arguments to control the bars on the plot. Default is {}
        '''
        barcolors, _ = self.create_color_list(df_plot, color_kwargs)
        bar_kwargs['width'] = bar_kwargs.get('width', 0.6)
        ax.bar(x=df_plot.index, height=df_plot[self.delta_col], bottom=df_plot[self.base_col], color=barcolors, **bar_kwargs)
        return ax
    
    def plot_link_lines(self, ax, df_plot, line_kwargs={}):
        '''
        Plot the line elements of the waterfall chart 
        Parameters:
            ax [Axes]: existing axes.
            df_plot [DataFrame]: data to plot.
            line_kwargs [dict]: (optional) arguments to control the lines on the plot. Default is {}
        '''
        # Create lines
        link_lines = df_plot[self.metric_col].repeat(3).shift(2)
        link_lines[1:-1:3] = np.nan
        link_lines = link_lines[1:-1]
        # Default kwargs
        line_kwargs['color'] = line_kwargs.get('color', 'grey')
        line_kwargs['linestyle'] = line_kwargs.get('linestyle', '--')
        # Plot
        ax.plot(link_lines, **line_kwargs)
        return ax

    def add_labels(self, ax, df_plot, bar_labels, color_kwargs={}):
        '''
        Add labels to the waterfall chart.
        Parameters:
            ax [Axes]: existing axes.
            df_plot [DataFrame]: data to plot.
            bar_labels [bool|list|str]: what to show as bar labels on the plot. Refer to check_label_type() for details. 
            color_kwargs [dict]: (optional) arguments to control the colors of the plot. Default is {}
        '''
        _, txtcolors = self.create_color_list(df_plot, color_kwargs)
        label_type = self.check_label_type(bar_labels)
        for i, v in enumerate(df_plot[self.metric_col]):
            if label_type == 'list':
                label = str(bar_labels[i])
            elif label_type == 'value':
                label = '{:,}'.format(int(df_plot[self.delta_col][i]))
            else:
                label = bar_labels
            ax.text(i, v*1.02, label, color=txtcolors[i],  
                    horizontalalignment='center', verticalalignment='baseline')
        return ax
    
    def create_color_list(self, df_plot, color_kwargs):
        '''
        Create the lists of colors (bar and label) for the corresponding values to plot
        Parameters:
            df_plot [DataFrame]: data to plot.
            color_kwargs [dict]: arguments to control the colors of the plot.
        '''
        c_bar_pos, c_bar_neg, c_bar_start, c_bar_end, c_text_pos, c_text_neg, c_text_start, c_text_end = self.get_colors(color_kwargs)
        mid_values = df_plot[self.delta_col][1:-1].values
        barcolors = [c_bar_start] + [c_bar_neg if x<0 else c_bar_pos for x in mid_values] + [c_bar_end]        
        txtcolors = [c_text_start] + [c_text_neg if x<0 else c_text_pos for x in mid_values] + [c_text_end]
        return barcolors, txtcolors
        
    @staticmethod
    def get_colors(color_kwargs):
        '''
        Available color controls and their default values.
        '''
        c_bar_pos = color_kwargs.get('c_bar_pos', 'seagreen') # Bar color for positive deltas
        c_bar_neg = color_kwargs.get('c_bar_neg', 'salmon') # Bar color for negative deltas
        c_bar_start = color_kwargs.get('c_bar_start', 'c') # Bar color for the very first bar
        c_bar_end = color_kwargs.get('c_bar_end', 'grey') # Bar color for the last bar
        c_text_pos = color_kwargs.get('c_text_pos', 'darkgreen') # Label text color for positive deltas
        c_text_neg = color_kwargs.get('c_text_neg', 'maroon') # Label text color for negative deltas
        c_text_start = color_kwargs.get('c_text_start', 'black') # Label text color for the very first bar
        c_text_end = color_kwargs.get('c_text_end', 'black') # Label text color for the last bar
        return c_bar_pos, c_bar_neg, c_bar_start, c_bar_end, c_text_pos, c_text_neg, c_text_start, c_text_end
    
    @staticmethod
    def check_label_type(bar_labels):
        '''
        Check label type. Valid types are:
            list: a list of labels to be shown for each bar.
            bool: whether to show labels or not. If True, the metric values (deltas and final value) will be shown as labels.
            str: a fixed string to be shown as the label for each bar.  
        '''
        if isinstance(bar_labels, list):
            label_type = 'list'
        elif isinstance(bar_labels, bool):
            label_type = 'value'
        elif isinstance(bar_labels, str):
            label_type = 'str'
        else:
            raise ValueError('bar_labels can only be of type bool, string, or list. Please check input type.')
        return label_type