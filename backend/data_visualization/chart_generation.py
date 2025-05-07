import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.interpolate import griddata

def generate_chart(df, x_column, y_column, chart_type='bar', color_column=None, sort_order='asc', custom_order=None):
    """
    Generate different types of charts based on the selected chart type.
    Handles missing values appropriately for each chart type.
    
    Args:
        df (pd.DataFrame): The input dataframe
        x_column (str): Column name for x-axis
        y_column (str/list): Column name(s) for y-axis
        chart_type (str): Type of chart to generate
        color_column (str): Column name for grouping
        sort_order (str): Sort order for the chart
        custom_order (str): Custom order for categoricals
        
    Returns:
        plotly.graph_objects.Figure: The generated chart figure
        
    Raises:
        ValueError: If the specified columns are not found in the dataframe
    """
    # Validate columns
    if x_column not in df.columns:
        raise ValueError(f"Column '{x_column}' not found in dataset")

    # Special validation for 3D and bubble charts
    if chart_type in ['scatter_3d', 'surface_3d', 'line_3d', 'mesh_3d']:
        if not isinstance(y_column, list) or len(y_column) != 2:
            raise ValueError(f"{chart_type} requires exactly 2 numeric columns for Y and Z axes")
        for col in y_column:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in dataset")
            if not np.issubdtype(df[col].dtype, np.number):
                raise ValueError(f"Column '{col}' must be numeric for {chart_type}")
    elif chart_type == 'bubble':
        if not isinstance(y_column, list) or len(y_column) != 2:
            raise ValueError("Bubble chart requires exactly 2 numeric columns: Y-axis and bubble size")
        for col in y_column:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in dataset")
            if not np.issubdtype(df[col].dtype, np.number):
                raise ValueError(f"Column '{col}' must be numeric for bubble chart")
    elif isinstance(y_column, list):
        for col in y_column:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in dataset")
    elif y_column not in df.columns and chart_type not in ['histogram', 'pie', 'treemap', 'sunburst']:
        raise ValueError(f"Column '{y_column}' not found in dataset")

    if color_column and color_column not in df.columns:
        raise ValueError(f"Column '{color_column}' not found in dataset")

    def y_label():
        if isinstance(y_column, list):
            return ', '.join(y_column)
        return y_column

    # Data preprocessing: custom order for categoricals
    df_plot = df.copy()
    if custom_order:
        order_list = [x.strip() for x in custom_order.split(',')]
        df_plot[x_column] = pd.Categorical(df_plot[x_column], categories=order_list, ordered=True)
    # Always sort by X (and group) columns
    sort_cols = [x_column]
    if color_column:
        sort_cols.append(color_column)
    df_plot = df_plot.sort_values(by=sort_cols, ascending=(sort_order == 'asc'))

    # Generate chart based on selected type
    try:
        if chart_type == 'bar':
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
            df_plot['is_missing'] = df_plot[y_column[0] if isinstance(y_column, list) else y_column].isna()
            title = f"Scatter Chart for {y_label()} by {x_column}"
            if color_column:
                title += f" grouped by {color_column}"
            fig = px.scatter(df_plot, x=x_column, y=y_column, color=color_column or 'is_missing', title=title,
                             color_discrete_map={True: 'red', False: 'blue'} if not color_column else None)
            yaxis_title = y_label()
            
        elif chart_type == 'pie':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            df_plot[y_col] = df_plot[y_col].fillna("Missing")
            title = f"Pie Chart for {y_col} by {x_column}"
            fig = px.pie(df_plot, names=x_column, values=y_col, title=title)
            yaxis_title = y_col
            
        elif chart_type == 'histogram':
            df_plot[x_column] = df_plot[x_column].fillna("Missing")
            title = f"Histogram Chart for {x_column}"
            fig = px.histogram(df_plot, x=x_column, title=title)
            yaxis_title = "Count"
            
        elif chart_type == 'box':
            df_plot['is_missing'] = df_plot[y_column[0] if isinstance(y_column, list) else y_column].isna()
            title = f"Box Chart for {y_label()} by {x_column}"
            if color_column:
                title += f" grouped by {color_column}"
            fig = px.box(df_plot, x=x_column, y=y_column, color=color_column or 'is_missing', title=title,
                         color_discrete_map={True: 'red', False: 'blue'} if not color_column else None)
            yaxis_title = y_label()
            
        elif chart_type == 'heatmap':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            pivot_df = df_plot.pivot_table(index=x_column, columns=y_col, aggfunc='size', fill_value=0)
            title = f"Heatmap for {x_column} vs {y_col}"
            fig = px.imshow(pivot_df, title=title)
            yaxis_title = y_col
            
        elif chart_type == 'contour':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            title = f"Contour Plot for {y_col} by {x_column}"
            fig = px.density_contour(df_plot, x=x_column, y=y_col, title=title)
            if color_column:
                fig.update_traces(contours_coloring="fill")
            yaxis_title = y_col

        elif chart_type == 'density_heatmap':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            title = f"Density Heatmap for {y_col} by {x_column}"
            fig = px.density_heatmap(df_plot, x=x_column, y=y_col, title=title)
            yaxis_title = y_col

        elif chart_type == 'polar':
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Polar Chart for {y_label()} by {x_column}"
                fig = px.line_polar(df_plot, r=y_column, theta=x_column, color=color_column, line_close=True, title=title)
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Polar Chart for {y_label()} by {x_column}"
                fig = px.line_polar(df_plot, r=y_column, theta=x_column, color=color_column, line_close=True, title=title)
            yaxis_title = y_label()

        elif chart_type == 'radar':
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Radar Chart for {y_label()} by {x_column}"
                fig = go.Figure()
                for col in y_column:
                    fig.add_trace(go.Scatterpolar(
                        r=df_plot[col],
                        theta=df_plot[x_column],
                        name=col,
                        fill='toself'
                    ))
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Radar Chart for {y_label()} by {x_column}"
                fig = go.Figure(go.Scatterpolar(
                    r=df_plot[y_column],
                    theta=df_plot[x_column],
                    fill='toself'
                ))
            fig.update_layout(title=title)
            yaxis_title = y_label()

        elif chart_type == 'parallel_coordinates':
            if isinstance(y_column, list):
                dimensions = [dict(range=[df_plot[col].min(), df_plot[col].max()],
                                 label=col, values=df_plot[col]) for col in y_column]
                dimensions.insert(0, dict(range=[df_plot[x_column].min(), df_plot[x_column].max()],
                                       label=x_column, values=df_plot[x_column]))
                title = f"Parallel Coordinates for {y_label()} with {x_column}"
                fig = go.Figure(data=go.Parcoords(
                    line=dict(color=df_plot[color_column] if color_column else df_plot[y_column[0]]),
                    dimensions=dimensions
                ))
            else:
                dimensions = [
                    dict(range=[df_plot[x_column].min(), df_plot[x_column].max()],
                         label=x_column, values=df_plot[x_column]),
                    dict(range=[df_plot[y_column].min(), df_plot[y_column].max()],
                         label=y_column, values=df_plot[y_column])
                ]
                title = f"Parallel Coordinates for {y_label()} with {x_column}"
                fig = go.Figure(data=go.Parcoords(
                    line=dict(color=df_plot[color_column] if color_column else df_plot[y_column]),
                    dimensions=dimensions
                ))
            fig.update_layout(title=title)
            yaxis_title = y_label()

        elif chart_type == 'parallel_categories':
            cols_to_use = [x_column]
            if isinstance(y_column, list):
                cols_to_use.extend(y_column)
            else:
                cols_to_use.append(y_column)
            if color_column:
                cols_to_use.append(color_column)
            
            title = f"Parallel Categories for {y_label()} with {x_column}"
            fig = px.parallel_categories(df_plot, dimensions=cols_to_use, title=title)
            yaxis_title = y_label()

        elif chart_type == 'scatter_3d':
            if isinstance(y_column, list) and len(y_column) >= 2:
                z_col = y_column[1]
                y_col = y_column[0]
                title = f"3D Scatter Plot for {y_col} vs {z_col} by {x_column}"
                fig = px.scatter_3d(df_plot, x=x_column, y=y_col, z=z_col,
                                  color=color_column, title=title)
                yaxis_title = y_col
            else:
                raise ValueError("3D Scatter Plot requires at least 2 numeric columns for Y and Z axes")

        elif chart_type == 'surface_3d':
            if isinstance(y_column, list) and len(y_column) >= 2:
                z_col = y_column[1]
                y_col = y_column[0]
                
                # Validate numeric columns
                for col in [x_column, y_col, z_col]:
                    if not np.issubdtype(df_plot[col].dtype, np.number):
                        raise ValueError(f"Column '{col}' must be numeric for 3D Surface Plot")
                
                # Handle duplicate points by averaging z values
                df_grouped = df_plot.groupby([x_column, y_col])[z_col].mean().reset_index()
                
                # Create evenly spaced x and y values
                x_unique = np.linspace(df_grouped[x_column].min(), df_grouped[x_column].max(), 100)
                y_unique = np.linspace(df_grouped[y_col].min(), df_grouped[y_col].max(), 100)
                x_mesh, y_mesh = np.meshgrid(x_unique, y_unique)
                
                # Interpolate z values for smoother surface
                points = df_grouped[[x_column, y_col]].values
                z_values = df_grouped[z_col].values
                z_mesh = griddata(points, z_values, (x_mesh, y_mesh), method='cubic', fill_value=np.nan)
                
                # Create the surface plot
                fig = go.Figure(data=[go.Surface(
                    x=x_mesh,
                    y=y_mesh,
                    z=z_mesh,
                    colorscale='Viridis',
                    showscale=True,
                    lighting=dict(
                        ambient=0.8,
                        diffuse=0.9,
                        fresnel=0.2,
                        specular=1,
                        roughness=0.5
                    ),
                    contours=dict(
                        x=dict(show=True, color='rgba(0,0,0,0.3)', width=1),
                        y=dict(show=True, color='rgba(0,0,0,0.3)', width=1),
                        z=dict(show=True, color='rgba(0,0,0,0.3)', width=1)
                    )
                )])
                
                title = f"3D Surface Plot for {z_col} by {x_column} and {y_col}"
                fig.update_layout(
                    title=title,
                    scene=dict(
                        camera=dict(
                            up=dict(x=0, y=0, z=1),
                            center=dict(x=0, y=0, z=0),
                            eye=dict(x=1.5, y=1.5, z=1.5)
                        ),
                        aspectmode='cube',
                        xaxis_title=x_column,
                        yaxis_title=y_col,
                        zaxis_title=z_col,
                        xaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True),
                        zaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True)
                    ),
                    margin=dict(l=0, r=0, t=40, b=0),
                    autosize=True
                )
                yaxis_title = y_col
            else:
                raise ValueError("3D Surface Plot requires exactly 2 numeric columns for Y and Z axes")

        elif chart_type == 'line_3d':
            if isinstance(y_column, list) and len(y_column) >= 2:
                z_col = y_column[1]
                y_col = y_column[0]
                title = f"3D Line Plot for {y_col} vs {z_col} by {x_column}"
                fig = px.line_3d(df_plot, x=x_column, y=y_col, z=z_col,
                               color=color_column, title=title)
                yaxis_title = y_col
            else:
                raise ValueError("3D Line Plot requires at least 2 numeric columns for Y and Z axes")

        elif chart_type == 'mesh_3d':
            if isinstance(y_column, list) and len(y_column) >= 2:
                z_col = y_column[1]
                y_col = y_column[0]
                # Create a mesh using a pivot table
                pivot_table = df_plot.pivot(index=x_column, columns=y_col, values=z_col)
                x_mesh, y_mesh = np.meshgrid(pivot_table.index, pivot_table.columns)
                title = f"3D Mesh Plot for {z_col} by {x_column} and {y_col}"
                fig = go.Figure(data=[go.Mesh3d(x=x_mesh.flatten(),
                                              y=y_mesh.flatten(),
                                              z=pivot_table.values.flatten(),
                                              intensity=pivot_table.values.flatten(),
                                              colorscale='Viridis')])
                fig.update_layout(title=title)
                yaxis_title = y_col
            else:
                raise ValueError("3D Mesh Plot requires at least 2 numeric columns for Y and Z axes")

        elif chart_type == 'stacked_bar':
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Stacked Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, x=x_column, y=y_column, color=color_column, barmode='stack', title=title)
                yaxis_title = y_label()
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Stacked Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, x=x_column, y=y_column, color=color_column, barmode='stack', title=title)
                yaxis_title = y_label()

        elif chart_type == 'horizontal_bar':
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Horizontal Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, y=x_column, x=y_column, color=color_column, barmode='group', 
                           orientation='h', title=title)
                yaxis_title = x_column
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Horizontal Bar Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.bar(df_plot, y=x_column, x=y_column, color=color_column, 
                           orientation='h', title=title)
                yaxis_title = x_column

        elif chart_type == 'area':
            if isinstance(y_column, list):
                for col in y_column:
                    df_plot[col] = df_plot[col].fillna(0)
                title = f"Area Chart for {y_label()} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.area(df_plot, 
                            x=x_column, 
                            y=y_column,
                            color=color_column,
                            title=title,
                            groupnorm='percent' if len(y_column) > 1 else None)
                yaxis_title = y_label()
            else:
                df_plot[y_column] = df_plot[y_column].fillna(0)
                title = f"Area Chart for {y_column} by {x_column}"
                if color_column:
                    title += f" grouped by {color_column}"
                fig = px.area(df_plot, 
                            x=x_column, 
                            y=y_column,
                            color=color_column,
                            title=title)
                yaxis_title = y_column

        elif chart_type == 'violin':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            title = f"Violin Plot for {y_col} by {x_column}"
            if color_column:
                title += f" grouped by {color_column}"
            fig = px.violin(df_plot, x=x_column, y=y_col, color=color_column, box=True, title=title)
            yaxis_title = y_col

        elif chart_type == 'treemap':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            title = f"Treemap for {y_col} by {x_column}"
            if color_column:
                fig = px.treemap(df_plot, path=[color_column, x_column], values=y_col, title=title)
            else:
                fig = px.treemap(df_plot, path=[x_column], values=y_col, title=title)
            yaxis_title = y_col

        elif chart_type == 'sunburst':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            title = f"Sunburst Chart for {y_col} by {x_column}"
            if color_column:
                fig = px.sunburst(df_plot, path=[color_column, x_column], values=y_col, title=title)
            else:
                fig = px.sunburst(df_plot, path=[x_column], values=y_col, title=title)
            yaxis_title = y_col

        elif chart_type == 'funnel':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            df_funnel = df_plot.groupby(x_column)[y_col].sum().reset_index()
            df_funnel = df_funnel.sort_values(y_col, ascending=True)
            
            fig = go.Figure(go.Funnel(
                y=df_funnel[x_column],
                x=df_funnel[y_col],
                textinfo="value+percent initial"
            ))
            fig.update_layout(title=f"Funnel Chart for {y_col} by {x_column}")
            yaxis_title = y_col

        elif chart_type == 'waterfall':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            df_waterfall = df_plot.groupby(x_column)[y_col].sum().reset_index()
            
            # Calculate the cumulative sum for measure
            measure = ['relative'] * len(df_waterfall)
            measure[-1] = 'total'
            
            fig = go.Figure(go.Waterfall(
                name="Waterfall",
                orientation="v",
                measure=measure,
                x=df_waterfall[x_column],
                y=df_waterfall[y_col],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))
            fig.update_layout(title=f"Waterfall Chart for {y_col} by {x_column}")
            yaxis_title = y_col

        elif chart_type == 'donut':
            y_col = y_column[0] if isinstance(y_column, list) else y_column
            df_plot[y_col] = df_plot[y_col].fillna("Missing")
            title = f"Donut Chart for {y_col} by {x_column}"
            fig = px.pie(df_plot, names=x_column, values=y_col, title=title, hole=0.4)
            yaxis_title = y_col

        elif chart_type == 'bubble':
            if not isinstance(y_column, list) or len(y_column) != 2:
                raise ValueError("Bubble chart requires exactly 2 numeric columns: Y-axis and bubble size")
            
            y_col = y_column[0]  # First column for Y-axis
            size_col = y_column[1]  # Second column for bubble size
            
            # Validate numeric columns
            for col in [y_col, size_col]:
                if not np.issubdtype(df[col].dtype, np.number):
                    raise ValueError(f"Column '{col}' must be numeric for bubble chart")
            
            title = f"Bubble Chart for {y_col} vs {x_column} (size: {size_col})"
            if color_column:
                title += f" grouped by {color_column}"
            
            fig = px.scatter(df_plot, 
                           x=x_column, 
                           y=y_col,
                           size=size_col,
                           color=color_column,
                           title=title,
                           hover_data=[size_col])
            yaxis_title = y_col

        # Update layout to better handle missing values
        fig.update_layout(
            showlegend=True,
            legend_title_text='Group' if color_column else 'Missing Values',
            xaxis_title=x_column if chart_type not in ['horizontal_bar'] else y_label(),
            yaxis_title=yaxis_title,
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            width=1000,
            height=700,
            margin=dict(
                l=50,
                r=50,
                b=50,
                t=100,
                pad=4
            ),
            scene=dict(
                camera=dict(
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0),
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            ) if chart_type in ['scatter_3d', 'surface_3d', 'line_3d', 'mesh_3d'] else None
        )

        return fig
    except Exception as e:
        raise Exception(f"Error generating chart: {str(e)}") 