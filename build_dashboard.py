
import argparse
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.io as pio

C = {"blue":"#2878B5", "teal":"#1B998B", "orange":"#F28E2B", "red":"#D9534F"}
MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

def style(fig, title, subtitle):
    fig.update_layout(title={"text": title + "<br><sup>" + subtitle + "</sup>", "x": 0.02},
        template="plotly_white", height=430, font={"family":"Arial","size":12,"color":"#263238"},
        margin={"l":55,"r":25,"t":85,"b":60}, legend={"orientation":"h","y":1.02,"x":1,"xanchor":"right"})
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(gridcolor="#E8EDF3", automargin=True)
    return fig

def embed(fig):
    return pio.to_html(fig, full_html=False, include_plotlyjs=False,
        config={"responsive":True,"displaylogo":False,"scrollZoom":True})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--csv",default="hotel_bookings.csv")
    parser.add_argument("--output",default="hotel_booking_interactive_dashboard.html")
    args=parser.parse_args()
    if not Path(args.csv).exists():
        raise FileNotFoundError("Download hotel_bookings.csv from Kaggle and place it beside this script.")
    df=pd.read_csv(args.csv,low_memory=False)
    required={"hotel","is_canceled","lead_time","arrival_date_year","arrival_date_month","adr","market_segment","deposit_type","total_of_special_requests"}
    missing=required-set(df.columns)
    if missing: raise ValueError("Missing expected columns: "+", ".join(sorted(missing)))
    for col in ["is_canceled","lead_time","adr","total_of_special_requests"]:
        df[col]=pd.to_numeric(df[col],errors="coerce")
    df=df[df["adr"].isna() | (df["adr"]>=0)].copy()
    df["Cancellation status"]=df["is_canceled"].map({0:"Not cancelled",1:"Cancelled"}).fillna("Unknown")
    total=len(df); rate=df["is_canceled"].mean()*100
    avg_lead=df["lead_time"].mean(); avg_adr=df["adr"].mean()

    a=df.groupby("hotel")["is_canceled"].mean().mul(100).reset_index(name="Cancellation rate (%)")
    f1=px.bar(a,x="hotel",y="Cancellation rate (%)",color="hotel",text=a["Cancellation rate (%)"].map(lambda x:f"{x:.1f}%"),color_discrete_sequence=[C["blue"],C["teal"]],labels={"hotel":"Hotel type"})
    f1.update_traces(textposition="outside")
    style(f1,"1. Which hotel type has more cancellations?","Compare cancellation rates across hotel types.")

    monthly=df.groupby(["arrival_date_year","arrival_date_month"]).size().reset_index(name="Bookings")
    monthly=monthly[monthly["arrival_date_month"].isin(MONTHS)].copy()
    monthly["arrival_date_month"]=pd.Categorical(monthly["arrival_date_month"],categories=MONTHS,ordered=True)
    monthly=monthly.sort_values(["arrival_date_year","arrival_date_month"])
    f2=px.line(monthly,x="arrival_date_month",y="Bookings",color="arrival_date_year",markers=True,color_discrete_sequence=[C["blue"],C["orange"],C["teal"]],labels={"arrival_date_month":"Arrival month","arrival_date_year":"Arrival year"})
    style(f2,"2. When do guests arrive?","Monthly booking volume by year; toggle years using the legend.")

    lead=df[df["lead_time"].notna() & (df["lead_time"]<=df["lead_time"].quantile(.99))]
    f3=px.histogram(lead,x="lead_time",color="Cancellation status",nbins=45,barmode="overlay",opacity=.72,color_discrete_map={"Not cancelled":C["teal"],"Cancelled":C["red"]},labels={"lead_time":"Days between booking and arrival"})
    style(f3,"3. Does lead time differ by cancellation status?","Extreme lead times above the 99th percentile are omitted for readability.")

    points=df.dropna(subset=["lead_time","adr"])
    points=points.sample(n=min(10000,len(points)),random_state=42)
    f4=px.scatter(points,x="lead_time",y="adr",color="Cancellation status",opacity=.55,hover_data=["hotel","market_segment","deposit_type"],color_discrete_map={"Not cancelled":C["teal"],"Cancelled":C["red"]},labels={"lead_time":"Lead time (days)","adr":"Average daily rate"})
    style(f4,"4. How do lead time and room rate relate?","Hover over points for booking details; up to 10,000 records are shown.")

    box=df.dropna(subset=["adr"]).copy()
    box=box[box["adr"]<=box["adr"].quantile(.99)]
    f5=px.box(box,x="hotel",y="adr",color="Cancellation status",points=False,color_discrete_map={"Not cancelled":C["teal"],"Cancelled":C["red"]},labels={"hotel":"Hotel type","adr":"Average daily rate"})
    style(f5,"5. How do room rates vary across groups?","Compare rates by hotel and cancellation status.")

    cols=[c for c in ["is_canceled","lead_time","adr","adults","children","babies","previous_cancellations","booking_changes","days_in_waiting_list","total_of_special_requests"] if c in df.columns]
    corr=df[cols].apply(pd.to_numeric,errors="coerce").corr()
    f6=px.imshow(corr,text_auto=".2f",aspect="auto",color_continuous_scale="RdBu_r",zmin=-1,zmax=1,labels={"color":"Correlation"})
    style(f6,"6. Which numerical variables are related?","Correlation does not prove causation.")

    top=a.sort_values("Cancellation rate (%)",ascending=False).iloc[0]
    seg=df.groupby("market_segment")["is_canceled"].mean().mul(100).sort_values(ascending=False)
    findings=[
      f"Overall cancellation rate: {rate:.1f}% across {total:,} records.",
      f"{top['hotel']} has the higher observed cancellation rate ({top['Cancellation rate (%)']:.1f}%).",
      f"Average booking lead time is {avg_lead:.1f} days.",
      f"Average daily rate is {avg_adr:.2f}.",
      f"Highest observed cancellation share by market segment: {seg.index[0]} ({seg.iloc[0]:.1f}%). Check group sizes before comparing rates."
    ]
    kpis=[("Booking records",f"{total:,}"),("Cancellation rate",f"{rate:.1f}%"),("Average lead time",f"{avg_lead:.1f} days"),("Average daily rate",f"{avg_adr:.2f}")]
    cards="".join("<div class='kpi'><span>"+k+"</span><strong>"+v+"</strong></div>" for k,v in kpis)
    insights="".join("<li>"+x+"</li>" for x in findings)
    groups=[("Bookings and cancellations",embed(f1)+embed(f2)),("Booking behaviour and pricing",embed(f3)+embed(f4)+embed(f5)),("Relationships between variables",embed(f6))]
    sections="".join("<section><h2>"+h+"</h2><div class='grid'>"+charts+"</div></section>" for h,charts in groups)
    template="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hotel Booking Demand Dashboard</title><script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#263238;font-family:Arial,sans-serif}
