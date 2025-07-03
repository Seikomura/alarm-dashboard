import dash
from dash import html, dcc, Input, Output, State, ctx, MATCH
import dash.dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from data_utils import load_data

app = dash.Dash(__name__)
app.title = "Machine Alarm Summary V 1.0.1"

# ------------------------------------------------------------------
# Helper: 15-minute dropdown
# ------------------------------------------------------------------
def generate_time_options():
    return [{"label": f"{h:02d}:{m:02d}", "value": f"{h:02d}:{m:02d}"}       # 00:00 … 23:45
            for h in range(24) for m in range(0, 60, 15)]

# ------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------
app.layout = html.Div([
    html.H4("Machine Alarm Summary"),

    # ------------ Date & Time picker row ---------------------------
    html.Div([
        # Start
        html.Div([
            dcc.DatePickerSingle(id="start-date", display_format="DD/MM/YYYY"),
            dcc.Dropdown(id="start-time", options=generate_time_options(), value="08:00"),
            html.Button("วันนี้", id="set-start-today")
        ], style={"display": "inline-block", "marginRight": "20px"}),

        # End
        html.Div([
            dcc.DatePickerSingle(id="end-date", display_format="DD/MM/YYYY"),
            dcc.Dropdown(id="end-time", options=generate_time_options(), value="08:00"),
            html.Button("วันนี้", id="set-end-today")
        ], style={"display": "inline-block", "marginRight": "20px"}),

        html.Button("Load Data", id="load-button")
    ], style={"marginBottom": "12px"}),

    # ------------ Checklist placeholder + spinner -----------------
    dcc.Loading(id="loading-spinner", type="circle",
                children=html.Div(id="alarm-checklist-div")),

    # ------------ Top-N selector -----------------------------------
    html.Div([
        html.Div("เลือกจำนวน Top N (สูงสุด 10):"),
        dcc.RadioItems(
            id="top-n", inline=True,
            options=[{"label": f"Top {n}", "value": n} for n in [3, 5, 10]],
            value=3
        )
    ], style={"marginTop": "12px"}),

    # ------------ Select / Deselect buttons ------------------------
    html.Div("เลือก Alarm ที่ต้องการดู Frequency:"),
    html.Button("เลือกทั้งหมด",  id="select-all"),
    html.Button("ยกเลิกทั้งหมด", id="deselect-all",
                style={"marginLeft": "10px", "marginBottom": "12px"}),

    # ------------ Action row (plot / clear / export) ---------------
    html.Div([
        html.Button("พอร์ตกราฟ", id="plot-button"),
        html.Button("ล้างข้อมูล", id="clear-button",   style={"marginLeft": "10px"}),
        html.Button("Export to Excel", id="export-button", style={"marginLeft": "10px"})
    ], style={"display": "flex", "justifyContent": "center",
              "alignItems": "center", "gap": "10px", "marginTop": "20px"}),

    # ------------ Summary tables + graph ---------------------------
    html.Div([
        html.Div(id="alarm-summary-tables", style={"width": "100%"}),
        dcc.Graph(id="alarm-bar-chart",
                  figure=go.Figure().update_layout(title="รอโหลดข้อมูล"))
    ]),

    dcc.Download(id="download-excel"),

    # ----- Auto-refresh timer -----
    dcc.Interval(
    id="interval-refresh",
    interval=30 * 60 * 1000,  # ทุก 30 นาที (หน่วยเป็นมิลลิวินาที)
    n_intervals=0
),

])

# ------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# Set today buttons
# ------------------------------------------------------------------
@app.callback(Output("start-date", "date"),
              Input("set-start-today", "n_clicks"), prevent_initial_call=True)
def set_today_start(_):
    return pd.Timestamp.now().strftime("%Y-%m-%d")

@app.callback(Output("end-date", "date"),
              Input("set-end-today", "n_clicks"), prevent_initial_call=True)
def set_today_end(_):
    return pd.Timestamp.now().strftime("%Y-%m-%d")

