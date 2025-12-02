import datetime
from covid import Covid
import matplotlib
matplotlib.use('Agg')  # Must be set before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import gc
import json
import csv

from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_caching import Cache

app = Flask(__name__)
covid = Covid()

# Configure cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route("/")
def root():
    routes = [
        {
            'path': '/regional',
            'name': 'Regional Analysis',
            'description': 'Compare key COVID statistics between the main regions across the globe'
        },
        {
            'path': '/country/world',
            'name': 'World COVID Statistics',
            'description': 'View detailed COVID statistics for the entire globe'
        },
        {
            'path': '/country/usa',
            'name': 'USA COVID Statistics',
            'description': 'View detailed COVID statistics for the USA'
        },
        {
            'path': '/country/china',
            'name': 'China COVID Statistics',
            'description': 'View detailed COVID statistics for China'
        },
        {
            'path': '/country/mexico',
            'name': 'Mexico COVID Statistics',
            'description': 'View detailed COVID statistics for Mexico'
        },
        {
            'path': '/country/russia',
            'name': 'Russia COVID Statistics',
            'description': 'View detailed COVID statistics for Russia'
        },
        {
            'path': '/search',
            'name': 'Search Country',
            'description': 'Search for any country COVID statistics'
        },
    ]
    
    return render_template("index.html", routes=routes)

@app.route("/regional")
@cache.cached(timeout=300)  # Cache for 5 minutes
def covid_comparison_regional():
    try:
        n_america = covid.get_status_by_country_name("north america")
        asia = covid.get_status_by_country_name("asia")
        eu = covid.get_status_by_country_name("europe")
        s_america = covid.get_status_by_country_name("south america")
        oceania = covid.get_status_by_country_name("oceania")
        africa = covid.get_status_by_country_name("africa")
        
        # Extract data
        regions = [n_america['country'], asia['country'], eu['country'], s_america['country'], oceania['country'], africa['country']]
        confirmed = [n_america['confirmed'], asia['confirmed'], eu['confirmed'], s_america['confirmed'], oceania['confirmed'], africa['confirmed']]
        deaths = [n_america['deaths'], asia['deaths'], eu['deaths'], s_america['deaths'], oceania['deaths'], africa['deaths']]
        recovered = [n_america['recovered'], asia['recovered'], eu['recovered'], s_america['recovered'], oceania['recovered'], africa['recovered']]
        
        # Create the plot
        img = create_compcovid_plot(regions, confirmed, deaths, recovered)
        
        # Convert plot to base64 for embedding in HTML
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

         # Force cleanup
        del img
        gc.collect()
        
        return render_template('regional.html', 
                             chart_image=img_base64,
                             countries=regions,
                             n_america_data=n_america,
                             asia_data=asia,
                             eu_data=eu,
                             s_america_data=s_america,
                             oceania_data=oceania,
                             africa_data=africa)
    
    except Exception as e:
        return f"Error fetching COVID data: {str(e)}"