header{background:#17324d;color:white;padding:28px max(20px,calc((100% - 1250px)/2))}header h1{margin:0 0 8px;font-size:34px}header p{margin:0;line-height:1.5}
main{max-width:1250px;margin:auto;padding:22px}.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}
.kpi,.panel,.grid>div{background:white;border-radius:12px;box-shadow:0 2px 9px #17324d12;overflow:hidden}.kpi{padding:18px}
.kpi span{display:block;color:#637381;font-size:13px;margin-bottom:8px}.kpi strong{font-size:25px;color:#17324d}
section{margin:24px 0}h2{color:#17324d}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:16px}
.panel{padding:20px}li{margin:9px 0;line-height:1.5}.note{font-size:13px;color:#637381;line-height:1.5}footer{text-align:center;padding:24px;color:#637381;font-size:12px}
</style></head><body><header><h1>Hotel Booking Demand</h1><p>Explore cancellation patterns, arrival seasonality, lead time, pricing, and variable relationships.<br>Hover, zoom, pan, and toggle chart legends to explore.</p></header>
<main><div class="kpis">__CARDS__</div><section><h2>Key observations</h2><div class="panel"><ul>__INSIGHTS__</ul><p class="note">Findings are descriptive, not causal. Selected charts omit extreme values for readability.</p></div></section>__SECTIONS__
<section><h2>How to explore</h2><div class="panel"><ul><li>Hover over chart marks to view values.</li><li>Drag to zoom; double-click to reset.</li><li>Click legend entries to show or hide groups.</li><li>Use chart controls to pan, zoom, or export images.</li></ul><p class="note">Source: Kaggle Hotel Booking Demand. Built with Python, Pandas, and Plotly.</p></div></section></main><footer>Hotel Booking Demand · Data Visualisation Project</footer></body></html>"""
    html=template.replace("__CARDS__",cards).replace("__INSIGHTS__",insights).replace("__SECTIONS__",sections)
    Path(args.output).write_text(html,encoding="utf-8")
    print(f"Dashboard created: {Path(args.output).resolve()}")
    print(f"Rows: {total:,}; columns: {df.shape[1]}; cancellation rate: {rate:.1f}%")

if __name__=="__main__": main()
