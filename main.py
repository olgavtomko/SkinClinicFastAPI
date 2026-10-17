from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
import os

app = FastAPI(title="Skin Clinic Campaign Analysis")

def run_campaign_analysis():
    csv_path = "skin clinic campaign.csv"
    if not os.path.exists(csv_path):
        return {"error": "File not found"}
        
    df = pd.read_csv(csv_path)
    df['Response_Num'] = (df['Response_to_Campaign'].str.strip().str.lower() == 'yes').astype(int)

    # 1. Gender vs Campaign Response
    gender_df = df.groupby('Gender')['Response_Num'].agg(['count', 'sum', 'mean']).reset_index()
    gender_df['Response Rate (%)'] = (gender_df['mean'] * 100).round(2)
    gender_df.rename(columns={'count': 'Total Customers', 'sum': 'Responded'}, inplace=True)

    # 2. Age Group vs Campaign Response
    age_df = df.groupby('AgeGroup')['Response_Num'].agg(['count', 'sum', 'mean']).reset_index()
    age_df['Response Rate (%)'] = (age_df['mean'] * 100).round(2)
    age_df.rename(columns={'AgeGroup': 'Age Group', 'count': 'Total Customers', 'sum': 'Responded'}, inplace=True)

    # 3. Purchase in Last Quarter vs Campaign Response
    pq_df = df.groupby('Purchase_Last_Quarter')['Response_Num'].agg(['count', 'sum', 'mean']).reset_index()
    pq_df['Response Rate (%)'] = (pq_df['mean'] * 100).round(2)
    pq_df.rename(columns={'Purchase_Last_Quarter': 'Purchase Last Quarter', 'count': 'Total Customers', 'sum': 'Responded'}, inplace=True)

    # 4 Product Usage vs Campaign Response
    def categorize_prod(val):
        if val <= 4:
            return '1–4'
        elif val <= 8:
            return '5–8'
        else:
            return '>8'

    df['Product Category'] = df['Unique_Products_Purchased'].apply(categorize_prod)
    prod_df = df.groupby('Product Category')['Response_Num'].agg(['count', 'sum', 'mean']).reset_index()
    prod_df['Response Rate (%)'] = (prod_df['mean'] * 100).round(2)
    prod_df.rename(columns={'count': 'Total Customers', 'sum': 'Responded'}, inplace=True)
    
    category_order = ['1–4', '5–8', '>8']
    prod_df['Product Category'] = pd.Categorical(prod_df['Product Category'], categories=category_order, ordered=True)
    prod_df = prod_df.sort_values('Product Category')

    return {
        "gender": gender_df[['Gender', 'Total Customers', 'Responded', 'Response Rate (%)']].to_dict(orient="records"),
        "age_group": age_df[['Age Group', 'Total Customers', 'Responded', 'Response Rate (%)']].to_dict(orient="records"),
        "last_quarter": pq_df[['Purchase Last Quarter', 'Total Customers', 'Responded', 'Response Rate (%)']].to_dict(orient="records"),
        "product_usage": prod_df[['Product Category', 'Total Customers', 'Responded', 'Response Rate (%)']].to_dict(orient="records")
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Skin Clinic API is running"}

@app.get("/campaign-analysis")
def get_campaign_analysis():
    return run_campaign_analysis()

@app.get("/", response_class=HTMLResponse)
def home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Skin Clinic Campaign Analysis</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
            h2 { color: #2c3e50; }
            h3 { color: #34495e; margin-top: 30px; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; background: #fff; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
            th { background-color: #2c3e50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            button { padding: 12px 20px; font-size: 16px; background-color: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #219150; }
        </style>
    </head>
    <body>
        <h2>Skin Clinic Marketing Campaign Analysis</h2>
        <button onclick="loadAnalysis()">Load Campaign Analysis</button>

        <div id="results"></div>

        <script>
            function buildTable(title, data, columns) {
                let html = `<h3>${title}</h3><table><thead><tr>`;
                columns.forEach(col => { html += `<th>${col}</th>`; });
                html += `</tr></thead><tbody>`;

                data.forEach(row => {
                    html += `<tr>`;
                    columns.forEach(col => { html += `<td>${row[col]}</td>`; });
                    html += `</tr>`;
                });

                html += `</tbody></table>`;
                return html;
            }

            function loadAnalysis() {
                fetch('/campaign-analysis')
                    .then(response => response.json())
                    .then(data => {
                        let content = '';
                        content += buildTable('1. Gender vs Campaign Response', data.gender, ['Gender', 'Total Customers', 'Responded', 'Response Rate (%)']);
                        content += buildTable('2. Age Group vs Campaign Response', data.age_group, ['Age Group', 'Total Customers', 'Responded', 'Response Rate (%)']);
                        content += buildTable('3. Purchase in Last Quarter vs Campaign Response', data.last_quarter, ['Purchase Last Quarter', 'Total Customers', 'Responded', 'Response Rate (%)']);
                        content += buildTable('4. Product Usage vs Campaign Response', data.product_usage, ['Product Category', 'Total Customers', 'Responded', 'Response Rate (%)']);
                        
                        document.getElementById('results').innerHTML = content;
                    })
                    .catch(err => alert('Error loading data: ' + err));
            }
        </script>
    </body>
    </html>
    """
    return html_content