# ------------------------------------------------------------------
# Unified handler: Load / Plot / Clear / Auto-refresh
# ------------------------------------------------------------------
@app.callback(
    Output("alarm-checklist-div", "children"),
    Output("alarm-summary-tables", "children"),
    Output("alarm-bar-chart",     "figure"),
    Input("load-button",  "n_clicks"),
    Input("plot-button",  "n_clicks"),
    Input("clear-button", "n_clicks"),
    Input("interval-refresh", "n_intervals"),        # 👈 เพิ่มตัวนี้
    State("start-date", "date"), State("start-time", "value"),
    State("end-date",   "date"), State("end-time",   "value"),
    State("top-n",      "value"),
    State({"type": "alarm-checklist", "index": dash.ALL}, "value"),
    prevent_initial_call=True
)
def unified_handler(load_btn, plot_btn, clear_btn, n_intervals,
                    sd, st, ed, et, top_n, selected_lists):

    trig = ctx.triggered_id           # ดูว่าใครเป็นคนเรียก

    # ----- Clear ----------------------------------------------------
    if trig == "clear-button":
        return html.Div(), "", go.Figure().update_layout(title="รอโหลดข้อมูล")

    # ดึงข้อมูลช่วงที่เลือก (ใช้ verbose=False เพื่อไม่ spam log)
    df = load_data(f"{sd} {st}", f"{ed} {et}", verbose=False)

    # ----- Load (สร้าง checklist) ----------------------------------
    if trig == "load-button":
        if df.empty or "signalname" not in df.columns:
            return html.Div("ไม่พบข้อมูล"), dash.no_update, dash.no_update

        sigs    = sorted(df["signalname"].dropna().unique())
        per_col = 15
        cols    = [sigs[i:i+per_col] for i in range(0, len(sigs), per_col)]

        checklist = html.Div([
            html.Div([
                html.Div([        
                    html.Button("เลือกทั้งแถว", id={"type": "select-sub", "index": idx}, n_clicks=0),
                    html.Button("ไม่เลือกทั้งแถว", id={"type": "deselect-sub", "index": idx}, n_clicks=0),
                ], style={"display": "flex", "justifyContent": "space-between", "marginBottom": "4px"}),

                dcc.Checklist(
                    id={"type": "alarm-checklist", "index": idx},
                    options=[{"label": s, "value": s} for s in col],
                    value=col,
                    labelStyle={"display": "block"}
                )
            ],
                style={"border": "1px solid #ccc", "padding": "8px",
                       "minWidth": "260px", "maxWidth": "420px",
                       "overflowX": "auto", "marginRight": "20px"}
            )
            for idx, col in enumerate(cols)
        ], style={"display": "flex", "flexWrap": "nowrap",
                  "overflowX": "auto", "whiteSpace": "nowrap"})

        return checklist, dash.no_update, dash.no_update

    # ----- Plot & Auto-refresh -------------------------------------
    # ใช้ร่วมกันสำหรับ plot-button และ interval-refresh
    if trig in ("plot-button", "interval-refresh"):

        # ยังไม่มี checklist หรือยังไม่เลือก -> ไม่ทำอะไร
        if not selected_lists:
            return dash.no_update, dash.no_update, dash.no_update

        selected = [s for sub in selected_lists for s in sub]
        df       = df[df["signalname"].isin(selected)]

        if df.empty:
            no_data_fig = go.Figure().update_layout(title="ไม่พบข้อมูล")
            return dash.no_update, html.Div("ไม่พบข้อมูล"), no_data_fig

        group  = df.groupby(["L1Name", "signalname"]).size().reset_index(name="Frequency")
        top_df = (group.sort_values(["L1Name", "Frequency"], ascending=[True, False])
                       .groupby("L1Name").head(top_n).reset_index(drop=True))

        tables = [html.Div([
                    html.H5(l1),
                    dash.dash_table.DataTable(
                        columns=[{"name": c, "id": c} for c in g.columns],
                        data=g.to_dict("records"),
                        style_table={"overflowX": "auto"},
                        style_cell={"textAlign": "left"},
                        style_header={"fontWeight": "bold"})
                 ], style={"display": "inline-block", "margin": "10px"})
                 for l1, g in top_df.groupby("L1Name")]

        fig = px.bar(top_df, x="L1Name", y="Frequency",
                     color="signalname", barmode="group",
                     title="Top Alarm Frequencies (Auto-refresh)")

        # ไม่แตะ checklist div
        return dash.no_update, tables, fig

    # กรณีอื่น (สำรอง)
    return dash.no_update, dash.no_update, dash.no_update

