
import pandas
import geopandas as gpd
import matplotlib.pyplot as plt


def import_data(filename):
	return pandas.read_csv(filename)


def import_map(filename):
	return gpd.read_file(filename)


def create_graph(map, name="Plot"):
	"""
	legend=True, column='margin', cmap='Crimes Per Thousand'
	"""

	fig, ax = plt.subplots(1)

	figsize = (6.4, 4.8)
	s = 2
	map.plot(ax=ax, color='#bababa')
	map.plot(ax=ax, column='POPESTIMATE2018', legend=True, linewidth=10, figsize=(s * figsize[0], s * figsize[1]))
	
	plt.xlabel('This is the longitude')
	plt.ylabel('This is the latitude')
	plt.title("This is a graph with resolution of 400 dpi")
	plt.axis([-128, -64, 22, 52])
	plt.savefig(name + '.png', dpi=800)


def convert_columns_to_floats(data, columns=[]):
	for col in columns:
		data[col] = data[col].str.replace(',', '').astype(float)


def main():
	print('Importing Data')
	washington_map = import_map('./src/washington.json')
	county_map = import_map('./src/data/5m-US-counties.json')
	crime_data = import_data('./src/data/US_Offense_Type_by_Agency_2018-trim.csv')
	pop_data = pandas.read_csv('./src/data/popest2018-trim.csv', encoding='latin-1')

	# Regularize the data
	convert_columns_to_floats(crime_data, ['Total Offenses', 'Population1'])
	agency_type_county = crime_data['Agency Type'].str.lower().str.contains("count")
	crime_data = crime_data[agency_type_county]

	# pop_data['CTYNAME'] = pop_data['CTYNAME'].astype(str)
	# print('as string', pop_data, '\n\n\n')
	county_county = pop_data['CTYNAME'].str.lower().str.contains("count")
	pop_data = pop_data[county_county]
	# print('remove cities', county_county, '\n\n\n')
	pop_data['CTYNAME'] = pop_data['CTYNAME'].str.replace(' County', '')
	# print('remove county word', pop_data, '\n\n\n')

	# print(crime_data.loc[:, 'Agency Name'])
	# print(county_map.loc[:, 'NAME'])
	# print(pop_data.loc[:, 'CTYNAME'])

	crime_data['test_crime'] = -1
	pop_data['test_pop'] = 0
	county_map['test_map'] = 1

	merged_data = pop_data.merge(crime_data, left_on='CTYNAME', right_on='Agency Name', how='outer')

	pandas.set_option('display.max_rows', 500)
	pandas.set_option('display.max_columns', 500)

	# print(washington_map)
	print('merged_data', merged_data)

	merged_map = county_map.merge(merged_data, left_on='NAME', right_on='CTYNAME', how='left')

	print('merged_map', merged_map)

	# Find the number of crimes per 1,000 people by coutny
	# merged['Crimes Per Thousand'] = 1000 * crime_data['Total Offenses'] / crime_data['Population1']

	"""
	county_map columns: ['id', 'STATEFP', 'COUNTYFP', 'COUNTYNS', 'AFFGEOID', 'GEOID', 'NAME', 'LSAD', 'ALAND', 'AWATER', 'geometry']
	crime_data columns: ['State', 'Agency Type', 'Agency Name,' 'Population1', 'Total Offenses', ...]
	
	Info:
	
	washington_map length: 39
	county_map length: 3233
	
	crime_data length: 5962
		regularized length: 1184
	pop_data length: 3193
		regularized length: 3007
	merged_data length: 6540
		
	counties: 1184

	ARIZONA Crimes Per Thousand: 47.934547
	"""
	
	# create_graph(merged_map)
	
	print('Finished.')


if __name__ == "__main__":
	main()
