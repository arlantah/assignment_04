"""
payroll_app.py — the weekly payroll, for someone who has never opened a terminal.

Every Friday the office manager at Salt City Coffee exports the week's timesheet
from the point-of-sale system. This page turns it into a paycheck table and the
CSV the online payroll provider imports — without the manager touching pandas.

The app is mostly *assembly*: the roster is loaded from data/, the upload comes
from the page, and one call to `build_payroll` does all the work. What the page
adds is what a manager needs to trust the numbers: totals, a loud warning about
anything the pipeline could not match, the full lineage table, and the download.

Run it:  Run and Debug -> "Streamlit Run: Current File"   (see README Reference #1)
Test it: pytest tests/test_pipeline.py -k app
"""

import streamlit as st

from payroll import build_payroll, load_employees, load_timesheet, payroll_export


st.title("Payroll")
st.write(
    "Upload this week's timesheet to review payroll and download the provider's CSV."
)

employees = load_employees()
upload = st.file_uploader("Upload a weekly timesheet CSV", type="csv", key="timesheet")

if upload is not None:
    timesheet = load_timesheet(upload)
    payroll = build_payroll(timesheet, employees)
    payroll_date = payroll["payroll_date"].iloc[0]
    st.subheader(f"Pay period ending {payroll_date}")

    total_hours = payroll["hours_worked"].sum()
    total_pay = payroll["gross_pay"].sum()
    overtime = payroll[payroll["pay_type"] == "overtime"]
    unmatched = payroll[payroll["pay_type"] == "unmatched"]
    employees_paid = len(payroll[payroll["pay_type"] != "unmatched"])

    metrics = st.columns(4)
    metrics[0].metric("Employees paid", employees_paid)
    metrics[1].metric("Total hours", f"{total_hours:g}")
    metrics[2].metric("Total gross pay", f"${total_pay:,.2f}")
    metrics[3].metric("Overtime weeks", len(overtime))

    if len(unmatched) > 0:
        employee_ids = ", ".join(unmatched["employee_id"])
        st.warning(f"These employee IDs are not on the roster: {employee_ids}")
    else:
        st.success("All employees matched to the roster.")

    st.dataframe(payroll)
    export = payroll_export(payroll)
    st.download_button(
        "Download payroll CSV for the provider",
        data=export.to_csv(index=False),
        file_name=f"payroll_{payroll_date}.csv",
        mime="text/csv",
        key="download",
    )
