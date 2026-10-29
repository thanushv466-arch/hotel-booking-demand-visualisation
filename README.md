# Hotel Booking Demand — Interactive Data Visualisation

An interactive dashboard exploring hotel booking demand, cancellations, arrival seasonality, lead time, room rates, and numerical-variable relationships.

## Live dashboard

After enabling GitHub Pages, the dashboard will be available at:

`https://YOUR-GITHUB-USERNAME.github.io/hotel-booking-demand-visualisation/`

Replace `YOUR-GITHUB-USERNAME` with your GitHub username.

## Dashboard highlights

Six interactive Plotly charts:
1. Bar chart — cancellation rate by hotel type
2. Line chart — monthly booking volume by year
3. Histogram — lead-time distribution by cancellation status
4. Scatter plot — lead time versus average daily rate
5. Box plot — room-rate distribution by hotel and cancellation status
6. Heatmap — correlations among numerical variables

Use hover tooltips, zoom, pan, legend toggles, and chart image export. The dashboard also includes KPI cards and key observations.

## Dataset

Source: Kaggle Hotel Booking Demand dataset by Nuno Antonio, Ana de Almeida, and Luis Nunes, distributed via Kaggle:
https://www.kaggle.com/datasets/jessemostipak/hotel-booking-demand

The HTML dashboard was generated from the provided `hotel_bookings.csv` dataset (119,389 records read; 33 columns). The raw CSV is intentionally not included in this repository.

## Rebuild locally

1. Download `hotel_bookings.csv` from the dataset source.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Generate the dashboard:
   ```bash
   python build_dashboard.py --csv hotel_bookings.csv --output index.html
   ```
4. Commit and push the updated `index.html`.

The published HTML loads Plotly JavaScript from a CDN, so a visitor needs an internet connection for interactive charts.

## Publish with GitHub Pages

1. Create a **public** repository named `hotel-booking-demand-visualisation`.
2. Upload `index.html`, `build_dashboard.py`, `requirements.txt`, and this `README.md` to the repository root.
3. Open **Settings → Pages**.
4. Under **Build and deployment**, select **Deploy from a branch**.
5. Choose branch `main` and folder `/ (root)`, then click **Save**.
6. Wait for deployment, then open the URL shown in Settings → Pages.
7. Test the live page, especially hover tooltips, zoom, and legend toggles.

## Interpretation note

These are descriptive comparisons, not proof of causation. Some charts omit extreme values or sample records for readability; each chart explains the relevant limitation.
