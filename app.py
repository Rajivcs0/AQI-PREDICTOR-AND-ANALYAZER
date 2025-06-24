

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

df = pd.read_csv("aqi_india.csv")

df

features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
target = 'AQI'
X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse:.2f}")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"R2 Score: {r2:.4f}")

plt.figure(figsize=(10, 6))
sns.scatterplot(x=y_test, y=y_pred, alpha=0.5)
plt.xlabel("Actual AQI")
plt.ylabel("Predicted AQI")
plt.title("Actual vs Predicted AQI")
plt.grid(True)
plt.savefig("aqi_prediction_plot.png")
plt.show()

##joblib.dump(model, "aqi_model.pkl")
##joblib.dump(scaler, "aqi_scaler.pkl")##

city_avg_aqi = df.groupby("City")["AQI"].mean().sort_values(ascending=False)

# Plotting
plt.figure(figsize=(12, 6))
sns.barplot(x=city_avg_aqi.index, y=city_avg_aqi.values, palette="coolwarm")

plt.title("Average AQI by City (Jan 2023 - May 2025)", fontsize=16)
plt.xlabel("City", fontsize=12)
plt.ylabel("Average AQI", fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()

# Save or show the plot
plt.savefig("average_aqi_by_city.png")  # Optional: saves the plot as an image
plt.show()

aqi_counts = df["AQI Level"].value_counts()

# Plot Pie Chart
colors = ['#66bb6a', '#cddc39', '#ffeb3b', '#ff9800', '#f44336', '#8e24aa']
plt.figure(figsize=(8, 8))
plt.pie(aqi_counts.values, labels=aqi_counts.index, autopct='%1.1f%%', startangle=140, colors=colors)
plt.title("AQI Level Distribution (Jan 2023 - May 2025)", fontsize=14)
plt.axis("equal")  # Equal aspect ratio ensures pie is a circle

# Save or show the chart
plt.savefig("aqi_level_distribution_pie.png")  # Optional
plt.show()

# Map AQI Level to colors
color_map = {
    "Good": "green",
    "Satisfactory": "yellowgreen",
    "Moderate": "gold",
    "Poor": "orange",
    "Very Poor": "red",
    "Severe": "purple"
}
colors = df["AQI Level"].map(color_map)

# Create a 3D scatter plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(df["PM2.5"], df["PM10"], df["AQI"],
                c=colors, s=20, alpha=0.6)

ax.set_xlabel("PM2.5 (µg/m³)")
ax.set_ylabel("PM10 (µg/m³)")
ax.set_zlabel("AQI")
ax.set_title("3D Visualization of AQI vs PM2.5 & PM10", fontsize=14)

# Custom legend
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', label=level,
                          markerfacecolor=clr, markersize=10)
                   for level, clr in color_map.items()]
ax.legend(handles=legend_elements, title="AQI Level", loc="best")

plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt

# Count of each AQI Level
aqi_counts = df["AQI Level"].value_counts()

# Pie chart
colors = ['#66bb6a', '#cddc39', '#ffeb3b', '#ff9800', '#f44336', '#8e24aa']
explode = [0.05] * len(aqi_counts)  # Explode all segments for a "3D" effect

plt.figure(figsize=(8, 8))
plt.pie(aqi_counts.values,
        labels=aqi_counts.index,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        explode=explode,
        shadow=True)
plt.title("AQI Level Distribution (3D-Style Pie)", fontsize=14)
plt.axis("equal")
plt.tight_layout()
plt.show()

from mpl_toolkits.mplot3d import Axes3D

# Group by city
city_avg = df.groupby("City")["AQI"].mean().sort_values()

# Bar chart data
cities = city_avg.index
aqi_vals = city_avg.values
x = np.arange(len(cities))
y = np.zeros_like(x)
z = np.zeros_like(x)
dx = np.ones_like(x)
dy = np.ones_like(x)
dz = aqi_vals

# Plot
fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(111, projection='3d')

ax.bar3d(x, y, z, dx, dy, dz, color='skyblue', shade=True)
ax.set_xticks(x)
ax.set_xticklabels(cities, rotation=45, ha='right')
ax.set_ylabel("Y-axis (not used)")
ax.set_zlabel("Average AQI")
ax.set_title("Average AQI by City (3D Bar Chart)", fontsize=14)
plt.tight_layout()
plt.show()


city_df = df[df["City"] == "Delhi"].copy()
city_df["Date"] = pd.to_datetime(city_df["Date"])
city_df.sort_values("Date", inplace=True)

# Plot line chart
plt.figure(figsize=(12, 6))
plt.plot(city_df["Date"], city_df["AQI"], label="Delhi AQI", color="teal")
plt.title("Delhi AQI Trend Over Time", fontsize=16)
plt.xlabel("Date")
plt.ylabel("AQI")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

city_avg = df.groupby("City")["AQI"].mean().sort_values()

# Plot
plt.figure(figsize=(12, 6))
sns.barplot(x=city_avg.index, y=city_avg.values, palette="Blues_r")
plt.xticks(rotation=45)
plt.title("Average AQI by City", fontsize=16)
plt.xlabel("City")
plt.ylabel("Average AQI")
plt.tight_layout()
plt.show()


features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3']
mumbai_avg = df[df["City"] == "Mumbai"][features].mean()

# Radar chart setup
labels = list(mumbai_avg.index)
values = mumbai_avg.values
angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
values = np.concatenate((values, [values[0]]))
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
ax.plot(angles, values, linewidth=2, linestyle='solid')
ax.fill(angles, values, alpha=0.25)
ax.set_thetagrids(np.degrees(angles[:-1]), labels)
ax.set_title("Mumbai – Pollution Profile Radar Chart")
plt.show()

plt.figure(figsize=(8, 6))
plt.scatter(df["PM2.5"], df["AQI"], alpha=0.5, c='teal')
plt.title("Scatter Plot: AQI vs PM2.5")
plt.xlabel("PM2.5")
plt.ylabel("AQI")
plt.grid(True)
plt.tight_layout()
plt.show()

import seaborn as sns

bubble_df = df.groupby("City")[["AQI", "PM10"]].mean().reset_index()

plt.figure(figsize=(10, 6))
plt.scatter(bubble_df["City"], bubble_df["AQI"],
            s=bubble_df["PM10"], alpha=0.6, c='skyblue')
plt.xticks(rotation=45)
plt.title("Bubble Chart: AQI vs City (Bubble size = PM10)")
plt.xlabel("City")
plt.ylabel("Average AQI")
plt.tight_layout()
plt.show()

aqi_counts = df["AQI Level"].value_counts()

print("\n📊 AQI Level Distribution (Pictorial)")
for level, count in aqi_counts.items():
    bar = '🟩' * (count // 500)  # scale down
    print(f"{level:<12}: {bar} ({count})")

df["Year"] = pd.to_datetime(df["Date"]).dt.year
top_cities = df["City"].value_counts().nlargest(5).index
grouped = df[df["City"].isin(top_cities)].groupby(["City", "Year"])["AQI"].mean().reset_index()

plt.figure(figsize=(12, 6))
sns.barplot(data=grouped, x="City", y="AQI", hue="Year", palette="Set2")
plt.title("Grouped Column Chart: AQI by City and Year")
plt.ylabel("Average AQI")
plt.tight_layout()
plt.show()