# ------------------------------------------------------------------
# Select / Deselect all
# ------------------------------------------------------------------
@app.callback(
    Output({"type": "alarm-checklist", "index": dash.ALL}, "value", allow_duplicate=True),
    Input("select-all",    "n_clicks"),
    Input("deselect-all",  "n_clicks"),
    State({"type": "alarm-checklist", "index": dash.ALL}, "options"),
    prevent_initial_call=True
)
def toggle_all(sel, desel, options):
    if ctx.triggered_id == "select-all":
        return [[o["value"] for o in opts] for opts in options]
    if ctx.triggered_id == "deselect-all":
        return [[] for _ in options]
    return dash.no_update

# ------------------------------------------------------------------
# Check Box each column Select / Deselect all
# ------------------------------------------------------------------
@app.callback(
    Output({"type": "alarm-checklist", "index": MATCH}, "value", allow_duplicate=True),
    Input({"type": "select-sub",   "index": MATCH}, "n_clicks"),
    Input({"type": "deselect-sub", "index": MATCH}, "n_clicks"),
    State({"type": "alarm-checklist", "index": MATCH}, "options"),
    prevent_initial_call=True
)
def toggle_sub_checklist(sel, desel, options):
    if ctx.triggered_id["type"] == "select-sub":
        return [o["value"] for o in options]
    elif ctx.triggered_id["type"] == "deselect-sub":
        return []
    return dash.no_update

# ------------------------------------------------------------------
# Export to Excel
# ------------------------------------------------------------------
@app.callback(
    Output("download-excel", "data"),
    Input("export-button", "n_clicks"),
    State("start-date", "date"), State("start-time", "value"),
    State("end-date",   "date"), State("end-time",   "value"),
    State({"type": "alarm-checklist", "index": dash.ALL}, "value"),
    prevent_initial_call=True
)
def export_to_excel(_, sd, st, ed, et, selected_lists):
    df = load_data(f"{sd} {st}", f"{ed} {et}")
    if df.empty:
        return dash.no_update

    selected = [s for sub in selected_lists for s in sub]
    df       = df[df["signalname"].isin(selected)]

    # ---------- ✨ จัดคอลัมน์ให้อยู่ในรูป export-friendly ----------
    df = df[["L1Name", "signalname", "value", "updatedate"]].copy()

    # แปลง updatedate (UTC) → string local-time เพื่อให้ XlsxWriter เขียนได้
    # ก่อน (ทำให้ error)
# df["updatedate"] = (df["updatedate"]
#                     .dt.tz_convert("Asia/Bangkok")
#                     .dt.strftime("%Y-%m-%d %H:%M:%S"))

# หลัง (ปลอดภัยกับทั้ง tz-naive และ tz-aware)
    df["updatedate"] = (pd.to_datetime(df["updatedate"], utc=True)          # ① บังคับให้เป็น UTC-aware
                    .dt.tz_convert("Asia/Bangkok")                          # ② แปลงเป็นเวลาไทย
                    .dt.strftime("%Y-%m-%d %H:%M:%S"))                      # ③ แปลงเป็นสตริง

    # ---------------------------------------------------------------

    # 🟡 ล้างอักขระต้องห้ามออกจาก sheet name
    safe_st = st.replace(":", "-")
    safe_et = et.replace(":", "-")
    sheet   = f"Alarm Summary {sd}-{safe_st} to {ed}-{safe_et}"[:31]

    output = io.BytesIO()
    with pd.ExcelWriter(
                        output,
                        engine="openpyxl",                        
                    ) as writer:
                    df.to_excel(writer, index=False, sheet_name=sheet)
    output.seek(0)

    fname = f"alarm_summary_{sd}_{safe_st}_to_{ed}_{safe_et}.xlsx"
    return dcc.send_bytes(output.read(), fname)



# ------------------------------------------------------------------

# -------------------------------
# Expose Flask app for Gunicorn
server = app.server     # ✅ ใช้ Flask server จริง
# -------------------------------



if __name__ == "__main__":
    app.run(debug=True, port=8050)
