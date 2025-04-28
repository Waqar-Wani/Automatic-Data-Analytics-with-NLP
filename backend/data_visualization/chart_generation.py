import plotly.express as px
import pandas as pd
import numpy as np

def generate_chart(df, x_column, y_column, chart_type='bar', color_column=None):
    """
    Generate different types of charts based on the selected chart type.
    Handles missing values appropriately for each chart type.
    
    Args:
        df (pd.DataFrame): The input dataframe
        x_column (str): Column name for x-axis
        y_column (str): Column name for y-axis
        chart_type (str): Type of chart to generate
        color_column (str): Column name for grouping
        
    Returns:
        plotly.graph_objects.Figure: The generated chart figure
        
    Raises:
        ValueError: If the specified columns are not found in the dataframe
    """
    # Validate columns
    if x_column not in df.columns:
        raise ValueError(f"Column '{x_column}' not found in dataset")
    if isinstance(y_column, list):
        for col in y_column:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in dataset")
    elif y_column not in df.columns and chart_type not in ['histogram', 'pie']:
        raise ValueError(f"Column '{y_column}' not found in dataset")
    if color_column and color_column not in df.columns:
        raise ValueError(f"Column '{color_column}' not found in dataset")

    def y_label():
        if isinstance(y_column, list):
            return ', '.join(y_column)
        return y_column

    # Generate chart based on selected type
    try:
        if chart_type == 'bar':
            df_plot = df.copy()
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, x=x_column, y=y_column, color=color_column, barmode='group', title=title)
                yaxis_title = y_label()
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, x=x_column, y=y_column, color=color_column, title=title)
                yaxis_title = y_label()
            
        elif chart_type == 'line':
            df_plot = df.copy()
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].interpolate()
                title = f"Line Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.line(df_plot, x=x_column, y=y_column, color=color_column, title=title, markers=True)
                yaxis_title = y_label()
            else:
                df_plot[y_column] = df_plot[y_column].interpolate()
                title = f"Line Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.line(df_plot, x=x_column, y=y_column, color=color_column, title=title, markers=True)
                yaxis_title = y_label()
            
        elif chart_type == 'scatter':
            df_plot = df.copy()
            df_plot['is_missing'] = df_plot[y_column[0] if isinstance(y_column, list) else y_column].isna()
            title = f"Scatter Chart for {y_label()} by {x_column}"
            if color_column:
                title += f" grouped by {color_column}"
            fig = px.scatter(df_plot, x=x_column, y=y_column, color=color_column or 'is_missing', title=title,
                             color_discrete_map={True: 'red', False: 'blue'} if not color_column else None)
            yaxis_title = y_label()
            
        elif chart_type == 'pie':
            df_plot = df.copy()
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            df_plot[y_col] = df_plot[y_col].fillna("Missing")
            title = f"Pie Chart for {y_col} by {x_column}"
            fig = px.pie(df_plot, names=x_column, values=y_col, title=title)
            yaxis_title = y_col
            
        elif chart_type == 'histogram':
            df_plot = df.copy()
            df_plot[x_column] = df_plot[x_column].fillna("Missing")
            title = f"Histogram Chart for {x_column}"
            fig = px.histogram(df_plot, x=x_column, title=title)
            yaxis_title = "Count"
            
        elif chart_type == 'box':
            df_plot = df.copy()
            df_plot['is_missing'] = df_plot[y_column[0] if isinstance(y_column, list) else y_column].isna()
            title = f"Box Chart for {y_label()} by {x_column}"
            if color_column:
                title += f" grouped by {color_column}"
            fig = px.box(df_plot, x=x_column, y=y_column, color=color_column or 'is_missing', title=title,
                         color_discrete_map={True: 'red', False: 'blue'} if not color_column else None)
            yaxis_title = y_label()
            
        elif chart_type == 'heatmap':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            pivot_df = df.pivot_table(index=x_column, columns=y_col, aggfunc='size', fill_value=0)
            title = f"Heatmap for {x_column} vs {y_col}"
            fig = px.imshow(pivot_df, title=title)
            yaxis_title = y_col
            
        else:
            df_plot = df.copy()
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, x=x_column, y=y_column, color=color_column, barmode='group', title=title)
                yaxis_title = y_label()
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, x=x_column, y=y_column, color=color_column, title=title)
                yaxis_title = y_label()

        # Update layout to better handle missing values
        fig.update_layout(
            showlegend=True,
            legend_title_text='Group' if color_column else 'Missing Values',
            xaxis_title=x_column,
            yaxis_title=yaxis_title,
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True)
        )

        return fig
    except Exception as e:
        raise Exception(f"Error generating chart: {str(e)}") 