def create_compcovid_plot(countries, confirmed, deaths, recovered):
    # Set up the plot
    x = np.arange(len(countries))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    # Create bars for each category
    bars1 = ax.bar(x - width, confirmed, width, label='Confirmed', color='#1f77b4', alpha=0.8)
    bars2 = ax.bar(x, deaths, width, label='Deaths', color='#d62728', alpha=0.8)
    bars3 = ax.bar(x + width, recovered, width, label='Recovered', color='#2ca02c', alpha=0.8)

    # Customize the chart
    ax.set_xlabel('Regions', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Cases (millions)', fontsize=12, fontweight='bold')
    ax.set_title('COVID: Regional Analysis', fontsize=16, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(countries, fontsize=12)
    ax.legend(fontsize=11)

    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=6, fontweight='bold')

    add_value_labels(bars1)
    add_value_labels(bars2)
    add_value_labels(bars3)

    # Adjust y-axis to accommodate the highest value
    plt.ylim(0, max(confirmed) * 1.15)

    # Add grid for better readability
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')

    plt.tight_layout()
    
    # Save plot to bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()  # Close the figure to free memory
    plt.close('all')
    gc.collect()
    
    return img_buffer

def create_sc_plt_donut(country_data):
    # Extract data
    country_name = country_data['country']
    
    # Set up the plot - single subplot now
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create donut chart with all categories
    pie_categories = ['Active', 'Critical', 'Deaths', 'Recovered']
    pie_values = [
        country_data['active'],
        country_data['critical'],
        country_data['deaths'],
        country_data['recovered']
    ]
    pie_colors = ['#ff7f0e', '#d62728', '#2ca02c', '#9467bd']
    
    # Only show donut chart if there are values to display
    if sum(pie_values) > 0:
        # Calculate percentages
        total = sum(pie_values)
        
        # Create donut chart
        wedges, _, autotexts = ax.pie(pie_values, colors=pie_colors, startangle=90,
                                         autopct=lambda pct: f'{pct:.1f}%' if pct >= 1 else '',
                                         textprops={'fontsize': 10},
                                         wedgeprops={'width': 0.6})  # This makes it a donut
        
        # Make autopct text white and bold for better visibility
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        # Add center text with total and country info
        center_circle = plt.Circle((0,0), 0.3, fc='white')
        ax.add_artist(center_circle)
        ax.text(0, 0.1, f'{country_name}', ha='center', va='center', 
                fontsize=14, fontweight='bold')
        ax.text(0, -0.1, f'Total Cases:\n{total:,}', ha='center', va='center', 
                fontsize=11, fontweight='bold')
        
        # Create a legend with all statistics
        legend_labels = []
        for cat, val in zip(pie_categories, pie_values):
            legend_labels.append(f'{cat}: {val:,}')
        
        # Add confirmed cases to legend since it's not in the donut
        legend_labels.append(f"Confirmed: {country_data['confirmed']:,}")
        
        ax.legend(wedges, legend_labels,
                 title="COVID Statistics",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1),
                 fontsize=10)
        
    else:
        # If no data, show a message
        ax.text(0.5, 0.5, f'No data available\nfor {country_name}', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=14, fontweight='bold')
        ax.set_title(f'COVID-19 Statistics: {country_name}', fontsize=16, fontweight='bold')
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    # Save plot to bytes buffer
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close(fig)  # Close the figure to free memory
    plt.close('all')
    gc.collect()
    
    return img_buffer

@app.route("/country/<country_name>")
@cache.cached(timeout=300)  # Cache for 5 minutes
def country_stats(country_name):
    try:
        country_data = covid.get_status_by_country_name(country_name.lower())
        
        # Create the plot
        img = create_sc_plt_donut(country_data)
        
        # Convert plot to base64 for embedding in HTML
        img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

        # Force cleanup
        del img
        gc.collect()
        
        return render_template('c_stats.html', 
                             chart_image=img_base64,
                             country_data=country_data)
    
    except Exception as e:
        return f"Error fetching COVID data for {country_name}: {str(e)}"

@app.route("/search", methods=["GET", "POST"])
def search_country():
    if request.method == "POST":
        country_name = request.form.get("country_name", "").strip().lower()
        if not country_name:
            return render_template("search.html", error="Please enter a country name")
        
        try:
            # Try to get the country data
            country_data = covid.get_status_by_country_name(country_name)
            return redirect(url_for('country_stats', country_name=country_name))
        except Exception as e:
            # Get all available countries
            all_countries = covid.list_countries()
            matching_countries = [
                country for country in all_countries 
                if country_name in country['name'].lower()
            ]
            return render_template('search_results.html', 
                                 search_term=country_name,
                                 countries=matching_countries)
    return render_template("search.html")

@app.route("/export/<country_name>/<format>")
def export_data(country_name, format):
    try:
        country_data = covid.get_status_by_country_name(country_name.lower())
        
        if format == 'csv':
            # Create CSV response
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Statistic', 'Value'])
            for key, value in country_data.items():
                if key != 'country':  # Already in filename
                    writer.writerow([key.replace('_', ' ').title(), value])
            
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = f"attachment; filename={country_name}_covid_data.csv"
            response.headers["Content-type"] = "text/csv"
            return response
        
        elif format == 'json':
            response = make_response(json.dumps(country_data, indent=2))
            response.headers["Content-Disposition"] = f"attachment; filename={country_name}_covid_data.json"
            response.headers["Content-type"] = "application/json"
            return response
        else:
            return "Invalid format. Use 'csv' or 'json'", 400
    
    except Exception as e:
        return f"Error exporting data: {str(e)}", 500

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)