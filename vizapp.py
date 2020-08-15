# Imports
from bokeh.plotting import figure
from bokeh.io import output_notebook, output_file, show, curdoc,save
from bokeh.models import GeoJSONDataSource, LinearColorMapper, \
ColorBar, NumeralTickFormatter, HoverTool, Select, ColumnDataSource,WheelZoomTool
from bokeh.layouts import layout
from bokeh.transform import factor_cmap
from bokeh.palettes import brewer,d3,inferno,viridis,cividis,mpl,Spectral6,magma
from bokeh.themes import built_in_themes
import geopandas as gp
import pandas as pd
import json

# Read the new 2019 census
latest_census = pd.read_csv('kenya_population_by_sex_and_county.csv')
latest_census.head()

# Read the shapefile
shapefile = 'Shapefile/ke_county.shp'
geofile = gp.read_file(shapefile)
geofile = geofile.rename(columns={'pop 2009': 'pop2009'})
geofile = geofile.sort_values(by='gid')

# Read the csv
# covid_data = pd.read_csv('covid_counties.csv', index_col=False)

# read csv of covid numbers into dataframe 
df_covid = pd.read_csv('corona_ke.csv')

# create a merged dataframe for the geofile dataframe and covid cases csv
merged = pd.merge(geofile,df_covid[['county', 'covid_num']], on='county')

# comprehensive data, merge the tables and use a left join to preserve the state of the merged df
comp_merged = pd.merge(merged,latest_census[['county','Male','Female','Intersex','Total']], on='county',how='left')

#comp_merged.dropna

# Read the data to json
merged_json = json.loads(comp_merged.to_json())

# convert to string like object
json_data = json.dumps(merged_json)

# Input GeoJSON source that contains features for plotting
geosource = GeoJSONDataSource(geojson=json_data) 

# Define a sequential multi-hue color palette.
palette = magma(50)

# Reverse colour order so that blue is for the highest density
palette = palette[::-1]

# Add Hover tool
hover = HoverTool(tooltips=[
    ('County','@county'),
    ('COVID-19 CASES','@covid_num'),
    ('Population 2019','@Total'),
    ('Male','@Male'),
    ('Female','@Female'),
    ('Intersex','@Intersex')
]
)

# Instantiate LinearColorMapper that maps numbers in a range into a sequence of colors
color_mapper = LinearColorMapper(palette=palette, low=0, high=10000)

# Create the color bar. 
color_bar = ColorBar(
    color_mapper=color_mapper,
    label_standoff=10,
    width=600,
    height=20,
    border_line_color=None,
    location = (0, 0), # major_label_overrides=tick_labels,
    orientation='horizontal')

# Create the figure object
p = figure(
    title='COVID-19 cases distribution per county Kenya (as of 23th April 2020). Hover/tap to view County details.',
    plot_height=1500,
    plot_width=1200,
    toolbar_location='right'
    )
p.xgrid.grid_line_color = None
p.xgrid.grid_line_color = None
p.sizing_mode = "scale_both"
p.background_fill_color= "aqua"
p.title.text_color = "teal"
p.title.text_font = "times"
p.title.text_font_style = "bold italic"
p.title.text_font_size = "27px"

# Add patch renderer to figure.
p.patches('xs', 'ys', source=geosource, 
    fill_color={'field':'covid_num','transform': color_mapper},
    line_color='black',
    line_width=0.25,
    fill_alpha=1
)

# Specify the figure of the layout.
p.add_layout(color_bar, 'below',)

# Add tools to the map
p.add_tools(hover)

# Initialize document to draw on

curdoc().add_root(p)

## Display figure inline in the Notebook
# output_notebook()

## Display figure 
# show(p)

# Read the data
ke_stats = pd.read_csv('covid_ke_stats.csv')

# Save graph in html when using a notebook
# output_file('kenyan_stats_covid.html')

# get the column values
Cases = ke_stats.columns.values

# get row values
numbers = list(ke_stats.iloc[0])

# Read to a form bokeh understands; to draw plots
source = ColumnDataSource(data=dict(Cases=Cases, numbers=numbers))

# plot the graph
p1 = figure(
    x_range=Cases,
    plot_height=1000,
    toolbar_location='right',
    title="COVID-19 CASES as at 15 August 2020",
    tools='hover',
    tooltips="@Cases: @numbers"
    )
p1.vbar(
    x='Cases',
    top='numbers',
    width=1,
    source=source,
    legend_field='Cases',
    line_color='white',
    fill_color=factor_cmap('Cases',
    palette=Spectral6,
    factors=Cases)
    )

p1.xgrid.grid_line_color = None
p1.y_range.start = 0 
p1.y_range.end = 400000
p1.legend.orientation = "vertical"
p1.legend.location = "top_right"
p1.background_fill_color = "beige"
p1.sizing_mode ="scale_both"
p1.title.text_color = "teal"
p1.title.text_font = "times"
p1.title.text_font_style = "bold italic"
p1.title.text_font_size = "27px"

# Combine the two figures into one display
z = layout([p],[p1])

# Initialize document to draw on
curdoc().add_root(z)

# Create a standalone HTML file with JS code included in 'inline' mode
output_file('covidke_data.html', title="COVID-KE data Kenya", mode='inline')
save(z)