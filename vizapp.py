# Imports
from bokeh.plotting import figure
from bokeh.io import output_notebook, output_file, show, curdoc
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter, HoverTool, Select, ColumnDataSource
from bokeh.layouts import widgetbox, row,column
from bokeh.transform import factor_cmap
from bokeh.palettes import brewer,d3,inferno,viridis,cividis,mpl,Spectral6
from bokeh.themes import built_in_themes
import geopandas as gp
import pandas as pd
import json

def vizapp(doc):
    # Read the new 2019 census
    latest_census = pd.read_csv('kenya_population_by_sex_and_county.csv')
    latest_census.head()

    # Read the shapefile
    shapefile = 'Shapefile/ke_county.shp'

    geofile = gp.read_file(shapefile)
    geofile = geofile.rename(columns={'pop 2009': 'pop2009'})
    #print(geofile)

    geofile = geofile.sort_values(by='gid')
    #print(geofile)

    # Read the csv
    #covid_data = pd.read_csv('covid_counties.csv', index_col=False)
    #print(covid_data)

    # some data cleaning  and stuff
    # geofile_col = geofile[['county']]
    # col_names = ['Counties','Covid_nums']
    # replace_data = pd.read_csv('covid_counties.csv')
    # #print(replace_data)
    # covid_num = replace_data[['CovidCases']]
    # #print(covid_num)
    # # print(geofile_col)
    # #counties.to_csv('covid_counties.csv',index=False)
    # # dicty = {'counties':geofile_col,'covid_num':covid_num}
    # # print(dicty)
    # # counties = pd.DataFrame()
    # # print(counties)

    # covid_num.to_csv('covid_count_ke.csv', index=False)

    # csv_input = pd.read_csv('covid_in_ke.csv')
    # csv_input['covid_num'] = covid_num
    # csv_input.to_csv('corona_ke.csv', index=False)

    # filter covid numbers
    df_covid = pd.read_csv('corona_ke.csv')

    # create a merged dataframe for the geofile dataframe and covid cases csv
    merged = pd.merge(geofile,df_covid[['county', 'covid_num']], on='county')

    # comprehensive data
    comp_merged = pd.merge(merged,latest_census[['county','Male','Female','Intersex','Total']], on='county',how='left')
    #comp_merged.dropna

    # write to csv

    # Read the data to json
    merged_json = json.loads(comp_merged.to_json())

    # convert to string like object
    json_data = json.dumps(merged_json)


    # check dataframe
    #merged

    # Input GeoJSON source that contains features for plotting
    geosource = GeoJSONDataSource(geojson=json_data) 

    # Define a sequential multi-hue color palette.
    palette = viridis(80)

    # Reverse colour order so that blue is for the highest density
    palette = palette[::-1]

    # Add Hover tool
    hover = HoverTool(tooltips = [
        ('County','@county'),
        ('COVID-19 CASES','@covid_num'),
        ('Population 2019','@Total'),
        ('Male','@Male'),
        ('Female','@Female'),
        ('Intersex','@Intersex')
    ])

    # Instantiate LinearColorMapper that maps numbers in a range into a sequence of colors
    color_mapper = LinearColorMapper(palette=palette, low = 0, high = 80)

    # Define custom tick labels for color bar
    tick_labels  = {
        '0':'0',
        '10':'10',
        '20':'20',
        '30':'30',
        '40':'40',
        '50':'50',
        '60':'60',
        '70':'70',
        '80':'>80'   
    }

    # Create the color bar. 
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=10, width = 500, height = 20, border_line_color=None, location = (0, 0), major_label_overrides = tick_labels, orientation= 'horizontal')

    # Create the figure object
    p = figure(title = 'COVID-19 cases per county, Kenya 2020', plot_height= 1500, plot_width= 1200, toolbar_location = None)
    p.xgrid.grid_line_color = None
    p.xgrid.grid_line_color = None

    # Add patch renderer to figure.
    p.patches('xs', 'ys', source = geosource, fill_color = {
        'field':'covid_num',
        'transform': color_mapper},line_color='black',line_width=0.25, fill_alpha = 1
    )

    # Specify the figure of the layout.
    p.add_layout(color_bar, 'below')

    # Add hover 
    p.add_tools(hover)

    # Make acustom layout for the plot
    layout = column(p)
    curdoc().add_root(layout)

    # Display figure inline in the Notebook
    output_notebook()

    # Display figure 
    show(layout)



def cov_plot(bplot):
    # Read the data
    ke_stats = pd.read_csv('covid_ke_stats.csv')
    # Save graph in html
    output_file('kenyan_stats_covid.html')
    # get the column values
    Cases = ke_stats.columns.values
    # get row values
    numbers = list(ke_stats.iloc[0])
    # print(Cases)
    # print(numbers)

    source = ColumnDataSource(data=dict(Cases=Cases, numbers=numbers))

    # plot the graph
    p = figure(x_range=Cases, plot_height=600, toolbar_location=None, title="COVID-19 CASES as at 17 April 2020", tools='hover', tooltips="@Cases: @numbers")
    p.vbar(x='Cases', top='numbers',width=1, source=source, legend_field='Cases', line_color='white',fill_color=factor_cmap('Cases', palette=Spectral6, factors=Cases))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0 
    p.y_range.end = 11000
    p.legend.orientation = "vertical"
    p.legend.location = "top_right"

    bplot.add_root(p)
show(cov_plot)
