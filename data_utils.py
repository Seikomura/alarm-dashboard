import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone


def load_data(start_date: str, end_date: str, verbose=True) -> pd.DataFrame:
    """
    Connects to MongoDB and loads data from the L1Signal_Pool collection between start_date and end_date.

    Args:
        start_date (str): Start date-time in format "YYYY-MM-DD HH:MM"
        end_date (str): End date-time in format "YYYY-MM-DD HH:MM"
        verbose (bool): Whether to print debug info

    Returns:
        pd.DataFrame: DataFrame containing MongoDB results
    """

    # ----- Step 1: Convert to UTC (local time - 7 hours) ----------------------
    start = datetime.strptime(start_date, "%Y-%m-%d %H:%M") - timedelta(hours=7)
    end = datetime.strptime(end_date, "%Y-%m-%d %H:%M") - timedelta(hours=7)
    start = start.replace(tzinfo=timezone.utc)
    end = end.replace(tzinfo=timezone.utc)

    # ----- Step 2: Connect to MongoDB -----------------------------------------
    mongo_uri = "mongodb://admin123:admin123@192.168.0.252/MTLINKi"
    client = MongoClient(mongo_uri)
    db = client["MTLINKi"]
    collection = db["L1Signal_Pool"]

    # ----- Step 3: Build query ------------------------------------------------
    query = {
        "updatedate": {
            "$gte": start,
            "$lte": end
        }
    }

    # ----- Step 4: Fetch and convert to DataFrame --------------------
    projection = {"_id": 0, "L1Name": 1, "signalname": 1, "value": 1, "updatedate": 1}
    cursor = collection.find(query, projection)
    data = list(cursor)
    df = pd.DataFrame(data)

    # ----- Step 5: Debug print ----------------------------------------
    if verbose:
        print("[DEBUG] Mongo query:", query)
        print("[DEBUG] docs fetched:", len(df))
        if not df.empty:
            print("[DEBUG] Unique L1Name ({}):".format(df["L1Name"].nunique()), df["L1Name"].unique().tolist())
            print("[DEBUG] First 5 rows:\n", df.head())

    return df


def export_to_excel(df, sd, st, ed, et):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"alarm_export_{timestamp}.xlsx"
    df.to_excel(filename, index=False)
    return dict(content=open(filename, "rb").read(), filename=filename)
