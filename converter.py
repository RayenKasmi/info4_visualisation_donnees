import pandas as pd

# 1. Load the data (adjust the filename to match yours)
# Most .data files use commas or spaces as separators. 
# 'sep=None' and 'engine=python' will automatically detect it.
df = pd.read_csv('./breast+cancer+wisconsin+diagnostic/wdbc.data', header=None, sep=None, engine='python')

# 2. Add the WDBC column names in the same order as the data file
df.columns = [
	'id', 'diagnosis',
	'radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean',
	'smoothness_mean', 'compactness_mean', 'concavity_mean',
	'concave_points_mean', 'symmetry_mean', 'fractal_dimension_mean',
	'radius_se', 'texture_se', 'perimeter_se', 'area_se',
	'smoothness_se', 'compactness_se', 'concavity_se',
	'concave_points_se', 'symmetry_se', 'fractal_dimension_se',
	'radius_worst', 'texture_worst', 'perimeter_worst', 'area_worst',
	'smoothness_worst', 'compactness_worst', 'concavity_worst',
	'concave_points_worst', 'symmetry_worst', 'fractal_dimension_worst'
]

# 3. Save to CSV
df.to_csv('converted_data.csv', index=False)

print("Conversion complete! Saved as 'converted_data.csv'")
